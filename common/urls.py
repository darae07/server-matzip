from django.urls import path, include
from .views import ProfileUpdateAPI

urlpatterns = [
    path('auth/profile/<int:user_pk>/update/', ProfileUpdateAPI.as_view()),
]