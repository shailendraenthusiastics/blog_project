from django.contrib import admin
from .models import BlogCategory, BlogTag, Blog ,UserInfo,LicenseModel,UserAdvertisementTransaction
admin.site.register(BlogCategory)
admin.site.register(BlogTag)
admin.site.register(Blog)
admin.site.register(UserInfo)
admin.site.register(LicenseModel)
admin.site.register(UserAdvertisementTransaction)
