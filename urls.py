from django.contrib import admin
from django.urls import path, include
from api.views import ckeditor_upload_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/', include('Admin.urls')),   
    path('accounts/', include('accounts.urls')),
    path('api/', include('api.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('user/', include('user.urls')),
    path('ckeditor/upload/', ckeditor_upload_view, name='ckeditor-upload'),
]