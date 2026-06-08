# -*- coding: utf-8 -*-
"""
Database murni SQL queries for BimzCam.
No ORM, pure PyMySQL with params binding.
"""

import pymysql
from flask import current_app

def get_db_connection():
    """Membuka koneksi manual ke database MySQL murni berdasarkan konfigurasi aplikasi"""
    return pymysql.connect(
        host=current_app.config['MYSQL_HOST'],
        user=current_app.config['MYSQL_USER'],
        password=current_app.config['MYSQL_PASSWORD'],
        database=current_app.config['MYSQL_DB'],
        port=int(current_app.config.get('MYSQL_PORT', 3310)),
        cursorclass=pymysql.cursors.DictCursor
    )

def get_profil(connection):
    """Mengambil data profil usaha BimzCam"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM profil_rental LIMIT 1")
        return cursor.fetchone()

def get_kategori_list(connection):
    """Mengambil semua kategori diurutkan dari nama_kategori"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM kategori ORDER BY nama_kategori ASC")
        return cursor.fetchall()

def get_produk_list(connection):
    """Mengambil semua produk digicam & aksesoris beserta nama kategori (JOIN SQL)"""
    with connection.cursor() as cursor:
        sql = """
            SELECT produk.*, kategori.nama_kategori 
            FROM produk 
            JOIN kategori ON produk.kategori_id = kategori.id
            ORDER BY produk.id DESC
        """
        cursor.execute(sql)
        return cursor.fetchall()

def get_ulasan_list(connection):
    """Mengambil semua testimoni/ulasan (LEFT JOIN SQL)"""
    with connection.cursor() as cursor:
        sql = """
            SELECT ulasan.*, produk.nama_produk
            FROM ulasan
            LEFT JOIN produk ON ulasan.produk_id = produk.id
            ORDER BY ulasan.id DESC
        """
        cursor.execute(sql)
        return cursor.fetchall()

def get_admin_summary(connection):
    """Menghitung ringkasan statistik item menggunakan query COUNT()"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as total FROM produk")
        tot_prod = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as total FROM ulasan")
        tot_ulas = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as total FROM kategori")
        tot_kat = cursor.fetchone()['total']

        return {
            "totalProduk": tot_prod,
            "totalUlasan": tot_ulas,
            "totalKategori": tot_kat
        }

def create_produk(connection, kategori_id, nama_produk, deskripsi, harga_per_hari, gambar_url, tipe='Sewa'):
    """Menambahkan produk katalog baru"""
    with connection.cursor() as cursor:
        sql = """
            INSERT INTO produk (kategori_id, nama_produk, deskripsi, harga_per_hari, gambar_url, tipe)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (kategori_id, nama_produk, deskripsi, harga_per_hari, gambar_url, tipe))
        connection.commit()
        return cursor.lastrowid

def update_produk(connection, id, kategori_id, nama_produk, deskripsi, harga_per_hari, gambar_url, tipe='Sewa'):
    """Memperbarui informasi produk katalog berdasarkan id"""
    with connection.cursor() as cursor:
        sql = """
            UPDATE produk 
            SET kategori_id = %s, nama_produk = %s, deskripsi = %s, harga_per_hari = %s, gambar_url = %s, tipe = %s
            WHERE id = %s
        """
        cursor.execute(sql, (kategori_id, nama_produk, deskripsi, harga_per_hari, gambar_url, tipe, id))
        connection.commit()

def delete_produk(connection, id):
    """Menghapus produk sewa/jual beserta ulasannya (MySQL murni DDL cascade safety)"""
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM ulasan WHERE produk_id = %s", (id,))
        cursor.execute("DELETE FROM produk WHERE id = %s", (id,))
        connection.commit()

def get_user_by_username(connection, username):
    """Mencari user admin sepadan username"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        return cursor.fetchone()

def ensure_default_admin(connection, hashed_password):
    """Mengecek bila tabel users kosong lalu men-seed admin default"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as count FROM users")
        if cursor.fetchone()['count'] == 0:
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", ('admin', hashed_password))
            connection.commit()
            return True
    return False
