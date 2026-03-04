import pytest
from unittest.mock import patch
from app import main

def test_mysql_connection_success():
    with patch('utils.get_mysql_connection') as mock_get_connection:
        mock_get_connection.return_value.is_connected.return_value = True
        mock_get_connection.return_value.close.return_value = None
        main()
        mock_get_connection.assert_called_once()

def test_mysql_connection_failure():
    with patch('utils.get_mysql_connection') as mock_get_connection:
        mock_get_connection.return_value = None
        main()
        mock_get_connection.assert_called_once()
