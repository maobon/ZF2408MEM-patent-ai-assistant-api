import connexion
import six

from swagger_server import util
from flask import jsonify, request
from swagger_server.models.mysql.db import create_connection, close_connection


def create_user(body):  # noqa: E501
    """Create a new user"""
    user_data = request.get_json()
    if not user_data or not user_data.get('name') or not user_data.get('email'):
        return jsonify({'message': 'Invalid input'}), 400

    connection = create_connection()
    if not connection:
        return jsonify({'message': 'Database connection failed'}), 500

    cursor = connection.cursor()
    query = "INSERT INTO users (name, email) VALUES (%s, %s)"
    cursor.execute(query, (user_data['name'], user_data['email']))
    connection.commit()
    close_connection(connection)

    return jsonify({'message': 'User created'}), 201
