import datetime
import hashlib
import json
import random
import threading
import time
import uuid

import django.db
import django.utils.timezone as timezone
from django.core.paginator import Paginator
from django.db import connection
from django.db.models import Model, QuerySet
from django.http import JsonResponse, QueryDict
from django.shortcuts import *
from django.template.response import *
from django.views import View
from pyecharts.charts import *
from django.db.models import Avg, Max, Min, Count, Sum
from pyecharts import options as opts

import app_web.models
from app_admin.models import *
from utils.ApiResponse import ApiResponse
from utils.db_data_convert import query_result_convert
from utils.generator import PersonalInfoGenerator
from utils.generator.PersonalInfoGenerator import get_name, get_tel
from utils.generator.username import get_userTeamName


def getAreaNameByCode(areaCode) -> object:
    temp = list(areaCode)
    province = temp[0] + temp[1]
    city = province + temp[2] + temp[3]
    area = city + temp[4] + temp[5]
    province_name = Province.objects.filter(code=province + '0000').first().name
    city_name = City.objects.filter(code=city + '00').first().name
    area_name = Area.objects.filter(code=area).first().name
    if city_name.__eq__(area_name):
        area_name = ''
    result = province_name + city_name + area_name
    return result


class LoginView(View):
    def get(self, request):
        return render(request, "admin/login.html")

    def post(self, request):
        phone_data = request.POST.get("phone")
        pwd_data = request.POST.get("password")
        encode_pwd = hashlib.md5(pwd_data.encode(encoding='UTF-8')).hexdigest()
        print(f"{phone_data} {pwd_data}")
        team = VolunteerTeam.objects.filter(team_login_name=phone_data, team_pwd=encode_pwd).first()
        if team is not None:
            request.session["team_id"] = team.team_id
            request.session["nick_name"] = team.team_name
            return HttpResponseRedirect("/admin/index/")
        else:
            return render(request, "admin/login.html", {"loginTip": "用户名或密码输入错误"})


