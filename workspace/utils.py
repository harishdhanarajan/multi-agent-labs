import mysql.connector
from mysql.connector import Error

def get_mysql_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''  # Provide the correct password or use environment variable
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error: {e}")
    return None
