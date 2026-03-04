import paramiko
from sftp_config import SFTPConfig

class SFTPClient:
    def __init__(self, config: SFTPConfig = None):
        self.config = config or SFTPConfig()
        # Extract settings for easier access
        cfg = self.config.get_config() if hasattr(self.config, "get_config") else vars(self.config)
        # Support both 'remote_dir' and 'emote_dir' fallback due to possible typo
        self.host = cfg.get("host", "localhost")
        self.port = cfg.get("port", 22)
        self.username = cfg.get("username", "")
        self.password = cfg.get("password", "")
        self.key_path = cfg.get("key_path", None)
        self.remote_dir = cfg.get("remote_dir") or cfg.get("emote_dir", "")
        # Some configs may provide 'local_dir'
        self.local_dir = getattr(self.config, "local_dir", None) or cfg.get("local_dir", "")

        self.ssh_client = None
        self.sftp_client = None

    def connect(self):
        """
        Establishes an SSH connection and opens an SFTP session.
        Tries key-based auth first if key_path is set, else password-based.
        Raises ConnectionError on failure.
        """
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Prefer key auth if key_path is set
            ssh_kwargs = {
                'hostname': self.host,
                'port': self.port,
                'username': self.username,
            }
            if self.key_path:
                # Create PKey and use pkey parameter
                ssh_kwargs['pkey'] = paramiko.RSAKey.from_private_key_file(self.key_path)
                # Optionally include passphrase (password) if needed; not always required
                # paramiko will prompt if key is encrypted and password is not given
            else:
                # Use password auth
                ssh_kwargs['password'] = self.password

            self.ssh_client.connect(**ssh_kwargs)
            self.sftp_client = self.ssh_client.open_sftp()
            return self.sftp_client
        except Exception as e:
            self.close()
            raise ConnectionError(f"Failed to connect to SFTP server: {e}")

    def upload_file(self, local_path, remote_path=None):
        """
        Uploads a local file to the SFTP server.
        :param local_path: The path to the local file to be uploaded.
        :param remote_path: The full path on the remote server. If None, uploads to remote_dir with same filename.
        :return: The remote path where the file was uploaded.
        :raises: RuntimeError if SFTP connection not established, FileNotFoundError if local file does not exist,
                 IOError for SFTP errors.
        """
        if self.sftp_client is None:
            raise RuntimeError("SFTP connection not established")
        import os

        if not os.path.isfile(local_path):
            raise FileNotFoundError(f"Local file not found: {local_path}")

        if remote_path is None:
            # Upload to remote_dir with same filename
            filename = os.path.basename(local_path)
            remote_path = f"{self.remote_dir.rstrip('/')}/{filename}"

        try:
            self.sftp_client.put(local_path, remote_path)
        except Exception as e:
            raise IOError(f"Failed to upload {local_path} to {remote_path}: {e}")
        return remote_path

    def download_file(self, remote_path, local_path=None):
        if self.sftp_client is None:
            raise RuntimeError("SFTP connection not established")
        if local_path is None:
            import os
            filename = os.path.basename(remote_path)
            local_path = f"{self.local_dir.rstrip('/')}/{filename}"
        self.sftp_client.get(remote_path, local_path)
        return local_path

    def list_files(self, remote_dir=None):
        if self.sftp_client is None:
            raise RuntimeError("SFTP connection not established")
        directory = remote_dir if remote_dir is not None else self.remote_dir
        return self.sftp_client.listdir(directory)

    def close(self):
        # Close SFTP and SSH, ignore exceptions, and nullify references.
        try:
            if self.sftp_client is not None:
                self.sftp_client.close()
        except Exception:
            pass
        try:
            if self.ssh_client is not None:
                self.ssh_client.close()
        except Exception:
            pass
        self.ssh_client = None
        self.sftp_client = None

    def disconnect(self):
        """
        Gracefully closes the SFTP and SSH connections.
        """
        self.close()

    # Context manager protocol
    def __enter__(self):
        """
        Enables use of 'with' statement. Automatically connects on entering context.
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Automatically closes connections upon exit from a 'with' block.
        Suppresses no exceptions.
        """
        self.close()