class LogOutView(View):
    def get(self, request):
        try:
            del request.session["user_id"]
            del request.session["nick_name"]
            return HttpResponseRedirect("/admin/login")
        except Exception as e:
            print(e)
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
            return JsonResponse(result)
        elif str(request.GET.get('method')).__eq__('resetPwd'):
            result = self.resetPwd(request)
            return JsonResponse(result, safe=False)
        elif str(request.GET.get('method')).__eq__('testAddVol'):
            self.add_volunteer()
            return HttpResponse('添加成功')
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

    def randomAreaCode(self) -> object:
        areaList = Area.objects.all()
        datas = areaList.values_list()
        index = random.randint(0, len(datas) - 1)
        return datas[index][1]

    def randomAreaName(self, areaCode) -> object:
        areaName = Area.objects.filter(code=areaCode).first().name
        return areaName

    def randomDataArray(self, start, end, num):
        random.seed(timezone.datetime.now())
        return random.sample(range(start, end), num)

    def add_volunteer(self):
        count = 1
        volunteer_list = []
        while True:
            random.seed(timezone.datetime.now())
            acode = self.randomAreaCode()
            aname = self.randomAreaName(acode)
            vol_obj = app_web.models.Volunteer(
                user_id=str(uuid.uuid4()).replace('-', ''),
                nick_name=PersonalInfoGenerator.get_name(),
                user_name=PersonalInfoGenerator.get_name(),
                user_mail=PersonalInfoGenerator.get_email(),
                qq=PersonalInfoGenerator.get_qq(),
                phone=PersonalInfoGenerator.get_tel(),
                id_card=PersonalInfoGenerator.get_idnum(),
                service_area=acode,
                hometown=acode,
                position=random.randint(1, 7),
                education=random.randint(1, 9),
                wechat='wx_id' + str(uuid.uuid4()).replace('-', ''),
                pwd=hashlib.md5(str('123456').encode(encoding='UTF-8')).hexdigest(),
                service_type=self.randomDataArray(1, 21, 4),
                punctual=random.random() * 5,
                train_time=random.randint(0, 3000),
                service_atitude=random.random() * 5,
                profess_level=random.random() * 5,
                remove_flag=0
            )
            count = count + 1
            volunteer_list.append(vol_obj)
            if count % 10 == 0:
                Volunteer.objects.bulk_create(volunteer_list)
                volunteer_list.clear()
            if count == 100000:
                break
            print(f'生成标记：{count}')

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
        areaRealName = ''
        serviceRealName = ''
        volunteer = Volunteer.objects.filter(user_id=userId)
        if volunteer.first().hometown != None:
            areaCode = volunteer.first().hometown
            areaRealName = getAreaNameByCode(areaCode)
        if volunteer.first().service_area != None:
            serviceCode = volunteer.first().service_area
            serviceRealName = getAreaNameByCode(serviceCode)
        tempObj = dict(ApiResponse.ok('获取成功', volunteer)).get('data')
        return {"code": 0, "msg": "获取成功", "data": tempObj, "area_real_name": areaRealName,
                "service_real_name": serviceRealName}

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
        if str(request.GET.get('method')).__eq__('a'):
            return HttpResponse(self.randomAreaCode())
        elif str(request.GET.get('method')).__eq__('getAllInfo'):
            result = self.get_all_volunteer_team_page(request)
            return JsonResponse(result)
        elif str(request.GET.get('method')).__eq__('getVolunteerTeamDetailByTeamId'):
            result = self.get_volunteer_team_detail_by_teamid(request)
            return JsonResponse(result, safe=False)
        elif str(request.GET.get('method')).__eq__('resetPwd'):
            result = self.resetPwd(request)
            return JsonResponse(result, safe=False)
        elif str(request.GET.get('method')).__eq__('searchVolunteerTeamWithComplexQuery'):
            result = self.searchVolunteerTeamWithComplexQuery(request)
            return JsonResponse(result, safe=False)
        provinceData = Province.objects.all()
        return render(request, 'admin/team.html', {"provinces": provinceData})

    def post(self, request):
        for x in range(10000):
            acode = self.randomAreaCode()
            aname = self.randomAreaName(acode)
            print(acode)
            try:
                VolunteerTeam.objects.create(
                    team_id=str(uuid.uuid4()).replace('-', ''),
                    team_name='' + aname + '志愿服务队',
                    team_login_name=get_userTeamName(),
                    team_pwd=hashlib.md5('123456'.encode(encoding='UTF-8')).hexdigest(),
                    team_intro='这是在' + aname + '的志愿服务队',
                    team_create_time=timezone.datetime.now(),
                    team_concact=get_name(),
                    team_concact_phone=get_tel(),
                    team_area=acode,
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

    def resetPwd(self, request) -> object:
        id = request.GET.get('id')
        print(id)
        encode_pwd = hashlib.md5('123456'.encode(encoding='UTF-8')).hexdigest()
        volunteerTeam = VolunteerTeam.objects.filter(team_id=id).update(team_pwd=encode_pwd)
        return ApiResponse.ok('密码重置成功')

    def randomAreaCode(self) -> object:
        areaList = Area.objects.all()
        datas = areaList.values_list()
        index = random.randint(0, len(datas) - 1)
        return datas[index][1]

    def randomAreaName(self, areaCode) -> object:
        areaName = Area.objects.filter(code=areaCode).first().name
        return areaName

    def searchVolunteerTeamWithComplexQuery(self, request):
        areaCode = request.GET.get('area_code', None)
        teamName = request.GET.get('team_name', None)
        startTime = request.GET.get('start_time', None)
        endTime = request.GET.get('end_time', None)
        print(areaCode, teamName, startTime, endTime)
        page = request.GET.get("page")
        limit = request.GET.get("limit")
        datas = VolunteerTeam.objects
        if (areaCode is not None) & (~(str(areaCode).__eq__(''))):
            datas = datas.filter(team_area__istartswith=areaCode)
        if (teamName is not None) & (~(str(teamName).__eq__(''))):
            datas = datas.filter(team_name__icontains=teamName)
        if (startTime is not None) & (endTime is not None) & (~(str(startTime).__eq__(''))) & (
                ~(str(endTime).__eq__(''))):
            datas = datas.filter(team_create_time__range=[startTime, endTime])
        datas = datas.filter(remove_flag=0)
        page_result = Paginator(datas, limit)
        return ApiResponse.ok('获取成功', page_result.page(number=page), page_result.count)


class VolunteerTeamCheckView(View):
    def dispatch(self, request, *args, **kwargs):
        result = super(VolunteerTeamCheckView, self).dispatch(request, *args, **kwargs)
        return result

    def get(self, request):
        if str(request.GET.get('method')).__eq__('applySuccess'):
            result = self.applySuccess(request)
            return JsonResponse(result)
        elif str(request.GET.get('method')).__eq__('getAllInfo'):
            result = self.get_all_volunteer_team_check_page(request)
            return JsonResponse(result)
        elif str(request.GET.get('method')).__eq__('searchTeamByName'):
            result = self.search_team_by_name(request)
            return JsonResponse(result)
        return render(request, 'admin/teamcheck.html')

    def post(self, request):
        datas = json.loads(json.dumps(request.POST))
        if str(datas.get('method')).__eq__('applyFailed'):
            result = self.applyFailed(datas)
        return JsonResponse(result)

    def applyFailed(self, datas) -> object:
        teamId = datas.get('team_id')
        markTip = datas.get('mark_tip')
        VolunteerTeam.objects.filter(team_id=teamId).update(remark=markTip, team_create_time=timezone.datetime.now())
        return ApiResponse.ok_simple()

    def applySuccess(self, request) -> object:
        teamId = request.GET.get('team_id')
        VolunteerTeam.objects.filter(team_id=teamId).update(remove_flag=0)
        return ApiResponse.ok_simple()

    def get_all_volunteer_team_check_page(self, request):
        try:
            page = request.GET.get("page")
            limit = request.GET.get("limit")
            datas = VolunteerTeam.objects.filter(remove_flag=1, remark=None)
            page_result = Paginator(datas, limit)
            return ApiResponse.ok('获取成功', page_result.page(number=page), page_result.count)
        except Exception as e:
            print(e)

    def search_team_by_name(self, request):
        teamName = request.GET.get("team_name")
        datas = VolunteerTeam.objects.filter(remove_flag=1, team_name__contains=teamName)
        print(datas)
        print(datas.query)
        return ApiResponse.ok('获取成功', datas, 0)


class TeamManageView(View):
    def dispatch(self, request, *args, **kwargs):
        result = super(TeamManageView, self).dispatch(request, *args, **kwargs)
        return result

    def get(self, request):
        if str(request.GET.get('method')).__eq__('getAllInfo'):
            result = self.get_all_team_member(request)
            print(result)
            return JsonResponse(result)
        return render(request, 'admin/teammemberapply.html')

    def post(self, request):
        datas = json.loads(json.dumps(request.POST))
        if str(datas.get('method')).__eq__('applyStatus'):
            result = self.applyStatus(datas)
            if result:
                return JsonResponse(ApiResponse.ok('操作成功'))
            else:
                return JsonResponse(ApiResponse.ok('操作失败'))

    def get_all_team_member(self, request):
        removeFlag = request.GET.get('remove_flag')
        teamId = request.GET.get('team_id')
        page = request.GET.get("page")
        limit = request.GET.get("limit")
        datas = TeamMember.objects.filter(remove_flag=removeFlag).all()
        print(datas)

        sql = "SELECT volunteer.user_name,volunteer.phone,volunteer.phone,volunteer.user_mail,volunteer.service_area,volunteer_team.team_name,join_time,team_member.team_id,team_member.user_id" \
              " FROM volunteer,volunteer_team,team_member " \
              "WHERE  team_member.remove_flag = %s"

        result = query_result_convert.origin_db_query(sql, [teamId, removeFlag])
        return ApiResponse.ok_simple(data=result, count=result.__len__())

    def applyStatus(self, datas):
        try:
            userId = datas.get('user_id', None)
            status = datas.get('remove_flag', None)
            with connection.cursor() as cursor:
                cursor.execute('update team_member set remove_flag=%s where user_id=%s', [status, userId])
            return True
        except Exception as e:
            print(e)
            return False


# 数据字典
class DataDict(View):
    def dispatch(self, request, *args, **kwargs):
        result = super(DataDict, self).dispatch(request, *args, **kwargs)
        return result

    def get(self, request):
        if str(request.GET.get('method')).__eq__('getAllDictType'):
            result = self.getAllDictType(request)
            return JsonResponse(result)
        elif str(request.GET.get('method')).__eq__('getDictDataByDictTypeCode'):
            result = self.getDictDataByDictTypeCode(request)
            return JsonResponse(result)
        elif str(request.GET.get('method')).__eq__('getDictDetailByDictTypeCode'):
            result = self.getDictDetailByDictTypeCode(request)
            return JsonResponse(result)
        elif str(request.GET.get('method')).__eq__('getDictTypeByDictTypeCode'):
            result = self.getDictTypeByDictTypeCode(request)
            return JsonResponse(result)
        elif str(request.GET.get('method')).__eq__('delDictType'):
            result = self.delDictType(request)
            return JsonResponse(result)
        elif str(request.GET.get('method')).__eq__('delDictDetail'):
            result = self.delDictDetail(request)
            return JsonResponse(result)
        return render(request, 'admin/datadict.html')

    def post(self, request):
        if str(request.POST.get('method')).__eq__('addDictType'):
            result = self.addDictType(request)
        elif str(request.POST.get('method')).__eq__('addDictDataDetail'):
            result = self.addDictDataDetail(request)
        elif str(request.POST.get('method')).__eq__('editDictDataDetail'):
            result = self.editDictDataDetail(request)
        elif str(request.POST.get('method')).__eq__('editDictDetail'):
            result = self.editDictDetail(request)
        return JsonResponse(result)

    def put(self, request):
        return HttpResponse('Put 请求')

    def delete(self, request):
        return HttpResponse('DELETE 请求')

    def getAllDictType(self, request) -> object:
        page = request.GET.get("page")
        limit = request.GET.get("limit")
        datas = DictType.objects.all()
        if (page is not None) | (limit is not None):
            page_result = Paginator(datas, limit)
            return ApiResponse.ok('获取成功', page_result.page(number=page), page_result.count)
        else:
            return ApiResponse.ok('获取成功', datas)

    def getDictDataByDictTypeCode(self, request) -> object:
        dictCode = request.GET.get('dict_code')
        datas = DictDetail.objects.filter(dict_code=dictCode).order_by('dict_detail_id')
        return ApiResponse.ok('获取成功', datas)

    def addDictType(self, request) -> object:
        dictTypeName = request.POST.get('dict_type_name')
        dictDescription = request.POST.get('dict_description')
        DictType.objects.create(
            dict_code=str(uuid.uuid4()).replace('-', ''),
            dict_type=dictTypeName,
            dict_description=dictDescription
        )
        return ApiResponse.ok(msg='添加成功')

    def addDictDataDetail(self, request) -> object:
        dictTypeCode = request.POST.get('dict_type_code')
        dictDataVal = request.POST.get('dict_val')
        datas = DictDetail.objects.filter(dict_code=dictTypeCode)
        with connection.cursor() as cursor:
            cursor.execute(
                "select max(dict_detail_id) 'maxKey' from dict_detail WHERE dict_code=%s", [dictTypeCode])
            row = cursor.fetchone()
        print(row[0])
        if row[0] is None:
            sortIndex = 1
        else:
            sortIndex = int(row[0]) + 1
        print(sortIndex)
        DictDetail.objects.create(
            dict_code=dictTypeCode,
            dict_detail_id=sortIndex,
            dict_info=dictDataVal
        )
        return ApiResponse.ok(msg='操作成功')

    def getDictDetailByDictTypeCode(self, request) -> object:
        dictCode = request.GET.get('dict_code')
        page = request.GET.get("page")
        limit = request.GET.get("limit")
        datas = DictDetail.objects.filter(dict_code=dictCode)
        page_result = Paginator(datas, limit)
        return ApiResponse.ok('获取成功', page_result.page(number=page), page_result.count)

    def getDictTypeByDictTypeCode(self, request):
        dictCode = request.GET.get('dict_code')
        datas = DictType.objects.filter(dict_code=dictCode)
        return ApiResponse.ok('获取成功', datas)

    def editDictDataDetail(self, request):
        dictCode = request.POST.get('dict_code')
        dictTypeName = request.POST.get('dict_type_name')
        dictDescription = request.POST.get('dict_description')
        datas = DictType.objects.filter(dict_code=dictCode).update(dict_type=dictTypeName,
                                                                   dict_description=dictDescription)
        return ApiResponse.ok_simple()

    def delDictDetail(self, request):
        dictCode = request.GET.get('dict_code')
        dictDetailName = request.GET.get('dict_detail_name')
        DictDetail.objects.filter(dict_code=dictCode, dict_info=dictDetailName).delete()
        return ApiResponse.ok_simple()

    def editDictDetail(self, request):
        dictCode = request.POST.get('dict_code')
        dictDetailKey = request.POST.get('dict_detail_key')
        dictDetailVal = request.POST.get('dict_detail_val')
        datas = DictDetail.objects.filter(dict_code=dictCode, dict_detail_id=dictDetailKey).update(
            dict_info=dictDetailVal)
        return ApiResponse.ok_simple()

    def delDictType(self, request):
        dictCode = request.GET.get('dict_code')
        DictType.objects.filter(dict_code=dictCode).delete()
        return ApiResponse.ok_simple()


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
        elif str(request.GET.get('method')).__eq__('getAreaAllNameByCode'):
            result = self.getAreaAllNameByCode(request)
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

    def getAreaAllNameByCode(self, request) -> object:
        dataCode = request.GET.get('area_code', None)
        if dataCode.__eq__('null'):
            return {"result": ""}
        temp = list(dataCode)
        province = temp[0] + temp[1]
        city = province + temp[2] + temp[3]
        area = city + temp[4] + temp[5]
        province_name = Province.objects.filter(code=province + '0000').first().name
        city_name = City.objects.filter(code=city + '00').first().name
        area_name = Area.objects.filter(code=area).first().name
        if city_name.__eq__(area_name):
            area_name = ''
        result = province_name + city_name + area_name
        return {"result": result}


# 数据可视化
class DataVisual(View):
    def dispatch(self, request, *args, **kwargs):
        result = super(DataVisual, self).dispatch(request, *args, **kwargs)
        return result

    def get(self, request):
        self.areaVolunTimeGraph()

        # self.renderVolunteerGraph()
        # self.renderTeamGraph()

        return render(request, "admin/datavisual.html", )

    def renderVolunteerGraph(self):
        x_volunteer_val = []
        y_volunteer_val = []
        c = Pie()

        volunteer_num = Volunteer.objects.values("hometown").annotate(c=Count("nick_name")).values("hometown",
                                                                                                   "c").order_by("-c")
        visualCount = 1
        print(volunteer_num.query)
        for temp in volunteer_num:
            visualCount += 1
            if dict(temp).get('hometown') is not None:
                hometownCode = dict(temp).get('hometown')
                x_volunteer_val.append(Area.objects.filter(code=hometownCode).first().name)
                y_volunteer_val.append(dict(temp).get('c'))
            if visualCount > 10:
                break
        c.add("", [list(z) for z in zip(x_volunteer_val, y_volunteer_val)], radius=["40%", "75%"])
        # 圆环的粗细和大小
        c.set_global_opts(title_opts=opts.TitleOpts(title="志愿者人数排名前10区域"),
                          legend_opts=opts.LegendOpts(orient="vertical", pos_top="5%", pos_left="2%"))
        c.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}:{c}"))
        c.render("templates/admin/render.html")

    def renderTeamGraph(self):
        x_volunteer_val = []
        y_volunteer_val = []
        c = Pie()

        volunteer_num = VolunteerTeam.objects.values("team_area").annotate(c=Count("team_name")).values("team_area",
                                                                                                        "c").order_by(
            "-c")
        visualCount = 1
        print(volunteer_num.query)
        for temp in volunteer_num:
            visualCount += 1
            if dict(temp).get('team_area') is not None:
                hometownCode = dict(temp).get('team_area')
                x_volunteer_val.append(Area.objects.filter(code=hometownCode).first().name)
                y_volunteer_val.append(dict(temp).get('c'))
            if visualCount > 10:
                break
        c.add("", [list(z) for z in zip(x_volunteer_val, y_volunteer_val)], radius=["40%", "75%"])
        # 圆环的粗细和大小
        c.set_global_opts(title_opts=opts.TitleOpts(title="志愿队伍数排名前10区域"),
                          legend_opts=opts.LegendOpts(orient="vertical", pos_top="5%", pos_left="2%"))
        c.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}:{c}"))
        c.render("templates/admin/teamGraph.html")

    def areaVolunTimeGraph(self):
        line = Line()
        line2 = Line()
        # pie = Pie("各地区志愿者人数统计")

        x_volunteer_time_val = []
        y_volunteer_time_val = []
        x_volunteer_time_low_val = []
        y_volunteer_time_low_val = []
        volunteer_vol_times = Volunteer.objects.values("hometown").annotate(c=Avg("train_time")).values("hometown",
                                                                                                        "c").order_by(
            "-c")
        volunteer_vol_low_times = Volunteer.objects.values("hometown").annotate(c=Avg("train_time")).values("hometown",
                                                                                                            "c").order_by(
            "c")
        visualCount = 0
        visualCountLow = 0
        for temp in volunteer_vol_times:
            visualCount += 1

            if dict(temp).get('hometown') is not None:
                hometownCode = dict(temp).get('hometown')
                x_volunteer_time_val.append(Area.objects.filter(code=hometownCode).first().name)
                y_volunteer_time_val.append(dict(temp).get('c'))
                if visualCount > 10:
                    break

        for temp1 in volunteer_vol_low_times:
            visualCountLow += 1
            if dict(temp1).get('hometown') is not None:
                hometownCode = dict(temp1).get('hometown')
                if Area.objects.filter(code=hometownCode).first().name == '市辖区':
                    continue
                x_volunteer_time_low_val.append(Area.objects.filter(code=hometownCode).first().name)
                y_volunteer_time_low_val.append(dict(temp1).get('c'))
                if visualCountLow > 10:
                    break

        line.add_xaxis(x_volunteer_time_val)
        line2.add_xaxis(x_volunteer_time_low_val)
        line.add_yaxis("平均志愿时长最多的10个地区", y_volunteer_time_val)
        line2.add_yaxis("平均志愿时长最少的10个地区", y_volunteer_time_low_val)
        line.render("templates/admin/timeGraph.html")
        line2.render("templates/admin/timeLowGraph.html")


