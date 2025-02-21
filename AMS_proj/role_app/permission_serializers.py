#serializers.py
from .models import PermissionCategory, Permission
from django.db import transaction
from rest_framework import serializers
from django.contrib.auth import get_user_model as User

class PermissionCategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermissionCategory
        fields = ['name']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['created_by'] = user
        with transaction.atomic():
            permissioncategory = PermissionCategory.objects.create(**validated_data)
            # permissioncategory = super().create(validated_data)
            methods = ["create","update", "read","delete"]
            for method in methods:
                permission = Permission.objects.create(
                    name=f"can {method} {permissioncategory.name.lower()}",
                    code=f"can_{method}_{permissioncategory.name.lower()}",
                    permissioncategory=permissioncategory,
                )
                permission.save()
            return permissioncategory


class PermissionCategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermissionCategory
        fields = ['id', 'name','is_active']


class PermissionCategoryDetailSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = PermissionCategory
        fields = ['id', 'name','is_active','permissions']

class PermissionCategoryDetailSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = PermissionCategory
        fields = ['id', 'name', 'is_active', 'permissions']

    def get_permissions(self, obj):
        return obj.permissions.values('id', 'name', 'code')
    
    def update(self, instance, validated_data):
        user = self.context['request'].user
        validated_data['updated_by'] = user
        with transaction.atomic():
            if 'name' in validated_data:    
                instance = super().update(instance, validated_data)
                methods = ["create","update", "read","delete"]
                for method in methods:
                    permission = Permission.objects.filter(permissioncategory=instance)
                    permission.update(
                        name=f"{method} {instance.name.lower()}",
                        code=f"{method}_{instance.name.lower()}",
                    )
                return instance
            else:
                return super().update(instance, validated_data)