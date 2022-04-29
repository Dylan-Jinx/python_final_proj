import json

from django.core import serializers


class ApiResponse:
    def api_reponse(msg) -> object:
        result = {"code": 0, "msg": "", "data": None}
        return result

    def api_reponse(data) -> object:
        try:
            result = []
            data_dict = json.loads(serializers.serialize('json', data))
            print(data)
            for temp in data_dict:
                print(temp["pk"])
                result.append(temp["fields"])
            for temp in data_dict:
                for t in result:
                    t["id"] = temp["pk"]
            print(result)
        except Exception as e:
            print(e)
        result = {"code": 0, "msg": "", "data": result}
        return result
