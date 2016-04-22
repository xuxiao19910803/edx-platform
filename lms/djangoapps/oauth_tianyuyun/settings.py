#!/usr/bin/env python
# -*- coding: utf-8 -*-

APPID = 'AP060000013174'
APPKEY = '423465d8c1c86441334b717540c00e2d'

# get ticket and usesessionid
LOCAL_OAUTH_LOGIN_URL = 'http://mcs.starc.com.cn/oauth_tianyuyun/login/tianyuyun'  # ticket=********
TIANYUYUN_LOGIN_URL = 'http://www.huijiaoyun.cn/index.php?r=portal/user/login&service={service}'

TIANYUYUN_LOGIN_REDIRECT_URL = 'http://manage.tianyuyun.cn:22007/aamif/ticketValidate?ticket={ticket}'

# get TOKEN json post
# appid, timestamp, keyinfo
# keyinfo:
#   对APPID、APPKEY、Timestamp进行sha1-hamc运算，加密串为APPID和APPKEY及Timestamp字符串相连,以APPKEY为加密参数
#   Php使用的签名函数：hash_hmac，hash_algos参数值为“sha1”
#   返回值大写
TIANYUYUN_GET_TOKEN_URL = 'http://manage.tianyuyun.cn:22015/apigateway/getaccesstoken'

TIANYUYUN_GET_SESSIONID_INFO_URL = 'http://manage.tianyuyun.cn:22015/aam/rest/user/getuserinfo/{sessionid}?token={token}'   # noqa
