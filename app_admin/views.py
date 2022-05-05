import hashlib
import json
import random
import uuid

import django.utils.timezone as timezone
from django.core.paginator import Paginator
from django.http import JsonResponse, QueryDict
from django.shortcuts import *
from django.views import View

from app_admin.models import Volunteer, VolunteerTeam, City, Province, Area
from utils.ApiResponse import ApiResponse
from utils.generator.PersonalInfoGenerator import get_name, get_tel
from utils.generator.username import get_userTeamName


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
        elif str(request.GET.get('method')).__eq__('searchVolunteerById'):
            result = self.search_volunteer_by_id(request)
            return JsonResponse(result, safe=False)
        elif str(request.GET.get('method')).__eq__('resetPwd'):
            result = self.resetPwd(request)
            return JsonResponse(result, safe=False)
        return render(request, "admin/volunteer.html")

    def post(self, request):
        datas = json.loads(json.dumps(request.POST))
        if datas.get('method').__eq__('updateVolunteer'):
            result = self.update_volunteer(datas)
        return JsonResponse(result)

    def put(self, request):
        return HttpResponse("Put 请求")

    def delete(self, request):
        method = request.GET.get('method')
        if str(method).__eq__('deleteById'):
            self.delete_by_id(request)
            return JsonResponse(ApiResponse.ok("操作成功"))
        elif str(method).__eq__('deleteByIds'):
            self.delete_by_ids(request)
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

    def search_volunteer_by_id(self, request) -> object:
        userId = request.GET.get('user_id')
        volunteer = Volunteer.objects.filter(user_id=userId)
        return ApiResponse.ok('获取成功', volunteer)

    def delete_by_id(self, request):
        id = request.GET.get('user_id')
        Volunteer.objects.filter(user_id=id).delete()

    def delete_by_ids(self, request):
        temp = QueryDict(request.body)
        tempItem = list(temp.lists())
        tx = list(tempItem.__getitem__(0))
        ids = str(list(tx.pop())).replace('[', '').replace(']', '')
        result = Volunteer.objects.raw('select * from volunteer where user_id in (' + ids + ')')
        for ax in result:
            Volunteer.delete(ax)

    def resetPwd(self, request):
        id = request.GET.get('id')
        print(id)
        encode_pwd = hashlib.md5('123456'.encode(encoding='UTF-8')).hexdigest()
        volunteer = Volunteer.objects.filter(user_id=id).update(pwd=encode_pwd)
        return ApiResponse.ok('密码重置成功')


class VolunteerTeamView(View):
    def dispatch(self, request, *args, **kwargs):
        result = super(VolunteerTeamView, self).dispatch(request, *args, **kwargs)
        return result

    def get(self, request):
        if str(request.GET.get('method')).__eq__('getAllInfo'):
            result = self.get_all_volunteer_team_page(request)
            return JsonResponse(result)
        elif str(request.GET.get('method')).__eq__('getVolunteerTeamDetailByTeamId'):
            result = self.get_volunteer_team_detail_by_teamid(request)
            return JsonResponse(result, safe=False)
        elif str(request.GET.get('method')).__eq__('resetPwd'):
            result = self.resetPwd(request)
            return JsonResponse(result, safe=False)
        return render(request, 'admin/team.html')

    def post(self, request):
        for x in range(1000):
            try:
                VolunteerTeam.objects.create(
                    team_id=str(uuid.uuid4()).replace('-', ''),
                    team_name='测试志愿项目',
                    team_login_name=get_userTeamName(),
                    team_pwd=hashlib.md5('123456'.encode(encoding='UTF-8')).hexdigest(),
                    team_intro='这是一个测试介绍',
                    team_create_time=timezone.datetime.now(),
                    team_concact=get_name(),
                    team_concact_phone=get_tel(),
                    remove_flag=random.randint(0, 1)
                )
                print(x)
            except Exception as e:
                print(e)
        return HttpResponse("生成成功")

    def put(self, request):
        return HttpResponse("Put 请求")

    def delete(self, request):
        method = request.GET.get('method')
        if str(method).__eq__('deleteById'):
            self.delete_by_id(request)
            return JsonResponse(ApiResponse.ok("操作成功"))
        elif str(method).__eq__('deleteByIds'):
            self.delete_by_ids(request)
            return JsonResponse(ApiResponse.ok("操作成功"))

    def get_all_volunteer_team_page(self, request):
        try:
            remove_flag = request.GET.get('remove_flag')
            page = request.GET.get("page")
            limit = request.GET.get("limit")
            datas = VolunteerTeam.objects.filter(remove_flag=remove_flag)
            page_result = Paginator(datas, limit)
            return ApiResponse.ok('获取成功', page_result.page(number=page), page_result.count)
        except Exception as e:
            print(e)

    def get_volunteer_team_detail_by_teamid(self, request):
        teamId = request.GET.get('team_id')
        volunteerTeam = VolunteerTeam.objects.filter(team_id=teamId)
        return ApiResponse.ok('获取成功', volunteerTeam)

    def delete_by_id(self, request):
        id = request.GET.get('team_id')
        VolunteerTeam.objects.filter(team_id=id).delete()

    def delete_by_ids(self, request):
        temp = QueryDict(request.body)
        tempItem = list(temp.lists())
        tx = list(tempItem.__getitem__(0))
        ids = str(list(tx.pop())).replace('[', '').replace(']', '')
        result = VolunteerTeam.objects.raw('select * from volunteer_team where team_id in (' + ids + ')')
        for ax in result:
            VolunteerTeam.delete(ax)

    def resetPwd(self, request):
        id = request.GET.get('id')
        print(id)
        encode_pwd = hashlib.md5('123456'.encode(encoding='UTF-8')).hexdigest()
        volunteerTeam = VolunteerTeam.objects.filter(team_id=id).update(team_pwd=encode_pwd)
        return ApiResponse.ok('密码重置成功')


