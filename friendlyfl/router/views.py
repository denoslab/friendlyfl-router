from uuid import UUID

from django.contrib.auth.models import User, Group
from django.db import transaction, DatabaseError
from django.utils import timezone
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets, mixins, generics
from rest_framework.decorators import action
from rest_framework.response import Response

from friendlyfl.router.models import Site, Project, ProjectParticipant, Run
from friendlyfl.router.serializers import SiteSerializer, \
    ProjectSerializer, ProjectParticipantSerializer, \
    ProjectParticipantCreateSerializer, RunSerializer, \
    RunRetrieveSerializer
from friendlyfl.router.serializers import UserSerializer, GroupSerializer
from friendlyfl.utils import display_util


def validate_uuid4(uuid_string):
    """
    Validate that a UUID string is in
    fact a valid uuid4.
    Happily, the uuid module does the actual
    checking for us.
    It is vital that the 'version' kwarg be passed
    to the UUID() call, otherwise any 32-character
    hex string is considered valid.
    """

    try:
        val = UUID(uuid_string, version=4)
    except ValueError:
        # If it's a value error, then the string
        # is not a valid hex code for a UUID.
        return False

    return True


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class SiteViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['GET'], url_path='lookup')
    def lookup_sites_by_uid(self, request):
        """
        Look up a site by its uid.
        """
        uid_param = request.GET.get('uid', None)
        if not validate_uuid4(uid_param):
            return Response("Invalid uid", status=status.HTTP_400_BAD_REQUEST)
        try:
            queryset = Site.objects.get(uid=uid_param)
        except Site.DoesNotExist:
            return Response("Site not found", status=status.HTTP_404_NOT_FOUND)
        serializer = SiteSerializer(queryset)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'], url_path='heartbeat')
    def heartbeat(self, request):
        """
        Sync heartbeat
        """

        uid_param = request.data.get('uid', None)
        status_param = request.data.get('status', None)

        if not validate_uuid4(uid_param):
            return Response("Invalid uid", status=status.HTTP_400_BAD_REQUEST)

        if not status_param in Site.SiteStatus:
            return Response("Status not supported", status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                site = Site.objects.select_for_update().get(uid=uid_param)
                site.status = status_param
                site.save()
            return Response(status=status.HTTP_202_ACCEPTED)
        except DatabaseError:
            return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, partial=True)

        if serializer.is_valid():
            serializer.create_with_participant(request.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'], url_path='lookup')
    def lookup_projects_by_site_id(self, request):
        """
        Look up ProjectParticipant by site ID/name.
        All projects this site is involved will be returned.
        """
        site_id_param = request.GET.get('site_id', None)
        name_param = request.GET.get('name', None)
        if site_id_param:
            try:
                queryset = ProjectParticipant.objects.filter(
                    site=site_id_param)
            except ProjectParticipant.DoesNotExist:
                return Response("ProjectParticipant not found", status=status.HTTP_404_NOT_FOUND)
            serializer = ProjectParticipantSerializer(queryset, many=True)
        else:
            try:
                queryset = Project.objects.get(name=name_param)
            except Project.DoesNotExist:
                return Response("Project not found", status=status.HTTP_404_NOT_FOUND)
            serializer = ProjectSerializer(queryset, many=False)
        return Response(serializer.data)


class ProjectParticipantViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = ProjectParticipant.objects.all()
    serializer_class = ProjectParticipantSerializer
    create_serializer_class = ProjectParticipantCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            if hasattr(self, 'create_serializer_class'):
                return self.create_serializer_class
        return super(ProjectParticipantViewSet, self).get_serializer_class()

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=['GET'], url_path='lookup')
    def get_participants_by_project(self, request):
        """
        Look up participants by project id.
        """
        project_id = request.GET.get('project', None)
        queryset = ProjectParticipant.objects.filter(project_id=project_id)
        participants_data = ProjectParticipantSerializer(
            queryset, many=True).data
        return Response(participants_data)


class RunViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Run.objects.all()
    serializer_class = RunSerializer
    retrieve_serializer_class = RunRetrieveSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            if hasattr(self, 'retrieve_serializer_class'):
                return self.retrieve_serializer_class
        return super(RunViewSet, self).get_serializer_class()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = {
            "log": request.data.get('log', None),
            "artifacts": request.data.get('artifacts', None),
        }
        serializer = self.serializer_class(
            instance=instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['PUT'], url_path='status')
    def update_status(self, request, pk=None):
        instance = self.get_object()
        data = {
            "status": request.data.get('status', None),
        }
        serializer = self.serializer_class(
            instance=instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.update_status(instance, data)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'], url_path='lookup')
    def lookup_runs_by_project_id(self, request):
        """
        Look up runs by project id.
        """
        project_id = request.GET.get('project', None)
        queryset = Run.objects.filter(project_id=project_id)
        serializer = RunSerializer(queryset, many=True)
        dic = display_util.sort_runs(serializer.data)
        return Response(dic)


class BulkCreateRunAPIView(generics.ListCreateAPIView):
    # serializer_class = RunSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        project_id = request.data.get('project', None)
        project = Project.objects.get(id=project_id)
        if project_id and project:
            curr_time = timezone.now()
            project.batch += 1
            project.save()
            records_to_create = []
            pps = ProjectParticipant.objects.filter(project=project_id)
            for pp in pps:
                data = {
                    "project": project,
                    "participant": pp,
                    "role": pp.role,
                    "status": Run.RunStatus.STANDBY,
                    "tasks": project.tasks,
                    "batch": project.batch,
                    "created_at": curr_time,
                    "updated_at": curr_time
                }
                records_to_create.append(data)
            created_records = Run.objects.bulk_create(
                [Run(**item) for item in records_to_create], batch_size=100)

            if created_records:
                return Response(status=status.HTTP_201_CREATED)
            else:
                return Response("Error while creating runs", status=status.HTTP_400_BAD_REQUEST)
        return Response("project not found", status=status.HTTP_400_BAD_REQUEST)
