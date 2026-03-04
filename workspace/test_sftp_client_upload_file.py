import pytest
import os
from unittest import mock

from sftp_client import SFTPClient

@pytest.fixture
def sftp_client_with_mocked_sftp():
    # Create a dummy config with a remote_dir and local_dir
    class DummyConfig:
        def get_config(self):
            return {
                "remote_dir": "/remote/destination",
                "host": "dummyhost",
                "port": 22,
                "username": "user",
                "password": "pass",
            }
        local_dir = "/local/source"

    client = SFTPClient(config=DummyConfig())
    # Patch the SFTP connection object
    client.sftp_client = mock.Mock()
    return client

def test_upload_file_success(tmp_path, sftp_client_with_mocked_sftp):
    # Create a temporary file to upload
    file_path = tmp_path / "test.txt"
    file_path.write_text("some test data")
    client = sftp_client_with_mocked_sftp

    # Call upload_file, remote_path should be '/remote/destination/test.txt'
    remote_path = client.upload_file(str(file_path))
    expected_remote_path = "/remote/destination/test.txt"

    client.sftp_client.put.assert_called_once_with(str(file_path), expected_remote_path)
    assert remote_path == expected_remote_path

def test_upload_file_with_custom_remote_path(tmp_path, sftp_client_with_mocked_sftp):
    file_path = tmp_path / "file.txt"
    file_path.write_text("abc123")
    client = sftp_client_with_mocked_sftp

    # Custom remote path
    remote_path = "/upload/othername.txt"
    result = client.upload_file(str(file_path), remote_path)
    client.sftp_client.put.assert_called_once_with(str(file_path), remote_path)
    assert result == remote_path

def test_upload_file_no_connection(tmp_path):
    from sftp_client import SFTPClient
    # using DummyConfig but do NOT set sftp_client
    class DummyConfig:
        def get_config(self):
            return {"remote_dir": "/foo"}
    client = SFTPClient(DummyConfig())
    test_file = tmp_path / "x.txt"
    test_file.write_text("data")

    with pytest.raises(RuntimeError, match="SFTP connection not established"):
        client.upload_file(str(test_file))

def test_upload_file_local_file_missing(sftp_client_with_mocked_sftp):
    client = sftp_client_with_mocked_sftp
    non_existent_file = "/tmp/imaginary_file_123.txt"
    assert not os.path.isfile(non_existent_file)

    with pytest.raises(FileNotFoundError) as excinfo:
        client.upload_file(non_existent_file)
    assert "Local file not found" in str(excinfo.value)

def test_upload_file_sftp_error(tmp_path, sftp_client_with_mocked_sftp):
    # Patch sftp_client.put to raise an IOError
    file_path = tmp_path / "abc.txt"
    file_path.write_text("abc")
    client = sftp_client_with_mocked_sftp
    client.sftp_client.put.side_effect = Exception("SFTP is down")

    with pytest.raises(IOError) as excinfo:
        client.upload_file(str(file_path))
    assert "Failed to upload" in str(excinfo.value)
    assert "SFTP is down" in str(excinfo.value)
