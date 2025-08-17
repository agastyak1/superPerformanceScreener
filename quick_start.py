#!/usr/bin/env python3
"""
Quick Start Script for SuperPerformanceScreener
Helps users set up and test the system step by step
"""
import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ is required. Current version:", sys.version)
        return False
    print("✅ Python version:", sys.version.split()[0])
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'requests', 'google-auth', 'google-api-python-client', 
        'python-dotenv', 'retry'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - missing")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False
    
    return True

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env file not found")
        print("📝 Creating .env file from template...")
        
        # Copy from env_example.txt
        example_file = Path('env_example.txt')
        if example_file.exists():
            with open(example_file, 'r') as f:
                content = f.read()
            
            with open(env_file, 'w') as f:
                f.write(content)
            
            print("✅ .env file created from template")
            print("⚠️  Please edit .env file with your API keys")
            return False
        else:
            print("❌ env_example.txt not found")
            return False
    
    # Check if API keys are set
    from dotenv import load_dotenv
    load_dotenv()
    
    eodhd_key = os.getenv('EODHD_API_KEY')
    spreadsheet_id = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
    
    if not eodhd_key or eodhd_key == 'your_eodhd_api_key_here':
        print("❌ EODHD API key not configured")
        return False
    else:
        print("✅ EODHD API key configured")
    
    if not spreadsheet_id or spreadsheet_id == 'your_spreadsheet_id_here':
        print("❌ Google Sheets ID not configured")
        return False
    else:
        print("✅ Google Sheets ID configured")
    
    return True

def check_credentials():
    """Check if Google credentials file exists"""
    credentials_file = Path('credentials.json')
    
    if not credentials_file.exists():
        print("❌ credentials.json not found")
        print("📋 Please follow the API_SETUP.md guide to set up Google Sheets API")
        return False
    
    print("✅ Google credentials file found")
    return True

def run_tests():
    """Run the test suite"""
    print("\n🧪 Running tests...")
    try:
        result = subprocess.run([sys.executable, '-m', 'unittest', 'test_screener.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ All tests passed")
            return True
        else:
            print("❌ Some tests failed")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def run_demo():
    """Run the demo"""
    print("\n🚀 Running demo...")
    try:
        result = subprocess.run([sys.executable, 'demo.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Demo completed successfully")
            return True
        else:
            print("❌ Demo failed")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error running demo: {e}")
        return False

def main():
    """Main quick start function"""
    print("🚀 SuperPerformanceScreener Quick Start")
    print("=" * 50)
    
    # Step 1: Check Python version
    print("\n1️⃣  Checking Python version...")
    if not check_python_version():
        return False
    
    # Step 2: Check dependencies
    print("\n2️⃣  Checking dependencies...")
    if not check_dependencies():
        return False
    
    # Step 3: Check environment setup
    print("\n3️⃣  Checking environment setup...")
    env_ok = check_env_file()
    credentials_ok = check_credentials()
    
    if not env_ok or not credentials_ok:
        print("\n📋 Setup required:")
        print("   1. Get EODHD API key from: https://eodhd.com/register")
        print("   2. Follow API_SETUP.md for Google Sheets setup")
        print("   3. Edit .env file with your keys")
        print("   4. Run this script again")
        return False
    
    # Step 4: Run tests
    print("\n4️⃣  Running tests...")
    if not run_tests():
        print("⚠️  Tests failed, but continuing...")
    
    # Step 5: Run demo
    print("\n5️⃣  Running demo...")
    if not run_demo():
        print("⚠️  Demo failed, but system may still work")
    
    # Success!
    print("\n🎉 Quick start completed!")
    print("\n📋 Next steps:")
    print("   1. Run with real data: python main.py --test")
    print("   2. Check your Google Sheet for results")
    print("   3. Adjust settings in config.py if needed")
    print("   4. Run full analysis: python main.py")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Quick start interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Quick start failed: {e}")
        sys.exit(1) 