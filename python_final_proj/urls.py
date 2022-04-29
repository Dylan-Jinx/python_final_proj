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

import app_web.views as web
import app_admin.views as admin
from python_final_proj.settings import STATIC_ROOT

urlpatterns = [
    path('admin/index/', admin.IndexView.as_view()),
    path('admin/login/', admin.LoginView.as_view()),
    path('admin/logout/', admin.LogOutView.as_view()),
    path('volunteer/', admin.VolunteerView.as_view()),


    path('api/v1/volunteer/', admin.VolunteerData.as_view()),

    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': STATIC_ROOT}),
]
