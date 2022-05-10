import hashlib

from django.core.paginator import Paginator
from django.http import *
from django.shortcuts import render
# Create your views here.
from django.views import View
import json

from app_web.models import *
from utils import ApiResponse


class AppIndex(View):
    def dispatch(self, request, *args, **kwargs):
        result = super(AppIndex, self).dispatch(request, *args, **kwargs)
        return result

    def get(self, request):

        if str(request.GET.get('method')).__eq__('loginPage'):
            return HttpResponseRedirect('../user/login/')
        if str(request.GET.get('method')).__eq__('registerRegPage'):
            return HttpResponseRedirect('../register/')
        if str(request.GET.get('method')).__eq__('registerRegTeamPage'):
            return HttpResponseRedirect('../register/team/')
        return render(request, 'web/index.html')


class LoginView(View):
    def dispatch(self, request, *args, **kwargs):
        result = super(LoginView, self).dispatch(request, *args, **kwargs)
        return result

    def get(self, request):
        return render(request, 'web/login.html', {'breadNav': '登录'})

    def post(self, request):
        datas = json.loads(json.dumps(request.POST))
        if str(datas.get('method')).__eq__('volunteerLogin'):
            result = self.volunteerLogin(datas)
            if result:
                return JsonResponse({'code': 200, 'msg': '登录成功'})
            else:
                return JsonResponse({'code': 0, 'msg': '账户名或密码错误'})

    def volunteerLogin(self, datas) -> bool:
        loginName = datas.get('login_name')
        loginPwd = str(datas.get('pwd'))
        realPwd = hashlib.md5(loginPwd.encode(encoding='UTF-8')).hexdigest()
        queryResult = Volunteer.objects.filter(id_card=loginName, pwd=realPwd)
        return queryResult.count() > 0


class TeamView(View):
    def dispatch(self, request, *args, **kwargs):
        result = super(TeamView, self).dispatch(request, *args, **kwargs)
        return result

    def get(self, request):
        method = request.GET.get('method')
        if str(method).__eq__('allWithPage'):
            page = request.GET.get('page')
            limit = request.GET.get('limit')
            result = self.allWithPage(page, limit)
            team_count = VolunteerTeam.objects.count()
            page_count = team_count/int(request.GET.get('limit'))
            page_count = int(page_count) + 1
            return render(request, 'web/team.html', {'breadNav': '志愿队伍', 'teamInfo': result, 'teamCount': team_count, 'pageIndex': int(page), 'pageCount': page_count})
        return render(request, 'web/team.html', {'breadNav': '志愿队伍', 'teamInfo': None})

    def allWithPage(self, page, limit):
        datas = VolunteerTeam.objects.all()
        page_result = Paginator(datas, limit)
        return page_result.page(page)


class RegisterView(View):
    def dispatch(self, request, *args, **kwargs):
        result = super(RegisterView, self).dispatch(request, *args, **kwargs)
        return result

    def get(self, request):
        return render(request, 'web/register.html')


class TeamRegisterView(View):
    def dispatch(self, request, *args, **kwargs):
        result = super(TeamRegisterView, self).dispatch(request, *args, **kwargs)
        return result

    def get(self, request):
        return render(request, 'web/team_register.html')


class BaseView(View):
    def dispatch(self, request, *args, **kwargs):
        result = super(BaseView, self).dispatch(request, *args, **kwargs)
        return result

    def get(self, request):
        return render(request, 'web/base_index.html')


class AreaIndexView(View):
    def dispatch(self, request, *args, **kwargs):
        result = super(AreaIndexView, self).dispatch(request, *args, **kwargs)
        return result

    def get(self, request):
        return render(request, 'web/user_index.html')