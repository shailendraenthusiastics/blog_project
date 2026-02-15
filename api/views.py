from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework import status
#from django.db.models import F

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .serializers import UserRegistrationSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Blog
from .serializers import BlogSerializer

class RegisterUserAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class BlogUserListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        users = User.objects.all()
        return Response([{"username": u.username} for u in users])

class BlogListCreateAPIView(APIView):
	permission_classes = [IsAuthenticatedOrReadOnly]
	def get(self, request):
		queryset = Blog.objects.filter(is_active=True)

		category = request.query_params.get("category")
		tag = request.query_params.get("tag")
		slug = request.query_params.get("slug")
		search = request.query_params.get("search")

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

		serializer = BlogSerializer(queryset, many=True, context={'request': request}) #
		return Response(serializer.data)

	def post(self, request):
		serializer = BlogSerializer(data=request.data, context={'request': request})
		if serializer.is_valid():
			serializer.save(author=request.user)
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BlogDetailAPIView(APIView):
	permission_classes = [IsAuthenticatedOrReadOnly]
	def get(self, request, pk):
		blog = get_object_or_404(Blog, pk=pk, is_active=True)
		blog.view_count +=1
		blog.save()
		# Blog.objects.filter(pk=pk).update(view_count=F('view_count') + 1) 
		serializer = BlogSerializer(blog, context={'request': request})
		return Response(serializer.data)

	def patch(self, request, pk):
		blog = get_object_or_404(Blog, pk=pk, is_active=True)
		if not (request.user.is_superuser or blog.author == request.user):
			return Response(
				{"detail": "You do not have permission to edit this blog."},
				status=status.HTTP_403_FORBIDDEN
			)
		
		serializer = BlogSerializer(blog, data=request.data, partial=True, context={'request': request})
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def put(self, request, pk):
		blog = get_object_or_404(Blog, pk=pk, is_active=True)
		if not (request.user.is_superuser or blog.author == request.user):
			return Response(
				{"detail": "You do not have permission to edit this blog."},
				status=status.HTTP_403_FORBIDDEN
			)
		
		serializer = BlogSerializer(blog, data=request.data, context={'request': request})
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	def delete(self, request, pk):
		blog = get_object_or_404(Blog, pk=pk, is_active=True)
		if not (request.user.is_superuser or blog.author == request.user):
			return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)
		blog.is_active = False
		blog.save()
		
		return Response({"detail": "Blog soft-deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
	



