# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from collections import namedtuple
from json import JSONEncoder

from django.db import models


class DictDetail(models.Model):
    dict_code = models.CharField(max_length=255, blank=True, null=True)
    dict_detail_id = models.CharField(max_length=255, blank=True, null=True)
    dict_info = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dict_detail'


class DictType(models.Model):
    dict_code = models.CharField(max_length=255, blank=True, null=True)
    dict_type = models.CharField(max_length=255, blank=True, null=True)
    dict_description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dict_type'


class ProjectJoin(models.Model):
    user_id = models.CharField(max_length=255, blank=True, null=True)
    project_id = models.CharField(max_length=255, blank=True, null=True)
    hour = models.CharField(max_length=255, blank=True, null=True)
    join_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_join'


class TeamMember(models.Model):
    team_id = models.CharField(max_length=255, blank=True, null=True)
    user_id = models.CharField(max_length=255, blank=True, null=True)
    join_time = models.DateTimeField(blank=True, null=True)
    remove_flag = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'team_member'


class TeamProject(models.Model):
    project_id = models.CharField(max_length=255, blank=True, null=True)
    team_id = models.CharField(max_length=255, blank=True, null=True)
    project_name = models.CharField(max_length=255, blank=True, null=True)
    project_info = models.TextField(blank=True, null=True)
    project_concact = models.CharField(max_length=255, blank=True, null=True)
    project_concact_phone = models.CharField(max_length=255, blank=True, null=True)
    project_icon = models.TextField(blank=True, null=True)
    service_type = models.CharField(max_length=255, blank=True, null=True)
    service_obj = models.CharField(max_length=255, blank=True, null=True)
    project_area = models.CharField(max_length=255, blank=True, null=True)
    project_mem = models.CharField(max_length=255, blank=True, null=True)
    start_time = models.DateField(blank=True, null=True)
    end_time = models.DateField(blank=True, null=True)
    check_status = models.CharField(max_length=255, blank=True, null=True)
    remove_flag = models.CharField(max_length=255, blank=True, null=True)
    service_hour = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'team_project'


class Volunteer(models.Model):
    user_id = models.CharField(max_length=255, blank=True, null=True)
    nick_name = models.CharField(max_length=255, blank=True, null=True)
    user_name = models.CharField(max_length=255, blank=True, null=True)
    id_card = models.CharField(max_length=255, blank=True, null=True)
    pwd = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    user_mail = models.CharField(max_length=255, blank=True, null=True)
    qq = models.CharField(max_length=255, blank=True, null=True)
    wechat = models.CharField(max_length=255, blank=True, null=True)
    hometown = models.CharField(max_length=255, blank=True, null=True)
    education = models.CharField(max_length=255, blank=True, null=True)
    position = models.CharField(max_length=255, blank=True, null=True)
    service_area = models.CharField(max_length=255, blank=True, null=True)
    user_icon = models.TextField(blank=True, null=True)
    remove_flag = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'volunteer'
        verbose_name = verbose_name_plural = '志愿者信息'

    def VolunteerReflect(obj):
        return namedtuple('Volunteer', obj.keys())(*obj.values())


class VolunteerComment(models.Model):
    id = models.BigAutoField(primary_key=True)
    team_id = models.CharField(max_length=255, blank=True, null=True)
    project_id = models.CharField(max_length=255, blank=True, null=True)
    user_id = models.CharField(max_length=255, blank=True, null=True)
    comment_content = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'volunteer_comment'


class VolunteerDetail(models.Model):
    user_id = models.CharField(max_length=255, blank=True, null=True)
    cloth_size = models.CharField(max_length=255, blank=True, null=True)
    blood_type = models.CharField(max_length=255, blank=True, null=True)
    service_exp = models.TextField(blank=True, null=True)
    service_type = models.CharField(max_length=255, blank=True, null=True)
    service_prof = models.CharField(max_length=255, blank=True, null=True)
    advanced = models.CharField(max_length=255, blank=True, null=True)
    team_invite_proj = models.CharField(max_length=255, blank=True, null=True)
    team_invite = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'volunteer_detail'


class VolunteerRank(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.CharField(max_length=255, blank=True, null=True)
    punctual = models.CharField(max_length=255, blank=True, null=True)
    service_atitude = models.CharField(max_length=255, blank=True, null=True)
    profess_level = models.CharField(max_length=255, blank=True, null=True)
    train_time = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'volunteer_rank'


class VolunteerTeam(models.Model):
    team_id = models.CharField(max_length=255, blank=True, null=True)
    team_login_name = models.CharField(max_length=255, blank=True, null=True)
    team_pwd = models.CharField(max_length=255, blank=True, null=True)
    team_concact = models.CharField(max_length=255, blank=True, null=True)
    team_concact_phone = models.CharField(max_length=255, blank=True, null=True)
    team_icon = models.TextField(blank=True, null=True)
    team_intro = models.TextField(blank=True, null=True)
    team_create_time = models.DateTimeField(blank=True, null=True)
    remove_flag = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'volunteer_team'
