import requests
import json
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "https://ewaw.netlify.app"
RETRY_COUNT = 3
RETRY_DELAY = 2  # seconds

def test_with_retry(func, *args, **kwargs):
    for attempt in range(RETRY_COUNT):
        try:
            result = func(*args, **kwargs)
            if result:
                return True
            time.sleep(RETRY_DELAY)
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < RETRY_COUNT - 1:
                time.sleep(RETRY_DELAY)
    return False

def test_health_check():
    try:
        logger.info("Testing health check endpoint...")
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Health check response: {json.dumps(data, indent=2)}")
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
        response = requests.get(f"{BASE_URL}/api/", timeout=10)
        
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
    # Add initial delay for cold start
    logger.info("Waiting for functions to warm up...")
    time.sleep(5)
    
    health_status = test_with_retry(test_health_check)
    django_status = test_with_retry(test_django_app)
    
    if health_status and django_status:
        logger.info("All tests passed successfully!")
        exit(0)
    else:
        logger.error("Some tests failed!")
        exit(1)