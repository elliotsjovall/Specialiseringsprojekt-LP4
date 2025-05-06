from cmath import pi
from flask import Flask, request, jsonify
from geopy.geocoders import Nominatim
from flask_cors import CORS
import redis
import json
import requests
import time
import threading
import atexit  # Lägg till atexit för att stänga ner Redis vid servernedstängning

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = 'dljsaklqk24e21cjn!Ew@@dsa5'

redis_server = redis.Redis(host='localhost', port=6379, decode_responses=True)

geolocator = Nominatim(user_agent="my_request")
region = ", Lund, Skåne, Sweden"

# update_url = "http://localhost:5002/planner"
# # Funktion för att uppdatera orderstatus på hemsidan
# def update_order_on_website(order_number, status):
#     d = {
#         'order_number': order_number,
#         'status': status
#     }
#     try:
#         response = requests.post(update_url, json=d)
#         if response.status_code == 200:
#             print(f"Order {order_number} status updated successfully on website.")
#         else:
#             print(f"Failed to update order {order_number} status on website.")
#     except Exception as e:
#         print(f"Error updating order {order_number} status on website: {e}")


# Funktion för att rensa Redis vid servernedstängning
def cleanup_redis():
    print("Cleaning up order-related Redis keys...")
    # Radera kön
    redis_server.delete('drone:queue')

    # Hämta alla nycklar
    all_keys = redis_server.keys('*')
    for key in all_keys:
        # Om nyckeln är ett heltal → vi antar det är ett ordernummer
        if key.isdigit():
            redis_server.delete(key)

# Registrera funktionen för att rensa Redis när servern stängs
atexit.register(cleanup_redis)

@app.route('/planner', methods=['POST'])
def route_planner():
    data = json.loads(request.data.decode())
    print("AAAAAAAAA", data)
    FromAddress = "Sölvegatan 14"
    ToAddress = data['taddr']
    order_number = data.get('order_number')
    
    from_location = geolocator.geocode(FromAddress + region, timeout=None)
    to_location = geolocator.geocode(ToAddress + region, timeout=None)
    print(f"from location: {from_location}")
    print(f"to location: {to_location}")

    if from_location is None:
        return 'Departure address not found, please input a correct address'
    elif to_location is None:
        return 'Destination address not found, please input a correct address'
    else:
        coords = {
            'pickup': (from_location.longitude, from_location.latitude),
            'destination': (to_location.longitude, to_location.latitude),
            'order_number': order_number
        }
        print(f"FromAdress: {coords}")
       
        drones = redis_server.smembers("drones")
        droneAvailable = None

        for drone in drones:
            droneData = redis_server.hgetall(drone)

            # checka om drönare är ledig
            if droneData.get('status') == 'idle':
                droneAvailable = drone
                coords['current'] = (
                    float(droneData['longitude']),
                    float(droneData['latitude'])
                )
                #sätta busy om upptaget
                redis_server.hset(drone, 'status', 'busy')
                break

        if droneAvailable is None:
            order_data = {
                'status': 'i kö',
                'drone': '', 
                'order_number': order_number
            }

            redis_server.hset(order_number, mapping=order_data) 
            redis_server.rpush('drone:queue', json.dumps(coords))
            return jsonify({'status': 'i kö', 'message': 'No available drone, your order has been queued'})
        else:
            redis_server.hset(order_number, mapping={
            'status': 'levereras',
            'drone': droneAvailable
            })

            DRONE_IP = redis_server.hget(droneAvailable, 'ip')
            DRONE_PORT = redis_server.hget(droneAvailable, 'port')
            DRONE_URL = f'http://{DRONE_IP}:{DRONE_PORT}'


            try:
                with requests.session() as session:
                    resp = session.post(DRONE_URL, json=coords)
                    print(resp.text)
                return jsonify({'status': 'levereras', 'message': 'Got address and sent request to the drone'})
            except Exception as e:
                print(e)
                return jsonify({'status': 'error', 'message': "Could not connect to the drone, please try again"})
            
@app.route('/queue-length', methods=['GET'])
def queue_length():
    length = redis_server.llen('drone:queue')
    return jsonify({'queue_length': length})

def drone_queue_worker():
    while True:
        order_data = redis_server.lindex('drone:queue', 0)
        if order_data:
            drones = redis_server.smembers("drones")
            for drone in drones:
                droneData = redis_server.hgetall(drone)
                if droneData.get('status') == 'idle':
                    coords = json.loads(order_data)
                    coords['current'] = (
                        float(droneData['longitude']),
                        float(droneData['latitude'])
                    )
                    redis_server.hset(drone, 'status', 'busy')

                    drone_ip = droneData['ip']
                    drone_port = droneData['port']
                    drone_url = f"http://{drone_ip}:{drone_port}"

                    try:
                        with requests.session() as session:
                            resp = session.post(drone_url, json=coords)
                            print(f"Sent queued job to {drone}: {resp.text}")
                        
                        redis_server.lpop('drone:queue') 
                        redis_server.hset(coords['order_number'], 'status', 'levereras')

                        update_order_on_website(coords['order_number'], 'levereras')

                    except Exception as e:
                        print(f"Failed to send queued job to {drone}: {e}")
                        redis_server.hset(coords['order_number'], 'status', 'error')
                    break
        time.sleep(5)

threading.Thread(target=drone_queue_worker, daemon=True).start()


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='5002')
