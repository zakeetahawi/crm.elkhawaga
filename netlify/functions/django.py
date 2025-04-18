import os
import sys
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('django_function')

# Add project root to Python path
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, root_path)

# Import the Mangum handler from our ASGI file
try:
    from crm.asgi import handler as asgi_handler
    logger.info("Successfully imported ASGI handler")
except Exception as e:
    logger.error(f"Failed to import ASGI handler: {str(e)}")
    raise

def handler(event, context):
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Initialize response from ASGI handler
        response = asgi_handler(event, context)
        logger.info(f"ASGI handler response: {json.dumps(response)}")
        
        # Ensure headers exist
        if 'headers' not in response:
            response['headers'] = {}
            
        # Add security and CORS headers
        response['headers'].update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block'
        })
        
        return response
        
    except Exception as e:
        logger.error(f"Error in handler: {str(e)}", exc_info=True)
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