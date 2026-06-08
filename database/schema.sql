-- ========================================================
-- DATABASE DDL (SCHEMA): BimzCam Retro Digicam & Aksesoris
-- RDBMS: MySQL murni, tanpa ORM, menggunakan Raw SQL
-- ========================================================

CREATE DATABASE IF NOT EXISTS bimzcam_db;
USE bimzcam_db;

-- 1. Membuat Tabel 'users' untuk Administrator
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

-- 2. Membuat Tabel 'profil_rental' (Profil Usaha BimzCam)
CREATE TABLE IF NOT EXISTS profil_rental (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama VARCHAR(150) NOT NULL,
    tentang TEXT NOT NULL,
    syarat_sewa TEXT NOT NULL,
    alamat VARCHAR(255) NOT NULL,
    whatsapp VARCHAR(20) NOT NULL,
    map_iframe TEXT NOT NULL
);

-- 3. Membuat Tabel 'kategori'
CREATE TABLE IF NOT EXISTS kategori (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama_kategori VARCHAR(100) UNIQUE NOT NULL
);

-- 4. Membuat Tabel 'produk' (Katalog dengan Tipe Jual/Sewa)
CREATE TABLE IF NOT EXISTS produk (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kategori_id INT NOT NULL,
    nama_produk VARCHAR(150) NOT NULL,
    deskripsi TEXT NOT NULL,
    harga_per_hari INT NOT NULL, -- Diartikan sebagai tarif sewa per hari atau harga jual langsung
    gambar_url VARCHAR(255) NOT NULL,
    tipe VARCHAR(50) NOT NULL DEFAULT 'Sewa', -- Tipe: 'Sewa' (Rental) atau 'Jual' (Catalog Penjualan)
    FOREIGN KEY (kategori_id) REFERENCES kategori(id) ON DELETE CASCADE
);

-- 5. Membuat Tabel 'ulasan'
CREATE TABLE IF NOT EXISTS ulasan (
    id INT AUTO_INCREMENT PRIMARY KEY,
    produk_id INT,
    nama_pengulas VARCHAR(100) NOT NULL,
    rating INT NOT NULL,
    komentar TEXT NOT NULL,
    FOREIGN KEY (produk_id) REFERENCES produk(id) ON DELETE CASCADE
);
