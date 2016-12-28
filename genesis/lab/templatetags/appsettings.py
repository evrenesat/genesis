# -*-  coding: utf-8 -*-
"""
"""
from django import template
from django.utils.safestring import mark_safe
from lab.models import Setting

register = template.Library()

@register.simple_tag
def AppSetting():
    return mark_safe('<script>AppSettings = %s;</script>' % Setting.get_all_val())
