from django.urls import path
from . import views

urlpatterns = [
    path('visitor/', views.VisitorView.as_view(), name='get-visitor' ),
    path('', views.RegisterVisitorView.as_view(), name='register-visitor' ),
]