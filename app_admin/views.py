import hashlib
import json
import uuid

from django.core.paginator import Paginator
from django.core.serializers import serialize
from django.http import JsonResponse
from django.shortcuts import *
from django.views import View

from app_admin.models import *
from utils.ApiResponse import ApiResponse


class LoginView(View):
    def get(self, request):
        return render(request, "admin/login.html")

    def post(self, request):
        phone_data = request.POST.get("phone")
        pwd_data = request.POST.get("password")
        encode_pwd = hashlib.md5(pwd_data.encode(encoding='UTF-8')).hexdigest()
        print(f"{phone_data} {pwd_data}")
        volunteer = Volunteer.objects.filter(phone=phone_data, pwd=encode_pwd).first()
        print(volunteer)
        if volunteer is not None:
            request.session["user_id"] = volunteer.user_id
            request.session["nick_name"] = volunteer.nick_name
            return HttpResponseRedirect("/admin/index/")
        else:
            return HttpResponseRedirect("/admin/login/")


class LogOutView(View):
    def get(self, request):
        del request.session["user_id"]
        del request.session["nick_name"]
        return HttpResponseRedirect("/admin/login")


class IndexView(View):
    def get(self, request):
        return render(request, "admin/index.html")


class VolunteerView(View):
    def dispatch(self, request, *args, **kwargs):
        result = super(VolunteerView, self).dispatch(request, *args, **kwargs)
        return result

    def get(self, request):
        if str(request.GET.get('method')).__eq__('getAllInfo'):
            result = self.get_all_volunteer_page(request)
            return JsonResponse(result)
        elif str(request.GET.get('method')).__eq__('getVolunteerDetail'):
            result = self.get_volunteer_detail(request)
            return JsonResponse(result, safe=False)
        elif str(request.GET.get('method')).__eq__('searchVolunteer'):
            result = self.search_volunteer(request)
            return JsonResponse(result, safe=False)
        return render(request, "admin/volunteer.html")

    def post(self, request):
        datas = json.loads(json.dumps(request.POST))
        # if datas.get('method').__eq__('addVolunteer'):
        #     result = self.add_volunteer(datas)
        if datas.get('method').__eq__('updateVolunteer'):
            result = self.update_volunteer(datas)
        return JsonResponse(result)

    def put(self, request):
        return HttpResponse("Put 请求")

    def delete(self, request):
        DELETE = json.loads(request.body)
        print(DELETE)
        id = DELETE.get('user_id')
        volunteer = Volunteer.objects.filter(user_id=id).delete()
        print(volunteer)
        return JsonResponse(ApiResponse.ok("操作成功"))

    def get_all_volunteer_page(self, request) -> object:
        try:
            page = request.GET.get("page")
            limit = request.GET.get("limit")
            datas = Volunteer.objects.all()
            page_result = Paginator(datas, limit)
            return ApiResponse.ok('获取成功', page_result.page(number=page), page_result.count)
        except Exception as e:
            print(e)

    def add_volunteer(self, datas):
        Volunteer.objects.create(
            user_id=str(uuid.uuid4()).replace('-', ''),
            nick_name=datas.get('nick_name'),
            user_name=datas.get('user_name'),
            user_mail=datas.get('user_mail'),
            qq=datas.get('qq'),
            phone=datas.get('phone'),
            id_card=datas.get('id_card'),
            pwd=hashlib.md5(str(datas.get('pwd')).encode(encoding='UTF-8')).hexdigest()
        )
        return ApiResponse.ok("添加成功")

    def update_volunteer(self, datas):
        Volunteer.objects \
            .filter(user_id=datas.get('user_id')) \
            .update(remove_flag='1')
        return ApiResponse.ok('更新成功')

    def get_volunteer_detail(self, request):
        userId = request.GET.get('user_id')
        volunteer = Volunteer.objects \
            .filter(user_id=userId)
        return ApiResponse.ok('获取成功', data=volunteer)

    def search_volunteer(self, request) -> object:
        volunteerName = request.GET.get('queryVolName')
        volunteer = Volunteer.objects.filter(user_name__contains=volunteerName)
        page = request.GET.get("page")
        limit = request.GET.get("limit")
        page_result = Paginator(volunteer, limit)
        return ApiResponse.ok('获取成功', page_result.page(number=page), page_result.count)
