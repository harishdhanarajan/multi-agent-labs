import os
import subprocess
import pytest

def test_mysql_connector_installed():
    """Test if mysql-connector-python is installed."""
    try:
        import mysql.connector
    except ImportError:
        pytest.fail("mysql-connector-python is not installed.")

def test_requirements_txt_exists():
    """Test if requirements.txt exists in the workspace directory."""
    assert os.path.exists('workspace/requirements.txt'), "requirements.txt does not exist."

def test_requirements_include_mysql_connector():
    """Test if requirements.txt includes mysql-connector-python."""
    with open('workspace/requirements.txt', 'r') as f:
        requirements = f.read()
    assert 'mysql-connector-python' in requirements, "mysql-connector-python is not listed in requirements.txt."
