import gspread
import os
import pandas as pd

from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

creds_info = {
    "type": os.getenv("GOOGLE_ACCOUNT_type"),
    "project_id": os.getenv("GOOGLE_ACCOUNT_project_id"),
    "private_key_id": os.getenv("GOOGLE_ACCOUNT_private_key_id"),
    "private_key": os.getenv("GOOGLE_ACCOUNT_private_key").replace("\\n", "\n"),
    "client_email": os.getenv("GOOGLE_ACCOUNT_client_email"),
    "client_id": os.getenv("GOOGLE_ACCOUNT_client_id"),
    "auth_uri": os.getenv("GOOGLE_ACCOUNT_auth_uri"),
    "token_uri": os.getenv("GOOGLE_ACCOUNT_token_uri"),
    "auth_provider_x509_cert_url": os.getenv(
        "GOOGLE_ACCOUNT_auth_provider_x509_cert_url"
    ),
    "client_x509_cert_url": os.getenv("GOOGLE_ACCOUNT_client_x509_cert_url"),
    "universe_domain": os.getenv("GOOGLE_ACCOUNT_universe_domain"),
}
creds = Credentials.from_service_account_info(creds_info, scopes=scopes)

client_google = gspread.authorize(creds)
