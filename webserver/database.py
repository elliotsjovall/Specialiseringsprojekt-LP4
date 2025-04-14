from flask import Flask, request
from flask_cors import CORS
import redis

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = 'dljsaklqk24e21cjn!Ew@@dsa5'

# Koppla mot Redis
redis_server = redis.Redis(host="localhost", decode_responses=True, charset="unicode_escape", port=6379)

# Sätt default-läge om du vill
redis_server.set('longitude', 13.21008)
redis_server.set('latitude', 55.71106)

@app.route('/drone', methods=['POST'])
def drone():
    drone = request.get_json()
    droneIP = request.remote_addr  # IP-adressen som anropar
    droneID = drone['id']
    drone_longitude = drone['longitude']
    drone_latitude = drone['latitude']
    drone_status = drone['status']

    # Spara i Redis
    drone_data = {
        'id': droneID,
        'ip': droneIP,
        'longitude': drone_longitude,
        'latitude': drone_latitude,
        'status': drone_status
    }

    # hmset är deprecated, men hset funkar liknande
    redis_server.hset(f"drone:{droneID}", mapping=drone_data)
    redis_server.sadd("drones", f"drone:{droneID}")

    return {'message': 'Drone data updated successfully'}, 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='5001')
