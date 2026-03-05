import os
import pytest
from db_config import DatabaseConfig

def test_default_config(monkeypatch):
    # Ensure environment variables are not set
    monkeypatch.delenv("DB_HOST", raising=False)
    monkeypatch.delenv("DB_PORT", raising=False)
    monkeypatch.delenv("DB_USER", raising=False)
    monkeypatch.delenv("DB_PASSWORD", raising=False)
    monkeypatch.delenv("DB_NAME", raising=False)
    config = DatabaseConfig()
    cfg = config.get_config()
    assert cfg['host'] == 'localhost'
    assert cfg['port'] == '3306'
    assert cfg['user'] == 'root'
    assert cfg['password'] == ''
    assert cfg['database'] == 'test_db'

def test_env_vars(monkeypatch):
    monkeypatch.setenv("DB_HOST", "remotehost")
    monkeypatch.setenv("DB_PORT", "1234")
    monkeypatch.setenv("DB_USER", "admin")
    monkeypatch.setenv("DB_PASSWORD", "secret")
    monkeypatch.setenv("DB_NAME", "maindb")
    config = DatabaseConfig()
    cfg = config.get_config()
    assert cfg['host'] == 'remotehost'
    assert cfg['port'] == '1234'
    assert cfg['user'] == 'admin'
    assert cfg['password'] == 'secret'
    assert cfg['database'] == 'maindb'

def test_print_config_mask_password(capsys):
    config = DatabaseConfig()
    config.password = "mypassword"
    config.print_config(mask_password=True)
    out = capsys.readouterr().out
    assert "Password : ****" in out

def test_print_config_unmasked_password(capsys):
    config = DatabaseConfig()
    config.password = "xyz"
    config.print_config(mask_password=False)
    out = capsys.readouterr().out
    assert "Password : xyz" in out
