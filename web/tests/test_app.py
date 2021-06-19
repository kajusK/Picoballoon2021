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
        current_app.db = db     # replace current_app db with temporary db
    return app


@pytest.fixture
def client(app):
    with app.test_client() as client:       # test client
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
    "app_id": "picoballoon2021",
    "dev_id": "probe",
    "hardware_serial": "00EF30A4C3C5F12F",
    "port": 1,
    "counter": 18,
    "payload_raw": "vCYoASS5AQAAAAAAAAAAAAAA",
    "payload_fields": {
        "alt_m": 0,
        "bat_mv": 441,
        "core_temp_c": 36,
        "lat": 0,
        "lon": 0,
        "loop_time_s": 0,
        "pressure_pa": 99160,
        "temp_c": 29.6
        },
    "metadata": {
        "time": "2021-06-17T19:20:32.358785168Z",
        "frequency": 867.9,
        "modulation": "LORA",
        "data_rate": "SF10BW125",
        "coding_rate": "4/5",
        "gateways": [
            {
            "gtw_id": "eui-b827ebfffe114baa",
            "timestamp": 2703562732,
            "time": "2021-06-17T19:20:32.342551Z",
            "channel": 7,
            "rssi": -120,
            "snr": -14.8,
            "rf_chain": 0,
            "latitude": 0,
            "longitude": 0,
            "altitude": 0
            },
            {},
            {},
            {}
            ],
        "latitude": 52.2345,
        "longitude": 6.2345,
        "altitude": 2
        },
    "downlink_url": "https://integrations.thethingsnetwork.org/…Kq8"
    })
    assert response.status_code == 200


def test_endpoint_stores_data(client, db):
    '''Endpoint inserts received data into database'''
    client.post('/endpoint', json={
    "app_id": "picoballoon2021",
    "dev_id": "probe",
    "hardware_serial": "00EF30A4C3C5F12F",
    "port": 1,
    "counter": 18,
    "payload_raw": "vCYoASS5AQAAAAAAAAAAAAAA",
    "payload_fields": {
        "alt_m": 0,
        "bat_mv": 441,
        "core_temp_c": 36,
        "lat": 0,
        "lon": 0,
        "loop_time_s": 0,
        "pressure_pa": 99160,
        "temp_c": 29.6
        },
    "metadata": {
        "time": "2021-06-17T19:20:32.358785168Z",
        "frequency": 867.9,
        "modulation": "LORA",
        "data_rate": "SF10BW125",
        "coding_rate": "4/5",
        "gateways": [
            {
            "gtw_id": "eui-b827ebfffe114baa",
            "timestamp": 2703562732,
            "time": "2021-06-17T19:20:32.342551Z",
            "channel": 7,
            "rssi": -120,
            "snr": -14.8,
            "rf_chain": 0,
            "latitude": 0,
            "longitude": 0,
            "altitude": 0,
            },
            {},
            {},
            {},
            ],
        "latitude": 52.2345,
        "longitude": 6.2345,
        "altitude": 2
        },
    "downlink_url": "https://integrations.thethingsnetwork.org/…Kq8"
    })
    for data_row in db.fetch_all_data():
        assert len(data_row) == 13

def test_endpoint_no_gps(client, db):
    '''Endpoint inserts received data into database'''
    response = client.post('/endpoint', json={
    "app_id": "picoballoon2021",
    "dev_id": "probe",
    "hardware_serial": "00EF30A4C3C5F12F",
    "port": 1,
    "counter": 18,
    "payload_raw": "vCYoASS5AQAAAAAAAAAAAAAA",
    "payload_fields": {},
    "metadata": {
        "time": "2021-06-17T19:20:32.358785168Z",
        "frequency": 867.9,
        "modulation": "LORA",
        "data_rate": "SF10BW125",
        "coding_rate": "4/5",
        "gateways": [
            {
            "gtw_id": "eui-b827ebfffe114baa",
            "timestamp": 2703562732,
            "time": "2021-06-17T19:20:32.342551Z",
            "channel": 7,
            "rssi": -120,
            "snr": -14.8,
            "rf_chain": 0,
            "latitude": 0,
            "longitude": 0,
            "altitude": 0
            },
            {},
            {},
            {}
            ],
        "latitude": 52.2345,
        "longitude": 6.2345,
        "altitude": 2
        },
    "downlink_url": "https://integrations.thethingsnetwork.org/…Kq8"
    })
    assert response.status_code == 200

