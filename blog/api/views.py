from django.db.models import Q
import re
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
import json
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.renderers import JSONRenderer
from .serializers import UserRegistrationSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Blog, BlogCategory, BlogTag, BlogImage
from .serializers import BlogSerializer, BlogListSerializer, BlogDetailSerializer, BlogAdminListSerializer

import csv
from django.http import HttpResponse 
from django.db.models import Q
from .models import LicenseModel

def ckeditor_upload_view(request):
	if not (request.user.is_authenticated and request.user.is_superuser):
		return JsonResponse({'error': 'Unauthorized'}, status=403)

	if request.method != 'POST' or not request.FILES.get('upload'):
		return JsonResponse({'error': 'Invalid request'}, status=400)

	uploaded_file = request.FILES['upload']
	allowed_types = ['image/jpeg', 'image/png', 'image/gif']
	if uploaded_file.content_type not in allowed_types:
		return JsonResponse({'error': 'Only JPG, PNG, and GIF files are allowed'}, status=400)

	if uploaded_file.size > 5 * 1024 * 1024:
		return JsonResponse({'error': 'File size must not exceed 5MB'}, status=400)

	try:
		blog_image = BlogImage.objects.create(image=uploaded_file)
		file_url = request.build_absolute_uri(blog_image.image.url)
		return JsonResponse({
			'url': file_url,
			'uploaded': 1,
			'fileName': uploaded_file.name,
		}, status=200)
	except Exception as error:
		return JsonResponse({'error': str(error)}, status=500)


class RegisterUserViewSet(viewsets.ViewSet):
	permission_classes = [AllowAny]

	def create(self, request):
		serializer = UserRegistrationSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BlogUserViewSet(viewsets.ViewSet):
	def list(self, request):
		users = User.objects.all()
		return Response([{"username": user.username} for user in users])


class BlogCategoryViewSet(viewsets.ViewSet):
	def list(self, request):
		categories = BlogCategory.objects.filter(is_active=True).order_by('name')
		return Response([{"id": category.id, "name": category.name} for category in categories])


class BlogTagViewSet(viewsets.ViewSet):
	permission_classes = [AllowAny]
	def list(self, request):
		tags = BlogTag.objects.filter(is_active=True).order_by('name')
		return Response([{"id": tag.id, "name": tag.name} for tag in tags])


