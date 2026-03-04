import os

class SFTPConfig:
    def __init__(
        self,
        host=None,
        port=None,
        username=None,
        password=None,
        key_path=None,
        remote_dir=None,
        local_dir=None,
    ):
        self.host = host or os.environ.get("SFTP_HOST", "ftp.example.com")
        self.port = int(port or os.environ.get("SFTP_PORT", 22))
        self.username = username if username is not None else os.environ.get("SFTP_USERNAME", "")
        self.password = password if password is not None else os.environ.get("SFTP_PASSWORD", "")
        self.key_path = key_path if key_path is not None else os.environ.get("SFTP_KEY_PATH", "")
        self.remote_dir = remote_dir or os.environ.get("SFTP_REMOTE_DIR", "/uploads")
        self.local_dir = local_dir or os.environ.get("SFTP_LOCAL_DIR", "./downloads")

    def get_config(self):
        # Always return only the canonical fields (no emote_dir/bc quirks)
        return {
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "key_path": self.key_path,
            "remote_dir": self.remote_dir,
            "local_dir": self.local_dir,
        }
