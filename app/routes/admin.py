# -*- coding: utf-8 -*-
"""
Admin Blueprint - CRUD Operations & Database Management for BimzCam
"""

import os
from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.utils import secure_filename
from app.models import (
    get_db_connection,
    get_admin_summary,
    create_produk,
    update_produk,
    delete_produk
)

admin_bp = Blueprint('admin', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def login_required(f):
    """Decorator to enforce admin authentication"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Sesi tidak sah. Sila login terlebih dahulu!"}), 401
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_bp.route('/api/admin/summary', methods=['GET'])
@login_required
def get_summary():
    connection = None
    try:
        connection = get_db_connection()
        summary = get_admin_summary(connection)
        return jsonify(summary)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            connection.close()

@admin_bp.route('/api/admin/produk', methods=['POST'])
@login_required
def add_new_product():
    kategori_id = request.form.get('kategori_id')
    nama_produk = request.form.get('nama_produk')
    deskripsi = request.form.get('deskripsi')
    harga_per_hari = request.form.get('harga_per_hari')
    tipe = request.form.get('tipe', 'Sewa')

    if not all([kategori_id, nama_produk, deskripsi, harga_per_hari]):
        return jsonify({"error": "Sila isikan semua kolom wajib!"}), 400

    filename_field = "/static/uploads/sony_a6400.png" # default fallback
    
    if 'gambar' in request.files:
        file = request.files['gambar']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_name = f"camera_{int(os.getpid())}_{filename}"
            # Save upload to application's upload folder
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
            file.save(filepath)
            filename_field = f"/static/uploads/{unique_name}"

    connection = None
    try:
        connection = get_db_connection()
        product_id = create_produk(connection, kategori_id, nama_produk, deskripsi, harga_per_hari, filename_field, tipe)
        return jsonify({"message": "Produk berhasil ditambahkan!", "id": product_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            connection.close()

@admin_bp.route('/api/admin/produk/<int:id>', methods=['PUT'])
@login_required
def edit_product(id):
    kategori_id = request.form.get('kategori_id')
    nama_produk = request.form.get('nama_produk')
    deskripsi = request.form.get('deskripsi')
    harga_per_hari = request.form.get('harga_per_hari')
    existing_gambar = request.form.get('existing_gambar')
    tipe = request.form.get('tipe', 'Sewa')

    if not all([kategori_id, nama_produk, deskripsi, harga_per_hari]):
        return jsonify({"error": "Sila penuhi semua kolom isian wajib!"}), 400

    filename_field = existing_gambar or "/static/uploads/sony_a6400.png"

    if 'gambar' in request.files:
        file = request.files['gambar']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_name = f"camera_{id}_{filename}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
            file.save(filepath)
            filename_field = f"/static/uploads/{unique_name}"

    connection = None
    try:
        connection = get_db_connection()
        update_produk(connection, id, kategori_id, nama_produk, deskripsi, harga_per_hari, filename_field, tipe)
        return jsonify({"message": "Unit rental/jual berhasil diperbarui!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            connection.close()

@admin_bp.route('/api/admin/produk/<int:id>', methods=['DELETE'])
@login_required
def remove_product(id):
    connection = None
    try:
        connection = get_db_connection()
        delete_produk(connection, id)
        return jsonify({"message": "Unit sewa/jual berhasil dihapus!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            connection.close()
