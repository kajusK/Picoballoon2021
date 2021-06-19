# To do list:
    # create sqlite database ✓
    # store data from cloud in database ✓
        # adjust format to correspond actual data ✓
        # estimate altitude from pressure ✓ --> need to be checked
    # write tests ✓
    # fill in Readme.md
    # display web content to user
        # related to map
            # display map ✓
            # send data to marker ✓
            # add multiple markers ✓
            # add trajectory ✓
            # adjust size according to balloon route ✓
        # display picture ✓ --> old one!
        # display summary table ✓
        # display graphs of temperature and altitude in time x
        # display basic info ✓ --> lorem for now
        # make index.html responsive ✓
        # make index.html pretty ✓
    # if there are no data from gps, use lat, lon, alt from gateway

import pathlib
from datetime import datetime
from flask import Flask, request, current_app, Response, render_template
from db import Database
from collections import defaultdict
from datetime import datetime

app = Flask(__name__)


def provide_data_markers():
    '''
    Provide data (a list of lists) to markers and their cards, specifically:
        - marker_id = number of a database entry (starting from 0)
        - time
        - card_body = information about temperature, battery, altitude, longitude and latitude
        - longitude, latitude
    '''
    data_all = provide_data()
    data_markers = []
    for i, entry in enumerate(data_all):
        time, pressure, temp, alt, lat, lon, battery = entry
        marker_id = i
        card_body = f'temperature: {temp}, probe battery: {battery}, altitude: {alt}, longitude: {lon}, latitude: {lat}'
        data_markers.append([marker_id, time, card_body, lon, lat])
    return data_markers


def provide_data():
    '''
    Provide data (a list of lists) (eg. for a summary table), specifically:
        - Time (day.month.year hour:minutes)
        - Pressure (HPa)
        - Temperature
        - Altitude (m)
        - Latitude
        - Longitude
        - Battery (V)
    If outside temperature seems to be invalid, use temperature of core.
    '''
    data_raw = current_app.db.fetch_all_data()
    data = []
    for entry in data_raw:
        timestamp, pressure, temp, core_temp, alt, lat, lon, battery_mv = entry[:8]
        time = datetime.fromtimestamp(timestamp).strftime("%d.%m.%Y %H:%M")
        pressure = '{:.2f} HPa'.format(pressure / 100)
        if temp < -100 or temp > 50 or temp == 0:      # if temperature is nonsense, use temperature of core
            temp = '{:.1f} °C'.format(core_temp)
        else:
            temp = '{:.1f} °C'.format(temp)
        if alt == 0:    # invalid input, calculate altitude from pressure
            alt = round((145366.45 * (1 - pow(pressure / 101325, 0.190284))) / 3.2808)
        alt = '{:.0f} m'.format(alt)
        lat = '{:.3f}'.format(lat)
        lon = '{:.3f}'.format(lon)
        battery = '{:.3f} V'.format(battery_mv / 1000)
        data.append([time, pressure, temp, alt, lat, lon, battery])
    return data


@app.route('/', methods=['GET'])
def index():
    '''
    For index page provide data for:
        - a summary table
        - markers and their cards
        - graphs of development of temperature and altitude
    '''
    data_table = provide_data()
    data_markers = provide_data_markers()
    return render_template('index.html',
                           data_markers=data_markers,
                           data_table=data_table)


@app.route('/endpoint', methods=['POST'])
def endpoint():
    '''Insert incoming data into database'''
    raw_data = request.get_json(force=True)
    received_data = defaultdict(lambda: None)
    received_data.update(raw_data)
    received_data['timestamp'] = datetime.timestamp(datetime.now())
    current_app.db.prepare_data(received_data)
    status_code = Response(status=200)
    return status_code


if __name__ == '__main__':
    path = str(pathlib.Path().resolve())
    with app.app_context():                 # management of the application context
        current_app.db = Database(path)     # proxy to the application handling the current request
    app.run(debug=True)
