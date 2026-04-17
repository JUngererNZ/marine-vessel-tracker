import asyncio
import websockets
import json
import os
from dotenv import load_dotenv

load_dotenv()

# 1. Load your MMSIs from vessels.txt
def get_target_mmsis(file_path):
    with open(file_path, 'r') as f:
        # Returns a list of MMSI strings
        return [line.strip().split(',')[0] for line in f if line.strip() and not line.startswith('mmsi')]

async def verify_vessels_live():
    targets = get_target_mmsis('vessels.txt')
    found_vessels = {}
    api_key = os.getenv("AISSTREAM_KEY")

    async with websockets.connect("wss://stream.aisstream.io/v0/stream") as websocket:
        subscribe_msg = {
            "APIKey": api_key,
            "FiltersShipMMSI": targets,
            "FilterMessageTypes": ["PositionReport"] 
        }

        await websocket.send(json.dumps(subscribe_msg))
        print(f"Waiting for signals from {len(targets)} vessels...")

        # Run for a set timeout (e.g., 60 seconds) to verify what's currently "visible"
        try:
            while len(found_vessels) < len(targets):
                message = await asyncio.wait_for(websocket.recv(), timeout=60)
                msg_data = json.loads(message)
                
                mmsi = str(msg_data["MetaData"]["MMSI"])
                name = msg_data["MetaData"]["ShipName"]
                
                if mmsi not in found_vessels:
                    found_vessels[mmsi] = name
                    print(f"✅ Verified: {mmsi} is '{name}'")
                    
        except asyncio.TimeoutError:
            print(f"\nVerification window closed. Found {len(found_vessels)}/{len(targets)} vessels.")
            missing = set(targets) - set(found_vessels.keys())
            if missing:
                print(f"❌ No signal received for: {', '.join(missing)}")

if __name__ == "__main__":
    asyncio.run(verify_vessels_live())