from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management import BaseCommand, call_command

from api.models import Blog, BlogImage


class Command(BaseCommand):
    help = "Load initial blog content into an empty database."

    gallery_sources = [
        Path("blog_images/gallery/Screenshot_2026-01-30_174952.png"),
        Path("blog_images/gallery/Screenshot_2026-02-03_163030.png"),
        Path("gallery/Screenshot_2026-01-30_174952.png"),
        Path("gallery/Screenshot_2026-02-03_163030.png"),
    ]

    def handle(self, *args, **options):
        if Blog.objects.filter(is_active=True).exists():
            self.stdout.write(self.style.SUCCESS("Active blog content already exists; skipping seed."))
        elif Blog.objects.exists():
            updated = Blog.objects.update(is_active=True)
            self.stdout.write(
                self.style.SUCCESS(
                    f"No active blogs found. Re-activated {updated} existing blog(s)."
                )
            )
        else:
            call_command("loaddata", "render_seed.json")
            self.stdout.write(self.style.SUCCESS("Loaded initial blog content from render_seed.json."))

        self._ensure_gallery_content()

    def _ensure_gallery_content(self):
        blogs = list(Blog.objects.filter(is_active=True).order_by("id"))
        if not blogs:
            return

        if all(blog.gallery.exists() for blog in blogs):
            self.stdout.write(self.style.SUCCESS("Gallery images already exist; skipping gallery seed."))
            return

        media_root = Path(settings.MEDIA_ROOT)
        created = 0

        for blog, relative_path in zip(blogs, self.gallery_sources):
            if blog.gallery.exists():
                continue

            image_path = media_root / relative_path
            if not image_path.exists():
                continue

            with image_path.open("rb") as image_file:
                blog_image = BlogImage.objects.create(image=File(image_file, name=image_path.name))
            blog.gallery.add(blog_image)
            created += 1

        if created:
            self.stdout.write(self.style.SUCCESS(f"Attached {created} gallery image(s) to blogs."))
        else:
            self.stdout.write(self.style.WARNING("No gallery images were attached."))
