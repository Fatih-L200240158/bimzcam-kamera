# -*- coding: utf-8 -*-
"""
Database murni SQL queries for BimzCam.
No ORM, pure Psycopg2 (PostgreSQL) dengan params binding.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import current_app

def get_db_connection():
    """Membuka koneksi manual ke database PostgreSQL Supabase dengan parameter SSL"""
    
    # Supabase mewajibkan SSL mode untuk koneksi yang aman
    # Kita ambil string koneksi non-pooling langsung dari environment
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        # Cadangan jika diakses secara lokal tanpa env global system
        # Menyesuaikan dengan format kredensial database di config Flask
        db_host = current_app.config.get('MYSQL_HOST', 'db.eivqiqnxvryeauzjwwkb.supabase.co')
        db_user = current_app.config.get('MYSQL_USER', 'postgres')
        db_password = current_app.config.get('MYSQL_PASSWORD', '8fJZ4jssyhlaT3iW')
        db_name = current_app.config.get('MYSQL_DB', 'postgres')
        db_port = current_app.config.get('MYSQL_PORT', 5432)
        database_url = f"postgres://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?sslmode=require"

    return psycopg2.connect(
        database_url, 
        cursor_factory=RealDictCursor  # Mengembalikan data berformat Dictionary (seperti DictCursor MySQL)
    )

def get_profil(connection):
    """Mengambil data profil usaha BimzCam"""
    with connection.cursor() as cursor:
        # Postgres lebih menyukai LIMIT 1 di akhir query tanpa masalah
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
        # Di PostgreSQL, untuk mengambil ID yang baru saja dibuat (lastrowid), 
        # kita tambahkan klausa 'RETURNING id' di akhir query INSERT
        sql = """
            INSERT INTO produk (kategori_id, nama_produk, deskripsi, harga_per_hari, gambar_url, tipe)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
        """
        cursor.execute(sql, (kategori_id, nama_produk, deskripsi, harga_per_hari, gambar_url, tipe))
        new_id = cursor.fetchone()['id']
        connection.commit()  # Wajib commit di Postgres agar data tersimpan permanen
        return new_id

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
    """Menghapus produk sewa/jual beserta ulasannya (PostgreSQL Cascade Handshake)"""
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM ulasan WHERE produk_id = %s", (id,))
        cursor.execute("DELETE FROM produk WHERE id = %s", (id,))
        connection.commit()

def get_user_by_username(connection, username):
    """Mencari user admin sepadan username"""
    with connection.cursor() as cursor:
        # Tuple satu parameter wajib diberi tanda koma di akhir (username,) agar dibaca sebagai Tuple oleh Psycopg2
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        return cursor.fetchone()

def ensure_default_admin(connection, hashed_password):
    """Mengecek bila tabel users kosong lalu men-seed admin default (Safe Mode)"""
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT COUNT(*) as count FROM users")
            if cursor.fetchone()['count'] == 0:
                cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", ('admin', hashed_password))
                connection.commit()
                return True
        except Exception as e:
            # Mengamankan aplikasi agar tidak crash jika tabel database fisik belum diinjeksi
            print("[Seeder Info] Tabel users belum siap atau belum dibuat di Supabase:", e)
    return False