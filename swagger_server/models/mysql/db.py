import json
from decimal import Decimal

import mysql.connector
from mysql.connector import Error


def create_connection():
    """Create a database connection."""
    try:
        connection = mysql.connector.connect(
            host='sh-cynosdbmysql-grp-b4dl8b8a.sql.tencentcdb.com',
            database='patent_ai_assistant',
            user='root',
            password='mem123456@',
            port=20501
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None


def close_connection(connection):
    """Close the database connection."""
    if connection.is_connected():
        connection.close()
        print("MySQL connection is closed")


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)
