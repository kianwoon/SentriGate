#!/usr/bin/env python3
"""
Monitoring script for the Vector DB Gateway service.
This runs as a separate process under supervisord.
"""

import time
import logging
import psutil
import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def check_api_health():
    """Check the health of the API by pinging the root endpoint."""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False

def monitor():
    """Continuously monitor the application."""
    while True:
        try:
            # Log memory usage
            memory_info = psutil.virtual_memory()
            logger.info(f"Memory usage: {memory_info.percent}% (used: {memory_info.used / 1024 / 1024:.1f}MB)")
            
            # Log CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            logger.info(f"CPU usage: {cpu_percent}%")
            
            # Check API health
            healthy = check_api_health()
            logger.info(f"API health: {'OK' if healthy else 'DEGRADED'}")
            
            # Sleep for a while before next check
            time.sleep(60)
        except Exception as e:
            logger.error(f"Error in monitoring: {e}")
            time.sleep(10)

if __name__ == "__main__":
    logger.info("Starting monitoring service")
    monitor()