class BlogViewSet(
	mixins.ListModelMixin,
	mixins.CreateModelMixin,
	mixins.RetrieveModelMixin,
	mixins.UpdateModelMixin,
	mixins.DestroyModelMixin,
	viewsets.GenericViewSet,
):
	permission_classes = [IsAuthenticatedOrReadOnly]
	queryset = Blog.objects.all().order_by('-created_at')

	def get_queryset(self):
		queryset = Blog.objects.filter(is_active=True).order_by('-created_at')
		category = self.request.query_params.get("category")
		tag = self.request.query_params.get("tag")
		slug = self.request.query_params.get("slug")
		search = self.request.query_params.get("search")
		title = self.request.query_params.get("title")

		if category:
			queryset = queryset.filter(categories__name__iexact=category)
		if tag:
			queryset = queryset.filter(tags__name__iexact=tag)
		if slug:
			queryset = queryset.filter(slug=slug)
		if search:
			queryset = queryset.filter(
				Q(title__icontains=search) | Q(short_description__icontains=search)
			)
		if title:
			queryset = queryset.filter(title=title)

		return queryset.distinct()

	def get_serializer_class(self):
		if self.action in ["create", "update", "partial_update"]:
			return BlogSerializer
		if self.action == "retrieve":
			return BlogDetailSerializer
		return BlogListSerializer

	def list(self, request, *args, **kwargs):
		queryset = self.filter_queryset(self.get_queryset())
		limit_param = request.query_params.get("limit")

		if limit_param is not None:
			try:
				limit = int(limit_param)
			except (TypeError, ValueError):
				limit = None

			if limit is not None and limit > 0:
				if limit > 100:
					limit = 100
				queryset = queryset[:limit]

		serializer = self.get_serializer(queryset, many=True, context={'request': request})
		return Response(serializer.data)

	def create(self, request, *args, **kwargs):
		if not request.user or not request.user.is_authenticated:
			return Response(
				{"detail": "Authentication credentials were not provided."},
				status=status.HTTP_401_UNAUTHORIZED,
			)

		serializer = self.get_serializer(data=request.data, context={'request': request})
		if serializer.is_valid():
			blog = serializer.save(author=request.user)
			response_serializer = BlogListSerializer(blog, context={'request': request})
			return Response(response_serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def retrieve(self, request, *args, **kwargs):
		blog = get_object_or_404(Blog, pk=kwargs.get('pk'), is_active=True)
		blog.view_count += 1
		blog.save(update_fields=['view_count'])
		serializer = BlogDetailSerializer(blog, context={'request': request})
		return Response(serializer.data)

	def update(self, request, *args, **kwargs):
		partial = kwargs.pop('partial', False)
		blog = get_object_or_404(Blog, pk=kwargs.get('pk'), is_active=True)

		if not request.user or not request.user.is_authenticated:
			return Response(
				{"detail": "Authentication credentials were not provided."},
				status=status.HTTP_401_UNAUTHORIZED,
			)

		if not (request.user.is_superuser or blog.author == request.user):
			return Response(
				{"detail": "You do not have permission to edit this blog. Only the author or superuser can edit."},
				status=status.HTTP_403_FORBIDDEN,
			)

		serializer = BlogSerializer(blog, data=request.data, partial=partial, context={'request': request})
		if serializer.is_valid():
			updated_blog = serializer.save()
			response_serializer = BlogDetailSerializer(updated_blog, context={'request': request})
			return Response(response_serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def partial_update(self, request, *args, **kwargs):
		kwargs['partial'] = True
		return self.update(request, *args, **kwargs)

	def destroy(self, request, *args, **kwargs):
		blog = get_object_or_404(Blog, pk=kwargs.get('pk'), is_active=True)

		if not request.user or not request.user.is_authenticated:
			return Response(
				{"detail": "Authentication credentials were not provided."},
				status=status.HTTP_401_UNAUTHORIZED,
			)

		if not (request.user.is_superuser or blog.author == request.user):
			return Response(
				{"detail": "You do not have permission to delete this blog. Only the author or superuser can delete."},
				status=status.HTTP_403_FORBIDDEN,
			)

		blog.is_active = False
		blog.save(update_fields=['is_active'])
		return Response({"detail": "Blog soft-deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

	def retrieve_by_slug(self, request, slug=None):
		blog = get_object_or_404(Blog, slug=slug, is_active=True)
		blog.view_count += 1
		blog.save(update_fields=['view_count'])
		serializer = BlogDetailSerializer(blog, context={'request': request})
		return Response(serializer.data)


class BlogDetailPageViewSet(viewsets.ViewSet):
	renderer_classes = [TemplateHTMLRenderer]
	template_name = 'blog_detail.html'
	permission_classes = [AllowAny]

	def list(self, request):
		blog_id = request.GET.get('id')
		blog = None
		blog_data = None
		if blog_id:
			try:
				blog = Blog.objects.get(id=blog_id, is_active=True)
				Blog.objects.filter(id=blog_id).update(view_count=Blog.objects.get(id=blog_id).view_count + 1)
				blog.refresh_from_db()
				serializer = BlogDetailSerializer(blog, context={'request': request})
				blog_data = serializer.data
			except Blog.DoesNotExist:
				pass

		response = Response({"blog": blog, "blog_data": blog_data})
		return response

	def retrieve(self, request, slug=None):
		blog = get_object_or_404(Blog, slug=slug, is_active=True)
		Blog.objects.filter(id=blog.id).update(view_count=blog.view_count + 1)
		blog.refresh_from_db()
		serializer = BlogDetailSerializer(blog, context={'request': request})
		response = Response({"blog": blog, "blog_data": serializer.data})
		
		return response


class BlogFrontendViewSet(viewsets.ViewSet):
	renderer_classes = [TemplateHTMLRenderer]
	template_name = 'blog_list.html'
	def list(self, request):
		search = request.query_params.get('search', '').strip()
		category = request.query_params.get('category', '').strip()
		tag = request.query_params.get('tag', '').strip()
		blogs = Blog.objects.filter(is_active=True)

		if search:
			blogs = blogs.filter(
				Q(title__icontains=search) | Q(short_description__icontains=search)
			)
		if category:
			blogs = blogs.filter(categories__name__iexact=category)
		if tag:
			blogs = blogs.filter(tags__name__iexact=tag)

		blogs = blogs.prefetch_related('categories', 'tags', 'gallery').order_by('-created_at').distinct()
		categories = BlogCategory.objects.filter(is_active=True).order_by('name')
		tags = BlogTag.objects.filter(is_active=True).order_by('name')

		response = Response({
			"blogs": blogs,
			"categories": categories,
			"tags": tags,
			"search": search,
			"category": category,
			"tag": tag,
		})
		return response


class BlogAdminViewSet(viewsets.ViewSet):
	permission_classes = [IsAuthenticatedOrReadOnly]

	def list(self, request):
		filter_status = request.query_params.get("status", "all")
		page = int(request.query_params.get("page", 1))
		page_size = int(request.query_params.get("page_size", 10))

		if filter_status == "active":
			queryset = Blog.objects.filter(is_active=True).order_by("-created_at")
		elif filter_status == "inactive":
			queryset = Blog.objects.filter(is_active=False).order_by("-created_at")
		else:
			queryset = Blog.objects.order_by("-created_at")

		queryset = queryset.prefetch_related('categories', 'tags')
		total_count = queryset.count()
		start = (page - 1) * page_size
		end = start + page_size
		queryset = queryset[start:end]

		serializer = BlogAdminListSerializer(queryset, many=True, context={'request': request})

		return Response({
			'results': serializer.data,
			'count': total_count,
			'page': page,
			'page_size': page_size,
			'total_pages': (total_count + page_size - 1) // page_size,
		})


def download_license_csv(request):

    filter_type = request.GET.get("filter")

    queryset = LicenseModel.objects.select_related(
        "generatedBy", "linkUser"
    ).all()

    if filter_type == "DeviceUsed":
        queryset = queryset.filter(
            Q(deviceSerialNumber__isnull=False) & ~Q(deviceSerialNumber="")
        )

    elif filter_type == "DeviceNotUsed":
        queryset = queryset.filter(
            Q(deviceSerialNumber__isnull=True) | Q(deviceSerialNumber="")
        )

    elif filter_type == "Suspended":
        queryset = queryset.filter(isSuspended=True)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="licenses.csv"'

    writer = csv.writer(response)

    writer.writerow([
        "License Key",
        "Device Serial Number",
        "Generated By",
        "Is_Suspended",
        
    ])

    for obj in queryset.iterator():
        writer.writerow([
            obj.licenseKey,
            obj.deviceSerialNumber,
            obj.generatedBy.username if obj.generatedBy else "",
            obj.isSuspended,
        ])

    return response