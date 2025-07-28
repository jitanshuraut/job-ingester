from dotenv import load_dotenv
import os
from supabase import create_client, Client
from typing import Optional

class SupabaseDB:
    def __init__(self):
        load_dotenv()
        self.url: Optional[str] = os.getenv("SUPABASE_URL")
        self.key: Optional[str] = os.getenv("SUPABASE_KEY")
        self.client: Optional[Client] = None

        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL or SUPABASE_KEY not found in environment variables.")
        
        self._connect()

    def _connect(self):
        try:
            self.client = create_client(self.url, self.key)
            response = self.client.table("jobs").select("*").limit(1).execute()
            print("✅ Successfully connected to Supabase.")
        except Exception as e:
            print("❌ Error connecting to Supabase:", e)
            raise e

    def get_client(self) -> Client:
        if not self.client:
            raise RuntimeError("Supabase client not initialized.")
        return self.client
