from django.urls import path
from . import views

urlpatterns = [
    path('register/department/', views.DepartmentRegistrationView.as_view(), name='register-depart' ),
    path('register/user/', views.UserRegistrationView.as_view(), name='register-user' ),
    path('login/', views.UserLoginView.as_view(), name='login-user' ),
    path('', views.GetUserInfo.as_view(), name='get-User-info' ),
    path('appointments/', views.RescheduleVisitor.as_view(), name='get-appointment-all' ),
    path('appointments/<int:pk>/', views.RescheduleVisitor.as_view(), name='get-appointment-all' ),
    path('user/<int:pk>/', views.UpdateUserView.as_view(), name='update-user-by-id' ),
    path('user/', views.UpdateUserView.as_view(), name='get-all-user' ),

]