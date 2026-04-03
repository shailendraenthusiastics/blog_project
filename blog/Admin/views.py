import re
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.utils.text import slugify
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from api.models import Blog, BlogCategory, BlogImage, BlogTag
from api.serializers import BlogAdminDetailSerializer 
from api.serializers import BlogAdminListSerializer
def _superuser_check(user):
	return user.is_authenticated and user.is_superuser
def _normalize_name(value):
	return value.strip()

def _normalize_text_spaces(value):
	if value is None:
		return ""
	return re.sub(r"\s+", " ", value).strip()

def _to_title_case(value):
	return _normalize_text_spaces(value).title()

def _is_letters_and_spaces_only(value):
	if not value:
		return False
	return re.match(r"^[A-Za-z ]+$", value) is not None

def _is_valid_name(value):
	if not value:
		return False
	return re.match(r"^[A-Za-z]+(?: [A-Za-z]+)*$", value) is not None

def _is_title_case(value):
	if not value:
		return False
	return value == value.title()

def _has_leading_or_trailing_space(value):
	if value is None:
		return False
	return value.startswith(" ") or value.endswith(" ")

def _has_multiple_spaces(value):
	if not value:
		return False
	return re.search(r" {2,}", value) is not None
def _generate_unique_slug_for(model, value, instance_id=None):
	base_slug = slugify(value) or "item"
	slug = base_slug
	counter = 1
	queryset = model.objects.all()
	if instance_id:
		queryset = queryset.exclude(pk=instance_id)
	while queryset.filter(slug=slug).exists():
		slug = f"{base_slug}-{counter}"
		counter += 1
	return slug
def _generate_unique_slug(title):
	base_slug = slugify(title) or "blog"
	slug = base_slug
	counter = 1
	while Blog.objects.filter(slug=slug).exists():
		slug = f"{base_slug}-{counter}"
		counter += 1
	return slug
def admin_login_view(request):
	if request.user.is_authenticated:
		if request.user.is_superuser:
			return redirect("admin_dashboard")
		logout(request)

	if request.method == "POST":
		username = request.POST.get("username", "").strip()
		password = request.POST.get("password", "").strip()
		user = authenticate(request, username=username, password=password)

		if user and user.is_superuser:
			login(request, user)
			return redirect("admin_dashboard")

		messages.error(request, "Invalid superuser credentials.")

	return render(request, "admin_login.html")
@user_passes_test(_superuser_check, login_url="admin_login")
def admin_logout_view(request):
	logout(request)
	return redirect("admin_login")
@user_passes_test(_superuser_check, login_url="admin_login")
def admin_dashboard_view(request):
	filter_status = request.GET.get("status", "all")
	page = request.GET.get("page", 1)
	
	if filter_status == "active":
		blogs = Blog.objects.filter(is_active=True).order_by("-created_at")
	elif filter_status == "inactive":
		blogs = Blog.objects.filter(is_active=False).order_by("-created_at")
	else:
		blogs = Blog.objects.order_by("-created_at")
	
	paginator = Paginator(blogs, 10)
	try:
		blogs_page = paginator.page(page)
	except PageNotAnInteger:
		blogs_page = paginator.page(1)
	except EmptyPage:
		blogs_page = paginator.page(paginator.num_pages)
	
	context = {
		"blog_count": Blog.objects.count(),
		"category_count": BlogCategory.objects.count(),
		"tag_count": BlogTag.objects.count(),
		"blogs": blogs_page,
		"filter_status": filter_status
	}
	return render(request, "admin_dashboard.html", context)

@user_passes_test(_superuser_check, login_url="admin_login")
def admin_blog_list_view(request):
	filter_status = request.GET.get("status", "all")
	page = request.GET.get("page", 1)
	if filter_status == "active":
		blogs = Blog.objects.filter(is_active=True).order_by("-created_at")
	elif filter_status == "inactive":
		blogs = Blog.objects.filter(is_active=False).order_by("-created_at")
	else:
		blogs = Blog.objects.order_by("-created_at")
	blogs = blogs.prefetch_related('categories', 'tags')
	
	paginator = Paginator(blogs, 10)
	try:
		blogs_page = paginator.page(page)
	except PageNotAnInteger:
		blogs_page = paginator.page(1)
	except EmptyPage:
		blogs_page = paginator.page(paginator.num_pages)
	serialized_blogs = BlogAdminListSerializer(blogs_page.object_list, many=True, context={'request': request}).data
	
	return render(request, "admin_blogs.html", {
		"blogs": serialized_blogs,
		"page_obj": blogs_page,
		"filter_status": filter_status,
		"total_pages": paginator.num_pages,
		"current_page": blogs_page.number
	})

