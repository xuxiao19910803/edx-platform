#!/usr/bin/env python
# -*- coding: utf-8 -*-
from hashlib import sha1
import hmac
import time

from .settings import APPID, APPKEY


def gen_security_code(timestamp):
    """
    验证加密内容
    :param timestamp:
    :return: keyinfo
    """
    msg = gen_msg(timestamp)
    my_sign = hmac.new(APPKEY, msg, sha1).hexdigest()
    return my_sign.upper()


def gen_msg(timestamp):
    """
    生成验证加密内容的 msg
    :param timestamp:
    :return: str
    """
    return '{appid}{appkey}{timestamp}'.format(appid=APPID, appkey=APPKEY, timestamp=timestamp)


def get_timestamp():
    """
    获取加密时间戳
    :return: str
    """
    return str(time.time()).replace('.', '')