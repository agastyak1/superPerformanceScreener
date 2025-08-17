"""
Configuration settings for SuperPerformanceScreener
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys - These need to be set in .env file
EODHD_API_KEY = os.getenv('EODHD_API_KEY')
GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE', 'credentials.json')
GOOGLE_SHEETS_SPREADSHEET_ID = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')

# EODHD API Configuration
EODHD_BASE_URL = "https://eodhd.com/api"

# Stock Screening Parameters
MIN_DAILY_VOLUME = 200000
MIN_GROWTH_PERCENTAGE = 5.0
MAX_DRAWDOWN_PERCENTAGE = 30.0
MIN_DRAWDOWN_PERCENTAGE = 15.0
GROWTH_MOVE_DAYS = 5
MAX_DAYS_WITHOUT_HIGH = 30
MAX_TOTAL_DAYS = 504
CONTINUATION_WINDOW_DAYS = 90

# Superperformance Thresholds
GROWTH_THRESHOLDS = {
    'growth_64_252': 100.0,  # 100% in 64-252 days
    'growth_252_504': 150.0,  # 150% in 252-504 days
    'super_64_252': 300.0,    # 300% in 64-252 days
    'super_252_504': 500.0    # 500% in 252-504 days
}

# Google Sheets Configuration
SHEET_NAME = "SuperPerformanceScreener"
HEADERS = [
    "Ticker",
    "Start Date",
    "End Date", 
    "Superperformance",
    "Drawdowns",
    "Continuation"
]

# API Rate Limiting
REQUEST_DELAY = 1.0  # seconds between requests
MAX_RETRIES = 3
RETRY_DELAY = 2.0

# Data Analysis Parameters
LOOKBACK_YEARS = 5 