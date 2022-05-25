import hashlib
import uuid
from datetime import datetime

from django.core.paginator import Paginator
from django.db.models import QuerySet
from django.http import *
from django.shortcuts import render
# Create your views here.
from django.utils import timezone
from django.views import View
import json

from app_web.models import *
from utils import ApiResponse
from utils.db_data_convert import query_result_convert


class AppIndex(View):
    def dispatch(self, request, *args, **kwargs):
        result = super(AppIndex, self).dispatch(request, *args, **kwargs)
        return result

    def get(self, request):
        if str(request.GET.get('method')).__eq__('loginPage'):
            return HttpResponseRedirect('../user/login/')
        return render(request, 'web/index.html')


class LoginView(View):
    def dispatch(self, request, *args, **kwargs):
        result = super(LoginView, self).dispatch(request, *args, **kwargs)
        return result

    def get(self, request):
        if str(request.GET.get('method')).__eq__('logout'):
            request.session['is_login'] = False
            request.session["user_id"] = ""
            request.session["nick_name"] = ""
            del request.session["user_id"]
            del request.session["nick_name"]
            return HttpResponseRedirect('../../index')
        return render(request, 'web/login.html', {'breadNav': {'登录'}})

    def post(self, request):
        datas = json.loads(json.dumps(request.POST))
        if str(datas.get('method')).__eq__('volunteerLogin'):
            result = self.volunteerLogin(datas)

            if result.count() > 0:
                request.session['is_login'] = True
                request.session['user_id'] = result.first().user_id
                request.session['nick_name'] = result.first().nick_name
                return JsonResponse({'code': 200, 'msg': '登录成功'})
            else:
                return JsonResponse({'code': 0, 'msg': '账户名或密码错误'})

    def volunteerLogin(self, datas) -> QuerySet:
        loginName = datas.get('login_name')
        loginPwd = str(datas.get('pwd'))
        realPwd = hashlib.md5(loginPwd.encode(encoding='UTF-8')).hexdigest()
        queryResult = Volunteer.objects.filter(id_card=loginName, pwd=realPwd)
        return queryResult


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
            page_count = team_count / int(request.GET.get('limit'))
            page_count = int(page_count) + 1
            return render(request, 'web/team.html',
                          {'breadNav': {'志愿队伍'}, 'teamInfo': result, 'teamCount': team_count, 'pageIndex': int(page),
                           'pageCount': page_count})
        return render(request, 'web/team.html', {'breadNav': {'志愿队伍'}, 'teamInfo': None})

    def allWithPage(self, page, limit):
        datas = VolunteerTeam.objects.all()
        page_result = Paginator(datas, limit)
        return page_result.page(page)


class TeamDetailView(View):
    def dispatch(self, request, *args, **kwargs):
        result = super(TeamDetailView, self).dispatch(request, *args, **kwargs)
        return result

    def get(self, request):
        try:
            teamId = request.GET.get('team_id')
            userId = request.session['user_id']
            commentInfo = TeamComment.objects.filter(team_id=teamId, ctr_flag__in=[0, 1])
            data = VolunteerTeam.objects.filter(team_id=teamId)
            if userId is not None:
                joinStatu = TeamMember.objects.filter(team_id=teamId, user_id=userId)
                if joinStatu.count() > 0:
                    return render(request, 'web/team_detail.html',
                                  {'breadNav': {'志愿队伍', '队伍详细'}, 'teamInfo': data, 'joinStatus': False,
                                   'comments': commentInfo})
                else:
                    return render(request, 'web/team_detail.html',
                                  {'breadNav': {'志愿队伍', '队伍详细'}, 'teamInfo': data, 'joinStatus': True,
                                   'comments': commentInfo})
            return render(request, 'web/team_detail.html',
                          {'breadNav': {'志愿队伍', '队伍详细'}, 'teamInfo': data, 'joinStatus': True, 'comments': None})
        except Exception as e:
            return render(request, 'web/team_detail.html',
                          {'breadNav': {'志愿队伍', '队伍详细'}, 'teamInfo': data, 'joinStatus': True})


class RegisterView(View):
    def dispatch(self, request, *args, **kwargs):
        result = super(RegisterView, self).dispatch(request, *args, **kwargs)
        return result

    def get(self, request):
        method = request.GET.get("method")
        if str(method).__eq__('vol'):
            return render(request, 'web/register.html', {'breadNav': {'志愿者注册'}})
        elif str(method).__eq__('team'):
            provinceData = Province.objects.all()
            return render(request, 'web/team_register.html', {'breadNav': {'志愿队伍注册'}, "provinces": provinceData})

    def post(self, request):
        datas = json.loads(json.dumps(request.POST))
        userCount = Volunteer.objects.filter(phone=datas.get('phone')).count()
        if userCount > 0:
            return JsonResponse(ApiResponse.ApiResponse.ok(msg="该手机号码已经被注册"))
        sql = "insert into volunteer(user_id,phone,nick_name,user_name,id_card,pwd,punctual,train_time,service_atitude,profess_level,remove_flag)" \
              "value(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,0)"
        result = query_result_convert.origin_db_query(sql, [str(uuid.uuid4()).replace('-', ''), datas.get('phone'),
                                                            datas.get('nick_name'), datas.get('real_name'),
                                                            datas.get('id_card'), hashlib.md5(
                str(datas.get('pwd')).encode(encoding='UTF-8')).hexdigest(), 5.0, 0, 5.0, 5.0])
        print(result)
        return JsonResponse(ApiResponse.ApiResponse.ok(msg="注册成功"))


