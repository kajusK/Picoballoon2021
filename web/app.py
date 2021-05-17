# To do list:
    # create sqlite database ✓
    # store data from cloud in database ✓
        # estimate longitude and latitude
    # write tests
    # fill in Readme.md
    # display web content to user
        # add information points in map

from flask import Flask, request
import os
from db import Database

app = Flask(__name__)
db = Database()


def database_status():
    if not os.path.exists('database.sqlite'):
        db.create_database_structure()


@app.route('/endpoint', methods=['POST'])
def endpoint():
    '''Insert incoming data into database'''
    data = request.get_json(force=True)
    db.store_data(data)


database_status()