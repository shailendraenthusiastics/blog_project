"""Compatibility settings module for legacy imports.

This file keeps old module paths working by re-exporting from
the current ``blog.settings`` module.
"""

from blog.settings import *  # noqa: F401,F403
