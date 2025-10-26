import os
import sys 
sys.path.insert(0, os.path.dirname(__file__))
import farris_ir.wsgi as wsgi


application = wsgi.application
