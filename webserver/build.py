from os import fdopen
from flask import Flask, render_template, request
from flask.json import jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import time
import redis
import pickle
import json
from lager import Produkt
from lager import Order
from lager import Test
from flask import redirect, url_for

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = 'dljsaklqk24e21cjn!Ew@@dsa5'
socket = SocketIO(app, cors_allowed_origins="*")

# change this so that you can connect to your redis server
# ===============================================
redis_server = redis.Redis(host = "localhost", decode_responses=True, charset="unicode_escape", port =6379)
# ===============================================

# Translate OSM coordinate (longitude, latitude) to SVG coordinates (x,y).
# Input coords_osm is a tuple (longitude, latitude).
def translate(coords_osm):
    x_osm_lim = (13.143390664, 13.257501336)
    y_osm_lim = (55.678138854000004, 55.734680845999996)

    x_svg_lim = (212.155699, 968.644301)
    y_svg_lim = (103.68, 768.96)

    x_osm = coords_osm[0]
    y_osm = coords_osm[1]

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
lista4 = [
    Produkt("Aloe Vera-gel", 100) 
]

olist = [
    Order(lista1, "Magistratsvägen 1", "12345"),
    Order(lista2, "Agardsgatan 1", "654321"),
    Order(lista3, "Tunavägen 5", "109876"),
    Order(lista4, "Södra Esplanaden 10", "567453")
]

test_obj = Test(olist)
# Route for the home page where the user can enter order number
@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/map', methods=['GET'])
def map():
    return render_template('index.html')

# Route for handling order number verification
@app.route('/verify_order', methods=['POST'])
def verify_order():
    order_number = request.form.get('order-number')
    
    # Hämta ordern från Test-objektet
    order = test_obj.getOrder(order_number)
    
    if order:
        # Om ordern finns, skicka vidare till /map med ordernummer
        return redirect(url_for('map', ordernumber=order_number))
    else:
        # Om ordern inte finns, skicka tillbaka ett felmeddelande
        return jsonify({'error': 'Ordernummer finns inte.'}), 404

@socket.on('get location')
def get_location():
    while True:
        longitude = float(redis_server.get('longitude'))
        latitude = float(redis_server.get('latitude'))
        x_svg, y_svg = translate((longitude, latitude))
        emit('get_location', (x_svg, y_svg))
        time.sleep(0.01)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='5000')
