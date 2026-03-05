import pytest
from sftp_client import SFTPClient

class DummySFTP:
    def __init__(self):
        self.put_calls = []
        self.get_calls = []
        self.listdir_calls = []
    def put(self, local, remote):
        self.put_calls.append((local, remote))
    def get(self, remote, local):
        self.get_calls.append((remote, local))
    def listdir(self, directory):
        self.listdir_calls.append(directory)
        return ["file1.txt", "file2.csv"]
    def close(self):
        pass

class DummySSH:
    def __init__(self):
        self.connect_calls = []
        self.closed = False
        self.sftp = DummySFTP()
    def set_missing_host_key_policy(self, policy):
        pass
    def connect(self, **kwargs):
        self.connect_calls.append(kwargs)
    def open_sftp(self):
        return self.sftp
    def close(self):
        self.closed = True

@pytest.fixture
def patched_paramiko(monkeypatch):
    import sftp_client
    monkeypatch.setattr("paramiko.SSHClient", lambda: DummySSH())
    monkeypatch.setattr("paramiko.AutoAddPolicy", lambda: object())
    monkeypatch.setattr("paramiko.RSAKey.from_private_key_file", lambda path: "dummykey")
    yield

@pytest.fixture
def sftp_client_obj(monkeypatch, patched_paramiko):
    import sftp_client
    client = sftp_client.SFTPClient()
    client.ssh_client = DummySSH()
    client.sftp_client = client.ssh_client.open_sftp()
    client.remote_dir = "/remote"
    client.local_dir = "/local"
    return client

def test_connect_password(monkeypatch, patched_paramiko):
    import sftp_client
    c = sftp_client.SFTPClient()
    c.config.password = "pass"
    c.config.key_path = None
    c.host = "host"
    c.port = 22
    c.username = "user"
    c.password = "pass"
    c.key_path = None
    c.ssh_client = DummySSH()
    monkeypatch.setattr("paramiko.SSHClient", lambda: c.ssh_client)
    monkeypatch.setattr("paramiko.AutoAddPolicy", lambda: object())
    c.connect()
    assert isinstance(c.sftp_client, DummySFTP)

def test_connect_key(monkeypatch, patched_paramiko):
    import sftp_client
    c = sftp_client.SFTPClient()
    c.config.key_path = "/some/key"
    c.key_path = "/some/key"
    c.host = "host"
    c.port = 22
    c.username = "user"
    c.password = None
    c.ssh_client = DummySSH()
    monkeypatch.setattr("paramiko.SSHClient", lambda: c.ssh_client)
    monkeypatch.setattr("paramiko.AutoAddPolicy", lambda: object())
    monkeypatch.setattr("paramiko.RSAKey.from_private_key_file", lambda path: "dummykey")
    c.connect()
    assert isinstance(c.sftp_client, DummySFTP)

def test_upload_file_success(tmp_path, sftp_client_obj, capsys):
    f = tmp_path / "file1.txt"
    f.write_text("testdata")
    uploaded_path = sftp_client_obj.upload_file(str(f))
    assert uploaded_path.endswith("file1.txt")
    assert ("file1.txt" in uploaded_path)
    out = capsys.readouterr().out
    assert "SFTP Upload - SUCCESS" in out

def test_upload_file_not_found(sftp_client_obj):
    with pytest.raises(FileNotFoundError):
        sftp_client_obj.upload_file("missing_file.txt")

def test_upload_file_failure(monkeypatch, tmp_path, sftp_client_obj):
    f = tmp_path / "filefail.txt"
    f.write_text("!")
    def fail_put(local, remote):
        raise IOError("uploadFail!")
    sftp_client_obj.sftp_client.put = fail_put
    with pytest.raises(IOError, match="uploadFail!"):
        sftp_client_obj.upload_file(str(f))

def test_download_file_success(tmp_path, sftp_client_obj, capsys):
    remote = "/remote/foo.csv"
    local = tmp_path / "foo.csv"
    res_local = sftp_client_obj.download_file(remote, str(local))
    assert str(local) == res_local
    out = capsys.readouterr().out
    assert "SFTP Download - SUCCESS" in out

def test_download_file_failure(sftp_client_obj):
    def fail_get(remote, local):
        raise IOError("failDL")
    sftp_client_obj.sftp_client.get = fail_get
    with pytest.raises(IOError, match="failDL"):
        sftp_client_obj.download_file("/remote/bar.csv", "/tmp/bar.csv")

def test_list_files(sftp_client_obj, capsys):
    files = sftp_client_obj.list_files("/dir")
    assert files == ["file1.txt", "file2.csv"]
    out = capsys.readouterr().out
    assert "Files in: /dir" in out
    assert "file1.txt" in out

def test_close_disconnect(sftp_client_obj):
    sftp_client_obj.disconnect()
    assert sftp_client_obj.ssh_client is None
    assert sftp_client_obj.sftp_client is None

def test_context_manager(monkeypatch, patched_paramiko):
    import sftp_client
    c = sftp_client.SFTPClient()
    monkeypatch.setattr(c, "connect", lambda: setattr(c, "connected", True))
    monkeypatch.setattr(c, "close", lambda: setattr(c, "closed", True))
    with c as client:
        assert hasattr(client, "connected")
    assert hasattr(c, "closed")