@user_passes_test(_superuser_check, login_url="admin_login")
def admin_blog_detail_view(request, pk):
	blog = get_object_or_404(Blog, pk=pk)
	serializer = BlogAdminDetailSerializer(blog, context={'request': request})
	blog_data = serializer.data
	return render(request, "admin_blog_detail.html", {"blog_data": blog_data, "blog": blog})

@user_passes_test(_superuser_check, login_url="admin_login")
def admin_category_list_view(request):
	filter_status = request.GET.get("status", "all")
	page = request.GET.get("page", 1)
	
	if filter_status == "active":
		categories = BlogCategory.objects.filter(is_active=True).order_by("name")
	elif filter_status == "inactive":
		categories = BlogCategory.objects.filter(is_active=False).order_by("name")
	else:
		categories = BlogCategory.objects.order_by("name")
	
	paginator = Paginator(categories, 10)
	try:
		categories_page = paginator.page(page)
	except PageNotAnInteger:
		categories_page = paginator.page(1)
	except EmptyPage:
		categories_page = paginator.page(paginator.num_pages)
	
	return render(request, "admin_categories.html", {
		"categories": categories_page,
		"filter_status": filter_status
	})

@user_passes_test(_superuser_check, login_url="admin_login")
def admin_category_add_view(request):
	form_data = {"name": ""}
	form_errors = {}

	if request.method == "POST":
		raw_name = request.POST.get("name", "")
		name = _normalize_name(raw_name)
		form_data["name"] = raw_name
		if not name:
			form_errors["name"] = "Category name is required."
		elif not _is_valid_name(name):
			form_errors["name"] = "Category name must contain letters only and single spaces between words."
		elif BlogCategory.objects.filter(name__iexact=name).exists():
			form_errors["name"] = "Category already exists."
		else:
			slug = _generate_unique_slug_for(BlogCategory, name)
			BlogCategory.objects.create(name=name, slug=slug)
			messages.success(request, "Category added successfully.")
			return redirect("admin_categories")

	return render(request, "admin_category_add.html", {
		"form_data": form_data,
		"form_errors": form_errors,
	})

@user_passes_test(_superuser_check, login_url="admin_login")
def admin_category_edit_view(request, pk):
	category = get_object_or_404(BlogCategory, pk=pk)

	if request.method == "POST":
		raw_name = request.POST.get("name", "")
		name = _normalize_name(raw_name)
		is_active = request.POST.get("is_active") == "on"
		if not name:
			messages.error(request, "Category name is required.")
		elif not _is_valid_name(name):
			messages.error(request, "Category name must contain letters only and single spaces between words.")
		elif BlogCategory.objects.filter(name__iexact=name).exclude(pk=category.pk).exists():
			messages.error(request, "Category name already exists.")
		else:
			name_changed = name.lower() != category.name.lower()
			category.name = name
			category.is_active = is_active
			if not category.slug or name_changed:
				category.slug = _generate_unique_slug_for(BlogCategory, name, instance_id=category.pk)
			category.save()
			messages.success(request, "Category updated successfully.")
			return redirect("admin_categories")

	return render(request, "admin_category_edit.html", {"category": category})

@user_passes_test(_superuser_check, login_url="admin_login")
def admin_category_delete_view(request, pk):
	category = get_object_or_404(BlogCategory, pk=pk)
	if request.method == "POST":
		category.is_active = False
		category.save()
		messages.success(request, "Category deleted successfully.")
	return redirect("admin_categories")

