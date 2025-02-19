from .models import Role,Permission,PermissionCategory
from rest_framework import serializers
from django.db import transaction
from django.contrib.auth import get_user_model as User


class RoleCreateSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(queryset=Permission.objects.all(), many=True)
    class Meta:
        model = Role
        fields = ['name', 'permissions']
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['created_by'] = user
        with transaction.atomic():
            role = Role.objects.create(**validated_data)
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
    
    def update(self, instance, validated_data):
        user = self.context['request'].user
        validated_data['updated_by'] = user
        return instance