from django.urls import path
from .views import (
    BlogListCreateAPIView, 
    BlogDetailAPIView, 
    BlogUserListView, 
    RegisterUserAPIView,
    
)

urlpatterns = [
    path('register/', RegisterUserAPIView.as_view(), name='register'),
    path('blogs/', BlogListCreateAPIView.as_view(), name='blog-list'),
    path('blogs/<int:pk>/', BlogDetailAPIView.as_view(), name='blog-detail'),
    path('users/', BlogUserListView.as_view(), name='blog-users'),
]

