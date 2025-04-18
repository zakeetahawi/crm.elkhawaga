import os
import sys
import json

# Add project root to Python path
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, root_path)

# Import the Mangum handler from our WSGI file
from crm.wsgi import handler as wsgi_handler

def handler(event, context):
    try:
        # Handle the request using Mangum
        response = wsgi_handler(event, context)
        
        # Ensure headers exist
        if 'headers' not in response:
            response['headers'] = {}
        
        # Add CORS headers
        response['headers'].update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
        })
        
        return response
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Internal server error'
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }