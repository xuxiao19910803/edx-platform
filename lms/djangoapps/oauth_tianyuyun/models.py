#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from .utils import create_new_user


class OAuthUserInfo(models.Model):
    OAUTH_COME_FROM_TIANYU = 1
    OAUTH_COME_FROM = (
        (OAUTH_COME_FROM_TIANYU, u'TIANYU'),
    )
    pid = models.CharField(primary_key=True, max_length=255)  # (come_from)_(oauth_user_id)
    come_from = models.IntegerField(choices=OAUTH_COME_FROM)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=None)
    username_reset = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('OAuthUserInfo')
        verbose_name_plural = _('OAuthUserInfo')

    @staticmethod
    def gen_pid(person_id, come_from):
        """
        :param person_id:
        :param come_from:
        :return: {person_id}_{come_from} to person_id
        """
        return '%s_%s' % (person_id, come_from)

    @classmethod
    def get_or_create_new_user(cls, person_id, come_from, user=None, name=''):
        """
        :param person_id:
        :param come_from:
        :param user:
        :param name:
        :return:
        """
        obj = cls.get_obj_or_none(person_id, come_from)
        create = False
        if not obj:
            pid = cls.gen_pid(person_id, come_from)
            obj, create = cls.objects.get_or_create(pid=pid, come_from=come_from)
            if not user:
                user = create_new_user(name)
            obj.user = user
            obj.save()
        return obj, create

    @classmethod
    def get_obj_or_none(cls, person_id, come_from):
        pid = cls.gen_pid(person_id, come_from)
        # return cls.objects.filter(pid=pid).first()
        objs = cls.objects.filter(pid=pid)
        return objs[0] if objs else None


class TianYuUserInfo(models.Model):
    idcardno = models.CharField(verbose_name=u'idcardno；', primary_key=True, max_length=255)
    personid = models.CharField(verbose_name=u'用户的统一ID；', max_length=255)
    gender = models.CharField(verbose_name=u'性别', max_length=1, default='')  # 0是女，1为男
    birthday = models.CharField(verbose_name=u'生日', max_length=64, default='')
    name = models.CharField(verbose_name=u'用户姓名', max_length=32, default='')
    usertype = models.CharField(verbose_name=u'用户类型', max_length=1, default='')  # 学生:0; 老师:1; 家长:2; 机构:3
    orgaid = models.CharField(verbose_name=u'机构编号', max_length=32, default='')
    organame = models.CharField(verbose_name=u'机构名称', max_length=64, default='')
    classid = models.CharField(verbose_name=u'班级id', max_length=32, default='')
    classname = models.CharField(verbose_name=u'班级名称', max_length=64, default='')
    account = models.CharField(verbose_name=u'账号', max_length=100, default='')

    @classmethod
    def get_or_create_by_info(cls, user_info):
        """
        :param user_info:{
            "personid" : "CF4D06BE8BC74A59866FFBE2745EB519",
            "birthday" : "1990-10-23",
            "gender" : "1",
            "name" : "柯宏树",
            "usertype" : "0",
            "idcardno" : "440901198508232100",
            "fnascount" : 0,
            "userlogolist" : [ ],
            "orgaid" : "C13B6DE0493848558F03F0B36B3F229B",
            "organame" : "华中师范大学第一附属中学",
            "orgaidentity" : [ "5" ],
            "classid" : "335181135C6A41F595C84008F3957C58",
            "classname" : "高二(12)班",
            "classidentity" : [ "5" ],
            "account" : "13800138012"
        }
        :return: User instance
        """
        idcardno = user_info.get('idcardno', '')
        if idcardno:
            u, create = cls.objects.get_or_create(idcardno=idcardno)
            for k, v in user_info.items():
                setattr(u, k, v)
            u.save()
            return u
