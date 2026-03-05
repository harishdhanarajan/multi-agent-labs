import os
import pytest
from sftp_config import SFTPConfig

def test_default_sftp_config(monkeypatch):
    monkeypatch.delenv("SFTP_HOST", raising=False)
    monkeypatch.delenv("SFTP_PORT", raising=False)
    monkeypatch.delenv("SFTP_USERNAME", raising=False)
    monkeypatch.delenv("SFTP_PASSWORD", raising=False)
    monkeypatch.delenv("SFTP_KEY_FILE", raising=False)
    monkeypatch.delenv("SFTP_KEY_PATH", raising=False)
    cfg = SFTPConfig()
    c = cfg.get_config()
    assert c['host'] == "ftp.example.com"
    assert c['port'] == 22
    assert c['username'] == ""
    assert c['password'] == "password"
    assert c['key_file'] is None
    assert c['key_path'] is None

def test_env_sftp_config(monkeypatch):
    monkeypatch.setenv("SFTP_HOST", "myhost")
    monkeypatch.setenv("SFTP_PORT", "2299")
    monkeypatch.setenv("SFTP_USERNAME", "uu")
    monkeypatch.setenv("SFTP_PASSWORD", "pw")
    monkeypatch.setenv("SFTP_KEY_FILE", "/id/keyf")
    monkeypatch.setenv("SFTP_KEY_PATH", "/id/keypath")
    cfg = SFTPConfig()
    c = cfg.get_config()
    assert c['host'] == "myhost"
    assert c['port'] == 2299
    assert c['username'] == "uu"
    assert c['password'] == "pw"
    assert c['key_file'] == "/id/keyf"
    assert c['key_path'] == "/id/keypath"

def test_print_config_masked_password(capsys):
    cfg = SFTPConfig()
    cfg.password = "secr"
    cfg.print_config(mask_password=True)
    out = capsys.readouterr().out
    assert "Password   : ****" in out

def test_print_config_unmasked_password(capsys):
    cfg = SFTPConfig()
    cfg.password = "abcdef"
    cfg.print_config(mask_password=False)
    out = capsys.readouterr().out
    assert "Password   : abcdef" in out

def test_print_config_auth_method_key(monkeypatch, capsys):
    monkeypatch.setenv("SFTP_KEY_PATH", "/xx/yy.key")
    cfg = SFTPConfig()
    cfg.print_config()
    out = capsys.readouterr().out
    assert "Auth Method: Key-based" in out
    assert "Key Path   : /xx/yy.key" in out

def test_print_config_auth_method_password(monkeypatch, capsys):
    monkeypatch.delenv("SFTP_KEY_PATH", raising=False)
    cfg = SFTPConfig()
    cfg.print_config()
    out = capsys.readouterr().out
    assert "Auth Method: Password-based" in out
