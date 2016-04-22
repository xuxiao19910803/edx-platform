#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.contrib.auth.backends import ModelBackend
from .models import OAuthUserInfo


class OAuthBackend(ModelBackend):
    """
    login with oauth_obj
    """
    def authenticate(self, oauth_obj=None, **kwargs):
        if oauth_obj and isinstance(oauth_obj, OAuthUserInfo):
            return oauth_obj.user if oauth_obj else None
        return None
