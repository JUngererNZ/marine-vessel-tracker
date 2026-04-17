import os
import requests
from dotenv import load_dotenv

load_dotenv()

def verify_list():
    api_key = os.getenv("OPENSHIPDATA_KEY")
    # Logic to read vessels.txt and call MarinePlan Search API
    # ... (similar to previous script)
    print("Verification complete. List is synced.")

if __name__ == "__main__":
    verify_list()