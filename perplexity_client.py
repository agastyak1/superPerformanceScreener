"""
Perplexity Sonar API Client for SuperPerformanceScreener
Handles all API calls with retry logic, caching, and structured responses
"""
import json
import time
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from retry import retry

from config import (
    PERPLEXITY_API_KEY, 
    PERPLEXITY_BASE_URL, 
    SONAR_MODELS,
    REQUEST_DELAY,
    MAX_RETRIES,
    RETRY_DELAY
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerplexityClient:
    """Client for interacting with Perplexity Sonar API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or PERPLEXITY_API_KEY
        if not self.api_key:
            raise ValueError("Perplexity API key is required")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.cache = {}
    
    @retry(tries=MAX_RETRIES, delay=RETRY_DELAY, backoff=2)
    def _make_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request with retry logic"""
        try:
            response = requests.post(
                PERPLEXITY_BASE_URL,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            # Rate limiting
            time.sleep(REQUEST_DELAY)
            
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
    
    def _get_cache_key(self, query: str, model: str) -> str:
        """Generate cache key for query"""
        return f"{model}:{hash(query)}"
    
    def query(self, 
              query: str, 
              model: str = 'pro', 
              use_cache: bool = True,
              json_mode: bool = True) -> Dict[str, Any]:
        """
        Make a query to Perplexity Sonar API
        
        Args:
            query: The query text
            model: Sonar model to use ('base', 'pro', 'reasoning')
            use_cache: Whether to use cached results
            json_mode: Whether to request JSON structured response
            
        Returns:
            API response as dictionary
        """
        if model not in SONAR_MODELS:
            raise ValueError(f"Invalid model: {model}. Use one of {list(SONAR_MODELS.keys())}")
        
        cache_key = self._get_cache_key(query, model)
        if use_cache and cache_key in self.cache:
            logger.info(f"Using cached result for query: {query[:50]}...")
            return self.cache[cache_key]
        
        payload = {
            "model": SONAR_MODELS[model],
            "messages": [{"role": "user", "content": query}]
        }
        
        if json_mode:
            payload["json_mode"] = True
        
        logger.info(f"Making API request with {model} model: {query[:50]}...")
        result = self._make_request(payload)
        
        if use_cache:
            self.cache[cache_key] = result
        
        return result
    
    def get_stock_volume(self, ticker: str) -> Optional[float]:
        """Get average daily volume for a stock ticker"""
        query = f"What is the average daily trading volume for {ticker} stock on NYSE or NASDAQ? Please provide only the numerical value in thousands or millions."
        
        try:
            result = self.query(query, model='base', json_mode=False)
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # Extract numerical value from response
            import re
            numbers = re.findall(r'[\d,]+\.?\d*', content.replace(',', ''))
            if numbers:
                volume = float(numbers[0])
                # Convert to actual volume (handle K, M suffixes)
                if 'thousand' in content.lower() or 'k' in content.lower():
                    volume *= 1000
                elif 'million' in content.lower() or 'm' in content.lower():
                    volume *= 1000000
                return volume
        except Exception as e:
            logger.error(f"Error getting volume for {ticker}: {e}")
        
        return None
    
    def get_historical_data(self, ticker: str, start_date: str, end_date: str) -> Optional[List[Dict]]:
        """Get historical OHLC data for a stock ticker"""
        query = f"""Get historical daily OHLC (Open, High, Low, Close) data for {ticker} stock between {start_date} and {end_date}. 
        Return the data as a JSON array with objects containing: date, open, high, low, close. 
        Format dates as YYYY-MM-DD and prices as numbers."""
        
        try:
            result = self.query(query, model='pro', json_mode=True)
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # Try to parse JSON from response
            if isinstance(content, str):
                # Extract JSON from markdown code blocks if present
                import re
                json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
                if json_match:
                    content = json_match.group(1)
                else:
                    # Try to find JSON array directly
                    json_match = re.search(r'\[.*\]', content, re.DOTALL)
                    if json_match:
                        content = json_match.group(0)
            
            if isinstance(content, str):
                data = json.loads(content)
            else:
                data = content
            
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'data' in data:
                return data['data']
            
        except Exception as e:
            logger.error(f"Error getting historical data for {ticker}: {e}")
        
        return None
    
    def get_stock_exchange(self, ticker: str) -> Optional[str]:
        """Get the exchange (NYSE or NASDAQ) for a stock ticker"""
        query = f"Which exchange does {ticker} stock trade on - NYSE or NASDAQ? Answer with only the exchange name."
        
        try:
            result = self.query(query, model='base', json_mode=False)
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '').strip().upper()
            
            if 'NYSE' in content:
                return 'NYSE'
            elif 'NASDAQ' in content:
                return 'NASDAQ'
        except Exception as e:
            logger.error(f"Error getting exchange for {ticker}: {e}")
        
        return None
    
    def get_high_volume_stocks(self) -> List[str]:
        """Get list of stocks with >200k average daily volume on NYSE/NASDAQ"""
        query = """Provide a list of stock tickers that trade on NYSE or NASDAQ with average daily trading volume greater than 200,000 shares. 
        Return as a JSON array of ticker symbols only."""
        
        try:
            result = self.query(query, model='pro', json_mode=True)
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            if isinstance(content, str):
                import re
                json_match = re.search(r'\[.*\]', content, re.DOTALL)
                if json_match:
                    tickers = json.loads(json_match.group(0))
                else:
                    tickers = json.loads(content)
            else:
                tickers = content
            
            if isinstance(tickers, list):
                return [str(ticker).upper() for ticker in tickers]
            
        except Exception as e:
            logger.error(f"Error getting high volume stocks: {e}")
        
        return []
    
    def analyze_growth_move(self, ticker: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Analyze a specific growth move for a stock"""
        query = f"""Analyze the growth move for {ticker} from {start_date} to {end_date}. 
        Return JSON with: peak_date, peak_price, growth_percentage, duration_days, drawdowns (array of dates), 
        continuation_occurred (boolean), superperformance_status (string: 'Growth', 'Superperformance', or 'None')."""
        
        try:
            result = self.query(query, model='reasoning', json_mode=True)
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            if isinstance(content, str):
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group(0))
                else:
                    analysis = json.loads(content)
            else:
                analysis = content
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing growth move for {ticker}: {e}")
            return {} 