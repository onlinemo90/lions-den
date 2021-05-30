from django import template
from django.urls import reverse_lazy

register = template.Library()

@register.filter
def addstr(arg1, arg2):
    return str(arg1) + str(arg2)

@register.filter
def rev_url(url_name):
    return reverse_lazy(url_name)