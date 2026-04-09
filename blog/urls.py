from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from django.conf import settings
from django.conf.urls.static import static
from api.views import (
    BlogFrontendViewSet,
    BlogDetailPageViewSet,
    BlogSitemap,
    ckeditor_upload_view,
)

sitemaps = {
    "blogs": BlogSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", BlogFrontendViewSet.as_view({"get": "list"}), name="home"),
    path("list/", BlogFrontendViewSet.as_view({"get": "list"}), name="blog-frontend"),
    path(
        "blog-detail/",
        BlogDetailPageViewSet.as_view({"get": "list"}),
        name="blog-detail-query",
    ),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("ckeditor/upload/", ckeditor_upload_view, name="ckeditor-upload"),
    path("dashboard/", include("Admin.urls")),
    path("api/", include("api.urls")),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
