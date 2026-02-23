"""
URL configuration for blog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from api.views import (
    BlogFrontendView,
    BlogDetailPageView,
    admin_login_view,
    admin_logout_view,
    admin_dashboard_view,
    admin_blog_list_view,
    admin_category_list_view,
    admin_category_add_view,
    admin_category_edit_view,
    admin_category_delete_view,
    admin_tag_list_view,
    admin_tag_add_view,
    admin_tag_edit_view,
    admin_tag_delete_view,
    admin_blog_add_view,
    admin_blog_edit_view,
    admin_blog_gallery_delete_view,
    admin_blog_delete_view,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('list/', BlogFrontendView.as_view(), name='blog_list'),
    path('blog-detail/', BlogDetailPageView.as_view(), name='blog_detail'),
    path('dashboard/login/', admin_login_view, name='admin_login'),
    path('dashboard/logout/', admin_logout_view, name='admin_logout'),
    path('dashboard/', admin_dashboard_view, name='admin_dashboard'),
    path('dashboard/blogs/', admin_blog_list_view, name='admin_blogs'),
    path('dashboard/categories/', admin_category_list_view, name='admin_categories'),
    path('dashboard/categories/add/', admin_category_add_view, name='admin_category_add'),
    path('dashboard/categories/<int:pk>/edit/', admin_category_edit_view, name='admin_category_edit'),
    path('dashboard/categories/<int:pk>/delete/', admin_category_delete_view, name='admin_category_delete'),
    path('dashboard/tags/', admin_tag_list_view, name='admin_tags'),
    path('dashboard/tags/add/', admin_tag_add_view, name='admin_tag_add'),
    path('dashboard/tags/<int:pk>/edit/', admin_tag_edit_view, name='admin_tag_edit'),
    path('dashboard/tags/<int:pk>/delete/', admin_tag_delete_view, name='admin_tag_delete'),
    path('dashboard/blogs/add/', admin_blog_add_view, name='admin_blog_add'),
    path('dashboard/blogs/<int:pk>/edit/', admin_blog_edit_view, name='admin_blog_edit'),
    path('dashboard/blogs/<int:pk>/gallery/<int:image_id>/delete/', admin_blog_gallery_delete_view, name='admin_blog_gallery_delete'),
    path('dashboard/blogs/<int:pk>/delete/', admin_blog_delete_view, name='admin_blog_delete'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
