from cmath import pi
from flask import Flask, request, jsonify
from geopy.geocoders import Nominatim
from flask_cors import CORS
import redis
import json
import requests

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = 'dljsaklqk24e21cjn!Ew@@dsa5'

redis_server = redis.Redis(host='localhost', port=6379, decode_responses=True)
geolocator = Nominatim(user_agent="my_request")
region = ", Lund, Skåne, Sweden"

@app.route('/planner', methods=['POST'])
def route_planner():
    Addresses = json.loads(request.data.decode())
    FromAddress = Addresses['faddr'] 
    ToAddress = Addresses['taddr']  

    from_location = geolocator.geocode(FromAddress + region, timeout=None)
    to_location = geolocator.geocode(ToAddress + region, timeout=None)

    if from_location is None:
        return 'Departure address not found, please input a correct address'
    elif to_location is None:
        return 'Destination address not found, please input a correct address'
    else:
        coords = {
            'pickup': (from_location.longitude, from_location.latitude),
            'destination': (to_location.longitude, to_location.latitude)
        }

        drones = redis_server.smembers("drones")
        droneAvailable = None
        for drone in drones:
            droneData = redis_server.hgetall(drone)
            if droneData['status'] == 'idle':
                droneAvailable = drone
                coords['current'] = (
                    float(droneData['longitude']),
                    float(droneData['latitude'])
                )
                break

        if droneAvailable is None:
            return 'No available drone, try later'
        else:
            DRONE_IP = redis_server.hget(droneAvailable, 'ip')
            DRONE_URL = 'http://' + DRONE_IP + ':5004'

            try:
                with requests.session() as session:
                    resp = session.post(DRONE_URL, json=coords)
                    print(resp.text)
                return 'Got address and sent request to the drone'
            except Exception as e:
                print(e)
                return "Could not connect to the drone, please try again"

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='5002')