@user_passes_test(_superuser_check, login_url="admin_login")
def admin_tag_list_view(request):
	filter_status = request.GET.get("status", "all")
	page = request.GET.get("page", 1)
	
	if filter_status == "active":
		tags = BlogTag.objects.filter(is_active=True).order_by("name")
	elif filter_status == "inactive":
		tags = BlogTag.objects.filter(is_active=False).order_by("name")
	else:
		tags = BlogTag.objects.order_by("name")
	
	paginator = Paginator(tags, 10)
	try:
		tags_page = paginator.page(page)
	except PageNotAnInteger:
		tags_page = paginator.page(1)
	except EmptyPage:
		tags_page = paginator.page(paginator.num_pages)
	
	return render(request, "admin_tags.html", {
		"tags": tags_page,
		"filter_status": filter_status
	})

@user_passes_test(_superuser_check, login_url="admin_login")
def admin_tag_add_view(request):
	form_data = {"name": ""}
	form_errors = {}

	if request.method == "POST":
		raw_name = request.POST.get("name", "")
		name = _normalize_name(raw_name)
		form_data["name"] = raw_name
		if not name:
			form_errors["name"] = "Tag name is required."
		elif not _is_valid_name(name):
			form_errors["name"] = "Tag name must contain letters only and single spaces between words."
		elif BlogTag.objects.filter(name__iexact=name).exists():
			form_errors["name"] = "Tag already exists."
		else:
			slug = _generate_unique_slug_for(BlogTag, name)
			BlogTag.objects.create(name=name, slug=slug)
			messages.success(request, "Tag added successfully.")
			return redirect("admin_tags")

	return render(request, "admin_tag_add.html", {
		"form_data": form_data,
		"form_errors": form_errors,
	})

@user_passes_test(_superuser_check, login_url="admin_login")
def admin_tag_edit_view(request, pk):
	tag = get_object_or_404(BlogTag, pk=pk)

	if request.method == "POST":
		raw_name = request.POST.get("name", "")
		name = _normalize_name(raw_name)
		is_active = request.POST.get("is_active") == "on"
		if not name:
			messages.error(request, "Tag name is required.")
		elif not _is_valid_name(name):
			messages.error(request, "Tag name must contain letters only and single spaces between words.")
		elif BlogTag.objects.filter(name__iexact=name).exclude(pk=tag.pk).exists():
			messages.error(request, "Tag name already exists.")
		else:
			name_changed = name.lower() != tag.name.lower()
			tag.name = name
			tag.is_active = is_active
			if not tag.slug or name_changed:
				tag.slug = _generate_unique_slug_for(BlogTag, name, instance_id=tag.pk)
			tag.save()
			messages.success(request, "Tag updated successfully.")
			return redirect("admin_tags")

	return render(request, "admin_tag_edit.html", {"tag": tag})

@user_passes_test(_superuser_check, login_url="admin_login")
def admin_tag_delete_view(request, pk):
	tag = get_object_or_404(BlogTag, pk=pk)
	if request.method == "POST":
		tag.is_active = False
		tag.save()
		messages.success(request, "Tag deleted successfully.")
	return redirect("admin_tags")
