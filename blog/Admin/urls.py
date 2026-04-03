from django.urls import path
from .views import (
    admin_login_view,
    admin_logout_view,
    admin_dashboard_view,
    admin_blog_list_view,
    admin_blog_detail_view,
    admin_blog_add_view,
    admin_blog_edit_view,
    admin_blog_delete_view,
    admin_blog_gallery_delete_view,
    admin_category_list_view,
    admin_category_add_view,
    admin_category_edit_view,
    admin_category_delete_view,
    admin_tag_list_view,
    admin_tag_add_view,
    admin_tag_edit_view,
    admin_tag_delete_view,
)

urlpatterns = [
    path('', admin_dashboard_view, name='admin_dashboard'), 
    path('login/', admin_login_view, name='admin_login'),     
    path('logout/', admin_logout_view, name='admin_logout'),  
    
    path('blogs/', admin_blog_list_view, name='admin_blogs'),
    path('blogs/add/', admin_blog_add_view, name='admin_blog_add'),
    path('blogs/<int:pk>/', admin_blog_detail_view, name='admin_blog_detail'),
    path('blogs/<int:pk>/edit/', admin_blog_edit_view, name='admin_blog_edit'),
    path('blogs/<int:pk>/delete/', admin_blog_delete_view, name='admin_blog_delete'),
    path('blogs/<int:pk>/gallery/<int:image_id>/delete/', admin_blog_gallery_delete_view, name='admin_blog_gallery_delete'),
    
    path('categories/', admin_category_list_view, name='admin_categories'),
    path('categories/add/', admin_category_add_view, name='admin_category_add'),
    path('categories/<int:pk>/edit/', admin_category_edit_view, name='admin_category_edit'),
    path('categories/<int:pk>/delete/', admin_category_delete_view, name='admin_category_delete'),
    
    path('tags/', admin_tag_list_view, name='admin_tags'),
    path('tags/add/', admin_tag_add_view, name='admin_tag_add'),
    path('tags/<int:pk>/edit/', admin_tag_edit_view, name='admin_tag_edit'),
    path('tags/<int:pk>/delete/', admin_tag_delete_view, name='admin_tag_delete'),
]