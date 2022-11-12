from django.db import models
from django.utils.translation import gettext_lazy as _


'''
from django.db import connections
database_id = user.username #just something unique
newDatabase = {}
newDatabase["id"] = database_id
newDatabase['ENGINE'] = 'django.db.backends.sqlite3'
newDatabase['NAME'] = '/path/to/db_%s.sql' % database_id
newDatabase['USER'] = ''
newDatabase['PASSWORD'] = ''
newDatabase['HOST'] = ''
newDatabase['PORT'] = ''
connections.databases[database_id] = newDatabase
'''
class DatabaseConnectionSettings(models.Model):

    engine = models.CharField(
        max_length=150, verbose_name='database engine')
    name = models.CharField(
        max_length=150, verbose_name='database name')
    user = models.CharField(
        max_length=150, verbose_name='database user')
    password = models.CharField(
        max_length=150, verbose_name='database password')
    host = models.CharField(
        max_length=150, verbose_name='database host')
    port = models.CharField(
        max_length=150, verbose_name='database port')

    class Meta:
        'Connection settings for the wikibase'
        verbose_name = _('database connection settings')
        verbose_name_plural = _('databases connections settings')
        db_table = 'django_data_battery_database_connection_settings'
