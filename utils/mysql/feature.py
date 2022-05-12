from django.db.backends.mysql import features

from django.utils.functional import cached_property


class DatabaseFeatures(features.DatabaseFeatures):

    @cached_property
    def is_sql_auto_is_null_enabled(self):
        with self.connection.cursor() as cursor:
            cursor.execute('SELECT @@SQL_AUTO_IS_NULL')
            result = cursor.fetchone()
            return result and result[0] == 1

    @cached_property
    def mysql_server_info(self):
        with self.temporary_connection() as cursor:
            cursor.execute('SELECT VERSION()')
            return cursor.fetchone()['VERSION()']