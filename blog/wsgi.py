"""
WSGI config for blog project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blog.settings")

if os.environ.get("RENDER", "").lower() == "true":
    import django
    from django.core.management import call_command

    django.setup()
    # Defensive migration hook for platforms where start command may skip migrate.
    call_command("migrate", interactive=False, verbosity=0)

application = get_wsgi_application()
