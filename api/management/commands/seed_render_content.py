from django.core.management import BaseCommand, call_command

from api.models import Blog


class Command(BaseCommand):
    help = "Load initial blog content into an empty database."

    def handle(self, *args, **options):
        if Blog.objects.filter(is_active=True).exists():
            self.stdout.write(self.style.SUCCESS("Active blog content already exists; skipping seed."))
            return

        if Blog.objects.exists():
            updated = Blog.objects.update(is_active=True)
            self.stdout.write(
                self.style.SUCCESS(
                    f"No active blogs found. Re-activated {updated} existing blog(s)."
                )
            )
            return

        call_command("loaddata", "render_seed.json")
        self.stdout.write(self.style.SUCCESS("Loaded initial blog content from render_seed.json."))
