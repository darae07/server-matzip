from django.urls import path, include
from .views import RegistrationAPI, LoginAPI, UserAPI, ProfileUpdateAPI

urlpatterns = [
    path('auth/register/', RegistrationAPI.as_view()),
    path('auth/login/', LoginAPI.as_view()),
    path('auth/user/', UserAPI.as_view()),
    path('auth/profile/<int:user_pk>/update/', ProfileUpdateAPI.as_view()),
]