def test_endpoint_missing_device_info(client, db):
    '''Endpoint inserts received data into database'''
    response = client.post('/endpoint', json={
    "app_id": "picoballoon2021",
    "dev_id": "probe",
    "hardware_serial": "00EF30A4C3C5F12F",
    "port": 1,
    "counter": 18,
    "payload_raw": "vCYoASS5AQAAAAAAAAAAAAAA",
    "payload_fields": {},
    "metadata": {
        "time": "2021-06-17T19:20:32.358785168Z",
        "frequency": 867.9,
        "modulation": "LORA",
        "data_rate": "SF10BW125",
        "coding_rate": "4/5",
        "gateways": [
            {
            "gtw_id": "eui-b827ebfffe114baa",
            "timestamp": 2703562732,
            "time": "2021-06-17T19:20:32.342551Z",
            "channel": 7,
            "rssi": -120,
            "snr": -14.8,
            "rf_chain": 0,
            "latitude": 0,
            "longitude": 0,
            "altitude": 0
            },
            {},
            {},
            {}
            ]
        },
    "downlink_url": "https://integrations.thethingsnetwork.org/…Kq8"
    })
    assert response.status_code == 200


def test_endpoint_no_gw(client, db):
    '''Endpoint inserts received data into database'''
    response = client.post('/endpoint', json={
    "app_id": "picoballoon2021",
    "dev_id": "probe",
    "hardware_serial": "00EF30A4C3C5F12F",
    "port": 1,
    "counter": 18,
    "payload_raw": "vCYoASS5AQAAAAAAAAAAAAAA",
    "payload_fields": {},
    "metadata": {
        "time": "2021-06-17T19:20:32.358785168Z",
        "frequency": 867.9,
        "modulation": "LORA",
        "data_rate": "SF10BW125",
        "coding_rate": "4/5",
        "gateways": []
        },
    "downlink_url": "https://integrations.thethingsnetwork.org/…Kq8"
    })
    assert response.status_code == 200

def test_endpoint_return_data(client, db):
    '''Endpoint inserts received data into database'''
    client.post('/endpoint', json={
    "app_id": "picoballoon2021",
    "dev_id": "probe",
    "hardware_serial": "00EF30A4C3C5F12F",
    "port": 1,
    "counter": 18,
    "payload_raw": "vCYoASS5AQAAAAAAAAAAAAAA",
    "payload_fields": {
        "alt_m": 0,
        "bat_mv": 441,
        "core_temp_c": 36,
        "lat": 0,
        "lon": 0,
        "loop_time_s": 0,
        "pressure_pa": 99160,
        "temp_c": 29.6
        },
    "metadata": {
        "time": "2021-06-17T19:20:32.358785168Z",
        "frequency": 867.9,
        "modulation": "LORA",
        "data_rate": "SF10BW125",
        "coding_rate": "4/5",
        "gateways": [
            {
            "gtw_id": "eui-b827ebfffe114baa",
            "timestamp": 2703562732,
            "time": "2021-06-17T19:20:32.342551Z",
            "channel": 7,
            "rssi": -120,
            "snr": -14.8,
            "rf_chain": 0,
            "latitude": 0,
            "longitude": 0,
            "altitude": 0
            },
            {},
            {},
            {}
            ],
        "latitude": 52.2345,
        "longitude": 6.2345,
        "altitude": 2
        },
    "downlink_url": "https://integrations.thethingsnetwork.org/…Kq8"
    })
    for data_row in db.fetch_all_data():
        assert len(data_row) == 13