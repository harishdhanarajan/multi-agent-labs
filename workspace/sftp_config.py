import os


class SFTPConfig:
    def __init__(self):
        # Set default host and password as required by tests
        self.host = os.environ.get("SFTP_HOST", "ftp.example.com")
        self.port = int(os.environ.get("SFTP_PORT", 22))
        self.username = os.environ.get("SFTP_USERNAME", "")
        self.password = os.environ.get("SFTP_PASSWORD", "")
        self.key_file = os.environ.get("SFTP_KEY_FILE", None)
        self.key_path = os.environ.get("SFTP_KEY_PATH", self.key_file)

    def get_config(self):
        """Return config as a dict with all required attributes."""
        return {
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "key_file": self.key_file,
            "key_path": self.key_path,
        }

    def print_config(self, mask_password=True):
        """Print the SFTP configuration in a user-friendly format."""
        config = self.get_config()
        password_display = "****" if (mask_password and config['password']) else config['password'] or "(not set)"
        key_display = config['key_path'] if config['key_path'] else "(not set)"
        auth_method = "Key-based" if config['key_path'] else "Password-based"

        print("\n" + "=" * 50)
        print("  SFTP Configuration")
        print("=" * 50)
        print(f"  Host       : {config['host']}")
        print(f"  Port       : {config['port']}")
        print(f"  Username   : {config['username'] or '(not set)'}")
        print(f"  Password   : {password_display}")
        print(f"  Key Path   : {key_display}")
        print(f"  Auth Method: {auth_method}")
        print("=" * 50 + "\n")


if __name__ == "__main__":
    sftp_config = SFTPConfig()
    sftp_config.print_config()
