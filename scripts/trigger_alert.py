import requests
import json
import time

# Base URL of the running FastAPI server
BASE_URL = "http://localhost:8000"

# A valid vehicle_id from the database
VEHICLE_ID = "01db2b8ad28944d0b5b910c2567ba233"

def trigger_high_risk_prediction():
    """
    Triggers a high-risk prediction by sending critical sensor values.
    This should trigger the NotificationService and send an email.
    """
    endpoint = f"{BASE_URL}/predictions/predict"
    
    # Critical values to ensure HIGH risk
    payload = {
        "vehicle_id": VEHICLE_ID,
        "engine_temp": 120.5,     # High (threshold 100)
        "oil_pressure": 25.0,     # Low (threshold 35)
        "rpm": 5500,              # High
        "vibration": 0.95,        # High (threshold 0.7)
        "battery_voltage": 11.2,  # Low
        "mileage": 85000
    }
    
    print(f"🚀 Triggering HIGH risk prediction for vehicle {VEHICLE_ID}...")
    
    try:
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        result = response.json()
        
        print("\n✅ Prediction Successful!")
        print(f"   Risk Level: {result.get('risk_level')}")
        print(f"   Failure Probability: {result.get('failure_probability')}")
        print(f"   Sensor Flags: {result.get('sensor_flags')}")
        
        print("\n📬 The system should now be processing the notification in the background.")
        print("Check your terminal logs for '--- MOCK EMAIL SEND ---' or email inbox if configured.")
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Could not connect to the server at {BASE_URL}. Is it running?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    trigger_high_risk_prediction()
