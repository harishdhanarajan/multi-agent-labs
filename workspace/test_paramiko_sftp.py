import pytest
import paramiko

@pytest.fixture
def sftp_client():
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect('sftp.example.com', username='username', password='password')
    return ssh_client.open_sftp()

def test_sftp_client_can_connect(sftp_client):
    assert sftp_client is not None

def test_sftp_client_can_list_files(sftp_client):
    files = sftp_client.listdir()
    assert len(files) > 0

def test_sftp_client_can_upload_file(sftp_client, tmp_path):
    file_path = tmp_path / 'test_file.txt'
    file_path.write_text('Hello, world!')
    sftp_client.put(str(file_path), '/remote/path/test_file.txt')
    assert sftp_client.exists('/remote/path/test_file.txt')

def test_sftp_client_can_download_file(sftp_client, tmp_path):
    remote_file_path = '/remote/path/test_file.txt'
    local_file_path = tmp_path / 'downloaded_file.txt'
    sftp_client.get(remote_file_path, str(local_file_path))
    assert local_file_path.exists()
