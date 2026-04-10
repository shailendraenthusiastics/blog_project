from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path
from django.views.static import serve
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
        "post/<slug:slug>/",
        BlogDetailPageViewSet.as_view({"get": "retrieve"}),
        name="blog-detail-page",
    ),
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

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
elif settings.MEDIA_URL == "/media/":
    # Render forwards all requests to Gunicorn, so we expose media in production too.
    urlpatterns += [
        re_path(
            r"^media/(?P<path>.*)$",
            serve,
            {"document_root": settings.MEDIA_ROOT},
        )
    ]
