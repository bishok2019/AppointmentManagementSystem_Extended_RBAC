from rest_framework import serializers
from .models import User, Department
from django.contrib.auth import authenticate
from visitor_app.models import Visitor
from role_app.models import Role
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), required=True, write_only = True)
    depart = serializers.CharField(source='department.name', read_only=True)
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), required=False, allow_null=True) 
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password','department','depart','role')
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        host = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            department=validated_data['department']
        )
        return host
 
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(email=email, password=password)

            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            attrs['user'] = user
            return attrs
        raise serializers.ValidationError('Must include "email" and "password".')
    
class VisitorInfoSerializer(serializers.ModelSerializer):
    department = serializers.CharField(source='visiting_to.department.name', read_only=True)
    visiting_to = serializers.CharField(source='visiting_to.username', read_only=True)

    class Meta:
        model = Visitor
        fields = ['id','name', 'email','photo','phone_num','status','visiting_to', 'meeting_date', 'meeting_time','reason','department',]
        read_only_fields = ['status']
        
class RescheduleSerializer(serializers.ModelSerializer):
    visiting_to = serializers.CharField(source='visiting_to.username')
    class Meta:
        model = Visitor
        fields = ['id','meeting_date', 'meeting_time','status','visiting_to']
        read_only_fields = ['id','visiting_to']

class UserUpdateSerializer(serializers.ModelSerializer):
    department = serializers.CharField(source='visiting_to.department.name', read_only=True)
    action = serializers.CharField(source='role.name', default="", read_only=True)

    class Meta:
        model = User
        fields = ['id','username','department','email','role','is_active','action']
        read_only_fields = ['id', 'username']