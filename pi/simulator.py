# === simulator.py ===
import math
import requests
import argparse

def getMovement(src, dst):
    speed = 0.000001
    dst_x, dst_y = dst
    x, y = src
    direction = math.sqrt((dst_x - x)**2 + (dst_y - y)**2)
    if direction == 0:
        return (0, 0)
    return speed * (dst_x - x) / direction, speed * (dst_y - y) / direction

def moveDrone(src, d_long, d_la):
    x, y = src
    return (x + d_long, y + d_la)

def distanceSquared(a, b):
    return ((b[0] - a[0])**2 + (b[1] - a[1])**2)

def run(drone_id, current_coords, pickup_coords, destination_coords, server_url):
    drone_coords = current_coords

    # current -> pickup
    d_long, d_la = getMovement(drone_coords, pickup_coords)
    while distanceSquared(drone_coords, pickup_coords)*10**6 > 0.0002:
        drone_coords = moveDrone(drone_coords, d_long, d_la)
        requests.post(server_url, json={
            'id': drone_id,
            'longitude': drone_coords[0],
            'latitude': drone_coords[1],
            'status': 'busy'
        })

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

    # destination -> back to pickup
    d_long, d_la = getMovement(drone_coords, pickup_coords)
    while distanceSquared(drone_coords, pickup_coords)*10**6 > 0.0002:
        drone_coords = moveDrone(drone_coords, d_long, d_la)
        requests.post(server_url, json={
            'id': drone_id,
            'longitude': drone_coords[0],
            'latitude': drone_coords[1],
            'status': 'busy'
        })

    drone_coords = pickup_coords
    requests.post(server_url, json={
        'id': drone_id,
        'longitude': drone_coords[0],
        'latitude': drone_coords[1],
        'status': 'busy'
    })

    requests.post(server_url, json={
        'id': drone_id,
        'longitude': drone_coords[0],
        'latitude': drone_coords[1],
        'status': 'idle'
    })

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
