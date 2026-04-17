import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
INPUT_FILE = 'vessels.txt'
OUTPUT_FILE = 'vessel_status.md'
API_KEY = os.getenv("VESSELFINDER_KEY")

def load_vessels():
    mmsi_list = []
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Error: {INPUT_FILE} not found.")
        return mmsi_list
    
    with open(INPUT_FILE, 'r') as f:
        for line in f:
            # Handle CSV format or simple list
            mmsi = line.strip().split(',')[0]
            if mmsi.isdigit():
                mmsi_list.append(mmsi)
    return mmsi_list

def fetch_vessel_data(mmsi_list):
    results = []
    # VesselFinder allows comma-separated MMSIs for bulk lookup (saves API credits)
    mmsi_str = ",".join(mmsi_list)
    url = f"https://api.vesselfinder.com/vesselslist?userkey={API_KEY}&mmsi={mmsi_str}"

    print(f"📡 Requesting data for {len(mmsi_list)} vessels...")
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ API Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")
    return []

def generate_markdown(data):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"# 🚢 Marine Vessel Tracker Report",
        f"**Last Sync:** {timestamp}",
        f"",
        f"| Vessel Name | MMSI | Status | Location | Last Updated (UTC) |",
        f"| :--- | :--- | :--- | :--- | :--- |"
    ]

    if not data:
        lines.append("| *No Data* | - | - | - | - |")
    else:
        for ship in data:
            name = ship.get("NAME", "Unknown")
            mmsi = ship.get("MMSI", "N/A")
            status = ship.get("STATUS", "N/A")
            lat = ship.get("LAT")
            lon = ship.get("LON")
            tstamp = ship.get("TSTAMP", "N/A")
            
            # Map Link
            map_link = f"[📍 View Map](https://www.google.com/maps?q={lat},{lon})"
            
            lines.append(f"| **{name}** | `{mmsi}` | {status} | {map_link} | {tstamp} |")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    print(f"📝 Report successfully updated in {OUTPUT_FILE}")

if __name__ == "__main__":
    mmsis = load_vessels()
    if mmsis:
        ship_data = fetch_vessel_data(mmsis)
        generate_markdown(ship_data)