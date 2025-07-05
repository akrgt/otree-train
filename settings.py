"""Django/oTree settings module with production-ready optimisations.

This file layers additional middleware and storage back-ends on top of
`otree.settings` defaults so that existing oTree apps continue to work
unchanged while gaining:

1. WhiteNoise static-file serving with Brotli/Gzip compression and hashed
   filenames for long-term client caching.
2. HTML minification to reduce payload size.
3. Secure default values suitable for production (DEBUG=False, strong
   caching headers, etc.).

You can point the `OTREE_SETTINGS_MODULE` environment variable to this
module (e.g. `export OTREE_SETTINGS_MODULE=settings`) or invoke `otree
runprodserver` with `--settings=settings`.
"""

from __future__ import annotations

import os
from os import environ
from pathlib import Path

import otree.settings

# ----------------------------------------------------------------------------
# Base directory helpers
# ----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

# ----------------------------------------------------------------------------
# Core settings extensions
# ----------------------------------------------------------------------------
DEBUG = environ.get("OTREE_PRODUCTION", "1") in {"0", "False", "false"}
SECRET_KEY = environ.get("DJANGO_SECRET_KEY", "replace-me")
ALLOWED_HOSTS = environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")

# ----------------------------------------------------------------------------
# Installed apps & middleware (prepend our additions)
# ----------------------------------------------------------------------------
INSTALLED_APPS = [
    "whitenoise.runserver_nostatic",  # ensures runserver uses WhiteNoise
] + otree.settings.INSTALLED_APPS

MIDDLEWARE = [
    # Minify HTML responses **before** WhiteNoise adds ETags/compression
    "htmlmin.middleware.HtmlMinifyMiddleware",
    "htmlmin.middleware.MarkRequestMiddleware",
    # WhiteNoise should come right after SecurityMiddleware (oTree already
    # inserts it for us) so we mimic that order here.
    "whitenoise.middleware.WhiteNoiseMiddleware",
] + otree.settings.MIDDLEWARE

# Enable manifest-based hashed filenames + gzip & brotli compression
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Cache-control max-age for immutable static assets (~1 year)
WHITENOISE_MAX_AGE = 31536000  # seconds

# ---------------------------------------------------------------------------
# Static files dirs & root (oTree calls collectstatic during deployment)
# ---------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS: list[os.PathLike[str]] = []

# ---------------------------------------------------------------------------
# HTMLMin configuration
# ---------------------------------------------------------------------------
HTML_MINIFY = not DEBUG
KEEP_COMMENTS_ON_MINIFY = False

# ---------------------------------------------------------------------------
# Import oTree default settings last so that our overrides stick.
# ---------------------------------------------------------------------------
otree.settings.update(globals())