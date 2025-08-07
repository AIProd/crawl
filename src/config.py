"""
Configuration module for Staff Directory Crawler
Centralizes all environment variables and constants including profile crawling
"""

import os
import dotenv

dotenv.load_dotenv()

# Concurrency Settings
MAX_CONCURRENT_JOBS = int(os.getenv('MAX_CONCURRENT_JOBS', '10'))
REQUEST_DELAY = float(os.getenv('REQUEST_DELAY', '3.0'))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))

# Profile Crawling Settings
ENABLE_PROFILE_CRAWLING = os.getenv('ENABLE_PROFILE_CRAWLING', 'true').lower() == 'true'
PROFILE_REQUEST_DELAY = float(os.getenv('PROFILE_REQUEST_DELAY', '2.0'))  # Faster for profiles
MAX_PROFILE_CONCURRENT_JOBS = int(os.getenv('MAX_PROFILE_CONCURRENT_JOBS', '10'))  # Lower for profiles
PROFILE_MAX_RETRIES = int(os.getenv('PROFILE_MAX_RETRIES', '2'))  # Fewer retries for profiles

# Browser Settings
BROWSER_TIMEOUT = int(os.getenv('BROWSER_TIMEOUT', '90000')) # 1,5 min
HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'true').lower() == 'true'
PAGE_TIMEOUT = int(os.getenv('PAGE_TIMEOUT', '60000')) # 1 min
JOB_TIMEOUT = int(os.getenv('JOB_TIMEOUT', '600000')) # 10 mins

# Scrolling Settings
MAX_SCROLL_ATTEMPTS = int(os.getenv('MAX_SCROLL_ATTEMPTS', '5'))
SCROLL_DELAY = float(os.getenv('SCROLL_DELAY', '1.0'))

# Processing Settings
BATCH_SAVE_SIZE = int(os.getenv('BATCH_SAVE_SIZE', '5'))
ROWS_PER_CHUNK = int(os.getenv('ROWS_PER_CHUNK', '25'))
YIELD_FREQUENCY = int(os.getenv('YIELD_FREQUENCY', '10'))
INPUT_FILE = os.getenv('INPUT_FILE', 'schools.csv')

# Logging Settings
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

# File Paths
JOBS_FILE = 'jobs.csv'  # Unified jobs file
FAILED_JOBS_FILE = 'failed_jobs.csv'
OUTPUT_FILE = 'staff_members_debug.csv'

# Browser Launch Arguments
BROWSER_ARGS = [
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--disable-extensions',
    '--disable-background-timer-throttling',
    '--disable-backgrounding-occluded-windows',
    '--disable-renderer-backgrounding',
    '--memory-pressure-off'
]

# User Agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# Browser Viewport
VIEWPORT_CONFIG = {
    'width': 1920,
    'height': 1080
}
