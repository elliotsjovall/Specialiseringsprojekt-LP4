import math
import requests
import argparse
import time  # 👈 viktigt
def getMovement(src, dst):
    speed = 0.00003
    dst_x, dst_y = dst
    x, y = src
    if src == dst:
        return 0.0, 0.0  # Inget att göra, ingen rörelse
    
    direction = math.sqrt((dst_x - x)**2 + (dst_y - y)**2)
    longitude_move = speed * ((dst_x - x) / direction )
    latitude_move = speed * ((dst_y - y) / direction )
    return longitude_move, latitude_move

def moveDrone(src, d_long, d_la):
    x, y = src
    x = x + d_long
    y = y + d_la        
    return (x, y)

def distanceSquared(a, b):
    return ((b[0] - a[0])**2 + (b[1] - a[1])**2)

def run(drone_id, current_coords, pickup_coords, destination_coords, server_url):
    drone_coords = current_coords

    # current -> pickup
      # Debugging: Skriv ut nuvarande status
    print(f"Moving to pickup: Current {drone_coords} -> Target {pickup_coords}")
    d_long, d_la = getMovement(drone_coords, pickup_coords)
    while distanceSquared(drone_coords, pickup_coords)*10**6 > 0.0002:
        drone_coords = moveDrone(drone_coords, d_long, d_la)
        with requests.Session() as session:
            drone_info = {'id': drone_id,
                          'longitude': drone_coords[0],
                          'latitude': drone_coords[1],
                          'status': 'busy'
                        }
            resp = session.post(SERVER_URL, json=drone_info)
        
     # Debugging: Skriv ut nuvarande status
    print(f"Moving to destination: Current {drone_coords} -> Target {destination_coords}")
     
    # pickup -> destination
    d_long, d_la = getMovement(drone_coords, destination_coords)
    while distanceSquared(drone_coords, destination_coords)*10**6 > 0.0002:
        drone_coords = moveDrone(drone_coords, d_long, d_la)


        requests.post(server_url, json={
            'id': drone_id,
            'longitude': drone_coords[0],
            'latitude': drone_coords[1],
            'status': 'busy'
        })
        time.sleep(0.05)
    print(f"Returning to pickup: Current {drone_coords} -> Target {pickup_coords}")
    # destination -> back to pickup
    d_long, d_la = getMovement(drone_coords, pickup_coords)
    while distanceSquared(drone_coords, pickup_coords)*10**6 > 0.0002:
        drone_coords = moveDrone(drone_coords, d_long, d_la)

        with requests.Session() as session:
            drone_info = {'id': drone_id,
                          'longitude': drone_coords[0],
                          'latitude': drone_coords[1],
                          'status': 'busy'
                        }
            resp = session.post(SERVER_URL, json=drone_info)
        time.sleep(0.05)  # 👈 Lägg till denna rad
    with requests.Session() as session:
            drone_info = {'id': drone_id,
                          'longitude': drone_coords[0],
                          'latitude': drone_coords[1],
                          'status': 'idle'
                         }
            resp = session.post(SERVER_URL, json=drone_info)
    return drone_coords[0], drone_coords[1]


if __name__ == "__main__":
    SERVER_URL = "http://localhost:5001/drone"

    parser = argparse.ArgumentParser()
    parser.add_argument("--id", type=str)
    parser.add_argument("--clong", type=float)
    parser.add_argument("--clat", type=float)
    parser.add_argument("--picklong", type=float)
    parser.add_argument("--picklat", type=float)
    parser.add_argument("--destlong", type=float)
    parser.add_argument("--destlat", type=float)
    args = parser.parse_args()

    current_coords = (args.clong, args.clat)
    pickup_coords = (args.picklong, args.picklat)
    destination_coords = (args.destlong, args.destlat)

    run(args.id, current_coords, pickup_coords, destination_coords, SERVER_URL)