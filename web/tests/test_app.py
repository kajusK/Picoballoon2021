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
    response = client.post('/endpoint', headers= {'Authorization': '1234'}, json={
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


def test_endpoint_passes_data(client, db):
    '''Endpoint passes received data to database'''
    response = client.post('/endpoint', headers= {'Authorization': '1234'}, json={
    "payload_fields": {
        "alt_m": 1000,
        "bat_mv": 441,
        "core_temp_c": 36,
        "lat": 40.455,
        "lon": 10.12,
        "loop_time_s": 100,
        "pressure_pa": 99160,
        "temp_c": 29.6
        },
    "metadata": {
        "frequency": 867.9,
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
            }
            ],
        "latitude": 52.2345,
        "longitude": 6.2345,
        "altitude": 2
        }
    })
    for data_row in db.fetch_all_data():
        for value in data_row:
            assert value != 'None'
    assert response.status_code == 200

def test_endpoint_save_externally(client, db):
    '''Endpoint saves incoming json to a new file'''
    from datetime import datetime
    from os import path
    response = client.post('/endpoint', headers= {'Authorization': '1234'}, json={})
    last_input = db.fetch_all_data()
    timestamp = last_input[0][0]
    assert path.exists(f"cloud_data/{timestamp}.txt") is True
    assert response.status_code == 200


def test_database_no_gps(client, db):
    '''Database can handle missing gps data and save data from device instead (not from gateway)'''
    response = client.post('/endpoint', headers= {'Authorization': '1234'}, json={
    "payload_fields": {},
    "metadata": {
        "gateways": [
            {
            "rssi": -120,
            "latitude": 10.32,
            "longitude": 14.22,
            "altitude": 5000
            },
            {},
            {},
            {}
            ],
        "latitude": 52.2345,
        "longitude": 6.2345,
        "altitude": 200
        }
    })
    for data_row in db.fetch_all_data():
        lat_gw, lon_gw, alt_gw, freq, rssi = data_row[9:-1]
        assert [lat_gw, lon_gw, alt_gw] == [52.2345, 6.2345, 200]
    assert response.status_code == 200


def test_database_missing_device_info(client, db):
    '''Database can handle missing gps data and missing device info data and save data from gateway instead'''
    response = client.post('/endpoint', headers= {'Authorization': '1234'}, json={
    "payload_fields": {},
    "metadata": {
        "frequency": 700.9,
        "gateways": [
            {
            "gtw_id": "eui-b827ebfffe114baa",
            "timestamp": 2703562732,
            "time": "2021-06-17T19:20:32.342551Z",
            "channel": 7,
            "rssi": -100,
            "snr": -14.8,
            "rf_chain": 0,
            "latitude": 53.2312345254,
            "longitude": 42.1,
            "altitude": 100
            },
            {},
            {},
            {}
            ]
        }
    })
    for data_row in db.fetch_all_data():
        lat_gw, lon_gw, alt_gw, freq, rssi = data_row[9:-1]
        assert [lat_gw, lon_gw, alt_gw, freq, rssi] == [53.2312345254, 42.1, 100, 700.9, -100]
    assert response.status_code == 200


def test_database_no_gw(client, db):
    '''
    Database can handle missing gps data, missing device info and missing gateway data
    Only timestamp is present
    '''
    response = client.post('/endpoint', headers= {'Authorization': '1234'}, json={
    "payload_fields": {},
    "metadata": {
        "frequency": 0,
        "gateways": []
        },
    })
    for data_row in db.fetch_all_data():
        for value in data_row[1:1]:     # except timestamp and json
            assert value == 'None'
    assert response.status_code == 200


def test_database_no_data(client, db):
    '''Database can handle empty json'''
    response = client.post('/endpoint', headers= {'Authorization': '1234'}, json={})
    for data_row in db.fetch_all_data():
        for value in data_row[1:1]:     # except timestamp and json
            assert value == 'None'
    assert response.status_code == 200


def test_database_handle_0(client, db):
    '''Database can treat 0 values as missing (None)'''
    response = client.post('/endpoint', headers= {'Authorization': '1234'}, json={
    "payload_fields": {
        "alt_m": 0,
        "bat_mv": 0,
        "core_temp_c": 0,
        "lat": 0,
        "lon": 0,
        "loop_time_s": 0,
        "pressure_pa": 0,
        "temp_c": 0
        },
    "metadata": {
        "frequency": 0,
        "gateways": [
            {
            "rssi": 0,
            "rf_chain": 0,
            "latitude": 0,
            "longitude": 0,
            "altitude": 0
            }
            ],
        "latitude": 0,
        "longitude": 0,
        "altitude": 0
        }
    })
    for data_row in db.fetch_all_data():
        for value in data_row[1:-1]:  # except timestamp and json
            assert value == 'None'
    assert response.status_code == 200


def test_database_strongest_gw(client, db):
    '''Database will use gateway with strongest rssi'''
    response = client.post('/endpoint', headers= {'Authorization': '1234'}, json={
    "metadata": {
        "frequency": 867.9,
        "gateways": [
            {
            "rssi": -120,
            "latitude": 10.00,
            "longitude": 10.00,
            "altitude": 5000
            },
            {
            "rssi": 100,
            "latitude": 20.00,
            "longitude": 20.00,
            "altitude": 6000
            },
            {
            "rssi": 50,
            "latitude": 30.00,
            "longitude": 30.00,
            "altitude": 7000
            }
            ],
        }
    })
    for data_row in db.fetch_all_data():
        lat_gw, lon_gw, alt_gw, freq, rssi = data_row[9:-1]
        assert [lat_gw, lon_gw, alt_gw, freq, rssi] == [20.00, 20.00, 6000, 867.9, 100]
    assert response.status_code == 200


def test_database_strings_invalid(client, db):
    '''Database will treat strins as missing'''
    response = client.post('/endpoint', headers= {'Authorization': '1234'}, json={
    "payload_fields": {"loop_time_s": "heey"},
    "metadata": {
        "frequency": "hey",
        "gateways": [
            {
            "latitude": "hello",
            "longitude": "hi",
            }
            ],
        }
    })
    for data_row in db.fetch_all_data():
        _, _, _, _, _, _, _, _, loop_time, lat_gw, lon_gw, _, freq, rssi = data_row[:-1]
        assert [lat_gw, lon_gw, freq, loop_time] == ['None', 'None', 'None', 'None']
    assert response.status_code == 200
