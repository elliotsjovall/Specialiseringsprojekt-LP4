from flask import Flask, request
from flask_cors import CORS
import redis
import json


app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = 'dljsaklqk24e21cjn!Ew@@dsa5'

# change this to connect to your redis server
# ===============================================
redis_server = redis.Redis(host = "localhost", decode_responses=True, charset="unicode_escape", port =6379)
# ===============================================

redis_server.set('longitude', 13.21008)
redis_server.set('latitude', 55.71106)

@app.route('/drone', methods=['POST'])
def drone():
    drone = request.get_json()
    droneIP = request.remote_addr
    droneID = drone['id']
    drone_longitude = drone['longitude']
    drone_latitude = drone['latitude']
    drone_status = drone['status']
    # Get the infomation of the drone in the request, and update the information in Redis database
    # Data that need to be stored in the database: 
    # Drone ID, logitude of the drone, latitude of the drone, drone's IP address, the status of the drone
    # Note that you need to store the metioned infomation for all drones in Redis, think carefully how to store them
    # =====================================================

    # Skapa en dictionary med drönardata
    drone_data = {
        'id': droneID,
        'ip': droneIP,
        'longitude': drone_longitude,
        'latitude': drone_latitude,
        'status': drone_status
    }

    # Spara drönarinformation i Redis under en unik nyckel per drönare
    redis_server.hmset(f"drone:{droneID}", drone_data)
    redis_server.sadd("drones", f"drone:{droneID}")  # <--- Lägg till detta


    return {'message': 'Drone data updated successfully'}, 200
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='5001')
