from django.urls import path
from .views import (
    BlogViewSet,
    BlogUserViewSet,
    RegisterUserViewSet,
    BlogFrontendViewSet,
    BlogCategoryViewSet,
    BlogTagViewSet,
    BlogDetailPageViewSet,
    BlogAdminViewSet,
)

urlpatterns = [
    path('register/', RegisterUserViewSet.as_view({'post': 'create'}), name='register'),
    path('blogs/', BlogViewSet.as_view({'get': 'list', 'post': 'create'}), name='blog-list'),
    path('blogs/<int:pk>/', BlogViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='blog-detail-by-id'),
    path('blogs/<slug:slug>/', BlogViewSet.as_view({'get': 'retrieve_by_slug'}), name='blog-detail-by-slug'),
    path('blog-detail/', BlogDetailPageViewSet.as_view({'get': 'list'}), name='blog-detail-query'),
    path('categories/', BlogCategoryViewSet.as_view({'get': 'list'}), name='blog-categories'),
    path('tags/', BlogTagViewSet.as_view({'get': 'list'}), name='blog-tags'),
    path('users/', BlogUserViewSet.as_view({'get': 'list'}), name='blog-users'),
    path('list/', BlogFrontendViewSet.as_view({'get': 'list'}), name='blog-frontend'),
    path('post/<slug:slug>/', BlogDetailPageViewSet.as_view({'get': 'retrieve'}), name='blog-detail-page'),
    path('admin/blogs/', BlogAdminViewSet.as_view({'get': 'list'}), name='blog-admin-list'),
]

