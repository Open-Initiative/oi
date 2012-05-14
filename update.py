import os, sys
_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PROJECT_NAME = "oi"
_MODULES_DIR = "%s/%s"%(_ROOT_DIR, "modules")
_PROJECT_DIR = "%s/%s"%(_ROOT_DIR, _PROJECT_NAME)
sys.path.insert(0, _PROJECT_DIR)
sys.path.insert(0, _ROOT_DIR)
sys.path.insert(0, _MODULES_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = "%s.settings" % _PROJECT_NAME

#from oi.notification.models import NoticeType
#n = NoticeType.objects.get(label="project__bid_cancel")
#n.label = "project_bid_cancel"
#n.save()