@user_passes_test(_superuser_check, login_url="admin_login")
def admin_blog_add_view(request):
	categories = BlogCategory.objects.filter(is_active=True).order_by("name")
	tags = BlogTag.objects.filter(is_active=True).order_by("name")
	form_data = {}
	selected_category_ids = []
	selected_tag_ids = []
	form_errors = {}

	if request.method == "POST":
		title_raw = request.POST.get("title", "")
		author_name_raw = request.POST.get("author_name", "")
		short_description_raw = request.POST.get("short_description", "")
		description_raw = request.POST.get("description", "")
		title = title_raw.strip()
		author_name = _normalize_name(author_name_raw)
		short_description = _to_title_case(short_description_raw)
		description = description_raw.strip()
		featured_image = request.FILES.get("featured_image")
		category_ids = request.POST.getlist("categories")
		tag_ids = request.POST.getlist("tags")
		gallery_files = request.FILES.getlist("gallery")
		selected_category_ids = category_ids
		selected_tag_ids = tag_ids
		form_data = {
			"title": title_raw,
			"author_name": author_name_raw,
			"short_description": short_description_raw,
			"description": description_raw,
		}

		if not title_raw.strip():
			form_errors["title"] = "Title is required."
		if not author_name_raw.strip():
			form_errors["author_name"] = "Author name is required."
		if not short_description_raw.strip():
			form_errors["short_description"] = "Short description is required."
		if not description_raw.strip():
			form_errors["description"] = "Full description is required."
		if not featured_image:
			form_errors["featured_image"] = "Featured image is required."
		if not category_ids:
			form_errors["categories"] = "Please select at least one category."
		if not tag_ids:
			form_errors["tags"] = "Please select at least one tag."

		if form_errors:
			return render(request, "admin_blog_add.html", {
				"categories": categories,
				"tags": tags,
				"form_data": form_data,
				"selected_category_ids": selected_category_ids,
				"selected_tag_ids": selected_tag_ids,
				"form_has_post": True,
				"form_errors": form_errors,
			})

		if _has_leading_or_trailing_space(title_raw):
			form_errors["title"] = "Title must not have leading or trailing spaces."
		elif _has_multiple_spaces(title_raw):
			form_errors["title"] = "Title must not contain multiple spaces between words."
		elif not _is_letters_and_spaces_only(title):
			form_errors["title"] = "Title must contain letters only."
		elif not _is_title_case(title):
			form_errors["title"] = "Title must be in title case."
		if _has_leading_or_trailing_space(description_raw):
			form_errors["description"] = "Full description must not have leading or trailing spaces."
		elif _has_multiple_spaces(description_raw):
			form_errors["description"] = "Full description must not contain multiple spaces between words."
		if _has_leading_or_trailing_space(author_name_raw):
			form_errors["author_name"] = "Author name must not have leading or trailing spaces."
		elif _has_multiple_spaces(author_name_raw):
			form_errors["author_name"] = "Author name must not contain multiple spaces between words."
		elif not _is_valid_name(author_name):
			form_errors["author_name"] = "Author name must contain letters only and single spaces between words."
		if form_errors:
			return render(request, "admin_blog_add.html", {
				"categories": categories,
				"tags": tags,
				"form_data": form_data,
				"selected_category_ids": selected_category_ids,
				"selected_tag_ids": selected_tag_ids,
				"form_has_post": True,
				"form_errors": form_errors,
			})
		blog = Blog.objects.create(
			title=title,
			slug=_generate_unique_slug(title),
			short_description=short_description,
			description=description,
			featured_image=featured_image,
			author=request.user,
			author_name=author_name,
		)
		if category_ids:
			blog.categories.set(BlogCategory.objects.filter(id__in=category_ids))
		if tag_ids:
			blog.tags.set(BlogTag.objects.filter(id__in=tag_ids))
		if gallery_files:
			for image_file in gallery_files:
				image = BlogImage.objects.create(image=image_file)
				blog.gallery.add(image)
		messages.success(request, "Blog created successfully.")
		return redirect("admin_blogs")
	context = {
		"categories": categories,
		"tags": tags,
		"form_data": form_data,
		"selected_category_ids": selected_category_ids,
		"selected_tag_ids": selected_tag_ids,
		"form_has_post": request.method == "POST",
		"form_errors": form_errors,
	}
	return render(request, "admin_blog_add.html", context)
