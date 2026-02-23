from django.urls import path
from .views import (
    BlogListCreateAPIView, 
    BlogDetailAPIView, 
    BlogUserListView, 
    RegisterUserAPIView,
    BlogFrontendView,
    BlogCategoryListView,
    BlogTagListView,
    BlogDetailPageView,
)

urlpatterns = [
    path('register/', RegisterUserAPIView.as_view(), name='register'),
    path('blogs/', BlogListCreateAPIView.as_view(), name='blog-list'),
    path('blogs/<int:pk>/', BlogDetailAPIView.as_view(), name='blog-detail'),
    path('categories/', BlogCategoryListView.as_view(), name='blog-categories'),
    path('tags/', BlogTagListView.as_view(), name='blog-tags'),
    path('users/', BlogUserListView.as_view(), name='blog-users'),
    path('list/', BlogFrontendView.as_view(), name='blog-frontend'),
    path('post/', BlogDetailPageView.as_view(), name='blog-detail-page'),
]
