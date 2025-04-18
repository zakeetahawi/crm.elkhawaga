import os
import sys

# Add project root to Python path
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, root_path)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
from mangum import Mangum

# Get the Django WSGI application
application = get_wsgi_application()

# Create handler for AWS Lambda / Netlify Functions
handler = Mangum(application, lifespan="off")