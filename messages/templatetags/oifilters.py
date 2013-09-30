import re
import string
import random
from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.contrib.auth.models import AnonymousUser
from oi.messages.models import Message, OI_READ, OI_WRITE, OI_ANSWER, OI_BID, OI_MANAGE
from oi.projects.models import Project
from oi.prjnotify.models import Observer
register = template.Library()

OI_ESCAPE_CODE = {"<hr />":"[[hr]]","<p":"[[p]]","</p>":"[[/p]]","<strong>":"[[strong]]","</strong>":"[[/strong]]","<em>":"[[em]]","</em>":"[[/em]]","<dd>":"[[dd]]","</dd>":"[[/dd]]","<dl>":"[[dl]]","</dl>":"[[/dl]]","<dt>":"[[dt]]","</dt>":"[[/dt]]","<b>":"[[b]]","</b>":"[[/b]]",
    "<ul>":"[[ul]]","</ul>":"[[/ul]]","<li>":"[[li]]","</li>":"[[/li]]","<blockquote>":"[[quote]]","</blockquote>":"[[/quote]]",
    "<a":"[[a]]","</a>":"[[/a]]","<img":"[[img]]","</img>":"[[/img]]",'<span':'[[s]]','</span>':'[[/s]]','<sub>':'[[sub]]','</sub>':'[[/sub]]','<sup>':'[[sup]]','</sup>':'[[/sup]]',
    '<table':'[[table]]','</table>':'[[/table]]','<tbody>':'[[tbody]]','</tbody>':'[[/tbody]]','<colgroup>':'[[colgroup]]','</colgroup>':'[[/colgroup]]','<col':'[[col]]','</col>':'[[/col]]','<tr':'[[tr]]','</tr>':'[[/tr]]','<td':'[[td]]','</td>':'[[/td]]',
    '<h':'[[h]]','</h':'[[/h]]','<pre>':'[[pre]]','</pre>':'[[/pre]]','<address>':'[[address]]','</address>':'[[/address]]',"<em>":"[[em]]","</em>":"[[/em]]","<ol>":"[[ol]]","</ol>":"[[/ol]]",
    "<br/>":"[[br]]","<br />":"[[br]]", "<br>":"[[br]]","&":"[[amp]]",'"':"[[dstr]]","'":"[[sstr]]"}

OI_SPECIAL_ESCAPE_CODE = {"<a(?P<param>.*?)>":"[[a]]","<p(?P<param>.*?)>":"[[p]]","<img(?P<param>.*?)>":"[[img]]","<span(?P<param>.*?)>":"[[s]]","<table(?P<param>.*?)>":"[[table]]","<col(?P<param>.*?)>":"[[col]]","<tr(?P<param>.*?)>":"[[tr]]","<td(?P<param>.*?)>":"[[td]]","<h(?P<param>\d)>":"[[h]]","</h(?P<param>\d)>":"[[/h]]"}

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
    # searches for ; to avoid cutting &eamp; and others
    length = max(100,text.find(";",100,105))
    return mark_safe(text[:length]) #returns only 100 first characters
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
def get(valueset, key):
    try:
        valueset = dict(valueset)
    finally:
        try:
            return valueset.__getitem__(key)
        except (KeyError, IndexError):
            try:
                return valueset.__getitem__(int(key))
            except (KeyError, IndexError, ValueError):
                return ''

@register.filter
def oidateshift(end_date, start_date):
    try:
        return (end_date-start_date).days+1
    except:
        return None
    
@register.filter
def filter_read(obj, user):
    return obj.filter_perm(user, OI_READ)

@register.filter
def can_manage(obj, user):
    can_manage  = getattr(obj, "can_manage", None) #request caching for performance
    if can_manage == None:
        can_manage = obj.has_perm(user, OI_MANAGE)
        setattr(obj, "can_manage", can_manage)
    return can_manage
    
@register.filter
def can_bid(obj, user):
    can_bid = getattr(obj, "can_bid", None) #request caching for performance
    if can_bid == None:
        can_bid = obj.has_perm(user, OI_BID)
        setattr(obj, "can_bid", can_bid)
    return can_bid
    
@register.filter
def can_read(obj, user):
    can_read = getattr(obj,"can_read",None) #request caching for performance
    if can_read==None:
        can_read = obj.has_perm(user, OI_READ)
        setattr(obj, "can_read", can_read)
    return can_read

@register.filter
def can_write(obj, user):
    can_write = getattr(obj,"can_write",None) #request caching for performance
    if can_write==None:
        can_write = obj.has_perm(user, OI_WRITE)
        setattr(obj, "can_write", can_write)
    return can_write

@register.filter
def can_answer(obj, user):
    can_answer = getattr(obj,"can_answer",None) #request caching for performance
    if can_answer==None:
        can_answer = obj.has_perm(user, OI_ANSWER)
        setattr(obj, "can_answer", can_answer)
    return can_answer

@register.filter
def bids(prj, user):
    return user.is_authenticated() and prj.bid_set.filter(user=user)

@register.filter
def is_following(prj, user):
    try:
        return Observer.objects.filter(user=user, project__descendants=prj).count() + Observer.objects.filter(user=user, project=prj).count() > 0
    except TypeError:
        return False

@register.filter
def ip_has_voted(obj,ip_address):
    return obj.has_voted(AnonymousUser(),ip_address)

@register.filter
def has_voted(obj, user):
    return obj.has_voted(user, "")

@register.filter
def is_contact(user, contact):
    return user.get_profile().contacts.filter(user=contact).count() > 0

@register.filter
def cleanfilename(path):
    return path.split("/").pop()
    
@register.filter    
def has_group(group_list, grouper):
    for group in group_list:
        if group["grouper"] == grouper:
            return True
    
    return False
    
@register.filter
def filter_order(specs, order):
    for spec in specs:
        if spec.order == order:
            return spec
    return False
    
@register.filter
def int_to_string(string, integer):
    return ""+string+str(integer)
    
@register.simple_tag
def show_stars(value, dest=None):
    id = "".join([random.choice(string.lowercase) for i in range(5)])
    size = "16"
    result = ""
    if dest:
        size=""
        result += '<input type="hidden" id="%(dest)s" value=%(value)s />'%{'id': id, 'value': value, 'dest': dest}
        result += '<img src="/img/icons/star0.png" id="star0_%(id)s" onmouseover="showStar(\'%(id)s\', 0)" onmouseout="resetStar(\'%(id)s\', \'%(dest)s\')" onclick="setStar(\'%(id)s\', \'%(dest)s\', 0)" />'%{'id': id,'dest': dest}
    for starnb in range(5):
        result += '<img src="/img/icons/star%(highligted)s%(size)s.png" '%{'starnb': starnb+1, 'id': id, 'highligted': starnb<value, 'size': size}
        if dest:
            result += 'id="star%(starnb)s_%(id)s" onmouseover="showStar(\'%(id)s\', %(starnb)s)" onmouseout="resetStar(\'%(id)s\', \'%(dest)s\')" onclick="setStar(\'%(id)s\', \'%(dest)s\', %(starnb)s)" '%{'starnb': starnb+1, 'id': id, 'dest': dest}
        result += '/>'
    return result
