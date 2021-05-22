import pytest


@pytest.fixture
def db(tmp_path):                       # create temporary database instance
    print(tmp_path)
    from db import Database
    db = Database(tmp_path)
    db.create_database_structure()
    yield db


@pytest.fixture
def app(db):
    from flask import current_app
    from app import app
    with app.app_context():
        current_app.db = db
    return app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


def test_db_private_attributes(db):
    '''Database attributes aren't accesible outside class'''
    with pytest.raises(AttributeError):
        assert db.__cursor
    with pytest.raises(AttributeError):
        assert db.__connection


def test_endpoint_returns_200(client):
    '''Endpoint receives data and return status_code 200'''
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


def test_endpoint_stores_data(client, db):
    '''Endpoint inserts received data into database'''
    client.post('/endpoint', json={
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
    for data_row in db.fetch_data():
        assert len(data_row) == 15