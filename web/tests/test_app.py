import pytest
import os
from app import database_status, endpoint
from db import Database


def test_database_creation():
    '''
    If there is no file "database.sqlite" in current directory,
    function database_status() creates one
    '''
    database_status()
    assert os.path.exists('database.sqlite')
    os.remove('database.sqlite')


@pytest.mark.parametrize('attribute', ['__cursor', '__connection'])
def test_db_private_attributes(attribute):
    '''Database attributes aren't accesible outside class'''
    db = Database()
    with pytest.raises(AttributeError):
        assert db.attribute

# To do:
    # endpoint can receive and insert data into database
