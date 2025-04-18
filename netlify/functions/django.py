import os
import sys

# Add project root to Python path
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, root_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')

from django.core.wsgi import get_wsgi_application
from django.core.handlers.wsgi import WSGIRequest
from urllib.parse import parse_qs

application = get_wsgi_application()

def handler(event, context):
    # Convert API Gateway event to WSGI request
    environ = {
        'REQUEST_METHOD': event['httpMethod'],
        'SCRIPT_NAME': '',
        'PATH_INFO': event['path'],
        'QUERY_STRING': event['queryStringParameters'] or '',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'SERVER_NAME': event['headers'].get('Host', 'localhost'),
        'SERVER_PORT': '443',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': '',
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
    }

    # Add headers
    for key, value in event['headers'].items():
        key = key.upper().replace('-', '_')
        if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            key = f'HTTP_{key}'
        environ[key] = value

    # Handle the request
    response = {}
    def start_response(status, headers):
        response['statusCode'] = int(status.split()[0])
        response['headers'] = dict(headers)

    # Get response body
    response_body = b''.join(application(environ, start_response))
    response['body'] = response_body.decode('utf-8')

    return response