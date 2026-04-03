
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from api.views import BlogFrontendViewSet, BlogDetailPageViewSet, ckeditor_upload_view

urlpatterns = [
     path('admin/', admin.site.urls),
    path('', BlogFrontendViewSet.as_view({'get': 'list'}), name='home'),
    path('list/', BlogFrontendViewSet.as_view({'get': 'list'}), name='blog-frontend'),
    path('blog-detail/', BlogDetailPageViewSet.as_view({'get': 'list'}), name='blog-detail-query'),
    path('ckeditor/upload/', ckeditor_upload_view, name='ckeditor-upload'),
    path('dashboard/', include('Admin.urls')), 
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

