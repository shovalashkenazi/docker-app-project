import os
import socket
import datetime
import mysql.connector
import logging
from flask import Flask, request, make_response

# Configure logs to be written to /app/logs/app.log
# Make sure there is a /app/logs directory in the container,
# and that you have mapped it to the host in docker-compose.
logging.basicConfig(
    filename="/app/logs/app.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

app = Flask(__name__)

def get_db_connection():
    conn = mysql.connector.connect(
        host=os.environ.get("DB_HOST", "db"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", "my_secret_password"),
        database=os.environ.get("DB_NAME", "app_db"),
    )
    return conn

def init_db():
    # Create tables if they don't exist
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS access_log (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME NOT NULL,
            client_ip VARCHAR(45) NOT NULL,
            server_ip VARCHAR(45) NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS counter (
            id INT PRIMARY KEY,
            value INT
        )
    """)
    # Ensure there is an initial record for the counter (id=1)
    cursor.execute("INSERT IGNORE INTO counter (id, value) VALUES (1, 0)")
    conn.commit()
    cursor.close()
    conn.close()
    logging.info("Database initialized (tables created if not exist)")

@app.route("/")
def index():
    # Get the container's internal IP
    server_ip = socket.gethostbyname(socket.gethostname())
    logging.info("Received request at '/', server_ip=%s", server_ip)

    # Increment the counter in the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE counter SET value = value + 1 WHERE id = 1")
    conn.commit()

    # Write a log record in the access_log table
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    client_ip = request.remote_addr or "unknown"
    cursor.execute("""
        INSERT INTO access_log (timestamp, client_ip, server_ip)
        VALUES (%s, %s, %s)
    """, (timestamp, client_ip, server_ip))
    conn.commit()
    logging.info("Inserted access_log record: client_ip=%s, server_ip=%s", client_ip, server_ip)

    cursor.close()
    conn.close()

    # Create a 5-minute (300 seconds) cookie named 'server'
    resp = make_response(server_ip)
    resp.set_cookie("server", server_ip, max_age=300)
    logging.info("Set cookie 'server' with IP=%s; max_age=300 seconds", server_ip)

    return resp

@app.route("/showcount")
def show_count():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM counter WHERE id=1")
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row:
        count_value = row[0]
        logging.info("Returning global counter=%s to client", count_value)
        return f"Global Counter: {count_value}"
    else:
        logging.warning("Counter not found!")
        return "Counter not found!"

# Initialize the DB before starting the Flask server
init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
