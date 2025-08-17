#!/usr/bin/env python3
"""
Demo script for SuperPerformanceScreener
Shows how to use the system with mock data for demonstration
"""
import sys
import logging
from datetime import datetime, timedelta
from typing import List, Dict

from stock_analyzer import StockAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_mock_stock_data(ticker: str, start_date: str, end_date: str, growth_pattern: str = "normal") -> List[Dict]:
    """Generate mock historical data for demonstration"""
    data = []
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    current_dt = start_dt
    base_price = 100.0
    
    while current_dt <= end_dt:
        days_since_start = (current_dt - start_dt).days
        
        if growth_pattern == "superperformance":
            # Simulate superperformance: 400% growth over ~365 days
            if days_since_start < 50:
                price = base_price - days_since_start * 0.5  # Initial decline
            elif days_since_start < 200:
                price = base_price + (days_since_start - 50) * 2.5  # Strong growth
            else:
                price = base_price + 375 - (days_since_start - 200) * 0.5  # Peak and decline
        elif growth_pattern == "growth":
            # Simulate growth: 150% growth over ~200 days
            if days_since_start < 30:
                price = base_price - days_since_start * 0.3  # Initial decline
            elif days_since_start < 150:
                price = base_price + (days_since_start - 30) * 1.2  # Growth
            else:
                price = base_price + 144 - (days_since_start - 150) * 0.3  # Peak and decline
        else:
            # Normal pattern: 50% growth over ~180 days
            if days_since_start < 20:
                price = base_price - days_since_start * 0.2  # Initial decline
            elif days_since_start < 120:
                price = base_price + (days_since_start - 20) * 0.5  # Growth
            else:
                price = base_price + 50 - (days_since_start - 120) * 0.2  # Peak and decline
        
        data.append({
            'date': current_dt.strftime('%Y-%m-%d'),
            'open': price,
            'high': price + 2.0,
            'low': price - 2.0,
            'close': price + (days_since_start % 3 - 1) * 0.5
        })
        
        current_dt += timedelta(days=1)
    
    return data

def demo_analysis():
    """Demonstrate the stock analysis functionality"""
    print("🚀 SuperPerformanceScreener Demo")
    print("=" * 50)
    
    analyzer = StockAnalyzer()
    
    # Demo stocks with different patterns
    demo_stocks = [
        ("AAL", "2016-06-27", "2016-12-09", "normal"),      # No superperformance
        ("NVDA", "2016-02-11", "2017-02-07", "superperformance"),  # Superperformance
        ("AMD", "2019-10-03", "2021-02-19", "growth"),      # Growth
        ("TSLA", "2019-08-23", "2021-01-22", "superperformance"),  # Superperformance with drawdowns
    ]
    
    all_results = []
    
    for ticker, start_date, end_date, pattern in demo_stocks:
        print(f"\n📊 Analyzing {ticker} ({start_date} to {end_date})")
        print("-" * 40)
        
        # Generate mock data
        data = generate_mock_stock_data(ticker, start_date, end_date, pattern)
        
        # Analyze the stock
        moves = analyzer.analyze_stock(ticker, data)
        valid_moves = analyzer.filter_valid_moves(moves)
        
        print(f"Found {len(moves)} total moves, {len(valid_moves)} valid moves")
        
        for i, move in enumerate(valid_moves):
            print(f"  Move {i+1}:")
            print(f"    Start: {move['start_date_formatted']}")
            print(f"    End: {move['end_date_formatted']}")
            print(f"    Growth: {move['growth_percentage']:.1f}%")
            print(f"    Duration: {move['duration_days']} days")
            print(f"    Superperformance: {move['superperformance']}")
            print(f"    Drawdowns: {move['drawdowns_formatted']}")
            print(f"    Continuation: {move['continuation_formatted']}")
            
            all_results.append(move)
    
    # Show summary table
    print(f"\n📋 Summary Results")
    print("=" * 50)
    print(f"{'Ticker':<8} {'Start':<12} {'End':<12} {'Super':<6} {'Drawdowns':<15} {'Cont':<4}")
    print("-" * 50)
    
    for result in all_results:
        drawdowns_str = ', '.join(result['drawdowns_formatted']) if result['drawdowns_formatted'] else 'none'
        print(f"{result['ticker']:<8} {result['start_date_formatted']:<12} {result['end_date_formatted']:<12} "
              f"{result['superperformance_formatted']:<6} {drawdowns_str:<15} {result['continuation_formatted']:<4}")
    
    print(f"\n✅ Demo completed! Found {len(all_results)} valid moves across {len(demo_stocks)} stocks.")
    print("\n💡 To run with real data:")
    print("   1. Set up your API keys in .env file")
    print("   2. Run: python main.py --test")
    print("   3. Check the generated Google Sheet for results")

if __name__ == "__main__":
    try:
        demo_analysis()
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        sys.exit(1) 