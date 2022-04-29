class ApiResponse:
    def api_reponse(data) -> object:
        result = {
            'code': 0,
            'msg': '获取成功',
            'data': data
        }
        return result

