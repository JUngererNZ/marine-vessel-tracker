# marine-vessel-tracker

A Python-based utility to verify and track marine vessels in real-time using MMSI identifiers.
Vibe coded with the best intentions........obviously!!

## 🚀 Features
- **MMSI Verification:** Cross-reference a list of MMSI numbers against OpenShipData to ensure vessel name accuracy.
- **Real-time Tracking:** Utilize WebSockets via AISStream.io for live position and status updates.
- **Automated Reporting:** Output current location data to text-based logs.

## 🛠️ Tech Stack
- **Language:** Python 3.9+
- **APIs:** OpenShipData (REST), AISStream.io (WebSocket)
- **Libraries:** `requests`, `websockets`, `asyncio`

## 📂 Project Structure
- `verify_vessels.py`: Script to validate your local list against global databases.
- `track_vessels.py`: The live tracking engine.
- `vessels.txt`: Your input file (Format: `MMSI, Optional Name`).
- `.env`: (Optional) Store your API keys here.

## 📖 Usage
1. Populate `vessels.txt` with your target MMSI numbers.
2. Run verification: `python verify_vessels.py`
3. Start live tracking: `python track_vessels.py`

