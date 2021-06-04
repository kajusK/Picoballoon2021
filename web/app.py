# To do list:
    # create sqlite database ✓
    # store data from cloud in database ✓
        # estimate longitude and latitude
        # adjust format to correspond actual data
    # write tests ✓
    # fill in Readme.md
    # display web content to user
        # related to map
            # display map ✓
            # send data to marker ✓
            # add multiple markers ✓
            # add trajectory
        # display picture ✓
        # display basic info

import pathlib
from datetime import datetime
from flask import Flask, request, current_app, Response, render_template
from db import Database

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    '''
    Send data to markers and their cards, specifically:
        - marker_id = number of a database entry (starting from 0)
        - longitude, latitude
        - time
        - card_body = information about temperature, battery, altitude, longitude and latitude
    '''
    data = current_app.db.fetch_data_for_markers()
    data_for_markers = []
    for i, data in enumerate(data):
        timestamp, temp_c, battery_mv, alt_m, lon, lat = data
        marker_id = i
        time = datetime.fromtimestamp(timestamp).strftime("%H:%M on %b %d.")
        card_body = f'- - - - - - - - - - - - - - - - - => temperature: {round(temp_c, 1)}°C => probe battery: {round(battery_mv, 0)} mV => altitude: {round(alt_m, 0)} metres => longitude: {round(lon, 5)} => latitude: {round(lat, 5)}'
        data_for_markers.append([marker_id, time, card_body, lon, lat])
    return render_template('index.html', data_for_markers=data_for_markers)


@app.route('/endpoint', methods=['POST'])
def endpoint():
    '''Insert incoming data into database'''
    data = request.get_json(force=True)
    current_app.db.store_data(data)
    status_code = Response(status=200)
    return status_code


if __name__ == '__main__':
    path = str(pathlib.Path().resolve())
    with app.app_context():                 # management of the application context
        current_app.db = Database(path)     # proxy to the application handling the current request
    app.run(debug=True)
