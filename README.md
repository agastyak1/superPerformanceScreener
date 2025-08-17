# SuperPerformanceScreener

A Python-based tool that detects growth moves and superperformance in stocks using real-time data from the EODHD API and outputs results to Google Sheets.

## 🚀 Features

- **Real-time Stock Data**: Pulls historical price data for NYSE and NASDAQ symbols with >200k average daily volume
- **Growth Move Detection**: Identifies stocks that rise ≥5% within 5 trading days from a Lowest-of-Day (LOD)
- **Superperformance Analysis**: Classifies moves as Growth (≥100% in 64-252 days, ≥150% in 252-504 days) or Superperformance (≥300% in 64-252 days, ≥500% in 252-504 days)
- **Drawdown Tracking**: Detects setbacks of 15-29.9% from peaks and identifies continuations
- **Google Sheets Output**: Automatically outputs results to a formatted Google Sheet

## 📋 Requirements

- Python 3.9+
- EODHD API key
- Google Sheets API credentials
- Internet connection for real-time data

## 🛠 Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd SuperPerformanceScreener
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp env_example.txt .env
   # Edit .env with your API keys
   ```

## 🔑 API Keys Setup

### 1. EODHD API Key

1. Go to [EODHD](https://eodhd.com/register)
2. Sign up or log in to your account
3. Get your API key from the dashboard
4. Add it to your `.env` file:
   ```
   EODHD_API_KEY=your_api_key_here
   ```

### 2. Google Sheets API Setup

#### Option A: Service Account (Recommended)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google Sheets API
4. Create a Service Account:
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Download the JSON credentials file
5. Rename the downloaded file to `credentials.json` and place it in the project root
6. Share your Google Sheet with the service account email (found in the JSON file)

#### Option B: OAuth2 (Alternative)

1. Follow the same steps as above but create OAuth2 credentials instead
2. Download the credentials and set up OAuth2 flow

### 3. Google Sheets Setup

1. Create a new Google Sheet
2. Copy the Spreadsheet ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
   ```
3. Add it to your `.env` file:
   ```
   GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id_here
   ```

## 🚀 Usage

### Basic Usage

```bash
python main.py
```

### Advanced Usage

```bash
# Run with custom parameters
python main.py --max-stocks 100 --test

# Use custom API keys
python main.py --eodhd-key YOUR_KEY --spreadsheet-id YOUR_SHEET_ID
```

### Command Line Options

- `--max-stocks`: Maximum number of stocks to analyze (default: 50)
- `--test`: Run in test mode with sample stocks (AAL, NVDA, AMD, TSLA)
- `--eodhd-key`: Override EODHD API key from .env
- `--google-credentials`: Override Google credentials file path
- `--spreadsheet-id`: Override Google Sheets ID from .env

## 📊 Output Format

The tool outputs results to Google Sheets with the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| Ticker | Stock symbol | AAL |
| Start Date | Growth move start date | Jun 27, 2016 |
| End Date | Growth move end date | Dec 9, 2016 |
| Superperformance | Yes/No | No |
| Drawdowns | List of drawdown dates | Jan 18, 2017 |
| Continuation | Yes/No | No |

## 🧪 Testing

Run the unit tests to verify the core logic:

```bash
python -m unittest test_screener.py
```

## 📈 Example Results

Based on the requirements, the tool should produce results like:

| Ticker | Start | End | Superperformance | Drawdowns | Continuation |
|--------|-------|-----|------------------|-----------|--------------|
| AAL | Jun 27, 2016 | Dec 9, 2016 | No | none | No |
| NVDA | Feb 11, 2016 | Feb 7, 2017 | Yes | Jan 18, 2017 | No |
| AMD | Oct 3, 2019 | Feb 19, 2021 | No | none | No |
| TSLA | Aug 23, 2019 | Jan 22, 2021 | Yes | [multiple] | Yes |

## 🔧 Configuration

Key parameters can be adjusted in `config.py`:

- `MIN_DAILY_VOLUME`: Minimum average daily volume (default: 200,000)
- `MIN_GROWTH_PERCENTAGE`: Minimum growth to start a move (default: 5.0%)
- `MAX_DRAWDOWN_PERCENTAGE`: Maximum drawdown before termination (default: 30.0%)
- `GROWTH_MOVE_DAYS`: Days to check for initial growth (default: 5)
- `MAX_DAYS_WITHOUT_HIGH`: Days without new high before termination (default: 30)
- `MAX_TOTAL_DAYS`: Maximum total days for a move (default: 504)

## 📝 Logging

The tool creates detailed logs in `superperformance_screener.log` and outputs to console. Log levels can be adjusted in `main.py`.

## 🚨 Error Handling

- **API Rate Limiting**: Built-in delays between requests
- **Retry Logic**: Automatic retries for failed API calls
- **Graceful Degradation**: Continues processing even if some stocks fail
- **Data Validation**: Validates all input data before processing

## 🔒 Security

- API keys are stored in environment variables
- No sensitive data is logged
- Google Sheets access is restricted to your specified spreadsheet

## 📞 Support

For issues or questions:

1. Check the logs in `superperformance_screener.log`
2. Verify your API keys are correct
3. Ensure your Google Sheet is shared with the service account
4. Run tests to verify core functionality

## 📄 License

This project is for educational and research purposes. Please ensure compliance with EODHD and Google API terms of service.

## 🔄 Updates

The tool uses the EODHD API for comprehensive stock data:
- **End-of-Day Data**: Historical OHLC data for technical analysis
- **Fundamentals**: Company information and exchange details
- **Volume Analysis**: Average daily trading volume calculations
- **Stock Discovery**: High-volume stock identification from major indices

---

**Note**: This tool is designed for educational and research purposes. Always verify results and consider consulting with financial professionals before making investment decisions. 