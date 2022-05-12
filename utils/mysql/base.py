from django.db.backends.mysql import base
from django.db.backends.mysql.base import CursorWrapper

from .feature import DatabaseFeatures


class DatabaseWrapper(base.DatabaseWrapper):
    features_class = DatabaseFeatures

    def create_cursor(self, name=None):
        cursor = self.connection.cursor()
        return CursorWrapper(cursor)
