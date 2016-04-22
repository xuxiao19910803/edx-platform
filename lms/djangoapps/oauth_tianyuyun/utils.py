#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib
import random
import re
import requests
import string
import time

from django.contrib.auth.models import User
from django.core.cache import cache


from .settings import (
    APPID,
    TIANYUYUN_LOGIN_REDIRECT_URL, LOCAL_OAUTH_LOGIN_URL, TIANYUYUN_LOGIN_URL,
    TIANYUYUN_GET_TOKEN_URL, TIANYUYUN_GET_SESSIONID_INFO_URL
)

from .tianyuyun_security import gen_security_code, get_timestamp

TIANYUYUN_TOKEN_KEY = 'TIANYUYUN_TOKEN_KEY'
TIANYUYUN_TOKEN_TIMEOUT = 10 * 60 - 10
TIANYUYUN_PASSWORD = 'sdkt_123456'

BASE_STRING = string.lowercase + string.digits


class TianYuClient(object):
    @staticmethod
    def parse_usesessionid(str_xml):
        m = re.search('<cas:user>(?P<usesessionid>.+)</cas:user>', str_xml)
        return m.groupdict().get('usesessionid', None) if m else None

    @staticmethod
    def get_tianyuyun_oauth_url():
        """
        获取oauth的tianyuyun登录地址
        :return:
        """
        return TIANYUYUN_LOGIN_URL.format(service=urllib.quote(LOCAL_OAUTH_LOGIN_URL))

    def get_usesessionid_by_ticket(self, ticket):
        """
        验证通过的报文
        <cas:serviceResponse xmlns:cas=“http://www.whty.aam.com”>
        <cas:authenticationSuccess>
        <cas:user>testss10</cas:user>
        </cas:authenticationSuccess>
        </cas:serviceResponse>
        验证不通过的报文
        <cas:serviceResponse xmlns:cas=“http://www.whty.aam.com”>
            <cas:authenticationFailure code=“INVALID_TICKET”>
        　Ticket  SO6YEWI93093UTYDVXBZ4513==  not recognized
        </cas:authenticationFailure>
        </cas:serviceResponse>
        :param ticket:
        :return: str
        """
        resp = requests.get(TIANYUYUN_LOGIN_REDIRECT_URL.format(ticket=ticket))
        # print resp, resp.content
        return self.parse_usesessionid(resp.content)

    def get_tianyuyun_token(self):
        """{
          token	:token信息
          validtime	:有效期，只在有效期内(2小时)，应用无需重新申请，服务保存token及有效期，有效期内只需做一次验证。
          platformCode	:平台编码。六位数字，标明当前登录用户所属的平台
        }
        :return: str
        """
        token = cache.get(TIANYUYUN_TOKEN_KEY, None)
        if token:
            return token
        timestamp = get_timestamp()
        data = {
            'appid': APPID,
            'timestamp': timestamp,
            'keyinfo': gen_security_code(timestamp)
        }
        resp = requests.post(TIANYUYUN_GET_TOKEN_URL, data=json.dumps(data))
        # 'get_tianyuyun_token: ', resp.status_code
        # 'get_tianyuyun_token: ', resp.content
        resp = json.loads(resp.content) or {}
        token = resp.get('tokenInfo', {}).get('token', '')
        ex = TIANYUYUN_TOKEN_TIMEOUT  # expired time
        cache.set(TIANYUYUN_TOKEN_KEY, token, ex)
        return token

    def get_userinfo_by_sessionid(self, sessionid):
        """{
            "result": "000000",
            "usessionid": "da9933b0-65a7-41ac-9858-1e01d23c7977",
            "platformCode": "000000",
            "userinfo": {
                "personid": "CF4D06BE8BC74A59866FFBE2745EB519",
                "birthday": "1990-10-23",
                "gender": "1",
                "name": "柯宏树",
                "usertype": "0",
                "idcardno": "440901198508232100",
                "fnascount": 0,
                "userlogolist": [],
                "orgaid": "C13B6DE0493848558F03F0B36B3F229B",
                "organame": "华中师范大学第一附属中学",
                "orgaidentity": ["5"],
                "classid": "335181135C6A41F595C84008F3957C58",
                "classname": "高二(12)班",
                "classidentity": ["5"],
                "account": "13800138012"
            }
        }

        {"usessionid":"c8123f45-146f-4303-ba5e-a619c5e7764a",
        "platformCode":"660000",
        "result":"000000",
        "userinfo":
            {"personid":"ce0941e3f7b84103a6e339359edb5a99",
            "birthday":"",
            "gender":"1",
            "name":"张晓华",
            "usertype":"0",
            "platformCode":"600",
            "platformName":"新疆生产建设兵团教育局",
            "fnascount":0,
            "updateTime":"2016-04-06 09:52:49",
            "userlogolist":[
                {"logotype":"1",
                "logourl":"/uploads/avatar/data/15/39/ce0941e3f7b84103a6e339359edb5a99_45x45.jpg"
                },{
                "logotype":"2",
                "logourl":"/uploads/avatar/data/15/f7b84103a6e339359edb5a99_90x90.jpg"
                },],
            "orgaid":"90d0a1a85043405b8c76e13c109bb3d5",
            "organame":"新疆生产建设兵团第二中学",
            "classid":"4a232f4e432649e2bd962c3ef27sname":"一年级(1)班","classidentity":["5"],"account":"zhangxiaohua2"},"desc":"success"}

        :return userinfo
        """
        resp = requests.get(
            TIANYUYUN_GET_SESSIONID_INFO_URL.format(
                sessionid=sessionid, token=self.get_tianyuyun_token()))
        # 'get_userinfo_by_sessionid:   ', resp.content
        resp = json.loads(resp.content)

        if resp.get('result', '') == "000000":
            return resp.get('userinfo', {})
        else:
            return {}

    def get_or_create_oauth_by_userinfo(self, user_info, user=None):
        """
        :param user_info:
        {
            "personid": "CF4D06BE8BC74A59866FFBE2745EB519",
            "birthday": "1990-10-23",
            "gender": "1",
            "name": "柯宏树",
            "usertype": "0",
            "idcardno": "440901198508232100",
            "fnascount": 0,
            "userlogolist": [],
            "orgaid": "C13B6DE0493848558F03F0B36B3F229B",
            "organame": "华中师范大学第一附属中学",
            "orgaidentity": ["5"],
            "classid": "335181135C6A41F595C84008F3957C58",
            "classname": "高二(12)班",
            "classidentity": ["5"],
            "account": "13800138012"
        }
        :param user:
        :return: User instance
        """
        from .models import OAuthUserInfo, TianYuUserInfo
        idcardno = user_info.get('idcardno', '')
        if idcardno:
            info, create = OAuthUserInfo.get_or_create_new_user(
                idcardno, OAuthUserInfo.OAUTH_COME_FROM_TIANYU, user, user_info.get('name', ''))
            TianYuUserInfo.get_or_create_by_info(user_info)
            return info, create
        return None, None


def gen_union_username():
    """
    gen_union_username
    :return: username
    """
    # time_str = str('%.6f' % time.time()).replace('.', '')
    # random_str = ''.join([random.choice(string.lowercase) for _ in xrange(6)])
    # return '%s%s' % (time_str, random_str)
    str_len = random.choice(range(7, 11))
    return ''.join([random.choice(BASE_STRING) for _ in xrange(str_len)])


def create_new_user(name=''):
    """
    new user
    :return:
    """
    def create_():
        password = TIANYUYUN_PASSWORD
        username = gen_union_username()
        email = '%s@ccnu.com' % username
        user = User(
            username=username,
            email=email,
            is_active=True
        )
        user.set_password(password)
        try:
            user.save()
        except:
            return None
        return user

    user = create_()
    if not user:
        while True:
            user = create_()
            if user:
                break
    # TODO UserProfile
    try:
        from student.models import UserProfile
        profile_name = name or 'someone'
        profile = UserProfile(user=user, name='someone')
        profile.save()
    except:
        pass

    return user