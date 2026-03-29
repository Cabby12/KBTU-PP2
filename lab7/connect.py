import psycopg2

def get_connection():
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="phonebook_db",
        user="postgres",
        password="alikhan2201"
    )
    return conn

