from django.urls import path
from . import views

urlpatterns = [
    path('department/register/', views.DepartmentRegistrationView.as_view(), name='register-depart' ),
    path('department/', views.GetDepartmentView.as_view(), name='get-depart' ),
    path('department/<int:pk>', views.UpdateDepartmentView.as_view(), name='update-depart' ),

    path('user/register/', views.UserRegistrationView.as_view(), name='register-user' ),
    path('login/', views.UserLoginView.as_view(), name='login-user' ),
    path('', views.GetUserInfo.as_view(), name='get-User-info' ),

    path('user/', views.GetUserView.as_view(), name='get-all-user' ),
    path('user/<int:pk>/', views.UpdateUserView.as_view(), name='update-user-by-id' ),

    # path('appointments/', views.RescheduleVisitor.as_view(), name='get-appointment-all' ),
    # path('appointments/<int:pk>/', views.RescheduleVisitor.as_view(), name='get-appointment-by-id' ),
    

]