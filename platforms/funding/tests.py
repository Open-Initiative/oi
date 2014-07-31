"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.utils import unittest
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.views.generic import TemplateView, DetailView
from oi.projects.models import Project, OINeedsPrjPerms, Spec, Reward, RewardForm
from oi.projects.views import *
from oi.helpers import OI_READ, OI_WRITE, SPEC_TYPES



class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)
        
        
class ProjectTest(TestCase):

#    def setUp(self):
#        Project.objects.create(name="lion", sound="roar")
#        Project.objects.create(name="cat", sound="meow")
        
    def create_new_project(self):
        """
        Tests if we can create new project
        """
        
        request = WSGIRequestGET:<QueryDict: {}>,POST:<QueryDict: {u'inline': [u'1'], u'app': [u'funding'], u'progress': [u'0'], u'title': [u'test']}>,COOKIES:{'csrftoken': '317c81c075b8dc1be1db417a9aee91cf', 'sessionid': '30a4b52103ced9566a73ee2545be802c'},META:{'CONTENT_LENGTH': '42', 'CONTENT_TYPE': 'application/xml', 'CSRF_COOKIE': '317c81c075b8dc1be1db417a9aee91cf', 'DOCUMENT_ROOT': '/home/maxi/www', 'GATEWAY_INTERFACE': 'CGI/1.1', 'HTTP_ACCEPT': '*/*', 'HTTP_ACCEPT_CHARSET': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3', 'HTTP_ACCEPT_ENCODING': 'gzip,deflate,sdch', 'HTTP_ACCEPT_LANGUAGE': 'fr-FR,fr;q=0.8,en-US;q=0.6,en;q=0.4', 'HTTP_CONNECTION': 'close', 'HTTP_COOKIE': 'sessionid=30a4b52103ced9566a73ee2545be802c; csrftoken=317c81c075b8dc1be1db417a9aee91cf', 'HTTP_HOST': 'localhost:8088', 'HTTP_ORIGIN': 'http://localhost:8088', 'HTTP_REFERER': 'http://localhost:8088/', 'HTTP_USER_AGENT': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.22 (KHTML, like Gecko) Ubuntu Chromium/25.0.1364.160 Chrome/25.0.1364.160 Safari/537.22', 'HTTP_X_CSRFTOKEN': '317c81c075b8dc1be1db417a9aee91cf', 'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest', 'PATH': '/usr/local/bin:/usr/bin:/bin', 'PATH_INFO': u'/project/save/0', 'PATH_TRANSLATED': 'redirect:/django_funding.fcgi/project/save/0/save/0', 'QUERY_STRING': '', 'REDIRECT_STATUS': '200', 'REDIRECT_URL': '/project/save/0', 'REMOTE_ADDR': '127.0.0.1', 'REMOTE_PORT': '60889', 'REQUEST_METHOD': 'POST', 'REQUEST_URI': '/project/save/0', 'SCRIPT_FILENAME': '/home/maxi/www/django_funding.fcgi', 'SCRIPT_NAME': u'', 'SERVER_ADDR': '127.0.0.1', 'SERVER_ADMIN': 'webmaster@localhost', 'SERVER_NAME': 'localhost', 'SERVER_PORT': '8088', 'SERVER_PROTOCOL': 'HTTP/1.1', 'SERVER_SIGNATURE': '<address>Apache/2.2.20 (Ubuntu) Server at localhost Port 8088</address>\n', 'SERVER_SOFTWARE': 'Apache/2.2.20 (Ubuntu)', 'wsgi.errors': <flup.server.fcgi_base.OutputStream object at 0xaf08e2c>, 'wsgi.input': <flup.server.fcgi_base.InputStream object at 0xaf08f2c>, 'wsgi.multiprocess': False, 'wsgi.multithread': True, 'wsgi.run_once': False, 'wsgi.url_scheme': 'http', 'wsgi.version': (1, 0)}
        
        p_id = 0
        
        saveproject(request, p_id)
        

