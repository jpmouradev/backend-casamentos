from supabase import create_client
import os

from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv("url"),
    os.getenv("key")
)