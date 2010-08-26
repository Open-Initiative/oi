from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from oi.messages.models import Message, OI_READ, OI_WRITE, OI_ANSWER
from oi.projects.models import Project
register = template.Library()

OI_ESCAPE_CODE = {"<p>":"[[p]]","</p>":"[[/p]]","<strong>":"[[strong]]","</strong>":"[[/strong]]",
    "<em>":"[[em]]","</em>":"[[/em]]",'<span style="text-decoration: underline;">':'[[un]]',
    '<span style="text-decoration: line-through;">':'[[lt]]','</span>':'[[/s]]',"<ul>":"[[ul]]",
    "</ul>":"[[/ul]]","<li>":"[[li]]","</li>":"[[/li]]","<em>":"[[em]]","</em>":"[[/em]]","<ol>":"[[ol]]","</ol>":"[[/ol]]","&":"[[amp]]"}

@register.filter
def oiunescape(text, autoescape=None):
    """unescapes tags used by the rich text editor"""
    if autoescape:
        text = conditional_escape(text)
    for code in OI_ESCAPE_CODE:
        text = text.replace(OI_ESCAPE_CODE[code], code)
    return mark_safe(text)
oiunescape.needs_autoescape = True

def oiescape(text):
    """escapes tags used by the rich text editor"""
    for code in OI_ESCAPE_CODE:
        text = text.replace(code, OI_ESCAPE_CODE[code])
    return text
    
@register.filter
def multiply(value, arg):
    return int(value) * int(arg)

@register.filter
def oidateshift(end_date, start_date):
    try:
        return (end_date-start_date).days+1
    except:
        return None
        
@register.filter
def can_read(obj, user):
    return obj.has_perm(user, OI_READ)

@register.filter
def can_write(obj, user):
    return obj.has_perm(user, OI_WRITE)

@register.filter
def can_answer(obj, user):
    return obj.has_perm(user, OI_READ)
    
@register.filter
def has_voted(obj, user):
    return obj.has_voted(user, OI_READ)
