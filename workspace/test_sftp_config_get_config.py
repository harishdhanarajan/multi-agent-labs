from sftp_config import SFTPConfig

def test_sftp_config_get_config():
    sftp_config = SFTPConfig()
    config = sftp_config.get_config()

    assert isinstance(config, dict)
    assert 'host' in config
    assert 'port' in config
    assert 'username' in config
    assert 'password' in config
    assert 'key_path' in config
