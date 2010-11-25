from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.contrib.auth.models import AnonymousUser
from oi.messages.models import Message, OI_READ, OI_WRITE, OI_ANSWER
from oi.projects.models import Project
import re
register = template.Library()

OI_ESCAPE_CODE = {"<p":"[[p]]","</p>":"[[/p]]","<strong>":"[[strong]]","</strong>":"[[/strong]]","<em>":"[[em]]","</em>":"[[/em]]",
    "<ul>":"[[ul]]","</ul>":"[[/ul]]","<li>":"[[li]]","</li>":"[[/li]]","<blockquote>":"[[quote]]","</blockquote>":"[[/quote]]",
    "<a":"[[a]]","</a>":"[[/a]]","<img":"[[img]]","</img>":"[[/img]]",'<span':'[[s]]','</span>':'[[/s]]',
    '<h':'[[h]]','</h':'[[/h]]','<pre>':'[[pre]]','</pre>':'[[/pre]]','<address>':'[[address]]','</address>':'[[/address]]',
    "<em>":"[[em]]","</em>":"[[/em]]","<ol>":"[[ol]]","</ol>":"[[/ol]]","<br />":"[[br]]","<hr />":"[[hr]]","&":"[[amp]]",'"':"[[dstr]]","'":"[[sstr]]"}

OI_SPECIAL_ESCAPE_CODE = {"<a(?P<param>.*?)>":"[[a]]","<p(?P<param>.*?)>":"[[p]]","<img(?P<param>.*?)>":"[[img]]","<span(?P<param>.*?)>":"[[s]]",
    "<h(?P<param>\d)>":"[[h]]","</h(?P<param>\d)>":"[[/h]]"}

@register.filter
def oiunescape(text, autoescape=None):
    """unescapes tags used by the rich text editor"""
    if autoescape:
        text = conditional_escape(text)
    for code in OI_ESCAPE_CODE:
        text = text.replace(OI_ESCAPE_CODE[code], code)
    return mark_safe(text.replace("[[close]]",">"))
oiunescape.needs_autoescape = True

@register.filter
def summarize(text, autoescape=None):
    """gets rid of tags used by the rich text editor and shortens text"""
    if autoescape:
        text = conditional_escape(text)
    for code in OI_ESCAPE_CODE:
        text = text.replace(OI_ESCAPE_CODE[code], code)
    text = text.replace("[[close]]",">") #close tags
    text = re.compile(r'<.*?>').sub('', text) #gets rid of all tags
    return mark_safe(text[:100]) #returns only 100 first characters
oiunescape.needs_autoescape = True

def repl(tag):
    return lambda g:"%s%s[[close]]"%(tag,g.group("param").replace('"', "[[dstr]]").replace("'", "[[sstr]]"))

def oiescape(text):
    """escapes tags used by the rich text editor"""
    for code in OI_SPECIAL_ESCAPE_CODE:
        text = re.sub(code, repl(OI_SPECIAL_ESCAPE_CODE[code]), text)
    for code in OI_ESCAPE_CODE:
        text = text.replace(code, OI_ESCAPE_CODE[code])
    return text
    
@register.filter
def multiply(value, arg):
    return float(value) * float(arg)

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
def is_bidder(prj, user):
    return prj.bid_set.filter(user=user).filter(rating=None).count() > 0

@register.filter
def ip_has_voted(obj,ip_address):
    return obj.has_voted(AnonymousUser(),ip_address)

@register.filter
def has_voted(obj, user):
    return obj.has_voted(user, "")
    
@register.filter
def cleanfilename(path):
    return path.split("/").pop()
