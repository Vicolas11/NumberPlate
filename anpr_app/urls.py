from django.urls import path
from . import views
from django.views.generic import TemplateView
from django.conf import settings


app_name = 'recognize'
urlpatterns = [
    path('dashboard', views.DashBoardView.as_view(), name='dashboard'),    
    path('signin/user/', views.LoginTempView.as_view(), name='signin_user'),
    path('signup/user/', views.RegistrationTempView.as_view(), name='signup_user'),
    path('image/upload/', views.plate_number_processed, name='image_upload'),
    path('logout', views.logout_request, name= "logout"),
]
