from .models import Visitor
from .serializers import VisitorSerializer, VisitorInfoSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser, AllowAny

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
    permission_classes = []
