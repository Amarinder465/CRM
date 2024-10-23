import pymysql

def get_db_connection():
    # Database configuration
    db_config = {
        'user': 'root',
        'password': 'pass',  # Change to your actual password
        'host': 'localhost',
        'database': 'class_management',
        'port': 3306,  # Optional: specify port if needed
        
    }

    try:
        # Attempt to connect to the database
        connection = pymysql.connect(**db_config)

        print("Successfully connected to the database!")
        return connection  # Return the connection object if connected
    except pymysql.MySQLError as err:
        print(f"Error: {err}")
        return None  # Return None if there was an error
    finally:
        # No need to close here since we want to return the connection to the caller
        pass

def close_db_connection(connection):
    if connection:
        connection.close()
        print("Database connection closed.")

# Example usage
if __name__ == "__main__":
    conn = get_db_connection()
    if conn:
        # Perform your database operations here
        # ...
        
        close_db_connection(conn)
