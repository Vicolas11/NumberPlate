from django.urls import path
from . import views
# from .anpr import detect

urlpatterns = [
    path('user/register/', views.RegisterView.as_view(), name='register'),
    path('user/signin/', views.SigninView.as_view(), name='login'),
    path('user/sigout/', views.SignoutView.as_view(), name='logout'),
    path('user/profile_update/', views.ProfileUpdateView.as_view(), name='profile-update-api'),
    path('user/change_password/', views.ChangePasswordView.as_view(), name='change-password-api'),
    # path('user/detect/', detect, name='detect'),
]
