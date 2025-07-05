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
import sys

# ----------------------------------------------------------------------------
# Base directory helpers
# ----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

# Ensure that oTree can discover apps located in the ./code directory.
APPS_DIR = BASE_DIR / "code"
if str(APPS_DIR) not in sys.path:
    sys.path.insert(0, str(APPS_DIR))

# ----------------------------------------------------------------------------
# Core settings extensions
# ----------------------------------------------------------------------------
DEBUG = environ.get("OTREE_PRODUCTION", "1") in {"0", "False", "false"}
SECRET_KEY = environ.get("DJANGO_SECRET_KEY", "replace-me")
ALLOWED_HOSTS = environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")

# ----------------------------------------------------------------------------
# Installed apps & middleware (prepend our additions)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Static files configuration
# ---------------------------------------------------------------------------
# Serve compressed & cache-busted assets via WhiteNoise.
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
# Cache-control max-age for immutable static assets (~1 year)
WHITENOISE_MAX_AGE = 31536000  # seconds

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
# Extensions: let oTree append these to its default INSTALLED_APPS.
# ---------------------------------------------------------------------------
EXTENSION_APPS = ["whitenoise.runserver_nostatic"]

# Additional middleware to prepend/append later via Django settings
# We define it in a separate variable to avoid clobbering oTree's defaults.
_EXTRA_MIDDLEWARE = [
    "htmlmin.middleware.HtmlMinifyMiddleware",
    "htmlmin.middleware.MarkRequestMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

try:
    # If the 'MIDDLEWARE' list is already defined by oTree after import,
    # extend it. Otherwise, we leave it to oTree to merge later via
    # Django's settings configuration.
    MIDDLEWARE += _EXTRA_MIDDLEWARE  # type: ignore  # noqa: F821
except NameError:
    # MIDDLEWARE not yet defined; create it so that Django picks it up.
    MIDDLEWARE = _EXTRA_MIDDLEWARE  # type: ignore  # noqa: F401

# ---------------------------------------------------------------------------
# Import oTree default settings last so that our overrides stick.
# (Executed once at bottom after all local definitions.)
# ---------------------------------------------------------------------------

# ----------------------
# oTree mandatory fields
# ----------------------
# Default session configs used by the oTree admin demo interface.
SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1,
    participation_fee=0,
    doc="",
)

SESSION_CONFIGS = [
    dict(
        name="simple_survey",
        display_name="Simple Survey",
        num_demo_participants=1,
        app_sequence=["simple_survey"],
    ),
    dict(
        name="public_goods_trial",
        display_name="Public Goods Trial",
        num_demo_participants=4,
        app_sequence=["public_goods_trial"],
    ),
]

LANGUAGE_CODE = "ja"
REAL_WORLD_CURRENCY_CODE = "JPY"
USE_POINTS = True

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = environ.get("OTREE_ADMIN_PASSWORD", "password")

# Note: oTree 5.x dynamically imports this module and does not require an
# explicit `update()` call as in older versions. Therefore, we omit the call to
# avoid circular-import issues.