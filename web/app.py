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
        # display summary table ✓ ---> fixed size ✓
        # display graphs of temperature and altitude in time x
        # display basic info ✓ --> lorem for now
        # make index.html responsive ✓
        # make index.html pretty ✓
    # if there are no data from gps, use lat, lon, alt from gateway ✓
    # add security check into database

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
    data_all = provide_data_table()
    data_markers = []
    for i, entry in enumerate(data_all):
        time, pressure, temp, alt, lat, lon, battery = entry
        if temp == 'None':
            temp = 'missing'
        if battery == 'None':
            battery = 'missing'
        if alt == 'None':
            alt = 'missing'
        if lon == 'None':
            lon = 'missing'
        if lat == 'None':
            lat = 'missing'
        marker_id = i
        card_body = f'temperature: {temp}, probe battery: {battery}, altitude: {alt}, longitude: {lon}, latitude: {lat}'
        data_markers.append([marker_id, time, card_body, lon, lat])
    return data_markers


def provide_data_table():
    '''
    Provide data for a summary table:
        - Time
        - Pressure
        - Temperature
        - Altitude
        - Latitude
        - Longitude
        - Battery
    If there are missing data from GPS use data from gateways
    '''
    data_all = provide_data()
    data_table = []
    for entry in data_all:
        time, pressure, temp, alt, lat, lon, battery, lat_gw, lon_gw, alt_gw = entry
        if alt in ['None', 0]:
            alt = alt_gw
        if lat in ['None', 0]:
            lat = lat_gw
        if lon in ['None', 0]:
            lon = lon_gw
        data_table.append([time, pressure, temp, alt, lat, lon, battery])
    return data_table


def provide_data():
    '''
    Provide data (a list of lists), specifically:
        - Time (day.month.year hour:minutes)
        - Pressure (HPa)
        - Temperature
        - Altitude (m)
        - Latitude
        - Longitude
        - Battery (V)
        - Latitude from gateway
        - Longitude from gateway
        - Altitude (m) from gateway
    If outside temperature seems to be invalid, use temperature of core.
    If altitude is None or 0, calculate it from pressure.
    '''
    data_raw = current_app.db.fetch_all_data()
    data = []
    for entry in data_raw:
        timestamp, pressure, temp, core_temp, alt, lat, lon, bat_mv, loop_time, lat_gw, lon_gw, alt_gw = entry[:-1]
        time = datetime.fromtimestamp(timestamp).strftime("%d.%m.%Y %H:%M")
        if alt == 0 or alt == 'None':    # invalid input, calculate altitude from pressure
            if pressure != 'None':
                alt = round((145366.45 * (1 - pow(pressure / 101325, 0.190284))) / 3.2808)
        if pressure != 'None':
            pressure = '{:.2f} HPa'.format(pressure / 100)
        if temp != 'None':
            if temp < -100 or temp > 50 or temp == 0:      # if temperature is nonsense, use temperature of core
                temp = '{:.1f} °C'.format(core_temp)
            else:
                temp = '{:.1f} °C'.format(temp)
        if alt != 'None':
            alt = '{:.0f} m'.format(alt)
        if lat != 'None':
            lat = '{:.3f}'.format(lat)
        if lon != 'None':
            lon = '{:.3f}'.format(lon)
        if bat_mv != 'None':
            battery = '{:.3f} V'.format(bat_mv / 1000)
        if lat_gw != 'None':
            lat_gw = '{:.3f}'.format(lat_gw)
        if lon_gw != 'None':
            lon_gw = '{:.3f}'.format(lon_gw)
        if alt_gw != 'None':
            alt_gw = '{:.0f} m'.format(alt_gw)
        data.append([time, pressure, temp, alt, lat, lon, battery, lat_gw, lon_gw, alt_gw])
    return data


@app.route('/', methods=['GET'])
def index():
    '''
    For index page provide data for:
        - a summary table
        - markers and their cards
        - graphs of development of temperature and altitude
    '''
    data_table = provide_data_table()
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
    app.run(debug=True)                     # must be disabled!
