import pytest
from unittest import mock
from sftp_client import SFTPClient

@pytest.fixture
def dummy_config():
    # Config object with get_config method returning typical values; includes both remote_dir/emote_dir if needed
    class DummyConfig:
        def get_config(self_inner):
            return {
                "host": "host.com",
                "port": 22,
                "username": "user",
                "password": "pw",
                "remote_dir": "/upload",
                "emote_dir": "/upload",  # typo for backward compat with sftp_client.py
                "local_dir": "/tmp",
                "key_path": None
            }
        local_dir = "/tmp"
    return DummyConfig()

def mock_paramiko_connect_success(monkeypatch):
    """Patch paramiko.SSHClient/connect/open_sftp, and RSAKey for key auth."""
    mock_ssh = mock.Mock()
    mock_sftp = mock.Mock()
    mock_ssh.open_sftp.return_value = mock_sftp

    monkeypatch.setattr("paramiko.SSHClient", mock.Mock(return_value=mock_ssh))
    monkeypatch.setattr("paramiko.AutoAddPolicy", mock.Mock())
    monkeypatch.setattr("paramiko.RSAKey.from_private_key_file", mock.Mock(return_value="pkeyObj"))
    return mock_ssh, mock_sftp

def test_connect_password_auth(monkeypatch, dummy_config):
    """connect() with password-based authentication."""
    mock_ssh, mock_sftp = mock_paramiko_connect_success(monkeypatch)

    # Prepare config without key_path
    orig_get_config = dummy_config.get_config
    def patched_get_config():
        cfg = orig_get_config()
        cfg["key_path"] = None
        return cfg
    dummy_config.get_config = patched_get_config

    client = SFTPClient(dummy_config)

    sftp = client.connect()
    assert sftp is mock_sftp
    assert client.ssh_client is mock_ssh
    assert client.sftp_client is mock_sftp
    # Should call connect without 'pkey'
    args, kwargs = mock_ssh.connect.call_args
    assert kwargs['hostname'] == "host.com"
    assert kwargs['username'] == "user"
    assert kwargs['password'] == "pw"
    assert 'pkey' not in kwargs

def test_connect_key_auth(monkeypatch, dummy_config):
    """connect() with key-based authentication."""
    mock_ssh, mock_sftp = mock_paramiko_connect_success(monkeypatch)

    orig_get_config = dummy_config.get_config
    def patched_get_config():
        cfg = orig_get_config()
        cfg["key_path"] = "/some/key"
        return cfg
    dummy_config.get_config = patched_get_config

    client = SFTPClient(dummy_config)

    sftp = client.connect()
    assert sftp is mock_sftp
    # Should call connect with 'pkey'
    args, kwargs = mock_ssh.connect.call_args
    assert kwargs['pkey'] == "pkeyObj"
    assert 'password' not in kwargs or kwargs.get('password', None) == ""

def test_connect_failure(monkeypatch, dummy_config):
    """connect() should raise if paramiko connect fails, and cleanup connections."""
    # Patch SSHClient.connect to raise
    mock_ssh = mock.Mock()
    mock_ssh.connect.side_effect = Exception("fail connect")
    mock_ssh.open_sftp = mock.Mock()
    monkeypatch.setattr("paramiko.SSHClient", mock.Mock(return_value=mock_ssh))
    monkeypatch.setattr("paramiko.AutoAddPolicy", mock.Mock())
    monkeypatch.setattr("paramiko.RSAKey.from_private_key_file", mock.Mock())
    orig_get_config = dummy_config.get_config
    def patched_get_config():
        cfg = orig_get_config()
        cfg["key_path"] = None
        return cfg
    dummy_config.get_config = patched_get_config

    client = SFTPClient(dummy_config)
    with pytest.raises(ConnectionError) as e:
        client.connect()
    assert "Failed to connect to SFTP server" in str(e.value)
    assert client.ssh_client is None
    assert client.sftp_client is None

def test_disconnect_closes_connections(monkeypatch, dummy_config):
    """disconnect() and close() set references to None and call .close() of both connections."""
    client = SFTPClient(dummy_config)
    sftp_closed = ssh_closed = False

    class FakeSFTP:
        def close(self_inner):
            nonlocal sftp_closed
            sftp_closed = True

    class FakeSSH:
        def close(self_inner):
            nonlocal ssh_closed
            ssh_closed = True

    client.sftp_client = FakeSFTP()
    client.ssh_client = FakeSSH()
    client.disconnect()
    assert sftp_closed
    assert ssh_closed
    assert client.sftp_client is None
    assert client.ssh_client is None

def test_disconnect_handles_exceptions(dummy_config):
    """disconnect()/close() swallow exceptions from close()."""
    client = SFTPClient(dummy_config)

    class BadSFTP:
        def close(self_inner):
            raise RuntimeError("fail sftp")

    class BadSSH:
        def close(self_inner):
            raise RuntimeError("fail ssh")

    client.sftp_client = BadSFTP()
    client.ssh_client = BadSSH()
    # Should not raise an exception!
    client.disconnect()
    assert client.sftp_client is None
    assert client.ssh_client is None

def test_upload_file_success(monkeypatch, tmp_path, dummy_config):
    """upload_file uploads to remote_dir/basename when remote_path is None."""
    # Patch client.sftp_client.put
    from sftp_client import SFTPClient
    client = SFTPClient(config=dummy_config)
    client.sftp_client = mock.Mock()
    # Create a file
    file_path = tmp_path / "abc.txt"
    file_path.write_text("data")
    # Run upload_file with only local path
    remote_path = client.upload_file(str(file_path))
    expect_remote_path = f"/upload/abc.txt"
    client.sftp_client.put.assert_called_once_with(str(file_path), expect_remote_path)
    assert remote_path == expect_remote_path

def test_upload_file_custom_remote_path(monkeypatch, tmp_path, dummy_config):
    """upload_file with explicit remote_path."""
    client = SFTPClient(config=dummy_config)
    client.sftp_client = mock.Mock()
    file_path = tmp_path / "def.txt"
    file_path.write_text("othertest")
    remote_path = "/upload2/blah.txt"
    uploaded = client.upload_file(str(file_path), remote_path)
    client.sftp_client.put.assert_called_once_with(str(file_path), remote_path)
    assert uploaded == remote_path

def test_upload_file_no_connection(tmp_path, dummy_config):
    """upload_file with no sftp_client set raises RuntimeError."""
    client = SFTPClient(config=dummy_config)
    file_path = tmp_path / "nofile.txt"
    file_path.write_text("d")
    with pytest.raises(RuntimeError, match="SFTP connection not established"):
        client.upload_file(str(file_path))

def test_upload_file_missing_local_file(dummy_config):
    """upload_file raises FileNotFoundError if local file does not exist."""
    client = SFTPClient(config=dummy_config)
    client.sftp_client = mock.Mock()
    non_existent = "/tmp/file_should_not_exist_123456789.txt"
    import os
    assert not os.path.isfile(non_existent)
    with pytest.raises(FileNotFoundError):
        client.upload_file(non_existent)

def test_upload_file_put_error(monkeypatch, tmp_path, dummy_config):
    """upload_file: errors in sftp_client.put raise IOError."""
    client = SFTPClient(config=dummy_config)
    client.sftp_client = mock.Mock()
    file_path = tmp_path / "tofail.txt"
    file_path.write_text("failme")
    # Make put fail
    client.sftp_client.put.side_effect = Exception("SFTP exploded")
    with pytest.raises(IOError) as e:
        client.upload_file(str(file_path))
    assert "Failed to upload" in str(e.value)
    assert "SFTP exploded" in str(e.value)
