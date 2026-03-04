import pytest
from unittest import mock
import mysql.connector  # Import the mysql.connector to define 'mysql'
from utils import get_mysql_connection

def test_get_mysql_connection():
    # Successful connection test (already implemented in your tests)
    pass

@mock.patch('utils.mysql.connector.connect')
def test_get_mysql_connection_error(mock_connect):
    # Simulate a connection error
    mock_connect.side_effect = mysql.connector.Error("Connection error")
    
    connection = get_mysql_connection()
    assert connection is None