# 三级省市联动
class ThreeLevelProvinceAndCityAndAreaLinker(View):
    def dispatch(self, request, *args, **kwargs):
        result = super(ThreeLevelProvinceAndCityAndAreaLinker, self).dispatch(request, *args, **kwargs)
        return result

    def get(self, request):
        if str(request.GET.get('method')).__eq__('getCitiesByProvinceCode'):
            result = self.getCitiesByProvinceCode(request)
        elif str(request.GET.get('method')).__eq__('getProvinceCodeByProvinceName'):
            result = self.getProvinceInfoByProvinceName(request)
        elif str(request.GET.get('method')).__eq__('getAreasByCityCode'):
            result = self.getAreasByCityCode(request)
        elif str(request.GET.get('method')).__eq__('getAllProvinces'):
            result = self.getAllProvinces(request)
        elif str(request.GET.get('method')).__eq__('getProvinceInfoByProvinceCode'):
            result = self.getProvinceInfoByProvinceCode(request)
        elif str(request.GET.get('method')).__eq__('getCityInfoByCityCode'):
            result = self.getCityInfoByCityCode(request)
        elif str(request.GET.get('method')).__eq__('getAreaInfoByAreaCode'):
            result = self.getAreaInfoByAreaCode(request)
        return JsonResponse(result)

    def getCitiesByProvinceCode(self, request) -> object:
        provinceCode = request.GET.get('province_code')
        datas = City.objects.filter(provincecode=provinceCode)
        return ApiResponse.ok('获取成功', datas)

    def getProvinceInfoByProvinceName(self, request) -> object:
        provinceName = request.GET.get('province_name')
        datas = Province.objects.filter(name=provinceName)
        return ApiResponse.ok('获取成功', datas)

    def getAreasByCityCode(self, request) -> object:
        cityCode = request.GET.get('city_code')
        datas = Area.objects.filter(citycode=cityCode)
        return ApiResponse.ok('获取成功', datas)

    def getAllProvinces(self, request) -> object:
        datas = Province.objects.all()
        return ApiResponse.ok('获取成功', datas)

    def getProvinceInfoByProvinceCode(self, request) -> object:
        provinceCode = request.GET.get('province_code')
        datas = Province.objects.filter(code=provinceCode)
        return ApiResponse.ok('获取成功', datas)

    def getCityInfoByCityCode(self, request) -> object:
        cityCode = request.GET.get('city_code')
        datas = City.objects.filter(code=cityCode)
        return ApiResponse.ok('获取成功', datas)

    def getAreaInfoByAreaCode(self, request) -> object:
        areaCode = request.GET.get('area_code')
        datas = Area.objects.filter(code=areaCode)
        return ApiResponse.ok('获取成功', datas)