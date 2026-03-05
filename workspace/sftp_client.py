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

            ssh_kwargs = {
                'hostname': self.host,
                'port': self.port,
                'username': self.username,
            }
            if self.key_path:
                ssh_kwargs['pkey'] = paramiko.RSAKey.from_private_key_file(self.key_path)
            else:
                ssh_kwargs['password'] = self.password

            self.ssh_client.connect(**ssh_kwargs)
            self.sftp_client = self.ssh_client.open_sftp()
            self._print_status("Connected", success=True)
            return self.sftp_client
        except Exception as e:
            self.close()
            self._print_status(f"Connection failed: {e}", success=False)
            raise ConnectionError(f"Failed to connect to SFTP server: {e}")

    def upload_file(self, local_path, remote_path=None):
        """
        Uploads a local file to the SFTP server.
        """
        if self.sftp_client is None:
            raise RuntimeError("SFTP connection not established")
        import os

        if not os.path.isfile(local_path):
            raise FileNotFoundError(f"Local file not found: {local_path}")

        if remote_path is None:
            filename = os.path.basename(local_path)
            remote_path = f"{self.remote_dir.rstrip('/')}/{filename}"

        try:
            self.sftp_client.put(local_path, remote_path)
        except Exception as e:
            self._print_transfer_result("Upload", local_path, remote_path, success=False, error=str(e))
            raise IOError(f"Failed to upload {local_path} to {remote_path}: {e}")

        self._print_transfer_result("Upload", local_path, remote_path, success=True)
        return remote_path

    def download_file(self, remote_path, local_path=None):
        """
        Downloads a file from the SFTP server.
        """
        if self.sftp_client is None:
            raise RuntimeError("SFTP connection not established")
        if local_path is None:
            import os
            filename = os.path.basename(remote_path)
            local_path = f"{self.local_dir.rstrip('/')}/{filename}"
        try:
            self.sftp_client.get(remote_path, local_path)
        except Exception as e:
            self._print_transfer_result("Download", remote_path, local_path, success=False, error=str(e))
            raise IOError(f"Failed to download {remote_path} to {local_path}: {e}")

        self._print_transfer_result("Download", remote_path, local_path, success=True)
        return local_path

    def list_files(self, remote_dir=None):
        """
        Lists files in a remote directory and prints them in a user-friendly format.
        """
        if self.sftp_client is None:
            raise RuntimeError("SFTP connection not established")
        directory = remote_dir if remote_dir is not None else self.remote_dir
        files = self.sftp_client.listdir(directory)
        self._print_file_listing(directory, files)
        return files

    def close(self):
        """Close SFTP and SSH, ignore exceptions, and nullify references."""
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
        """Gracefully closes the SFTP and SSH connections."""
        self.close()
        self._print_status("Disconnected", success=True)

    # Context manager protocol
    def __enter__(self):
        """Enables use of 'with' statement. Automatically connects on entering context."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Automatically closes connections upon exit from a 'with' block."""
        self.close()

    # --- User-friendly output helpers ---

    def _print_status(self, message, success=True):
        """Print a user-friendly connection status message."""
        status = "✓" if success else "✗"
        print(f"  [{status}] SFTP {message} ({self.host}:{self.port})")

    def _print_transfer_result(self, operation, source, destination, success=True, error=None):
        """Print a user-friendly file transfer result."""
        status = "SUCCESS" if success else "FAILED"
        print("")
        print("-" * 50)
        print(f"  SFTP {operation} - {status}")
        print("-" * 50)
        print(f"  Source      : {source}")
        print(f"  Destination : {destination}")
        if error:
            print(f"  Error       : {error}")
        print("-" * 50)

    def _print_file_listing(self, directory, files):
        """Print a user-friendly listing of remote files."""
        print("")
        print("=" * 50)
        print(f"  Files in: {directory}")
        print("=" * 50)
        if files:
            for i, filename in enumerate(files, 1):
                print(f"  {i:>4}. {filename}")
        else:
            print("  (no files found)")
        print(f"\n  Total: {len(files)} file(s)")
        print("=" * 50)
