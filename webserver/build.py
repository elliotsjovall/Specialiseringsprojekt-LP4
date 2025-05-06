from os import fdopen
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
import redis
import json
import requests
from lager import Produkt, Order, Test
import base64

from dotenv import load_dotenv
import os
from weather import get_current_weather  # our new weather module

# ─── load & verify API key ───────────────────────────────
load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
if not WEATHER_API_KEY:
    raise RuntimeError(
        "WEATHER_API_KEY not set; please add WEATHER_API_KEY=your_key to webserver/.env"
    )

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = 'dljsaklqk24e21cjn!Ew@@dsa5'

redis_server = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True,
    charset="unicode_escape"
)

def translate(coords_osm):
    x_osm_lim = (13.143390664, 13.257501336)
    y_osm_lim = (55.678138854000004, 55.734680845999996)

    x_svg_lim = (212.155699, 968.644301)
    y_svg_lim = (103.68, 768.96)

    x_osm, y_osm = coords_osm
    x_ratio = (x_svg_lim[1] - x_svg_lim[0]) / (x_osm_lim[1] - x_osm_lim[0])
    y_ratio = (y_svg_lim[1] - y_svg_lim[0]) / (y_osm_lim[1] - y_osm_lim[0])

    x_svg = x_ratio * (x_osm - x_osm_lim[0]) + x_svg_lim[0]
    y_svg = y_ratio * (y_osm_lim[1] - y_osm) + y_svg_lim[0]

    return x_svg, y_svg

lista1 = [
    Produkt("Sårsalvor och antiseptiska medel", 50),
    Produkt("Nässprej", 20),
    Produkt("C-vitamin", 500),
]
lista2 = [
    Produkt("Paracetamol", 10),
    Produkt("Ibuprofen", 16),
    Produkt("Acetylsalicylsyra", 10),
]
lista3 = [
    Produkt("Acetylsalicylsyra", 10),
    Produkt("Antihistaminer", 2),
    Produkt("Laktosintoleransmedel", 4),
    Produkt("Antacida", 48),
]
lista4 = [ Produkt("Aloe Vera-gel", 100) ]

olist = [
    Order(lista1, "Magistratsvägen 1", "1"),
    Order(lista2, "Nationsgatan 1", "2"),
    Order(lista3, "Tunavägen 5", "3"),
    Order(lista4, "Södra Esplanaden 10", "4"),
    Order(lista1, "Södra Esplanaden 1", "5")
]
test_obj = Test(olist)

def check_available_drones():
    for key in redis_server.keys("drone:*"):
        if key == "drone:queue":
            continue
        if redis_server.type(key) != 'hash':
            continue
        if redis_server.hget(key, 'status') == 'idle':
            return True
    return False

@app.route('/', methods=['GET'])
def home():
    try:
        weather = get_current_weather("Lund", WEATHER_API_KEY)
    except Exception as e:
        app.logger.error(f"Weather fetch failed: {e}")
        weather = {
            "description": "Unavailable",
            "temp_c": "--",
            "wind_kph": "--",
            "is_raining": False
        }

    return render_template('home.html', weather=weather)

@app.route('/map', methods=['GET'])
def map():
    return render_template('index.html')

@app.route('/qr', methods=['GET'])
def qr_scanner():
    return render_template('qrcode.html')

@app.route('/verify_order', methods=['POST'])
def verify_order():
    order_number = request.form.get('order-number')
    order = test_obj.getOrder(order_number)
    if not order:
        return jsonify({'error': 'Ordernummer finns inte.'}), 400

    from_addr = "Sölvegatan 14"
    to_addr   = order.getAdress()
    total_weight = order.getTotWeight()
    products = [p.namn for p in order.lists]
    product_json = base64.urlsafe_b64encode(json.dumps(products).encode()).decode()

    available = check_available_drones()
    order_status = "levereras" if available else "i kö"

    try:
        resp = requests.post(
            "http://localhost:5002/planner",
            json={
                "faddr": from_addr,
                "taddr": to_addr,
                "order_number": order_number
            },
            timeout=3
        )
        app.logger.info(f"Planner response: {resp.text}")
    except Exception as e:
        app.logger.error(f"Planner error: {e}")

    return redirect(url_for(
        'map',
        ordernumber=order_number,
        address=to_addr,
        weight=total_weight,
        products=product_json,
        status=order_status
    ))

@app.route('/get_drones', methods=['GET'])
def get_drones():
    drone_dict = {}
    for key in redis_server.keys("drone:*"):
        drone_id = key.split(":", 1)[1]
        data = redis_server.hgetall(key)
        if not data:
            continue
        try:
            lon = float(data.get('longitude', 0))
            lat = float(data.get('latitude', 0))
            status = data.get('status', 'unknown')
            x_svg, y_svg = translate((lon, lat))
            drone_dict[drone_id] = {
                'longitude': x_svg,
                'latitude': y_svg,
                'status': status
            }
        except Exception:
            continue
    return jsonify(drone_dict)

@app.route('/order_status/<order_number>', methods=['GET'])
def get_order_status(order_number):
    status = redis_server.hget(order_number, 'status') or 'okänd'
    return jsonify({'status': status})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
