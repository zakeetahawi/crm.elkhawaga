import os
from django.core.asgi import get_asgi_application
from mangum import Mangum

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')

# Get the ASGI application
django_asgi_app = get_asgi_application()

# Create Mangum handler
handler = Mangum(django_asgi_app, lifespan="off")

# Export handler for AWS Lambda / Netlify Functions
application = handler
