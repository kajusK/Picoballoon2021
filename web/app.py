import pathlib
import secrets
from datetime import datetime
from flask import Flask, request, current_app, Response, render_template
from db import Database
from collections import defaultdict

app = Flask(__name__)

def pretty_format(value, digits=None, suffix=None, divisor=None):
    if value == 'None':
        return 'missing'
    else:
        if divisor:
            value = value / divisor
        value = round(value, digits)
        if not suffix:
            return value
        else:
            return f'{value} {suffix}'


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
        if lat != 'missing' and lon != 'missing':   # marker must be localizable
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
    for row in data_all:
        time, pressure, temp, alt, lat, lon, battery, lat_gw, lon_gw, alt_gw = row
        if alt == 'missing':
            alt = alt_gw
        if lat == 'missing':
            lat = lat_gw
        if lon == 'missing':
            lon = lon_gw
        data_table.append([time, pressure, temp, alt, lat, lon, battery])
    return data_table


def provide_data_graph():
    data_all = provide_data()
    data_temp_time = []
    data_temp = []
    data_alt_time = []
    data_alt = []
    for row in data_all:
        time, pressure, temp, alt, lat, lon, battery, lat_gw, lon_gw, alt_gw = row
        # remove suffixes! and to float
        if temp != 'missing':
            temp = float(temp.split()[0])
            data_temp_time.append(time)
            data_temp.append(temp)
        if alt != 'missing':
            alt = float(alt.split()[0])
            data_alt_time.append(time)
            data_alt.append(alt)
    return (data_temp_time, data_temp, data_alt_time, data_alt)


def provide_data():
    '''
    Provide data (a list of lists), specifically:
        - Time (day.month. hour:minutes)
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
    If altitude is None, calculate it from pressure.
    '''
    data_raw = Database.get_db(app.config['DATABASE_PATH']).fetch_all_data()
    data = []
    for row in data_raw:
        timestamp, pressure, temp, core_temp, alt, lat, lon, bat_mv, loop_time, lat_gw, lon_gw, alt_gw = row[:-3]
        # invalid / missing input handling
        if alt == 'None' and pressure != 'None':    # missing altitude value, calculation from pressure
            alt = round((145366.45 * (1 - pow(pressure / 101325, 0.190284))) / 3.2808)
        if temp != 'None' and core_temp != 'None':
            # use temperature of core for nonsense temperatures values
            if temp in range(-100, 50):
                pass
            elif temp not in range(-100, 50) and core_temp in range(-100, 50):
                temp = core_temp
            else:   # cannot use temperature of core, discard value
                temp = 'None'
        # pretty formatting
        time = datetime.fromtimestamp(timestamp).strftime("%d.%m. %H:%M")
        pressure = pretty_format(pressure, digits=2, suffix='HPa', divisor=100)
        temp = pretty_format(temp, digits=1, suffix='°C')
        alt = pretty_format(alt, digits=0, suffix='m')
        lat = pretty_format(lat, digits=3)
        lon = pretty_format(lon, digits=3)
        battery = pretty_format(bat_mv, digits=3, suffix='V', divisor=1000)
        lat_gw = pretty_format(lat_gw, digits=3)
        lon_gw = pretty_format(lon_gw, digits=3)
        alt_gw = pretty_format(alt_gw, digits=0, suffix='m')
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
    data_temp_time, data_temp, data_alt_time, data_alt = provide_data_graph()
    return render_template('index.html',
                           data_markers=data_markers,
                           data_table=data_table,
                           data_temp_time=data_temp_time,
                           data_temp=data_temp,
                           data_alt_time=data_alt_time,
                           data_alt=data_alt
                           )


@app.route('/endpoint', methods=['POST'])
def endpoint():
    '''
    Save incoming data to a text file (with timestamp as a name)
    If data are dictionary, insert them into database, pass them as a default dictionary (+ add current timestamp)
    If everything goes smooth, return response status 200 (OK), else return 403 (Forbidden)
    '''
    # authorization header
    header = request.headers.get('Authorization')
    with open('token.txt') as f:
        token = f.read()
    if type(header) == str:
        if secrets.compare_digest(header, token):
            # obtain data
            raw_data = request.get_json(force=True)
            # save data externally
            timestamp = datetime.timestamp(datetime.now())
            with open(f'''{app.config['DATABASE_PATH']}/cloud_data/{timestamp}.txt''', 'w') as new_file:
                print(raw_data, file=new_file)
            # pass data to database (as default dictionary)
            if type(raw_data) == dict:
                received_data = defaultdict(lambda: None)
                received_data.update(raw_data)
                received_data['timestamp'] = timestamp      # add current timestamp
                Database.get_db(app.config['DATABASE_PATH']).prepare_data(received_data)
                # everything goes fine = return 200
                status_code = Response(status=200)
            else:
                # wrong data format
                status_code = Response(status=403)
        else:
            # wrong token
            status_code = Response(status=403)
    else:
        # missing header
        status_code = Response(status=403)
    return status_code


if __name__ == '__main__':
    app.config['DATABASE_PATH'] = str(pathlib.Path().resolve())
    app.run(debug=False)
