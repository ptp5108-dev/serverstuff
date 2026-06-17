
import base64
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
app = Flask(__name__)
# CORS(app)
CORS(app, origins=["*"], resources={r"/*": {"origins": "*"}})

print("yippeee")
API_URL = "https://console.helium-iot.xyz/api/devices/94944a0000071530/queue"
API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJjaGlycHN0YWNrIiwiaXNzIjoiY2hpcnBzdGFjayIsInN1YiI6ImY4Y2UwNDQ5LTBmOTItNDFlNi05ZjBiLThjZmFjMjdiNDMxNSIsInR5cCI6ImtleSJ9.jE4OlznQGvsFqJ1BN5Ew5BdVgB8voF40_A01Wx4hXTo"
@app.route("/api/downlink", methods=['POST'])
def downlink_process():
    try:
        
        data=request.json
        command = data.get("command")
        if not command:
            return jsonify({"error":"no command"}),400
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        }

        payload = {
        "flushQueue": False,
        "queueItem": {
            "confirmed": False,
            "data": "string",
            # "expiresAt": "2026-06-17T11:54:15.788Z",
            "fCntDown": 0,
            "fPort": 223,
            "id": "string",
            "isEncrypted": False,
            "isPending": True,
            "object": {
        "command":command
        }
        }
        }
        response = requests.post(API_URL, json=payload, headers=headers, verify=False)
        if response.status_code == 200:
            print("Success! Downlink successfully enqueued.")
            return(response.json())
        else:
            return(f"Failed with code {response.status_code}: {response.text}")
    except Exception as e:
        return(f"Network error: {e}")


@app.route('/webhook', methods=['POST'])
def receive_lora_data():
    # 1. Grab the JSON payload sent by the LoRaWAN integration
    payload = request.json
    
    if not payload:
        return jsonify({"status": "error", "message": "No JSON payload received"}), 400

    print("--- New Uplink Received ---")
    
    # 2. Extract your decoded object
    # ChirpStack and TTN usually wrap your custom decoder output inside an 'object' or 'data' field
    object_data = payload.get('object') or payload.get('data', {})
    
    # 3. Pull out your "foo" value
    foo_value = object_data.get('foo')
    dev_eui = payload.get('devEui') # Good practice to track which device sent it!

    if foo_value:
        print(f"Device EUI: {dev_eui}")
        print(f"Extracted Pair -> foo: {foo_value}")
        
        # This is where you would save the data to a database (SQLite, PostgreSQL, etc.)
        # e.g., save_to_db(dev_eui, foo_value)
    else:
        print("Webhook received, but 'foo' key wasn't found in the decoded data.")
        print(f"Raw payload for debugging: {payload}")

    # 4. Always return a 200 OK to the LoRaWAN server so it knows you got the data
    return jsonify({"status": "success"}), 200

    
import os

if __name__ == "__main__":
    # Look for the port assigned by the cloud provider. 
    # If it's not found (like when running on your laptop), default to 5000.
    port = int(os.environ.get("PORT", 5000))
    
    # host="0.0.0.0" opens the server up to accept external connections
    # debug=False is recommended for production cloud environments
    app.run(host="0.0.0.0", port=port, debug=False)