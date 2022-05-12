from django.db import connection


def origin_db_query(sql, params) -> list:
    result = []
    with connection.cursor() as cursor:
        try:
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            for row in rows:
                result.append(dict(zip(columns, row)))
        except Exception as e:
            print(e)
    return result
