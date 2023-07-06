from django.contrib.auth.models import User, Group
from rest_framework import serializers
from friendlyfl.router.models import Site, Project
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
    name = serializers.CharField(required=True, allow_blank=False, max_length=100)
    description = serializers.CharField(style={'base_template': 'textarea.html'})
    uid = serializers.UUIDField(format='hex_verbose', read_only=True)
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
        instance.description = validated_data.get('description', instance.code)
        instance.updated_at = datetime.now()
        instance.save()
        return instance


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'site', 'tasks', 'created_at', 'updated_at']
