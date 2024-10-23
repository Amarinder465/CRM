from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
from db import get_db_connection, close_db_connection
from pymysql.cursors import DictCursor  # Import DictCursor
from datetime import datetime  # Import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change to a more secure secret key

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/add_client', methods=['GET', 'POST'])
def add_client():
    if request.method == 'POST':
        client_name = request.form.get('client_name')
        client_email = request.form.get('client_email')
        client_number = request.form.get('client_number')
        client_car = request.form.get('client_car')

        selected_tags = request.form.getlist('tags')  # This will be a list of tag IDs

        try:
            connection = get_db_connection()
            if connection is None:
                return "Failed to connect to the database.", 500

            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO clients (name, contact_info, number, car) VALUES (%s, %s, %s, %s)",
                (client_name, client_email, client_number, client_car)
            )
            connection.commit()

            client_id = cursor.lastrowid

            # Debugging: Check if client_id is valid
            print(f"Inserted client ID: {client_id}")

            for tag_id in selected_tags:
                cursor.execute("INSERT INTO client_tags (client_id, tag_id) VALUES (%s, %s)", (client_id, tag_id))

            connection.commit()
            flash('Client added successfully with selected tags!', 'success')
            return redirect(url_for('dashboard'))
        except pymysql.MySQLError as err:
            connection.rollback()
            print(f"Error while adding client: {err}")  # Debugging output
            flash(f"Error: {err}", 'danger')
        finally:
            close_db_connection(connection)

    try:
        connection = get_db_connection()
        if connection is None:
            return "Failed to connect to the database.", 500

        cursor = connection.cursor(DictCursor)
        cursor.execute("SELECT id, name FROM tags")
        tags = cursor.fetchall()
    except pymysql.MySQLError as err:
        print(f"Error fetching tags: {err}")  # Debugging output
        return f"Error: {err}", 500
    finally:
        close_db_connection(connection)

    return render_template('add_client.html', tags=tags)

@app.route('/client_profile/<int:client_id>', methods=['GET', 'POST'])
def client_profile(client_id):
    try:
        connection = get_db_connection()
        if connection is None:
            return "Failed to connect to the database.", 500

        cursor = connection.cursor(DictCursor)
        
        # Get client details and their associated tags
        cursor.execute(""" 
            SELECT c.id, c.name, c.contact_info, c.number, c.car, 
                   c.last_contacted, c.notes,
                   GROUP_CONCAT(t.name) as tags
            FROM clients c
            LEFT JOIN client_tags ct ON c.id = ct.client_id
            LEFT JOIN tags t ON ct.tag_id = t.id
            WHERE c.id = %s
            GROUP BY c.id
        """, (client_id,))
        client = cursor.fetchone()
        if not client:
            return "Client not found.", 404

        client['tags'] = client['tags'].split(',') if client['tags'] else []
        client['last_contacted'] = client['last_contacted'].strftime('%Y-%m-%d %H:%M:%S') if client['last_contacted'] else "Never"

        # Fetch all tags to display in the checkbox form
        cursor.execute("SELECT id, name FROM tags")
        all_tags = cursor.fetchall()

        # If POST request, handle updates
        if request.method == 'POST':
            # Handle updating tags
            if 'tags' in request.form:
                selected_tags = request.form.getlist('tags')  # This will be a list of tag IDs

                # Clear current tags for this client
                cursor.execute("DELETE FROM client_tags WHERE client_id = %s", (client_id,))
                # Add selected tags back
                for tag_id in selected_tags:
                    cursor.execute("INSERT INTO client_tags (client_id, tag_id) VALUES (%s, %s)", (client_id, tag_id))
                
                connection.commit()
                flash('Tags updated successfully!', 'success')
            
            # Handle updating last contacted
            if 'contacted' in request.form:
                now = datetime.now()
                cursor.execute("UPDATE clients SET last_contacted = %s WHERE id = %s", (now, client_id))
                connection.commit()
                flash('Last contacted date updated successfully!', 'success')

            # Handle saving notes
            if 'notes' in request.form:
                notes = request.form.get('notes')
                cursor.execute("UPDATE clients SET notes = %s WHERE id = %s", (notes, client_id))
                connection.commit()
                flash('Notes updated successfully!', 'success')

            # Redirect back to the client profile
            return redirect(url_for('client_profile', client_id=client_id))

    except pymysql.MySQLError as err:
        return f"Error: {err}", 500
    finally:
        close_db_connection(connection)

    return render_template('client_profile.html', client=client, tags=all_tags)

@app.route('/view_clients', methods=['GET', 'POST'])
def view_clients():
    try:
        connection = get_db_connection()
        if connection is None:
            return "Failed to connect to the database.", 500

        cursor = connection.cursor(DictCursor)
        
        # Get all tags for filter checkboxes
        cursor.execute("SELECT * FROM tags")
        tags = cursor.fetchall()

        # Initialize the query
        query = """
            SELECT c.id, c.name, c.contact_info, c.number, c.car, GROUP_CONCAT(t.name) as tags
            FROM clients c
            LEFT JOIN client_tags ct ON c.id = ct.client_id
            LEFT JOIN tags t ON ct.tag_id = t.id
            WHERE 1=1
        """
        
        # Handle filtering if a form is submitted
        selected_tags = request.form.getlist('tags')
        if selected_tags:
            query += " AND ct.tag_id IN ({})".format(','.join(selected_tags))

        query += " GROUP BY c.id"

        cursor.execute(query)
        clients = cursor.fetchall()

        if not clients:
            print("No clients found.")
        else:
            print("Clients found:", clients)

    except pymysql.MySQLError as err:
        return f"Error: {err}", 500
    finally:
        close_db_connection(connection)

    return render_template('view_clients.html', clients=clients, tags=tags)

@app.route('/remove_clients', methods=['GET'])
def remove_clients():
    try:
        connection = get_db_connection()
        if connection is None:
            return "Failed to connect to the database.", 500

        cursor = connection.cursor(DictCursor)
        cursor.execute("SELECT id, name, contact_info FROM clients")
        clients = cursor.fetchall()
    except pymysql.MySQLError as err:
        return f"Error: {err}", 500
    finally:
        close_db_connection(connection)

    return render_template('remove_client.html', clients=clients)


@app.route('/remove_client/<int:client_id>', methods=['POST'])
def remove_client(client_id):
    try:
        connection = get_db_connection()
        if connection is None:
            return "Failed to connect to the database.", 500

        cursor = connection.cursor()
        cursor.execute("DELETE FROM clients WHERE id = %s", (client_id,))
        connection.commit()
        flash('Client removed successfully!', 'success')
    except pymysql.MySQLError as err:
        connection.rollback()
        flash(f"Error: {err}", 'danger')
    finally:
        close_db_connection(connection)

    return redirect(url_for('remove_clients'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
