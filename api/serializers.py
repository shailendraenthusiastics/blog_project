from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Blog, BlogCategory, BlogTag, BlogImage
import os
import re
from django.utils.text import slugify



class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password'] 

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user

class BlogImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogImage
        fields = ['id', 'image']

    def validate_image(self, value):
        ext = os.path.splitext(value.name)[1].lower()
        valid_extensions = ['.jpg', '.jpeg', '.png']
        if ext not in valid_extensions:
            raise serializers.ValidationError("Only JPG, JPEG, and PNG files are allowed.")
        limit = 5 * 1024 * 1024
        if value.size > limit:
            raise serializers.ValidationError("Image file size cannot exceed 5MB.")
        return value


class RelatedNameField(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        return value.name


class RelatedImageUrlField(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        if not value.image:
            return None
        request = self.context.get('request')
        url = value.image.url
        if request:
            return request.build_absolute_uri(url)
        return url

class BlogSerializer(serializers.ModelSerializer):
    categories = RelatedNameField(
        queryset=BlogCategory.objects.all(),
        many=True
    )
    tags = RelatedNameField(
        queryset=BlogTag.objects.all(),
        many=True
    )
    title = serializers.CharField(trim_whitespace=False)
    author = serializers.SlugRelatedField(slug_field='username', read_only=True)
    is_active = serializers.BooleanField(default=True, required=False)
    slug = serializers.SlugField(required=False, allow_blank=True)
    gallery = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        allow_empty=True,
        write_only=True
    )

    class Meta:
        model = Blog
        fields = [
            'id', 'title', 'slug', 'short_description', 'description',
            'view_count',
            'author', 'featured_image', 'gallery',
            'categories', 'tags', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['author', 'slug', 'view_count']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        gallery_images = instance.gallery.all()
        
        if gallery_images:
            if request:
                representation['gallery'] = [request.build_absolute_uri(img.image.url) for img in gallery_images]
            else:
                representation['gallery'] = [img.image.url for img in gallery_images]
        else:
            representation['gallery'] = []
        
        return representation

    def create(self, validated_data):
        categories = validated_data.pop('categories', [])
        tags = validated_data.pop('tags', [])
        gallery = validated_data.pop('gallery', [])
        
        if not validated_data.get('slug'):
            generated_slug = slugify(validated_data['title'])
            if Blog.objects.filter(slug=generated_slug).exists():
                raise serializers.ValidationError({"slug": ["Slug already exists."]})
            validated_data['slug'] = generated_slug
        blog = Blog.objects.create(**validated_data)
        blog.categories.set(categories)
        blog.tags.set(tags)
        if gallery:
            for image_data in gallery:
                new_image = BlogImage.objects.create(image=image_data)
                blog.gallery.add(new_image)

        return blog
    
    def update(self, instance, validated_data):
        categories = validated_data.pop('categories', None)
        tags = validated_data.pop('tags', None)
        gallery = validated_data.pop('gallery', None)
        if 'title' in validated_data and validated_data['title'] != instance.title:
            if not validated_data.get('slug'):
                generated_slug = slugify(validated_data['title'])
                if Blog.objects.filter(slug=generated_slug).exclude(pk=instance.pk).exists():
                    raise serializers.ValidationError({"slug": ["Slug already exists."]})
                validated_data['slug'] = generated_slug
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if categories is not None:
            instance.categories.set(categories)
        if tags is not None:
            instance.tags.set(tags)
        
        if gallery:
            instance.gallery.clear()  
            for image_data in gallery:
                new_image = BlogImage.objects.create(image=image_data)
                instance.gallery.add(new_image)
        
        return instance
    
    def validate_slug(self, value):
        if value:
            if not re.match(r'^[-a-zA-Z0-9_]+$', value):
                raise serializers.ValidationError("Slug can only contain letters, numbers, underscores or hyphens.")
            if value.startswith('-') or value.endswith('-') or '--' in value:
                raise serializers.ValidationError("Invalid slug format.")
        return value
    
    def validate_title(self, value):
        if value != value.strip():
            raise serializers.ValidationError(
                "Title cannot contain leading or trailing spaces."
            )

        if re.search(r'\s{2,}', value):
            raise serializers.ValidationError(
                "Multiple spaces between words are not allowed."
            )

        return value



