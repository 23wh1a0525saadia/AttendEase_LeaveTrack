import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="attendease",
        password="2005",
        database="leavetrack"
    )
