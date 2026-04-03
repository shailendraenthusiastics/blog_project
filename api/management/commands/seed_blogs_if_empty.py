from pathlib import Path
import os

from django.conf import settings
from django.db import connection
from django.core.management import BaseCommand, call_command
from django.core.management.color import no_style
from django.contrib.auth.models import User

from api.models import Blog, BlogCategory, BlogTag

SEED_DATA = {
    "users": [
        {
            "id": 1,
            "username": "admin",
        },
    ],
    "categories": [
        {"id": 1, "name": "Nature", "slug": "nature"},
        {"id": 2, "name": "Travel", "slug": "travel"},
        {"id": 3, "name": "Adventure", "slug": "adventure"},
    ],
    "tags": [
        {"id": 1, "name": "Mountains", "slug": "mountains"},
        {"id": 2, "name": "Trekking", "slug": "trekking"},
        {"id": 3, "name": "Adventure", "slug": "adventure"},
        {"id": 4, "name": "Beach", "slug": "beach"},
        {"id": 5, "name": "Sea", "slug": "sea"},
        {"id": 6, "name": "Travel", "slug": "travel"},
    ],
    "blogs": [
        {
            "id": 1,
            "title": "The Magic Of Mountains A Journey Above The Clouds",
            "slug": "the-magic-of-mountains-a-journey-above-the-clouds",
            "short_description": "Discover The Peaceful And Breathtaking Beauty Of Mountains.",
            "description": "<p>Mountains have always attracted travelers with their majestic beauty and calm atmosphere. Whether it�s the Himalayas or any local hill station, the experience of standing above the clouds is unforgettable. The fresh air, scenic views, and silence of nature help you disconnect from stress and reconnect with yourself. Trekking in mountains not only builds physical strength but also mental peace.</p>",
            "view_count": 3,
            "author_name": "Shailendra",
            "author_id": 1,
            "featured_image": "featured/1a7262ea69a6ac0dcfcdc1a41b001f73.jpg",
            "categories": [1, 2],
            "tags": [1, 2, 3],
        },
        {
            "id": 2,
            "title": "Exploring The Calm And Adventure Of Beaches",
            "slug": "exploring-the-calm-and-adventure-of-beaches",
            "short_description": "Beaches Offer Both Relaxation And Thrilling Activities.",
            "description": "<p>Beaches are the perfect blend of relaxation and adventure. From enjoying a peaceful sunset to engaging in thrilling water sports like surfing and jet skiing, beaches offer something for everyone. The sound of waves and the vast ocean horizon create a calming environment, making it a perfect escape from daily life.</p>",
            "view_count": 2,
            "author_name": "Shailendra",
            "author_id": 1,
            "featured_image": "featured/photo-1676836050373-76bf93d08a41.jpg",
            "categories": [1, 3],
            "tags": [1, 4, 5, 6],
        },
    ],
}


class Command(BaseCommand):
    help = "Seed initial blog data from fixture when blog table is empty."

    def _seed_from_embedded_data(self):
        admin_username = os.environ.get("ADMIN_USERNAME", "admin")
        admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")

        for user_data in SEED_DATA["users"]:
            user, created = User.objects.get_or_create(
                id=user_data["id"],
                defaults={"username": admin_username},
            )
            if created or user.username != admin_username:
                user.username = admin_username
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.set_password(admin_password)
            user.save()

        for category in SEED_DATA["categories"]:
            BlogCategory.objects.update_or_create(
                id=category["id"],
                defaults={
                    "name": category["name"],
                    "slug": category["slug"],
                    "is_active": True,
                },
            )

        for tag in SEED_DATA["tags"]:
            BlogTag.objects.update_or_create(
                id=tag["id"],
                defaults={
                    "name": tag["name"],
                    "slug": tag["slug"],
                    "is_active": True,
                },
            )

        for blog_data in SEED_DATA["blogs"]:
            blog, _ = Blog.objects.update_or_create(
                id=blog_data["id"],
                defaults={
                    "title": blog_data["title"],
                    "slug": blog_data["slug"],
                    "short_description": blog_data["short_description"],
                    "description": blog_data["description"],
                    "view_count": blog_data["view_count"],
                    "author_name": blog_data["author_name"],
                    "author_id": blog_data["author_id"],
                    "featured_image": blog_data["featured_image"],
                    "is_active": True,
                },
            )
            blog.categories.set(blog_data["categories"])
            blog.tags.set(blog_data["tags"])

    def _ensure_admin_superuser(self):
        admin_username = os.environ.get("ADMIN_USERNAME", "admin")
        admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")

        user, _ = User.objects.get_or_create(username=admin_username)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(admin_password)
        user.save()

    def _reset_sequences(self):
        sequence_sql = connection.ops.sequence_reset_sql(
            no_style(), [User, BlogCategory, BlogTag, Blog]
        )
        if not sequence_sql:
            return

        with connection.cursor() as cursor:
            for statement in sequence_sql:
                cursor.execute(statement)

    def handle(self, *args, **options):
        self._ensure_admin_superuser()
        self._reset_sequences()

        existing_count = Blog.objects.count()
        if existing_count > 0:
            self.stdout.write(
                self.style.NOTICE(
                    f"Skipping seed: {existing_count} blogs already exist."
                )
            )
            return

        fixture_path = (
            Path(settings.BASE_DIR) / "api" / "fixtures" / "initial_data.json"
        )
        if not fixture_path.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"Fixture not found: {fixture_path}. Using embedded seed data."
                )
            )
            self._seed_from_embedded_data()
            self.stdout.write(
                self.style.SUCCESS("Seeded initial blog data successfully.")
            )
            return

        try:
            call_command("loaddata", str(fixture_path))
        except Exception as error:
            self.stdout.write(
                self.style.WARNING(
                    f"loaddata failed: {error}. Using embedded seed data."
                )
            )
            self._seed_from_embedded_data()

        if Blog.objects.count() == 0:
            self.stdout.write(
                self.style.WARNING(
                    "Fixture load completed but blog table is still empty. Using embedded seed data."
                )
            )
            self._seed_from_embedded_data()

        self._reset_sequences()

        self.stdout.write(self.style.SUCCESS("Seeded initial blog data successfully."))
