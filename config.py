import mysql.connector

def get_connection():
    return mysql.connector.connect(
    host="localhost",
    user="root",
    password="TennisDB10987",
    database="Tennis_db"
)


def get_engine():
    return get_connection()