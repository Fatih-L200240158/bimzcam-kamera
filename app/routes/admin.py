# -*- coding: utf-8 -*-
"""
Admin Blueprint - CRUD Operations & Database Management for BimzCam (Cloudinary Version)
"""

import os
from flask import Blueprint, request, jsonify, session
import cloudinary
import cloudinary.uploader
from app.models import (
    get_db_connection,
    get_admin_summary,
    create_produk,
    update_produk,
    delete_produk
)

admin_bp = Blueprint('admin', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

# Configuration Cloudinary (Membaca otomatis dari Environment Variables Vercel)
cloudinary.config(
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key = os.environ.get('CLOUDINARY_API_KEY'),
    api_secret = os.environ.get('CLOUDINARY_API_SECRET'),
    secure = True
)

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
            try:
                # membaca data biner gambar secara mentah (stream bytes)
                file_bytes = file.read()
                
                # kirim dalam bentuk bytes ke Cloudinary agar Vercel tidak crash
                upload_result = cloudinary.uploader.upload(
                    file_bytes,
                    folder="bimzcam_katalog",
                    resource_type="image"
                )
                filename_field = upload_result.get('secure_url')
            except Exception as upload_error:
                return jsonify({"error": f"Gagal ke Cloudinary: {str(upload_error)}"}), 500

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
            try:
                # 🔥 TRICK: Unggah file gambar baru langsung ke Cloudinary saat edit produk
                upload_result = cloudinary.uploader.upload(
                    file,
                    folder="bimzcam_katalog",
                    resource_type="image"
                )
                filename_field = upload_result.get('secure_url')
            except Exception as upload_error:
                return jsonify({"error": f"Gagal memperbarui gambar ke cloud Cloudinary: {str(upload_error)}"}), 500

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