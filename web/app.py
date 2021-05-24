# To do list:
    # create sqlite database ✓
    # store data from cloud in database ✓
        # estimate longitude and latitude
    # write tests ✓
    # fill in Readme.md
    # display web content to user
        # add information points in map

import os
import pathlib
from flask import Flask, request, current_app, Response, render_template
from db import Database

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/endpoint', methods=['POST'])
def endpoint():
    '''Insert incoming data into database'''
    data = request.get_json(force=True)
    current_app.db.store_data(data)
    status_code = Response(status=200)
    return status_code


if __name__ == '__main__':
    path = str(pathlib.Path().absolute())
    with app.app_context():                 # management of the application context
        current_app.db = Database(path)     # proxy to the application handling the current request
    app.run(debug=True)
