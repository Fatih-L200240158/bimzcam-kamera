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
    # Menentukan folder template dan static secara presisi agar tidak tersasar di serverless Vercel
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static'
    )

    # 1. Secret Key setup
    app.secret_key = os.environ.get('SECRET_KEY', 'bimzcam_secret_key_extremely_secure_773')

    # 2. Database configs (Murni membaca dari Environment Variables Vercel/Cloud)
    app.config['MYSQL_HOST'] = os.environ.get('DB_HOST', '127.0.0.1')
    app.config['MYSQL_USER'] = os.environ.get('DB_USER', 'root')
    app.config['MYSQL_PASSWORD'] = os.environ.get('DB_PASSWORD', 'rahasiafatih')
    app.config['MYSQL_DB'] = os.environ.get('DB_NAME', 'bimzcam_db')
    app.config['MYSQL_PORT'] = int(os.environ.get('DB_PORT', 3310))

    # 3. Setup uploads directory untuk tempat gambar katalog
    UPLOAD_FOLDER = os.path.join(app.root_path, 'static/uploads')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # 4. Register Blueprints (Rute halaman publik, autentikasi, dan panel admin)
    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    return app