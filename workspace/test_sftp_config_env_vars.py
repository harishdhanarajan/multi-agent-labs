import os
from sftp_config import SFTPConfig

def test_sftp_config_env_vars():
    # Set environment variables
    os.environ['SFTP_HOST'] = 'test_host'
    os.environ['SFTP_PORT'] = '2222'
    os.environ['SFTP_USERNAME'] = 'test_username'
    os.environ['SFTP_PASSWORD'] = 'test_password'
    os.environ['SFTP_KEY_PATH'] = 'test_key_path'

    sftp_config = SFTPConfig()
    config = sftp_config.get_config()

    assert config['host'] == 'test_host'
    assert config['port'] == 2222
    assert config['username'] == 'test_username'
    assert config['password'] == 'test_password'
    assert config['key_path'] == 'test_key_path'
