from .models import Role,Permission,PermissionCategory
from rest_framework import serializers
from django.db import transaction
from django.contrib.auth import get_user_model as User


class RoleCreateSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(queryset=Permission.objects.all(), many=True)
    class Meta:
        model = Role
        fields = ['name', 'permissions']
    
    # def create(self, validated_data):
    #     # Extract permissions from validated_data
    #     permissions = validated_data.pop('permissions',[])
    #     # creating the role without permissions
    #     user = self.context['request'].user
    #     validated_data['created_by'] = user
    #     role = Role.objects.create(**validated_data)
    #     #assigning permissions using .set()
    #     role.permissions.set(permissions)
    #     return role
    
    def create(self, validated_data):
        # Extract permissions from validated_data
        permissions = validated_data.pop('permissions',[])
        # creating the role without permissions
        user = self.context['request'].user
        validated_data['created_by'] = user
        with transaction.atomic():
            role = Role.objects.create(**validated_data)
            #assigning permissions using .set()
            role.permissions.set(permissions)
            return role

class RoleListSerializer(serializers.ModelSerializer):  
    class Meta:
        model = Role
        fields = ['id', 'name', 'is_active']

class RoleDetailSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = ['id', 'name', 'is_active', 'permissions']
    
    def get_permissions(self, obj):
        return obj.permissions.values('id', 'name', 'code')
    
    # def update(self, instance, validated_data):
    #     user = self.context['request'].user
    #     validated_data['updated_by'] = user
    #     return instance

    def update(self, instance, validated_data):
        user = self.context['request'].user
        permissions = validated_data.pop('permissions', None)
        instance.name = validated_data.get('name', instance.name)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.updated_by = user
        if permissions is not None:
            instance.permissions.set(permissions)
        instance.save()
        return instance