from django.shortcuts import render
from .serializers import DepartmentSerializer,UserSerializer,LoginSerializer, RescheduleSerializer, VisitorInfoSerializer, UserUpdateSerializer
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .permissions import IsAdmin, IsAdminOrManager, IsAdminOrManagerOrHost, IsManager, IsHost, IsStaff, IsAllowedUserType
from visitor_app.models import Visitor
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import User
# Create your views here.

class GetUserInfo(APIView):
    permission_classes=[IsAllowedUserType]
    serializer_class = UserSerializer
    def get(self, request):
        host= request.user
        serializer = UserSerializer(host)
        return Response(serializer.data)

class DepartmentRegistrationView(APIView):
    permission_classes = [IsAdmin]
    serializer_class = DepartmentSerializer
    
    def post(self, request):
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            department = serializer.save()
            return Response({'status': 'success','message': 'Department created successfully.','data': DepartmentSerializer(department).data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            host = serializer.save()
            return Response({'status': 'success','message': 'User created successfully.','data': UserSerializer(host).data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserLoginView(APIView):
    permission_classes = []
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data,context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            return Response({
                'status': 'success',
                'message': 'Login successful',
                'data': {
                    'user': UserSerializer(user).data
                }
            }, status=status.HTTP_200_OK)
        
        return Response({
            'status': 'error',
            'message': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class RescheduleVisitor(APIView):
    permission_classes = [IsHost]
    serializer_class = RescheduleSerializer

    def get(self, request,pk=None):
        host = request.user
        if pk is not None:
            visitors = Visitor.objects.filter(pk=pk, visiting_to=host)
            if visitors.exists():
                serializer = RescheduleSerializer(visitors, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"msg": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)

        visitor = Visitor.objects.filter(visiting_to=host)
        if visitor.exists():
            serializer = VisitorInfoSerializer(visitor, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"msg": "You have no appointments."}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, pk=None, format=None):
        host = request.user
        visitor = Visitor.objects.filter(pk=pk, visiting_to=host).first()
        if not visitor:
            return Response({"msg": "Appointment not found."},status=status.HTTP_404_NOT_FOUND)
        serializer = RescheduleSerializer(visitor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'Appointment successfully rescheduled!'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def delete(self, request, pk=None, format=None):
    #     host = request.user
    #     visitor = Visitor.objects.filter(pk=pk,visiting_to=host)
    #     if not visitor:
    #         return Response({"msg": "Appointment not found."},status=status.HTTP_404_NOT_FOUND)
    #     if visitor.visiting_to != request.user:
    #         return Response({"msg": "You do not have permission to delete this appointment."},status=status.HTTP_403_FORBIDDEN)
    #     visitor.delete()
    #     return Response({'msg': 'Appointment successfully deleted!'}, status=status.HTTP_204_NO_CONTENT)

class UpdateUserView(APIView):
    permission_classes = [IsAdminOrManager]
    serializer_class = UserUpdateSerializer

    def get(self, request, pk=None):
        if pk is not None:
            user = User.objects.filter(pk=pk)
            if user.exists():
                serializer = UserUpdateSerializer(user, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"msg": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)
        user = User.objects.all()
        if user.exists():
            serializer = UserUpdateSerializer(user, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"msg": "You have no appointments."}, status=status.HTTP_404_NOT_FOUND)
    
    # def patch(self, request, pk=None, format=None):
    #     user = User.objects.filter(pk=pk).first()
    #     if not user:
    #         return Response({"msg": "User not found."},status=status.HTTP_404_NOT_FOUND)
    #     serializer = UserUpdateSerializer(user, data=request.data, partial=True)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response({'msg': 'User successfully updated!'}, status=status.HTTP_200_OK)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None, format=None):
        user_to_update = User.objects.filter(pk=pk).first()
        if not user_to_update:
            return Response({"msg": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check the logged-in user's role
        logged_in_user = request.user

        # Admin can update Manager and Staff
        if logged_in_user.user_type == 'ADMIN':
            pass

        # Manager can only update Staff
        elif logged_in_user.user_type == 'MANAGER':
            if user_to_update.user_type == 'ADMIN':
                return Response(
                    {"msg": "Managers are not allowed to update Admins."},
                    status=status.HTTP_403_FORBIDDEN
                )
            if 'user_type' in request.data and 'user_type' in request.data == 'ADMIN' or 'MANAGER':
            # if 'user_type' in request.data and request.data['user_type'] == 'ADMIN' or 'MANAGER':
                return Response({"msg":"Only Admin can perform this action."})

        # Other roles or STaff cannot update any user
        else:
            return Response({"msg": "You do not have permission to update users."}, status=status.HTTP_403_FORBIDDEN)

        # Perform the update
        serializer = UserUpdateSerializer(user_to_update, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'User successfully updated!'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)