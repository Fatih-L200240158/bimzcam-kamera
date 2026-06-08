# -*- coding: utf-8 -*-
"""
Public Routing & Public Read-Only APIs for BimzCam
"""

from flask import Blueprint, render_template, redirect, url_for, session, jsonify
from app.models import (
    get_db_connection,
    get_profil,
    get_kategori_list,
    get_produk_list,
    get_ulasan_list
)

public_bp = Blueprint('public', __name__)

# ==========================================
# 1. HTML TEMPLATE RENDERING (Server-Side MVC)
# ==========================================

@public_bp.route('/')
def home():
    """Halaman depan publik BimzCam"""
    return render_template('index.html')

@public_bp.route('/login.html')
def login_page():
    """Halaman masuk administrator"""
    if 'user_id' in session:
        return redirect(url_for('public.admin_page'))
    return render_template('login.html')

@public_bp.route('/admin.html')
def admin_page():
    """Halaman dashboard kelola admin"""
    if 'user_id' not in session:
        return redirect(url_for('public.login_page'))
    # Di dalam struktur baru, admin.html ditaruh di dalam templates/admin/dashboard.html atau templates/admin.html
    # Mari kita render templates/admin.html (atau admin/dashboard.html)
    return render_template('admin.html')


# ==========================================
# 2. PUBLIC JSON GET ENDPOINTS
# ==========================================

@public_bp.route('/api/profil', methods=['GET'])
def fetch_profil():
    connection = None
    try:
        connection = get_db_connection()
        profil = get_profil(connection)
        return jsonify(profil)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            connection.close()

@public_bp.route('/api/kategori', methods=['GET'])
def fetch_kategori():
    connection = None
    try:
        connection = get_db_connection()
        categories = get_kategori_list(connection)
        return jsonify(categories)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            connection.close()

@public_bp.route('/api/produk', methods=['GET'])
def fetch_produk():
    connection = None
    try:
        connection = get_db_connection()
        products = get_produk_list(connection)
        return jsonify(products)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            connection.close()

@public_bp.route('/api/ulasan', methods=['GET'])
def fetch_ulasan():
    connection = None
    try:
        connection = get_db_connection()
        reviews = get_ulasan_list(connection)
        return jsonify(reviews)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            connection.close()
