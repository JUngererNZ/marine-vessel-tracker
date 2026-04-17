import asyncio
import websockets
import json
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
INPUT_FILE = 'vessels.txt'
OUTPUT_FILE = 'vessel_status.md'
API_KEY = os.getenv("AISSTREAM_KEY")
RUN_TIMEOUT = 120  # Total seconds to wait for signals (2 minutes)

def load_vessels():
    vessels = []
    if not os.path.exists(INPUT_FILE): return vessels
    with open(INPUT_FILE, 'r') as f:
        for line in f:
            parts = line.strip().split(',')
            if parts and parts[0].isdigit():
                vessels.append(parts[0].strip())
    return vessels

async def connect_ais_stream():
    targets = load_vessels()
    if not targets:
        print("❌ No MMSI targets found in vessels.txt")
        return

    tracked_data = {}
    
    print(f"📡 Starting sync for {len(targets)} vessels (Timeout: {RUN_TIMEOUT}s)...")

    try:
        async with websockets.connect("wss://stream.aisstream.io/v0/stream") as websocket:
            # Using the official Global Bounding Box + MMSI Filter
            subscribe_message = {
                "APIKey": API_KEY,
                "BoundingBoxes": [[[-90, -180], [90, 180]]], 
                "FiltersShipMMSI": targets,
                "FilterMessageTypes": ["PositionReport"]
            }

            await websocket.send(json.dumps(subscribe_message))

            # Start timer
            start_time = asyncio.get_event_loop().time()

            while (asyncio.get_event_loop().time() - start_time) < RUN_TIMEOUT:
                try:
                    # Wait for message with a 1s buffer
                    message_json = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    message = json.loads(message_json)
                    
                    if message.get("MessageType") == "PositionReport":
                        meta = message.get("MetaData", {})
                        pos = message['Message']['PositionReport']
                        
                        mmsi = str(meta.get("MMSI"))
                        name = meta.get("ShipName", "Unknown").strip()
                        
                        tracked_data[mmsi] = {
                            "name": name,
                            "lat": pos['Latitude'],
                            "lon": pos['Longitude'],
                            "status": pos.get("NavigationalStatus", "Moving/Unknown"),
                            "time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                        }
                        print(f"✅ Found: {name} ({mmsi})")

                        # If we found everyone, we can stop early
                        if len(tracked_data) == len(targets):
                            break
                            
                except asyncio.TimeoutError:
                    continue # Keep loop alive until RUN_TIMEOUT is hit

    except Exception as e:
        print(f"❌ Connection Error: {e}")

    generate_markdown(tracked_data, targets)

def generate_markdown(data, targets):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"# 🚢 Marine Vessel Tracker Report",
        f"**Sync Time:** {timestamp} (Local)",
        f"",
        f"| Vessel Name | MMSI | Status | Location | Last Seen |",
        f"| :--- | :--- | :--- | :--- | :--- |"
    ]

    for mmsi in targets:
        if mmsi in data:
            v = data[mmsi]
            map_url = f"https://www.google.com/maps?q={v['lat']},{v['lon']}"
            lines.append(f"| **{v['name']}** | `{mmsi}` | {v['status']} | [📍 View Map]({map_url}) | {v['time']} |")
        else:
            # This is where the fallback would go
            lines.append(f"| *Signal Lost* | `{mmsi}` | Offline/Out of Range | - | - |")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    print(f"📝 Report updated in {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(connect_ais_stream())