from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand, call_command

from api.models import Blog


class Command(BaseCommand):
    help = "Seed initial blog data from fixture when blog table is empty."

    def handle(self, *args, **options):
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
            self.stdout.write(self.style.WARNING(f"Fixture not found: {fixture_path}"))
            return

        call_command("loaddata", str(fixture_path))
        self.stdout.write(self.style.SUCCESS("Seeded initial blog data successfully."))
