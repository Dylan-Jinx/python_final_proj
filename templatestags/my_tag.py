import datetime as dt

from django import template

from app_web.models import *

register = template.Library()


@register.filter()
def get_service_type(value, arg):
    datas = arg
    datas = str(datas).replace('[', '').replace(']', '').replace(' ','').split(',')
    value = []
    for temp in datas:
        serviceInfo = DictDetail.objects.filter(dict_code='6b2f6f24a23a4b079ed19b97eab2ce4b',dict_detail_id=temp).first().dict_info
        value.append(serviceInfo)
    return value


@register.filter()
def match_team_name(value, arg):
    value = VolunteerTeam.objects.filter(team_id=arg).first().team_name
    return value


@register.filter()
def access_result_convert(value, arg):
    value = str(arg)[0:3]
    return value


@register.filter()
def area_convert(value, arg):
    value = Area.objects.filter(code=arg).first().name
    return value


@register.filter()
def real_area_detail(value, arg):
    areaInfo = Area.objects.filter(code=arg).first()
    cityInfo = City.objects.filter(code=areaInfo.citycode).first()
    provinceInfo = Province.objects.filter(code=cityInfo.provincecode).first()
    value = f'{provinceInfo.name}{cityInfo.name}{areaInfo.name}'
    return value


@register.filter()
def datetime_convert(value, arg):
    value = dt.datetime.strftime(arg, '%Y-%m-%d')
    return value


@register.filter()
def string_check(value, arg):
    if arg is not None:
        value = True
    else:
        value = False
    return value
