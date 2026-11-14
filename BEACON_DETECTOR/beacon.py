import time
import requests
from datetime import datetime

SERVER_URL = "http://127.0.0.1:5000/api/heartbeat"
BEACON_NAME = "Student Demo Beacon"
BEACON_ID = "BEACON-001"
HEARTBEAT_INTERVAL = 2  # Send a heartbeat every 2 seconds


def main():
    print("=" * 48)
    print("SAFE DEMO BEACON")
    print("Sending heartbeat to the local Flask server")
    print("Press CTRL+C to stop the beacon")
    print("=" * 48)

    while True:
        payload = {
            "source_name": BEACON_NAME,
            "source_id": BEACON_ID,
            "sent_at": datetime.now().isoformat(timespec="seconds")
        }

        try:
            response = requests.post(
                SERVER_URL,
                json=payload,
                timeout=3
            )
            response.raise_for_status()
            print(f"[{datetime.now():%H:%M:%S}] Heartbeat sent - server acknowledged")
        except requests.RequestException as error:
            print(f"[{datetime.now():%H:%M:%S}] Server unavailable: {error}")
            print("Make sure app.py is running.")

        time.sleep(HEARTBEAT_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBeacon stopped by user.")