import pytest
import os
from app import database_status, endpoint
from db import Database

db = Database()

def test_database_created():
    database_status()
    assert not os.path.exists('/../database.sqlite')


@pytest.mark.parametrize('attribute', ['__cursor', '__connection'])
def test_db_private_attributes(attribute):
    with pytest.raises(AttributeError):
        assert db.attribute


# To do:
    # endpoint can receive data
    # endpoint is able to insert data into database
