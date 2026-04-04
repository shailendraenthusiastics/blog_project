from django.core.management import BaseCommand, call_command

from api.models import Blog


class Command(BaseCommand):
    help = "Load initial blog content into an empty database."

    def handle(self, *args, **options):
        if Blog.objects.exists():
            self.stdout.write(self.style.SUCCESS("Blog content already exists; skipping seed."))
            return

        call_command("loaddata", "render_seed.json")
        self.stdout.write(self.style.SUCCESS("Loaded initial blog content from render_seed.json."))
