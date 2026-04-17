import asyncio
import websockets
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configuration
INPUT_FILE = 'vessels.txt'
OUTPUT_FILE = 'vessel_status.md'
TIMEOUT_SECONDS = 30  # How long to listen for signals per run
API_KEY = os.getenv("AISSTREAM_KEY")

def load_targets():
    targets = []
    if not os.path.exists(INPUT_FILE):
        return targets
    with open(INPUT_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('mmsi'):
                # Extract MMSI (first column)
                targets.append(line.split(',')[0].strip())
    return targets

async def sync_vessels():
    targets = load_targets()
    if not targets:
        print("No MMSIs found in vessels.txt")
        return

    results = {}
    
    print(f"Connecting to AISStream to track {len(targets)} vessels...")
    
    try:
        async with websockets.connect("wss://stream.aisstream.io/v0/stream") as websocket:
            subscribe_msg = {
                "APIKey": API_KEY,
                "FiltersShipMMSI": targets,
                "FilterMessageTypes": ["PositionReport"]
            }

            await websocket.send(json.dumps(subscribe_msg))

            # Listen for signals until timeout
            start_time = asyncio.get_event_loop().time()
            while (asyncio.get_event_loop().time() - start_time) < TIMEOUT_SECONDS:
                try:
                    # Wait for a message with a short internal timeout to check the loop condition
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    msg_data = json.loads(message)
                    
                    mmsi = str(msg_data["MetaData"]["MMSI"])
                    name = msg_data["MetaData"]["ShipName"].strip()
                    lat = msg_data["Message"]["PositionReport"]["Latitude"]
                    lon = msg_data["Message"]["PositionReport"]["Longitude"]
                    status = msg_data["Message"]["PositionReport"].get("NavigationalStatus", "N/A")
                    
                    # Update/Add result (keeps the latest signal)
                    results[mmsi] = {
                        "name": name,
                        "lat": lat,
                        "lon": lon,
                        "status": status,
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    print(f"Captured: {name} ({mmsi})")
                    
                except asyncio.TimeoutError:
                    continue 
                    
    except Exception as e:
        print(f"Connection error: {e}")

    # Generate Markdown Output
    write_markdown(results, targets)

def write_markdown(results, targets):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    lines = [
        f"# Marine Vessel Tracker Report",
        f"**Last Sync:** {timestamp}",
        f"",
        f"| Vessel Name | MMSI | Latitude | Longitude | Status | Last Seen |",
        f"| :--- | :--- | :--- | :--- | :--- | :--- |"
    ]
    
    for mmsi in targets:
        if mmsi in results:
            v = results[mmsi]
            lines.append(f"| {v['name']} | `{mmsi}` | {v['lat']} | {v['lon']} | {v['status']} | {v['time']} |")
        else:
            lines.append(f"| Unknown | `{mmsi}` | - | - | *No signal in window* | - |")

    with open(OUTPUT_FILE, 'w') as f:
        f.write("\n".join(lines))
    
    print(f"\nReport generated: {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(sync_vessels())