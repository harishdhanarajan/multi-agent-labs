import pytest
import builtins
import app

def test_connect_to_mysql_success(capsys, monkeypatch):
    monkeypatch.setattr(app, "get_mysql_connection", lambda: True)
    app.connect_to_mysql()
    out = capsys.readouterr().out
    assert "[SUCCESS] Connected to MySQL database." in out
    assert "Hello from the app!" in out

def test_connect_to_mysql_fail(capsys, monkeypatch):
    def fake_conn():
        return False
    monkeypatch.setattr(app, "get_mysql_connection", fake_conn)
    with pytest.raises(Exception):
        app.connect_to_mysql()
    out = capsys.readouterr().out
    assert "[FAILED]  Could not establish MySQL connection." in out

def test_connect_to_mysql_exception(capsys, monkeypatch):
    def raise_exception():
        raise Exception("Boom!")
    monkeypatch.setattr(app, "get_mysql_connection", raise_exception)
    app.connect_to_mysql()
    out = capsys.readouterr().out
    assert "[ERROR]   Boom!" in out
    assert "Please check your database configuration" in out
