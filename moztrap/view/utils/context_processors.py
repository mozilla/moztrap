"""
General site context processors.

"""
from django.db import connection


def db_status(request):
    cursor = connection.cursor()
    cursor.execute("show variables like 'read_only'")
    return {"DB_READ_ONLY": cursor.fetchone()[1] == 'ON'}
