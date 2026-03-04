import pytest
from unittest import mock
from sftp_client import SFTPClient

@pytest.fixture
def mock_paramiko(monkeypatch):
    mock_ssh = mock.Mock()
    mock_sftp = mock.Mock()
    mock_ssh.open_sftp.return_value = mock_sftp
    monkeypatch.setattr("paramiko.SSHClient", mock.Mock(return_value=mock_ssh))
    monkeypatch.setattr("paramiko.AutoAddPolicy", mock.Mock())
    monkeypatch.setattr("paramiko.RSAKey.from_private_key_file", mock.Mock())
    return mock_ssh, mock_sftp

def test_context_manager_connect_and_close(mock_paramiko):
    mock_ssh, mock_sftp = mock_paramiko

    # Use a dummy config object
    class DummyConfig:
        def get_config(self):
            return {
                "host": "example.com",
                "port": 22,
                "username": "user",
                "password": "pass",
                "remote_dir": "/upload"
            }
    config = DummyConfig()
    with SFTPClient(config) as client:
        # Inside the context, connection objects should be non-None
        assert client.ssh_client is mock_ssh
        assert client.sftp_client is mock_sftp

    # After context, connections should be closed (None)
    assert client.ssh_client is None
    assert client.sftp_client is None
    assert mock_ssh.close.called
    assert mock_sftp.close.called

def test_context_manager_with_exception(mock_paramiko):
    mock_ssh, mock_sftp = mock_paramiko

    class DummyConfig:
        def get_config(self):
            return {
                "host": "example.com",
                "port": 22,
                "username": "user",
                "password": "pass",
                "remote_dir": "/upload"
            }
    config = DummyConfig()
    class CustomException(Exception):
        pass

    with pytest.raises(CustomException):
        with SFTPClient(config) as client:
            raise CustomException("Something went wrong")
    # Connections should still be closed
    assert client.ssh_client is None
    assert client.sftp_client is None
    assert mock_ssh.close.called
    assert mock_sftp.close.called
