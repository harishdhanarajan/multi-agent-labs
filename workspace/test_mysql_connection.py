import pytest
from unittest import mock
import mysql.connector
from utils import get_mysql_connection

@mock.patch('utils.mysql.connector.connect')
def test_successful_mysql_connection(mock_connect):
    """
    Test case for successful MySQL connection.
    """
    mock_connection = mock.Mock()
    mock_connect.return_value = mock_connection

    connection = get_mysql_connection()
    assert connection is not None
    assert connection == mock_connection
    print("Test for successful MySQL connection passed.")


@mock.patch('utils.mysql.connector.connect')
def test_mysql_connection_error(mock_connect):
    """
    Test case for MySQL connection error.
    """
    mock_connect.side_effect = mysql.connector.Error("Connection error")

    connection = get_mysql_connection()
    assert connection is None
    print("Test for MySQL connection error passed.")

