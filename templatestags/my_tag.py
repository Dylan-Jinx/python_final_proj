import datetime as dt

from django import template

from app_web.models import *

register = template.Library()


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
