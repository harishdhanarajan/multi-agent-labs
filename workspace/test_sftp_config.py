import os
from sftp_config import SFTPConfig

def test_sftp_config_defaults():
    sftp_config = SFTPConfig()
    config = sftp_config.get_config()
    assert config['host'] == 'ftp.example.com'
    assert config['port'] == 22
    assert config['username'] == 'ftp_user'
    assert config['password'] == 'ftp_password'
    assert config['key_path'] == '/path/to/sftp/key'
    assert config['remote_dir'] == '/remote/path'
    assert config['local_dir'] == '/local/path'

def test_sftp_config_env_vars():
    os.environ['SFTP_HOST'] = 'custom_host'
    os.environ['SFTP_PORT'] = '2222'
    os.environ['SFTP_USERNAME'] = 'custom_user'
    os.environ['SFTP_PASSWORD'] = 'custom_password'
    os.environ['SFTP_KEY_PATH'] = '/custom/key/path'
    sftp_config = SFTPConfig()
    config = sftp_config.get_config()
    assert config['host'] == 'custom_host'
    assert config['port'] == 2222
    assert config['username'] == 'custom_user'
    assert config['password'] == 'custom_password'
    assert config['key_path'] == '/custom/key/path'

def test_get_config():
    sftp_config = SFTPConfig()
    config = sftp_config.get_config()
    assert isinstance(config, dict)
    assert len(config) == 6
    assert set(config.keys()) == {'host', 'port', 'username', 'password', 'key_path', 'emote_dir', 'local_dir'}
