import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "https://ewaw.netlify.app"

def test_health_check():
    try:
        logger.info("Testing health check endpoint...")
        response = requests.get(f"{BASE_URL}/health")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Health check succeeded: {json.dumps(data, indent=2)}")
            assert data['status'] == 'healthy'
            return True
        else:
            logger.error(f"Health check failed with status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error during health check: {str(e)}")
        return False

def test_django_app():
    try:
        logger.info("Testing Django application...")
        response = requests.get(BASE_URL)
        
        if response.status_code == 200:
            logger.info("Django application is responding")
            return True
        else:
            logger.error(f"Django app test failed with status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error testing Django app: {str(e)}")
        return False

if __name__ == "__main__":
    health_status = test_health_check()
    django_status = test_django_app()
    
    if health_status and django_status:
        logger.info("All tests passed successfully!")
        exit(0)
    else:
        logger.error("Some tests failed!")
        exit(1)