import mimetypes
import pymysql

pymysql.install_as_MySQLdb()
mimetypes.add_type("text/css", ".css", True)
mimetypes.add_type("text/javascript", ".js", True)