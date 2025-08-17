"""
SuperPerformanceScreener - Main Application
Orchestrates the complete workflow for detecting growth moves and superperformance
"""
import sys
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import argparse

from eodhd_client import EODHDClient
from stock_analyzer import StockAnalyzer
from google_sheets_client import GoogleSheetsClient
from config import LOOKBACK_YEARS, MIN_DAILY_VOLUME

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('superperformance_screener.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SuperPerformanceScreener:
    """Main application class for SuperPerformanceScreener"""
    
    def __init__(self, eodhd_api_key: str = None, google_credentials_file: str = None, spreadsheet_id: str = None):
        """Initialize the screener with API clients"""
        try:
            self.eodhd_client = EODHDClient(eodhd_api_key)
            self.analyzer = StockAnalyzer()
            
            # Make Google Sheets optional
            try:
                self.sheets_client = GoogleSheetsClient(google_credentials_file, spreadsheet_id)
                logger.info("Google Sheets client initialized successfully")
            except Exception as e:
                logger.warning(f"Google Sheets client failed to initialize: {e}")
                self.sheets_client = None
                
            logger.info("SuperPerformanceScreener initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SuperPerformanceScreener: {e}")
            raise
    
    def get_analysis_date_range(self) -> tuple:
        """Get the date range for analysis (last 5 years)"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=LOOKBACK_YEARS * 365)
        
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
    
    def discover_stocks(self, max_stocks: int = 100) -> List[str]:
        """Discover stocks that meet volume and exchange criteria"""
        logger.info("Discovering stocks with >200k daily volume on NYSE/NASDAQ...")
        
        try:
            # Get high volume stocks from EODHD
            stocks = self.eodhd_client.get_high_volume_stocks()
            
            if not stocks:
                logger.warning("No stocks returned from Perplexity API")
                return []
            
            # Limit to max_stocks
            stocks = stocks[:max_stocks]
            
            # Verify exchange and volume for each stock
            valid_stocks = []
            for i, ticker in enumerate(stocks):
                logger.info(f"Verifying stock {i+1}/{len(stocks)}: {ticker}")
                
                # Check exchange
                exchange = self.eodhd_client.get_stock_exchange(ticker)
                if exchange not in ['NYSE', 'NASDAQ']:
                    logger.info(f"Skipping {ticker} - not on NYSE/NASDAQ")
                    continue
                
                # Check volume
                volume = self.eodhd_client.get_stock_volume(ticker)
                if volume is None or volume < MIN_DAILY_VOLUME:
                    logger.info(f"Skipping {ticker} - volume {volume} < {MIN_DAILY_VOLUME}")
                    continue
                
                valid_stocks.append(ticker)
                logger.info(f"Added {ticker} ({exchange}, {volume:,.0f} volume)")
                
                # Rate limiting
                time.sleep(1)
            
            logger.info(f"Found {len(valid_stocks)} valid stocks out of {len(stocks)} candidates")
            return valid_stocks
            
        except Exception as e:
            logger.error(f"Error discovering stocks: {e}")
            return []
    
    def analyze_stock(self, ticker: str) -> List[Dict[str, Any]]:
        """Analyze a single stock for growth moves"""
        logger.info(f"Analyzing {ticker}...")
        
        try:
            # Get date range
            start_date, end_date = self.get_analysis_date_range()
            
            # Get historical data
            historical_data = self.eodhd_client.get_historical_data(ticker, start_date, end_date)
            
            if not historical_data:
                logger.warning(f"No historical data found for {ticker}")
                return []
            
            # Analyze for growth moves
            moves = self.analyzer.analyze_stock(ticker, historical_data)
            
            # Filter to only valid moves (Growth or Superperformance)
            valid_moves = self.analyzer.filter_valid_moves(moves)
            
            logger.info(f"Found {len(valid_moves)} valid moves for {ticker}")
            return valid_moves
            
        except Exception as e:
            logger.error(f"Error analyzing {ticker}: {e}")
            return []
    
    def run_screening(self, max_stocks: int = 50, test_mode: bool = False) -> List[Dict[str, Any]]:
        """Run the complete screening process"""
        logger.info("Starting SuperPerformanceScreener...")
        
        # Discover stocks
        stocks = self.discover_stocks(max_stocks)
        
        if not stocks:
            logger.error("No stocks to analyze")
            return []
        
        # Test mode - use sample stocks
        if test_mode:
            test_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'AMD']
            # Use test stocks that are actually in the discovered list
            available_test_stocks = [s for s in test_stocks if s in stocks]
            if available_test_stocks:
                stocks = available_test_stocks
                logger.info(f"Test mode: analyzing {stocks}")
            else:
                # If no test stocks found, use first few discovered stocks
                stocks = stocks[:4]
                logger.info(f"Test mode: no test stocks found, using first 4 discovered: {stocks}")
        
        # Analyze each stock
        all_results = []
        for i, ticker in enumerate(stocks):
            logger.info(f"Processing stock {i+1}/{len(stocks)}: {ticker}")
            
            moves = self.analyze_stock(ticker)
            all_results.extend(moves)
            
            # Rate limiting
            time.sleep(2)
        
        logger.info(f"Screening complete. Found {len(all_results)} total moves across {len(stocks)} stocks")
        return all_results
    
    def output_results(self, results: List[Dict[str, Any]]):
        """Output results to Google Sheets or console"""
        if not results:
            logger.warning("No results to output")
            return
        
        if self.sheets_client:
            try:
                logger.info(f"Outputting {len(results)} results to Google Sheets...")
                self.sheets_client.write_results(results)
                
                spreadsheet_url = self.sheets_client.get_spreadsheet_url()
                logger.info(f"Results written to: {spreadsheet_url}")
                
            except Exception as e:
                logger.error(f"Error outputting results to Google Sheets: {e}")
                logger.info("Falling back to console output...")
                self._output_to_console(results)
        else:
            logger.info("Google Sheets not available, outputting to console...")
            self._output_to_console(results)
    
    def _output_to_console(self, results: List[Dict[str, Any]]):
        """Output results to console"""
        print(f"\n{'='*80}")
        print(f"SUPERPERFORMANCE SCREENER RESULTS - {len(results)} MOVES FOUND")
        print(f"{'='*80}")
        
        for i, move in enumerate(results, 1):
            print(f"\n{i}. {move['ticker']} - {move['superperformance']}")
            print(f"   Period: {move['start_date_formatted']} to {move['end_date_formatted']}")
            if move.get('drawdowns_formatted'):
                print(f"   Drawdowns: {', '.join(move['drawdowns_formatted'])}")
            print(f"   Continuation: {move.get('continuation_formatted', 'N/A')}")
        
        print(f"\n{'='*80}")
    
    def run(self, max_stocks: int = 50, test_mode: bool = False):
        """Run the complete SuperPerformanceScreener workflow"""
        try:
            # Run screening
            results = self.run_screening(max_stocks, test_mode)
            
            # Output results
            if results:
                self.output_results(results)
                logger.info("SuperPerformanceScreener completed successfully!")
            else:
                logger.warning("No results found")
                
        except Exception as e:
            logger.error(f"SuperPerformanceScreener failed: {e}")
            raise

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='SuperPerformanceScreener')
    parser.add_argument('--max-stocks', type=int, default=50, help='Maximum number of stocks to analyze')
    parser.add_argument('--test', action='store_true', help='Run in test mode with sample stocks')
    parser.add_argument('--eodhd-key', help='EODHD API key (overrides .env)')
    parser.add_argument('--google-credentials', help='Google credentials file (overrides .env)')
    parser.add_argument('--spreadsheet-id', help='Google Sheets ID (overrides .env)')
    
    args = parser.parse_args()
    
    try:
        # Initialize screener
        screener = SuperPerformanceScreener(
            eodhd_api_key=args.eodhd_key,
            google_credentials_file=args.google_credentials,
            spreadsheet_id=args.spreadsheet_id
        )
        
        # Run screening
        screener.run(max_stocks=args.max_stocks, test_mode=args.test)
        
    except KeyboardInterrupt:
        logger.info("Screening interrupted by user")
    except Exception as e:
        logger.error(f"Screening failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 