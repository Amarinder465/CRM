import pymysql

def get_db_connection():
    # Database configuration
    db_config = {
        'user': 'v9z9v3q2qr38xokh',  # Your database user
        'password': 'nd16v01f8r08imlm',  # Your database password
        'host': 'y2w3wxldca8enczv.cbetxkdyhwsb.us-east-1.rds.amazonaws.com',  # Your database host
        'database': 'px2pifryiw7qmszr',  # Your database name
        'port': 3306,  # Use the correct MySQL port
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
