# -*- coding: utf-8 -*-
"""
Authentication Blueprint for BimzCam Admin Panel login
"""

from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash
from app.models import get_db_connection, get_user_by_username

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username dan Password wajib dikirim!"}), 400

    connection = None
    try:
        connection = get_db_connection()
        user = get_user_by_username(connection, username)
        
        if not user:
            return jsonify({"error": "Username atau Password salah!"}), 401

        if check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return jsonify({"message": "Login berhasil!"})
        else:
            return jsonify({"error": "Username atau Password salah!"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            connection.close()

@auth_bp.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return jsonify({"message": "Logout berhasil!"})

@auth_bp.route('/api/check-session', methods=['GET'])
def check_session():
    if 'user_id' in session:
        return jsonify({"loggedIn": True, "username": session.get('username')})
    return jsonify({"loggedIn": False})
