#role_serializers.py
from .models import Role,Permission,PermissionCategory
from rest_framework import serializers
from django.db import transaction
from django.contrib.auth import get_user_model as User

class RoleCreateSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(queryset=Permission.objects.all(), many=True)
    class Meta:
        model = Role
        fields = ['name', 'permissions', 'created_by', 'updated_by', 'is_active']
        read_only_fields =['created_by', 'updated_by']
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['created_by'] = user
        # Extract permissions from validated_data
        permissions = validated_data.pop('permissions',[])
        # creating the role without permissions
        # user = self.context['request'].user
        # validated_data['created_by'] = user
        with transaction.atomic():
            role = Role.objects.create(**validated_data)
            #assigning permissions using .set()
            role.permissions.set(permissions)
        return role

class RoleListSerializer(serializers.ModelSerializer):  
    class Meta:
        model = Role
        fields = ['id', 'name', 'is_active', 'created_by', 'updated_by']

class RoleDetailSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()
    created_by = serializers.CharField(source='created_by.username', read_only=True)
    updated_by = serializers.CharField(source='updated_by.username', read_only=True)
    
    class Meta:
        model = Role
        fields = ['id', 'name', 'is_active', 'permissions', 'created_by', 'updated_by']
    
    def get_permissions(self, obj):
        return obj.permissions.values('id', 'name', 'code')
    
class RoleUpdateSerializer(serializers.ModelSerializer):
    # permissions = serializers.PrimaryKeyRelatedField(queryset=Permission.objects.all(), many=True, source='permission.name')
    created_by = serializers.CharField(source='created_by.username', read_only=True)
    updated_by = serializers.CharField(source='updated_by.username', read_only=True)
    class Meta:
        model = Role
        fields = ['id', 'name', 'is_active', 'permissions','created_by', 'updated_by']


    def update(self, instance, validated_data):
        validated_data['updated_by'] = self.context['request'].user
        permissions = validated_data.pop('permissions', None)

        with transaction.atomic():
            
            instance = super().update(instance, validated_data)
            if permissions is not None:
                instance.permissions.set(permissions)

        return instance