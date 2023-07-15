from django.contrib.auth.models import User, Group
from friendlyfl.router.models import Site, Project, ProjectParticipant, Run
from friendlyfl.router.serializers import UserSerializer, GroupSerializer
from friendlyfl.router.serializers import SiteSerializer, ProjectSerializer, ProjectParticipantSerializer, RunSerializer
from rest_framework import viewsets, mixins, generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.utils import timezone


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


class ProjectParticipantViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = ProjectParticipant.objects.all()
    serializer_class = ProjectParticipantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


class RunViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Run.objects.all()
    serializer_class = RunSerializer
    permission_classes = [permissions.IsAuthenticated]

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
