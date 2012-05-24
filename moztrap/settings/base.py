"""
Default Django settings for MozTrap project.

"""
from os.path import dirname, join, abspath
from os import environ

BASE_PATH = dirname(dirname(dirname(abspath(__file__))))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = [
    ("Carl Meyer", "cmeyer@mozilla.com"),
]

MANAGERS = ADMINS

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "moztrap",
        "USER": environ.get("USER", ""),
        "PASSWORD": "",
        "OPTIONS": {
            "init_command": "SET storage_engine=InnoDB",
            },
        "STORAGE_ENGINE": "InnoDB"
        }
    }

# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = None

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en-us"

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = False

# Absolute path to the directory that holds static files.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = join(BASE_PATH, "collected-assets")

# URL that handles the static files served from STATIC_ROOT.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = "/static/"

MEDIA_ROOT = join(BASE_PATH, "media")

MEDIA_URL = "/media/"

# A list of locations of additional static files
STATICFILES_DIRS = [join(BASE_PATH, "static")]

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]

# Make this unique, and don"t share it with anybody.
SECRET_KEY = "override this"

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = [
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
]

TEMPLATE_CONTEXT_PROCESSORS = [
    "django.core.context_processors.request",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.auth.context_processors.auth",
    "django.contrib.messages.context_processors.messages",
    "session_csrf.context_processor",
    "moztrap.view.users.context_processors.browserid",
]

MIDDLEWARE_CLASSES = [
    "django.middleware.common.CommonMiddleware",
    "djangosecure.middleware.SecurityMiddleware",
    "django.middleware.transaction.TransactionMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "session_csrf.CsrfMiddleware",
    "moztrap.view.users.middleware.SetUsernameMiddleware",
]

ROOT_URLCONF = "moztrap.view.urls"

TEMPLATE_DIRS = [
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don"t forget to use absolute paths, not relative paths.
    join(BASE_PATH, "templates"),
]

FIXTURE_DIRS = [
    join(BASE_PATH, "fixtures"),
    ]

DATE_FORMAT = "Y-m-d"

INSTALLED_APPS = [
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.humanize",
    "django_browserid",
    "south",
    "preferences",
    "moztrap.model.core",
    "moztrap.model.library",
    "moztrap.model.environments",
    "moztrap.model.execution",
    "moztrap.model.attachments",
    "moztrap.model.tags",
    "moztrap.view",
    "moztrap.view.lists",
    "moztrap.view.markup",
    "moztrap.view.manage",
    "moztrap.view.owa",
    "moztrap.view.results",
    "moztrap.view.runtests",
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

AUTHENTICATION_BACKENDS = [
    "moztrap.model.core.auth.ModelBackend",
    "moztrap.model.core.auth.BrowserIDBackend",
    ]

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler"
        }
    },
    "loggers": {
        "django.request":{
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
    }
}

INSTALLED_APPS += ["registration"]

ACCOUNT_ACTIVATION_DAYS = 1

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "do-not-reply@example.com"

INSTALLED_APPS += ["django_sha2"]

INSTALLED_APPS += ["compressor"]
COMPRESS_CSS_FILTERS = ["compressor.filters.css_default.CssAbsoluteFilter",
                        "compressor.filters.cssmin.CSSMinFilter"]

INSTALLED_APPS += ["floppyforms"]

INSTALLED_APPS += ["djangosecure"]
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 8 * 60 * 60 # 8 hours
SECURE_FRAME_DENY = True

MINIMUM_PASSWORD_CHARS = 8
PASSWORD_REQUIRE_ALPHA_NUMERIC = True
FORBIDDEN_PASSWORDS = [
    "password",
    "password1",
    "pass",
    "123",
    "test"
    ] # @@@ get full list from InfraSec

ALLOW_ANONYMOUS_ACCESS = False

INSTALLED_APPS += ["icanhaz"]
ICANHAZ_DIRS = [join(BASE_PATH, "jstemplates")]

INSTALLED_APPS += ["html5accordion"]

INSTALLED_APPS += ["messages_ui"]
MIDDLEWARE_CLASSES.insert(
    MIDDLEWARE_CLASSES.index(
        "django.contrib.messages.middleware.MessageMiddleware"
        ) + 1,
    "messages_ui.middleware.AjaxMessagesMiddleware")

INSTALLED_APPS += ["ajax_loading_overlay"]

LOGIN_URL = "/users/login/"
LOGIN_REDIRECT_URL = "/"

TEST_RUNNER = "tests.runner.DiscoveryDjangoTestSuiteRunner"
TEST_DISCOVERY_ROOT = join(BASE_PATH, "tests")

SOUTH_MIGRATION_MODULES = {
    "preferences": "moztrap.model.migrations.preferences",
    }

SITE_URL = "http://localhost:8000"
BROWSERID_CREATE_USER = "moztrap.model.core.auth.browserid_create_user"

USE_BROWSERID = True
