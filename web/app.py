# To do list:
    # create sqlite database ✓
    # store data from cloud in database ✓
        # estimate longitude and latitude
    # write tests
    # fill in Readme.md
    # display web content to user
        # add information points in map

import os
import pathlib
from flask import Flask, request
from db import Database

app = Flask(__name__)

def database_status(db):
    if not os.path.exists('database.sqlite'):
        db.create_database_structure()


@app.route('/endpoint', methods=['POST'])
def endpoint():
    '''Insert incoming data into database'''
    data = request.get_json(force=True)
    db.store_data(data)
    return 200


if __name__ == '__main__':
    path = str(pathlib.Path().absolute())
    db = Database(path)
    database_status(db)
    app.run(debug=True)