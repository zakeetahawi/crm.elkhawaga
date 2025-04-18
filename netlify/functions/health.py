import json
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('health_check')

def handler(event, context):
    try:
        logger.info("Health check requested")
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'healthy',
                'message': 'Django ASGI function is running',
                'runtime': 'Python 3.9',
                'timestamp': context.get('timestamp', '')
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'X-Health-Check': 'passed'
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'unhealthy',
                'error': str(e)
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }