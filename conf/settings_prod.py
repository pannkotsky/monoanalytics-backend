from .settings import *  # noqa: F403

DEBUG = False
ALLOWED_HOSTS = [".monoanalytics.app", ".herokuapp.com"]

DATABASES["default"]["CONN_MAX_AGE"] = 600  # noqa: F405
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True  # noqa: F405
DATABASES["default"]["OPTIONS"] = {"sslmode": "require"}  # noqa: F405

CORS_ALLOWED_ORIGINS = [
    "https://monoanalytics-ui.vercel.app",
    "https://monoanalytics.app",
]

SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
