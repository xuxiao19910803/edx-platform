#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url


urlpatterns = patterns(
    'oauth_tianyuyun.views',
    url(r'^login/tianyuyun$', 'login_tianyuyun', name='login_tianyuyun'),
)
