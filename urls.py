from django.contrib import admin
from django.urls import path, include
from api.views import ckeditor_upload_view
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/', include('Admin.urls')),   
    path('accounts/', include('accounts.urls')),
    path('api/', include('api.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('user/', include('user.urls')),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('ckeditor/upload/', ckeditor_upload_view, name='ckeditor-upload'),
]