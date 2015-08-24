#encoding=utf-8
"""
Public views
"""
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.conf import settings

from edxmako.shortcuts import render_to_response

from external_auth.views import (ssl_login_shortcut, ssl_get_cert_from_request,
                                 redirect_with_get)
from microsite_configuration import microsite
############
from util.json_request import JsonResponse
import json
from uuid import uuid4
import urllib
import urllib2
import os
import socket
import time
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
__all__ = ['signup', 'login_page', 'howitworks','ajaxUploadVideo']


@ensure_csrf_cookie
def signup(request):
    """
    Display the signup form.
    """
    csrf_token = csrf(request)['csrf_token']
    if request.user.is_authenticated():
        return redirect('/course/')
    if settings.FEATURES.get('AUTH_USE_CERTIFICATES_IMMEDIATE_SIGNUP'):
        # Redirect to course to login to process their certificate if SSL is enabled
        # and registration is disabled.
        return redirect_with_get('login', request.GET, False)

    return render_to_response('register.html', {'csrf': csrf_token})


@ssl_login_shortcut
@ensure_csrf_cookie
def login_page(request):
    #显示登录的表单情况
    """
    Display the login form.
    """
    csrf_token = csrf(request)['csrf_token']
    if (settings.FEATURES['AUTH_USE_CERTIFICATES'] and
            ssl_get_cert_from_request(request)):
        # SSL login doesn't require a login view, so redirect
        # to course now that the user is authenticated via
        # the decorator.
        next_url = request.GET.get('next')
        if next_url:
            return redirect(next_url)
        else:
            return redirect('/course/')
    if settings.FEATURES.get('AUTH_USE_CAS'):
        # If CAS is enabled, redirect auth handling to there
        return redirect(reverse('cas-login'))
    context={
        'csrf': csrf_token,
        #'//localhost:8000/login#forgot-password-modal'
        'forgot_password_link': "//{base}/login#forgot-password-modal".format(base=settings.LMS_BASE),
        'platform_name': microsite.get_value('platform_name', settings.PLATFORM_NAME),
    }
    return render_to_response('login.html',context)

#home or howitworks.html with no authenticated
def howitworks(request):
    "Proxy view"
    if request.user.is_authenticated():
        #redirect to a home html in status of the authenticate
        #redirect to /contentstore/views/course.py/course_listing
        return redirect('/home/')
    else:
        return render_to_response('howitworks.html', {})
def ajaxUploadVideo(request):
    def handle_uploaded_file(f):
        print (f.name)
        file_name = ""
        suffixName = ""
        try:
            path = "media/editor/"
            if not os.path.exists(path):
                os.makedirs(path)
            name = "" + f.name
            suffixName = name.split(".")[-1]
            suffix2Name =name[name.rfind('.'):]
            uuid = unicode(uuid4())
            file_name = path + uuid + "." +suffixName
            destination = open(file_name, 'wb+')
            for chunk in f.chunks():
                destination.write(chunk)
            destination.close()
        except Exception, e:
            print e

        return file_name
    def handel_RestuploadFile(filepath):
        try:
            files=open(filepath,"rb")
            register_openers()
            url = "http://119.97.166.182:8090/TestMvc/restAdd"
            datagen, headers = multipart_encode({"mp1": files})
            request = urllib2.Request(url, datagen,headers)
            res_data =urllib2.urlopen(request)
            res = res_data.read().strip()
            data = json.loads(res)
            resurl = data["data"]["url"]
            return resurl
        except Exception,e:
            print e
    #Request中取出file文件
    tmp=request.FILES['file']
    if tmp is None or "":
        return JsonResponse({
            "success": False,
            "msg": "文件为空",
        })
    #uploaFile类读取文件，写入本地临时文件
    try:
        fileName=handle_uploaded_file(tmp)
    except Exception,e:
        print e
        return JsonResponse({
            "success": False,
            "msg": "文件写入本地失败",
        })
    #返回绝对路径
    abFileName="/edx/app/edxapp/edx-platform/"+fileName
    #Rest上传，并取回上传成功后的地址
    try:
        url=handel_RestuploadFile(abFileName)
        print ("url:"+url);
    except Exception,e:
        print e
        return JsonResponse({
            "success": False,
            "msg": "文件Rest上传失败",
        })
    return JsonResponse({
        "success": True,
        "resurl": url,
    })