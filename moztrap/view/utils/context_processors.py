"""
General site context processors.

"""
from django.db import connection
from django.conf import settings


def db_status(request):
    cursor = connection.cursor()
    cursor.execute("show variables like 'read_only'")
    return {"DB_READ_ONLY": cursor.fetchone()[1] == 'ON'}


def google_analytics(request):
    """Use Google Analytics on the site if either you have explicitly
    set settings.USE_GOOGLE_ANALYTICS=True or if you're NOT in DEBUG
    mode."""
    return {
        "GOOGLE_ANALYTICS_ID": settings.GOOGLE_ANALYTICS_ID,
        "USE_GOOGLE_ANALYTICS": getattr(
            settings,
            'USE_GOOGLE_ANALYTICS',
            not settings.DEBUG
        )
    }
