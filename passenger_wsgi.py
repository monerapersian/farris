import os
import sys 
sys.path.insert(0, os.path.dirname(__file__))
import farris_ir.wsgi as wsgi


application = wsgi.application


# import sys, os


# PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
# sys.path.insert(0, PROJECT_DIR)

# # تنظیم متغیر محیطی برای Django
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farris_ir.settings')

# # بارگذاری برنامه WSGI
# from django.core.wsgi import get_wsgi_application
# application = get_wsgi_application()