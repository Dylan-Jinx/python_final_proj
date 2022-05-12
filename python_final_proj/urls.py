"""python_final_proj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, re_path
from django.views.static import serve

import app_admin.views as admin
import app_web.views as web
from python_final_proj.settings import STATIC_ROOT

urlpatterns = [
    path('admin/index/', admin.IndexView.as_view()),
    path('admin/login/', admin.LoginView.as_view()),
    path('admin/logout/', admin.LogOutView.as_view()),

    path('volunteer/', admin.VolunteerView.as_view()),
    path('team/', admin.VolunteerTeamView.as_view()),
    path('teamcheck/', admin.VolunteerTeamCheckView.as_view()),
    path('regioncode/', admin.ThreeLevelProvinceAndCityAndAreaLinker.as_view()),
    path('dict/', admin.DataDict.as_view()),
    path('manageteam/', admin.TeamManageView.as_view()),


    path('index/', web.AppIndex.as_view()),
    path('user/login/', web.LoginView.as_view()),
    path('area/', web.AreaIndexView.as_view()),
    path('user/jointeam/', web.JoinTeamView.as_view()),
    path('user/team/', web.TeamView.as_view()),
    path('user/team/detail', web.TeamDetailView.as_view()),
    path('user/teamcomment/', web.TeamCommentView.as_view()),
    path('register/user/', web.RegisterView.as_view()),
    path('register/team/', web.RegisterView.as_view()),

    path('base/', web.BaseView.as_view()),

    re_path(r'^$', web.AppIndex.as_view()),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': STATIC_ROOT}),
]
