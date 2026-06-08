# -*- coding: utf-8 -*-
"""
Application Factory to build and configure the BimzCam Flask Application
"""

import os
from flask import Flask
from .routes.public import public_bp
from .routes.auth import auth_bp
from .routes.admin import admin_bp

def create_app():
    # We specify template_folder and static_folder so flask knows precisely where they are relative to app packager
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static'
    )

    # 1. Secret Key setups
    app.secret_key = os.environ.get('SECRET_KEY', 'bimzcam_secret_key_extremely_secure_773')

    # 2. Database configs (Disesuaikan dengan nama variabel standar Aiven/Vercel)
    app.config['MYSQL_HOST'] = os.environ.get('DB_HOST', os.environ.get('MYSQL_HOST', '127.0.0.1'))
    app.config['MYSQL_USER'] = os.environ.get('DB_USER', os.environ.get('MYSQL_USER', 'root'))
    app.config['MYSQL_PASSWORD'] = os.environ.get('DB_PASSWORD', os.environ.get('MYSQL_PASSWORD', 'rahasiafatih'))
    app.config['MYSQL_DB'] = os.environ.get('DB_NAME', os.environ.get('MYSQL_DB', 'bimzcam_db'))
    app.config['MYSQL_PORT'] = int(os.environ.get('DB_PORT', os.environ.get('MYSQL_PORT', 3310)))

    # 3. Setup uploads directory
    UPLOAD_FOLDER = os.path.join(app.root_path, 'static/uploads')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # 4. Register Blueprints
    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    # 5. OTOMATISASI CLOUD: Buat Tabel dari schema.sql & Isi Admin Otomatis
    from werkzeug.security import generate_password_hash
    from app.models import get_db_connection, ensure_default_admin
    
    try:
        connection = get_db_connection()
        
        # --- KODE PENYARING SCHEMA.SQL (ANTI-ERROR AIVEN) ---
        schema_path = os.path.join(os.path.dirname(app.root_path), 'database', 'schema.sql')
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                sql_file = f.read()
                sql_commands = sql_file.split(';')
                
                with connection.cursor() as cursor:
                    for command in sql_commands:
                        clean_command = command.strip()
                        
                        # 1. Abaikan baris kosong atau baris komentar
                        if not clean_command or clean_command.startswith('--'):
                            continue
                            
                        # 2. PENTING: Lewati perintah CREATE DATABASE dan USE agar tidak di-block oleh Aiven
                        if clean_command.upper().startswith('CREATE DATABASE') or clean_command.upper().startswith('USE '):
                            print(f"[Database Cloud] Melewati perintah lingkungan lokal: {clean_command[:30]}...")
                            continue
                        
                        # 3. Eksekusi perintah pembentukan tabel (CREATE TABLE, dsb.)
                        try:
                            cursor.execute(clean_command)
                        except Exception as sql_err:
                            print(f"[Database Warning] Perintah SQL gagal dieksekusi: {clean_command[:50]}... | Error: {sql_err}")
                                
            connection.commit()
            print("[Database] Berhasil inisialisasi seluruh tabel dari schema.sql otomatis!")
        else:
            print(f"[Database Warning] File schema.sql tidak ditemukan di lokasi: {schema_path}")
        # ----------------------------------------------------------------------

        # Seeder bawaan kelompokmu
        hashed_pw = generate_password_hash('admin123')
        seeded = ensure_default_admin(connection, hashed_pw)
        if seeded:
            print("[Seeder] Berhasil membuat user default: admin (password: admin123)")
            
        connection.close()
    except Exception as ex:
        print("[Warning] Gagal melakukan inisialisasi database otomatis:", ex)

    return app