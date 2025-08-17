"""
Google Sheets Client for SuperPerformanceScreener
Handles authentication and data output to Google Sheets
"""
import os
from typing import List, Dict, Any
import logging
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import (
    GOOGLE_SHEETS_CREDENTIALS_FILE,
    GOOGLE_SHEETS_SPREADSHEET_ID,
    SHEET_NAME,
    HEADERS
)

logger = logging.getLogger(__name__)

class GoogleSheetsClient:
    """Client for interacting with Google Sheets API"""
    
    def __init__(self, credentials_file: str = None, spreadsheet_id: str = None):
        self.credentials_file = credentials_file or GOOGLE_SHEETS_CREDENTIALS_FILE
        self.spreadsheet_id = spreadsheet_id or GOOGLE_SHEETS_SPREADSHEET_ID
        
        if not self.spreadsheet_id:
            raise ValueError("Google Sheets Spreadsheet ID is required")
        
        self.service = self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API"""
        try:
            # Try service account authentication first
            if os.path.exists(self.credentials_file):
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_file,
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
                logger.info("Using service account authentication")
            else:
                # Fall back to OAuth2 if service account file doesn't exist
                logger.warning(f"Service account file {self.credentials_file} not found. Please set up OAuth2 authentication.")
                raise FileNotFoundError(f"Credentials file not found: {self.credentials_file}")
            
            return build('sheets', 'v4', credentials=credentials)
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise
    
    def create_spreadsheet(self, title: str = None) -> str:
        """Create a new Google Spreadsheet"""
        try:
            spreadsheet = {
                'properties': {
                    'title': title or 'SuperPerformanceScreener Results'
                },
                'sheets': [
                    {
                        'properties': {
                            'title': SHEET_NAME,
                            'gridProperties': {
                                'rowCount': 1000,
                                'columnCount': len(HEADERS)
                            }
                        }
                    }
                ]
            }
            
            spreadsheet = self.service.spreadsheets().create(body=spreadsheet).execute()
            spreadsheet_id = spreadsheet['spreadsheetId']
            
            logger.info(f"Created new spreadsheet: {spreadsheet_id}")
            return spreadsheet_id
            
        except HttpError as e:
            logger.error(f"Error creating spreadsheet: {e}")
            raise
    
    def clear_sheet(self, sheet_name: str = None):
        """Clear all data from the sheet"""
        try:
            range_name = f"{sheet_name or SHEET_NAME}!A:Z"
            self.service.spreadsheets().values().clear(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            logger.info(f"Cleared sheet: {sheet_name or SHEET_NAME}")
            
        except HttpError as e:
            logger.error(f"Error clearing sheet: {e}")
            raise
    
    def write_headers(self, sheet_name: str = None):
        """Write headers to the sheet"""
        try:
            range_name = f"{sheet_name or SHEET_NAME}!A1:F1"
            body = {
                'values': [HEADERS]
            }
            
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"Wrote headers to sheet: {sheet_name or SHEET_NAME}")
            
        except HttpError as e:
            logger.error(f"Error writing headers: {e}")
            raise
    
    def append_rows(self, rows: List[List[str]], sheet_name: str = None):
        """Append rows to the sheet"""
        if not rows:
            return
        
        try:
            range_name = f"{sheet_name or SHEET_NAME}!A:F"
            body = {
                'values': rows
            }
            
            self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            logger.info(f"Appended {len(rows)} rows to sheet: {sheet_name or SHEET_NAME}")
            
        except HttpError as e:
            logger.error(f"Error appending rows: {e}")
            raise
    
    def format_sheet(self, sheet_name: str = None):
        """Apply formatting to the sheet"""
        try:
            requests = [
                # Format headers
                {
                    'repeatCell': {
                        'range': {
                            'sheetId': 0,
                            'startRowIndex': 0,
                            'endRowIndex': 1,
                            'startColumnIndex': 0,
                            'endColumnIndex': len(HEADERS)
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': {
                                    'red': 0.2,
                                    'green': 0.6,
                                    'blue': 0.8
                                },
                                'textFormat': {
                                    'bold': True,
                                    'foregroundColor': {
                                        'red': 1.0,
                                        'green': 1.0,
                                        'blue': 1.0
                                    }
                                }
                            }
                        },
                        'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                    }
                },
                # Auto-resize columns
                {
                    'autoResizeDimensions': {
                        'dimensions': {
                            'sheetId': 0,
                            'dimension': 'COLUMNS',
                            'startIndex': 0,
                            'endIndex': len(HEADERS)
                        }
                    }
                }
            ]
            
            body = {
                'requests': requests
            }
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=body
            ).execute()
            
            logger.info(f"Applied formatting to sheet: {sheet_name or SHEET_NAME}")
            
        except HttpError as e:
            logger.error(f"Error formatting sheet: {e}")
            # Don't raise - formatting is not critical
    
    def get_spreadsheet_url(self) -> str:
        """Get the URL of the spreadsheet"""
        return f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}"
    
    def write_results(self, results: List[Dict[str, Any]], sheet_name: str = None):
        """Write complete results to the sheet"""
        try:
            # Clear existing data
            self.clear_sheet(sheet_name)
            
            # Write headers
            self.write_headers(sheet_name)
            
            # Format results for output
            rows = []
            for result in results:
                row = [
                    result['ticker'],
                    result['start_date_formatted'],
                    result['end_date_formatted'],
                    result['superperformance_formatted'],
                    result.get('drawdowns_formatted', 'none'),
                    result['continuation_formatted']
                ]
                rows.append(row)
            
            # Append data rows
            if rows:
                self.append_rows(rows, sheet_name)
            
            # Apply formatting
            self.format_sheet(sheet_name)
            
            logger.info(f"Successfully wrote {len(rows)} results to sheet")
            
        except Exception as e:
            logger.error(f"Error writing results: {e}")
            raise 