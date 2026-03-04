import os
from sftp_config import SFTPConfig

def test_sftp_config_defaults():
    # Clear environment variables
    os.environ.pop('SFTP_HOST', None)
    os.environ.pop('SFTP_PORT', None)
    os.environ.pop('SFTP_USERNAME', None)
    os.environ.pop('SFTP_PASSWORD', None)
    os.environ.pop('SFTP_KEY_PATH', None)

    sftp_config = SFTPConfig()
    config = sftp_config.get_config()

    assert config['host'] == 'localhost'
    assert config['port'] == 22
    assert config['username'] == ''
    assert config['password'] == ''
    assert config['key_path'] == ''
