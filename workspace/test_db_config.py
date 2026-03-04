import os
import pytest
from db_config import DatabaseConfig

@pytest.fixture(autouse=True)
def reset_env():
    # Store original environment variables
    original_env = {key: os.getenv(key) for key in ['DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']}
    yield
    # Restore original environment variables
    for key, value in original_env.items():
        if value is not None:
            os.environ[key] = value
        else:
            os.environ.pop(key, None)

def test_default_config():
    db_config = DatabaseConfig()
    config = db_config.get_config()
    
    assert config['host'] == 'localhost'
    assert config['port'] == '3306'
    assert config['user'] == 'root'
    assert config['password'] == ''
    assert config['database'] == 'test_db'

def test_custom_env_variables():
    os.environ['DB_HOST'] = '127.0.0.1'
    os.environ['DB_PORT'] = '5432'
    os.environ['DB_USER'] = 'admin'
    os.environ['DB_PASSWORD'] = 'secret'
    os.environ['DB_NAME'] = 'production_db'
    
    db_config = DatabaseConfig()
    config = db_config.get_config()

    assert config['host'] == '127.0.0.1'
    assert config['port'] == '5432'
    assert config['user'] == 'admin'
    assert config['password'] == 'secret'
    assert config['database'] == 'production_db'
