# InfoCom Drone Project - Part 5 – Multi-drone System

This project simulates a multi-drone medicine delivery system for the city of Lund using Flask, Redis, and Python. Each drone communicates with the server and follows route plans, which are adjusted based on weather conditions.

---

## Required Installations for Windows

You have to install the following packages for the program to work. 


```bash
sudo apt update
sudo apt install redis-server
sudo apt install python3-pip
sudo apt install python3-socketio
sudo apt install python3-engineio
sudo apt install python3-flask-socketio
sudo apt install python3-flask-cors
sudo apt install python3-geopy

pip3 install -r requirements.txt

```
## Required Installations for Mac 

You have to install the following packages for the program to work.

```bash
Need the user to have homebrew installed
brew install redis
brew services start redis
pip3 install redis
pip3 install python-socketio
pip3 install python-engineio
pip3 install flask-socketio
pip3 install flask-cors
pip3 install geopy
pip3 install python-dotenv

pip3 install -r requirements.txt
```
For this program to work you must provide a weather API key from https://www.weatherapi.com

when you go to the webserver /webserver you have to create a .env file
```bash
pip3 install python-dotenv ## You have to downlaod dotenv for this to work!
cd webserver
touch .env
```
Add your key to the file:
```bash
WEATHER_API_KEY=your_api_key_here
```

## On the Server Pi:
Go to `/webserver`, start your Redis server (if it is not already running, which it probably is – test using `redis-cli`) and run the three flask servers that make up the server side of the drone application:

1. Run the server for writing data to the redis server
    ```
    export FLASK_APP=database.py
    export FLASK_DEBUG=1
    python3 -m flask run --port=5001 --host=0.0.0.0
    ```

2. Start up the drones

Open up 4 terminals and go to `/pi`, run the following commands for each terminal window
```
    python3 drone.py --id DRONE1 --port 5004 for the first drone 
    python3 drone.py --id DRONE2 --port 5005 for the second drone
    python3 drone.py --id DRONE3 --port 5006 for the third drone 
    python3 drone.py --id DRONE4 --port 5007 for the fourth drone 
```
3. Open a new terminal, go to `/webserver`, and run the route planner
    ```
    export FLASK_APP=route_planner.py
    export FLASK_DEBUG=1
    python3 -m flask run --port=5002 --host=0.0.0.0
    ```

4. Open a new terminal, go to `/webserver`,  and run the website server
    ```
    export FLASK_APP=build.py
    export FLASK_DEBUG=1
    python3 -m flask run --port=5000 --host=0.0.0.0    
    ```

5.  Open a web browser (e.g. Chromium) on your Raspberry Pi and enter the following URL. You should see a map of Lund as in the previous assignment. Make sure you see two red dots on top of each other representing the drone at the LTH location.

    ```
    http://localhost:5000
    ```

Note: Don't use `python3 build.py`, `python3 route_planner.py`, `python3 database.py` or `python3 drone.py` to run the webservers, since this does not provide all the functionality required by the application.

