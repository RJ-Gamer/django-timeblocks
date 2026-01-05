from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

SECRET_KEY = "test-secret-key"

DEBUG = True

USE_TZ = True

TIME_ZONE = "UTC"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test.sqlite3",
    }
}

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "timeblocks",
]

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
