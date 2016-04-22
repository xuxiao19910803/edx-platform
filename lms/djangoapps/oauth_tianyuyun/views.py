# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, logout, login

from .utils import TianYuClient

from .settings import TIANYUYUN_LOGIN_URL

LOGIN_SUCCESS_REDIRECT_URL = '/dashboard'
LOGIN_CREATE_SUCCESS_REDIRECT_URL = '/dashboard'    # '/account/settings'
LOGIN_ERROR_REDIRECT_URL = TIANYUYUN_LOGIN_URL.split('?')[0]


def login_tianyuyun(request):
    ticket = request.GET.get('ticket', '')
    if ticket:
        client = TianYuClient()
        usesessionid = client.get_usesessionid_by_ticket(ticket)
        if usesessionid:
            userinfo = client.get_userinfo_by_sessionid(usesessionid)
            if userinfo.get('idcardno', ''):
                user = request.user if request.user.is_authenticated() else None
                oauth_obj, create = client.get_or_create_oauth_by_userinfo(userinfo, user)
                if oauth_obj and oauth_obj.user:
                    user = authenticate(oauth_obj=oauth_obj, username='')
                    login(request, user)
                    if create:
                        return HttpResponseRedirect(LOGIN_CREATE_SUCCESS_REDIRECT_URL)
                    else:
                        return HttpResponseRedirect(LOGIN_SUCCESS_REDIRECT_URL)
    return HttpResponseRedirect(LOGIN_SUCCESS_REDIRECT_URL)
