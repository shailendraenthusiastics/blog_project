"""Compatibility WSGI module for legacy Render/Gunicorn start commands.

Some older deploy configs still reference ``blog_project.wsgi``.
This module forwards to the current project WSGI application.
"""

from blog.wsgi import application
