import os
import sys
 
sys.path.append('/home/c/ck25508/globalgo.uz/public_html')
sys.path.append('/home/c/ck25508/myenv/lib/python3.6/site-packages')
os.environ['DJANGO_SETTINGS_MODULE'] = 'djangoProject.settings'
import django
django.setup()
 
from django.core.handlers import wsgi
application = wsgi.WSGIHandler()