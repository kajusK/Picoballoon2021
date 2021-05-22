import pytest
import os


@pytest.fixture(scope="session")
def db(tmp_path):                       # temporary path
    from db import Database
    db = Database(tmp_path)
    db.create_database_structure()
    yield db


@pytest.fixture(scope="session")
def app(db):
    from flask import current_app
    from app import app
    with app.app_context():
        current_app.db = db
    return app


@pytest.fixture(scope="session")
def client(app):
    with app.test_client() as client:
        yield client


def test_database_creation(db):
    '''
    If there is no file "database.sqlite" in current directory,
    function database_status() creates one
    '''
    from app import database_status
    database_status(db)
    assert os.path.exists('database.sqlite')
    os.remove('database.sqlite')


def test_db_private_attributes(db):
    '''Database attributes aren't accesible outside class'''
    with pytest.raises(AttributeError):
        assert db.__cursor
    with pytest.raises(AttributeError):
        assert db.__connection


def test_endpoint_returns_200(client):
    response = client.post('/endpoint', json={
        'timestamp': 12092021,
        'freq': 99.5,
        'rssi': 4,
        'estimated_lat': 49.195061,
        'estimated_lon': 16.606836,
        'pressure_pa': 101,
        'temp_c': 20.5,
        'core_temp_c': 15.5,
        'alt_m': 1000,
        'lat': 49.195061,
        'lon': 16.606836,
        'battery_mv': 30,
        'loop_time_s': 70000,
        'gps_fix': 1,
        'json': 'all data here'
    })
    assert response.status_code == 200
