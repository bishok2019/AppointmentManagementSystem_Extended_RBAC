from .models import Visitor
from .serializers import VisitorSerializer, VisitorInfoSerializer, RescheduleSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from host_app.permissions import HasRolePermission
# Create your views here.
class RegisterVisitorView(APIView):
    serializer_class = VisitorSerializer
    permission_classes = [AllowAny]
    def post(self, request, pk=None):
        registration_serializer = VisitorSerializer(data=request.data)
        if registration_serializer.is_valid():
            visitor = registration_serializer.save()
            display_serializer = VisitorInfoSerializer(visitor)
            return Response({'msg':'Meeting Appointed','data':display_serializer.data}, status=status.HTTP_201_CREATED)
        return Response(registration_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VisitorView(ListAPIView):
    queryset = Visitor.objects.all()
    serializer_class = VisitorInfoSerializer
    permission_classes = [HasRolePermission]
    required_permission =  'can_read_visitor'

class UpdateVisitorView(APIView):
    serializer_class = VisitorSerializer
    permission_classes = [HasRolePermission]
    required_permission =  'can_update_visitor'
    def get(self, request, pk=None):
        if pk is not None:
            visitors = Visitor.objects.filter(pk=pk).first()
            if visitors:
                serializer = VisitorSerializer(visitors)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"msg": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)
    
    def patch(self, request, pk=None, format=None):
        visitor = Visitor.objects.filter(pk=pk).first()
        if not visitor:
            return Response({"msg": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = VisitorSerializer(visitor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'Appointment successfully rescheduled!'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)        

class YourAppointmentView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RescheduleSerializer
    def get(self, request, pk=None):
        host = request.user
        visitor = Visitor.objects.filter(visiting_to=host)
        if visitor.exists():
            serializer = VisitorInfoSerializer(visitor, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"msg": "You have no appointments."}, status=status.HTTP_404_NOT_FOUND)

class UpdateYourAppointmentView(APIView):
    # permission_classes = [HasRolePermission]
    serializer_class = RescheduleSerializer
    # required_permission = 'can_update_appointment'

    def get(self, request, pk=None):
        host = request.user
        if pk is not None:
            visitors = Visitor.objects.filter(pk=pk, visiting_to=host).first()
            if visitors:
                serializer = RescheduleSerializer(visitors)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"msg": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, pk=None, format=None):
        host = request.user
        visitor = Visitor.objects.filter(pk=pk, visiting_to=host).first()
        if not visitor:
            return Response({"msg": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = RescheduleSerializer(visitor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'Appointment successfully rescheduled!'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)