class ProjectInfoView(View):
    def dispatch(self, request, *args, **kwargs):
        result = super(ProjectInfoView, self).dispatch(request, *args, **kwargs)
        return result

    def get(self, request):
        if str(request.GET.get('method')).__eq__('getAllInfo'):
            result = self.get_all_project_page(request)
            return JsonResponse(result)
        elif str(request.GET.get('method')).__eq__('deleteProject'):
            result = self.delete_team_project(request)
            return JsonResponse(result)
        return render(request, "admin/teamprojectinfo.html")


    def get_all_project_page(self, request):
        try:
            teamId = request.GET.get('team_id')
            page = request.GET.get("page")
            limit = request.GET.get("limit")
            datas = TeamProject.objects.filter(team_id=teamId)
            page_result = Paginator(datas, limit)
            return ApiResponse.ok('获取成功', page_result.page(number=page), page_result.count)
        except Exception as e:
            print(e)

    def delete_team_project(self, request):
        projectId = request.GET.get('project_id')
        TeamProject.objects.filter(project_id=projectId).delete()
        return ApiResponse.api_reponse('操作成功')


class CreateProjectView(View):
    def dispatch(self, request, *args, **kwargs):
        result = super(CreateProjectView, self).dispatch(request, *args, **kwargs)
        return result

    def get(self, request):

        return render(request, "admin/project_add.html")
