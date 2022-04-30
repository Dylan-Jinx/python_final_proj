import json

from django.core import serializers
from django.db.models import QuerySet


class ApiResponse:

    def ok_simple(data: str = None, count: int = 0) -> object:
        result = {"code": 0, "msg": '获取成功', "count": count, "data": data}
        print(result)
        return result

    def ok(msg: str, data: QuerySet = None, count: int = 0) -> object:
        if data is not None:
            result = []
            data_dict = json.loads(serializers.serialize('json', data))
            print(data)
            for temp in data_dict:
                result.append(temp["fields"])
            for temp in data_dict:
                for t in result:
                    t["id"] = temp["pk"]
            result = {"code": 0, "msg": msg, "count": count, "data": result}
        else:
            result = {"code": 0, "msg": msg, "count": 0, "data": None}
        return result

    def error(self) -> object:
        result = {"code": 0, "msg": "操作失败", "data": None}
        return result

    def api_reponse(msg: str) -> object:
        result = {"code": 0, "msg": msg, "data": None}
        return result









    def api_reponse(data: QuerySet) -> object:
        try:
            result = []
            data_dict = json.loads(serializers.serialize('json', data))
            print(data)
            for temp in data_dict:
                result.append(temp["fields"])
            for temp in data_dict:
                for t in result:
                    t["id"] = temp["pk"]
        except Exception as e:
            print(e)
        result = {"code": 0, "msg": "", "data": result}
        return result

    def api_reponse(data: QuerySet) -> object:
        try:
            result = []
            data_dict = json.loads(serializers.serialize('json', data))
            print(data)
            for temp in data_dict:
                result.append(temp["fields"])
            for temp in data_dict:
                for t in result:
                    t["id"] = temp["pk"]
        except Exception as e:
            print(e)
        result = {"code": 0, "msg": "", "data": result}
        return result

    def api_reponse(data, count: int) -> object:
        try:
            result = []
            data_dict = json.loads(serializers.serialize('json', data))
            print(data)
            for temp in data_dict:
                result.append(temp["fields"])
        except Exception as e:
            print(e)
        result = {"code": 0, "msg": "", "count": count, "data": result}
        return result