@user_passes_test(_superuser_check, login_url="admin_login")
def admin_blog_edit_view(request, pk):
	blog = get_object_or_404(Blog, pk=pk)
	categories = BlogCategory.objects.order_by("name")
	tags = BlogTag.objects.order_by("name")
	form_data = {}
	selected_category_ids = []
	selected_tag_ids = []
	form_errors = {}
	if request.method == "POST":
		title_raw = request.POST.get("title", "")
		author_name_raw = request.POST.get("author_name", "")
		short_description_raw = request.POST.get("short_description", "")
		description_raw = request.POST.get("description", "")
		title = title_raw.strip()
		author_name = _normalize_name(author_name_raw)
		short_description = _to_title_case(short_description_raw)
		description = description_raw.strip()
		featured_image = request.FILES.get("featured_image")
		category_ids = request.POST.getlist("categories")
		tag_ids = request.POST.getlist("tags")
		gallery_files = request.FILES.getlist("gallery")
		is_active = request.POST.get("is_active") == "on"
		selected_category_ids = category_ids
		selected_tag_ids = tag_ids
		form_data = {
			"title": title_raw,
			"author_name": author_name_raw,
			"short_description": short_description_raw,
			"description": description_raw,
			"is_active": is_active,
		}

		if not title_raw.strip():
			form_errors["title"] = "Title is required."
		if not author_name_raw.strip():
			form_errors["author_name"] = "Author name is required."
		if not short_description_raw.strip():
			form_errors["short_description"] = "Short description is required."
		if not description_raw.strip():
			form_errors["description"] = "Full description is required."
		if not category_ids:
			form_errors["categories"] = "Please select at least one category."
		if not tag_ids:
			form_errors["tags"] = "Please select at least one tag."

		if form_errors:
			return render(request, "admin_blog_edit.html", {
				"blog": blog,
				"categories": categories,
				"tags": tags,
				"form_data": form_data,
				"selected_category_ids": selected_category_ids,
				"selected_tag_ids": selected_tag_ids,
				"form_has_post": True,
				"form_errors": form_errors,
			})

		if _has_leading_or_trailing_space(title_raw):
			form_errors["title"] = "Title must not have leading or trailing spaces."
		elif _has_multiple_spaces(title_raw):
			form_errors["title"] = "Title must not contain multiple spaces between words."
		elif not _is_letters_and_spaces_only(title):
			form_errors["title"] = "Title must contain letters only."
		elif not _is_title_case(title):
			form_errors["title"] = "Title must be in title case."
		if _has_leading_or_trailing_space(description_raw):
			form_errors["description"] = "Full description must not have leading or trailing spaces."
		elif _has_multiple_spaces(description_raw):
			form_errors["description"] = "Full description must not contain multiple spaces between words."
		if _has_leading_or_trailing_space(author_name_raw):
			form_errors["author_name"] = "Author name must not have leading or trailing spaces."
		elif _has_multiple_spaces(author_name_raw):
			form_errors["author_name"] = "Author name must not contain multiple spaces between words."
		elif not _is_valid_name(author_name):
			form_errors["author_name"] = "Author name must contain letters only and single spaces between words."

		if form_errors:
			return render(request, "admin_blog_edit.html", {
				"blog": blog,
				"categories": categories,
				"tags": tags,
				"form_data": form_data,
				"selected_category_ids": selected_category_ids,
				"selected_tag_ids": selected_tag_ids,
				"form_has_post": True,
				"form_errors": form_errors,
			})

		title_changed = title != blog.title
		blog.title = title
		blog.author_name = author_name
		blog.short_description = short_description
		blog.description = description
		blog.is_active = is_active
		if title_changed:
			blog.slug = _generate_unique_slug(title)
		if featured_image:
			blog.featured_image = featured_image
		blog.save()
		blog.categories.set(BlogCategory.objects.filter(id__in=category_ids))
		blog.tags.set(BlogTag.objects.filter(id__in=tag_ids))
		if gallery_files:
			for image_file in gallery_files:
				image = BlogImage.objects.create(image=image_file)
				blog.gallery.add(image)
		messages.success(request, "Blog updated successfully.")
		return redirect("admin_blogs")

	context = {
		"blog": blog,
		"categories": categories,
		"tags": tags,
		"form_data": form_data,
		"selected_category_ids": selected_category_ids,
		"selected_tag_ids": selected_tag_ids,
		"form_has_post": request.method == "POST",
		"form_errors": form_errors,
	}
	return render(request, "admin_blog_edit.html", context)

@user_passes_test(_superuser_check, login_url="admin_login")
def admin_blog_gallery_delete_view(request, pk, image_id):
	blog = get_object_or_404(Blog, pk=pk)
	image = get_object_or_404(BlogImage, pk=image_id)
	if request.method == "POST":
		blog.gallery.remove(image)
		if not image.blogs.exclude(pk=blog.pk).exists():
			image.delete()
		messages.success(request, "Gallery image deleted successfully.")
	return redirect("admin_blog_edit", pk=pk)

@user_passes_test(_superuser_check, login_url="admin_login")
def admin_blog_delete_view(request, pk):
	blog = get_object_or_404(Blog, pk=pk)
	if request.method == "POST":
		blog.is_active = False
		blog.save()
		messages.success(request, "Blog deleted successfully.")
	return redirect("admin_blogs")

