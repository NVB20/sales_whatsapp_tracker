import os
import gspread
from google.oauth2.service_account import Credentials

def init_sheets_connection():
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials_file = os.getenv("CREDENTIALS_FILE")
    creds = Credentials.from_service_account_file(credentials_file, scopes=SCOPES)
    client = gspread.authorize(creds)

    return client
