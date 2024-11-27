import psycopg2

# Database connection details
db_config = {
    "host": "uaw-datasystem-db-do-user-10919819-0.b.db.ondigitalocean.com",
    "port": 25060,
    "dbname": "UCUAW",
    "user": "uawadmin",
    "password": "Gas2!Half!Chamomile"
}

try:
    # Establish the connection
    conn = psycopg2.connect(**db_config)
    print("Connected to the database successfully!")

    # Create a cursor to execute queries
    cursor = conn.cursor()

    # Test query
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()
    print("PostgreSQL Database Version:", db_version)

    # Close the cursor and connection
    cursor.close()
    conn.close()

except psycopg2.Error as e:
    print("Error connecting to the database:", e)
