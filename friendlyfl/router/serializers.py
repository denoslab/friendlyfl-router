from django.contrib.auth.models import User, Group
from rest_framework import serializers
from friendlyfl.router.models import Site, Project, ProjectParticipant
import uuid


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class SiteSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(
        required=True, allow_blank=False, max_length=100)
    description = serializers.CharField(
        style={'base_template': 'textarea.html'})
    uid = serializers.UUIDField(format='hex_verbose', read_only=True)
    status = serializers.CharField(source='get_status_display', read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        """
        Create and return a new `Site` instance, given the validated data.
        """
        return Site.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Site` instance, given the validated data.
        """
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.updated_at = datetime.now()
        instance.save()
        return instance

    class Meta:
        model = Site
        fields = ['id', 'name', 'description', 'uid',
                  'status', 'created_at', 'updated_at']
        create_only_fields = ('uid',)


class ProjectSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(
        required=True, allow_blank=False, max_length=100)
    description = serializers.CharField(
        style={'base_template': 'textarea.html'})
    site = serializers.PrimaryKeyRelatedField(
        many=False, queryset=Site.objects.all())
    tasks = serializers.JSONField(
        binary=False, default='{}', initial='{}', encoder=None)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        """
        Create and return a new `Project` instance, given the validated data.
        """
        return Project.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Project` instance, given the validated data.
        """
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.updated_at = datetime.now()
        instance.save()
        return instance

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'site',
                  'tasks', 'created_at', 'updated_at']
        create_only_fields = ('site', 'tasks')


class ProjectParticipantSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    site = serializers.PrimaryKeyRelatedField(
        many=False, queryset=Site.objects.all())
    project = serializers.PrimaryKeyRelatedField(
        many=False, queryset=Project.objects.all())
    role = serializers.CharField(source='get_role_display')
    notes = serializers.CharField(style={'base_template': 'textarea.html'})
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        """
        Create and return a new `ProjectParticipant` instance, given the validated data.
        """
        return ProjectParticipant.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `ProjectParticipant` instance, given the validated data.
        """
        instance.notes = validated_data.get('notes', instance.code)
        instance.updated_at = datetime.now()
        instance.save()
        return instance

    class Meta:
        model = ProjectParticipant
        fields = ['id', 'site', 'project', 'role',
                  'notes', 'created_at', 'updated_at']
        create_only_fields = ('site', 'project')
