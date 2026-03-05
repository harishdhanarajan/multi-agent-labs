import os


class DatabaseConfig:
    def __init__(self):
        # Load environment variables or set default values
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = os.getenv('DB_PORT', '3306')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        self.database = os.getenv('DB_NAME', 'test_db')

    def get_config(self):
        """Returns the database configuration as a dictionary."""
        return {
            'host': self.host,
            'port': self.port,
            'user': self.user,
            'password': self.password,
            'database': self.database
        }

    def print_config(self, mask_password=True):
        """Print the database configuration in a user-friendly format."""
        config = self.get_config()
        password_display = "****" if (mask_password and config['password']) else config['password'] or "(not set)"

        print("\n" + "=" * 50)
        print("  Database Configuration")
        print("=" * 50)
        print(f"  Host     : {config['host']}")
        print(f"  Port     : {config['port']}")
        print(f"  User     : {config['user']}")
        print(f"  Password : {password_display}")
        print(f"  Database : {config['database']}")
        print("=" * 50 + "\n")


# Example usage
if __name__ == "__main__":
    db_config = DatabaseConfig()
    db_config.print_config()
