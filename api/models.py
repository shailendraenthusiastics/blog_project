from django.db import models
from django.contrib.auth.models import User

class BlogCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name

class BlogTag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
class BlogImage(models.Model):
    image = models.ImageField(upload_to='gallery/')
    is_active = models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    

class Blog(models.Model):
    title = models.CharField(max_length=150 )
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    short_description = models.CharField(max_length=255)
    description = models.TextField()
    view_count = models.PositiveIntegerField(default=0)
    author_name = models.CharField(max_length=50, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    gallery = models.ManyToManyField(BlogImage, related_name='blogs', blank=True)
    featured_image = models.ImageField(upload_to='featured/')
    categories = models.ManyToManyField(BlogCategory, related_name='blogs')
    tags = models.ManyToManyField(BlogTag, related_name='blogs')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)


