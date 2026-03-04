from utils import get_mysql_connection

def main():
    print("Hello from the app")

    # Demonstrating MySQL connection
    connection = get_mysql_connection()
    if connection:
        print("MySQL connection established successfully.")
        connection.close()
        print("Connection closed.")
    else:
        print("Failed to establish MySQL connection.")

if __name__ == "__main__":
    main()
