from flask import Flask, request
from flask_cors import CORS
import subprocess
import requests
import argparse

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = 'dljsaklqk24e21cjn!Ew@@dsa5'

parser = argparse.ArgumentParser()
parser.add_argument("--id", default="DRONE1", help="Unikt ID för drönaren, t.ex. DRONE1")
parser.add_argument("--port", default=5004, type=int, help="Port som denna drönar-server körs på")
args = parser.parse_args()

myID = args.id

current_longitude = 13.21008
current_latitude = 55.71106

SERVER = "http://localhost:5001/drone"

drone_info = {
    'id': myID,
    'longitude': current_longitude,
    'latitude': current_latitude,
    'status': 'idle'
}
with requests.Session() as session:
    resp = session.post(SERVER, json=drone_info)
    print("Registering drone:", resp.text)

@app.route('/', methods=['POST'])
def main():
    coords = request.json
    # coords = { "current": (x,y), "pickup": (x,y), "destination": (x,y) }

    current = coords['current']
    pickup = coords['pickup']
    destination = coords['destination']

    subprocess.Popen([
        "python3", "simulator.py",
        "--id", myID,
        "--clong", str(current[0]),
        "--clat", str(current[1]),
        "--picklong", str(pickup[0]),
        "--picklat", str(pickup[1]),
        "--destlong", str(destination[0]),
        "--destlat", str(destination[1])
    ])
    return "New route received", 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=args.port)
