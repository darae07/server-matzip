from django.urls import path
from . import views


urlpatterns = [
    path('', views.StoreList.as_view(), name='index'),
    path('<int:pk>/', views.StoreDetail.as_view(), name='detail')
]