class TeamRegisterView(View):
    def dispatch(self, request, *args, **kwargs):
        result = super(TeamRegisterView, self).dispatch(request, *args, **kwargs)
        return result

    def get(self, request):
        return render(request, 'web/team_register.html')

    def post(self, request):
        datas = json.loads(json.dumps(request.POST))
        loginNameCount = VolunteerTeam.objects.filter(team_login_name=datas.get('login_name')).count()
        if loginNameCount > 0:
            return JsonResponse(ApiResponse.ApiResponse.ok(msg="登录名已被注册"))
        sql = "insert into volunteer_team(team_id,team_name,team_login_name,team_pwd,team_concact,team_concact_phone,team_intro,team_create_time,team_area,remove_flag)" \
              "value(%s,%s,%s,%s,%s,%s,%s,%s,%s,0)"
        result = query_result_convert.origin_db_query(sql, [str(uuid.uuid4()).replace('-', ''), datas.get('team_name'),
                                                            datas.get('login_name'), hashlib.md5(
                str(datas.get('pwd')).encode(encoding='UTF-8')).hexdigest(), datas.get('contact_name'),
                                                            datas.get('phone'), datas.get('team_info'),
                                                            timezone.datetime.now(),
                                                            datas.get('policy_code')])
        print(result)
        return JsonResponse(ApiResponse.ApiResponse.ok(msg="注册成功"))


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


class JoinTeamView(View):
    def dispatch(self, request, *args, **kwargs):
        result = super(JoinTeamView, self).dispatch(request, *args, **kwargs)
        return result

    def get(self, request):
        return render(request, 'web/user_index.html')

    def post(self, request):
        datas = json.loads(json.dumps(request.POST))
        if str(datas.get('method')).__eq__('applyTeam'):
            if self.applyTeam(datas):
                return JsonResponse(ApiResponse.ApiResponse.ok_simple('提交申请成功'))
            else:
                return JsonResponse(ApiResponse.ApiResponse.ok_simple('已经是该队伍的成员了'))

    def applyTeam(self, datas) -> bool:
        teamId = datas.get('team_id')
        userId = datas.get('user_id')
        datas = TeamMember.objects.filter(team_id=teamId, user_id=userId, )
        if datas.count() == 0:
            TeamMember.objects.create(
                team_id=teamId,
                user_id=userId,
                join_time=timezone.datetime.now(),
                remove_flag=0
            )
            return True
        else:
            return False


class TeamCommentView(View):
    def dispatch(self, request, *args, **kwargs):
        result = super(TeamCommentView, self).dispatch(request, *args, **kwargs)
        return result

    def post(self, request):
        datas = json.loads(json.dumps(request.POST))
        if str(datas.get('method')).__eq__('submitTeamComment'):
            if self.submitTeamComment(datas):
                return JsonResponse(ApiResponse.ApiResponse.ok('发表评论成功'))
            else:
                return JsonResponse(ApiResponse.ApiResponse.ok('发表评论成功'))

    def submitTeamComment(self, datas):
        try:
            comment = datas.get('comment', None)
            userId = datas.get('user_id', None)
            teamId = datas.get('team_id', None)
            if comment is not None:
                TeamComment.objects.create(
                    comment_content=comment,
                    team_id=teamId,
                    user_id=userId,
                    ctr_flag=0,
                    create_time=timezone.datetime.now()
                )
                return True
            return False
        except Exception as e:
            print(e)
            return False


class UserDetailView(View):
    def dispatch(self, request, *args, **kwargs):
        result = super(UserDetailView, self).dispatch(request, *args, **kwargs)
        return result

    def get(self, request):
        userId = request.GET.get("user_id")
        datas = Volunteer.objects.filter(user_id=userId).first()
        teamCount = TeamMember.objects.filter(user_id=userId).count()
        commentCount = TeamComment.objects.filter(user_id=userId).count()
        print(teamCount)
        print(datas)
        return render(request, 'web/user_detail.html',
                      {'breadNav': {'用户信息'}, 'volunteer': datas, 'team_count': teamCount,
                       'comment_count': commentCount})
