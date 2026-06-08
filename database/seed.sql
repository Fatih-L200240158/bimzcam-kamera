-- ========================================================
-- DATA SEEDER AWAL: BimzCam Retro Digicam & Aksesoris
-- RDBMS: MySQL murni, tanpa ORM, menggunakan Raw SQL
-- ========================================================

USE bimzcam_db;

-- Seed User Admin (Username: admin, Password: admin123)
-- Hash PBKDF2 dari 'admin123'
-- Password Hash baru = 'scrypt:32768:8:1$77dElPGOnk2gSpXo$d6ebae730c6db27e6141ae4527c177d0f80ee559fc07d7a19a0115ac502fe00616442e306258d9b6bb9cf07b94b74c15ad2ed3d76e300e514a32ef5ce85aa334'
INSERT INTO users (username, password_hash) 
VALUES ('admin', 'scrypt:32768:8:1$uH3W5vA1f4g7$8ab88d7dfb2ee3a6b5a32ec4ee9e1ee10c85b54a72fa74ef5c03780f2eb1119f')
ON DUPLICATE KEY UPDATE id=id;

-- Seed Profil BimzCam
INSERT INTO profil_rental (nama, tentang, syarat_sewa, alamat, whatsapp, map_iframe)
VALUES (
    'BimzCam Digicam & Aksesoris',
    'Pusat penyewaan dan penjualan kamera digicam (digital vintage/pocket camera) serta aksesoris terlengkap di Solo. BimzCam menghadirkan keindahan estetika retro lo-fi khas digicam tahun 2000-an dengan unit yang terawat dan siap pakai. Kami menyediakan persewaan harian yang terjangkau serta unit digicam siap pakai yang bisa Anda beli untuk dikoleksi!',
    '1. Menyerahkan kartu identitas asli yang masih berlaku (KTP/KTM/SIM/KK) sebagai jaminan sewa.\n2. Pembayaran lunas di awal via transfer atau tunai sebelum serah terima unit digicam.\n3. Batas waktu sewa terhitung penuh 24 jam sejak unit diterima.\n4. Unit sewa digicam sudah lengkap dibekali baterai, memory card, dan card reader.\n5. Kerusakan atau kehilangan unit sewa menjadi tanggung jawab penuh penyewa sesuai kisaran kerugian.',
    'Jl. Letjen Suprapto No.45, Sumber, Kec. Banjarsari, Kota Surakarta, Jawa Tengah 57138',
    '6281234567890',
    'https://www.openstreetmap.org/export/embed.html?bbox=110.81200%2C-7.55000%2C110.82200%2C-7.54000&layer=mapnik&marker=-7.54472%2C110.81667'
)
ON DUPLICATE KEY UPDATE id=id;

-- Seed Kategori
INSERT INTO kategori (id, nama_kategori) VALUES (1, 'Digicam Vintage') ON DUPLICATE KEY UPDATE id=id;
INSERT INTO kategori (id, nama_kategori) VALUES (2, 'Modern Retro Pocket') ON DUPLICATE KEY UPDATE id=id;
INSERT INTO kategori (id, nama_kategori) VALUES (3, 'Aksesoris & Strap') ON DUPLICATE KEY UPDATE id=id;
INSERT INTO kategori (id, nama_kategori) VALUES (4, 'Memory Card & Kits') ON DUPLICATE KEY UPDATE id=id;

-- Seed Produk (Rentals and Sales)
INSERT INTO produk (id, kategori_id, nama_produk, deskripsi, harga_per_hari, gambar_url, tipe)
VALUES (
    1, 
    1, 
    'Sony Cyber-shot DSC-W350', 
    'Kamera saku vintage dengan sensor CCD legendaris yang menghasilkan tone warna hangat & mood retro khas 2000-an awal. Ringan, kompak, siap hunting!', 
    80000, 
    '/static/uploads/sony_a6400.png',
    'Sewa'
)
ON DUPLICATE KEY UPDATE id=id;

INSERT INTO produk (id, kategori_id, nama_produk, deskripsi, harga_per_hari, gambar_url, tipe)
VALUES (
    2, 
    1, 
    'Canon IXY Digital 930 IS (Full Set)', 
    'Unit digicam langka premium, kondisi super mulus 95%. Fungsi tombol, zoom, flash bekerja 100%. Kelengkapan box, strap, baterai dapet card reader!', 
    1450000, 
    '/static/uploads/canon_3000d.png',
    'Jual'
)
ON DUPLICATE KEY UPDATE id=id;

INSERT INTO produk (id, kategori_id, nama_produk, deskripsi, harga_per_hari, gambar_url, tipe)
VALUES (
    3, 
    3, 
    'Vintage Leather Camera Strap', 
    'Tali kamera gantungan kulit asli berkualitas tinggi buatan pengrajin lokal (handmade). Pas untuk digicam saku kesayangan menambah kesan retro estetik.', 
    125000, 
    '/static/uploads/sony_50mm.png',
    'Jual'
)
ON DUPLICATE KEY UPDATE id=id;

INSERT INTO produk (id, kategori_id, nama_produk, deskripsi, harga_per_hari, gambar_url, tipe)
VALUES (
    4, 
    4, 
    'SanDisk SD Card 8GB + Multi Reader', 
    'Paket sewa kartu memori andalan compatible penuh dengan speed digicam lawas, lengkap dengan OTG USB multi card reader praktis kirim ke handphone.', 
    15000, 
    '/static/uploads/sony_50mm.png',
    'Sewa'
)
ON DUPLICATE KEY UPDATE id=id;

INSERT INTO produk (id, kategori_id, nama_produk, deskripsi, harga_per_hari, gambar_url, tipe)
VALUES (
    5, 
    2, 
    'Samsung PL120 Dual View', 
    'Digicam unik layar ganda depan-belakang memudahkan swafoto/selfie jadul. Memberikan tone vintage digital yang asyik dikoleksi.', 
    100000, 
    '/static/uploads/sony_a6400.png',
    'Sewa'
)
ON DUPLICATE KEY UPDATE id=id;

INSERT INTO produk (id, kategori_id, nama_produk, deskripsi, harga_per_hari, gambar_url, tipe)
VALUES (
    6, 
    3, 
    'Y2K Pastel Beaded Wrist Strap', 
    'Tali gantungan manik-manik Y2K bernuansa pastel menggemaskan. Bikin outfit digicam saku Anda makin stylish, ceria, dan retro!', 
    35000, 
    '/static/uploads/sony_50mm.png',
    'Jual'
)
ON DUPLICATE KEY UPDATE id=id;

-- Seed Ulasan
INSERT INTO ulasan (produk_id, nama_pengulas, rating, komentar)
VALUES (
    1, 
    'Rian Hidayat', 
    5, 
    'Sewa digicam di BimzCam sangat memuaskan, unitnya bersih, dapet charger dan card reader juga jadi gampang mindahin foto langsung ke HP. Tone warnanya vintage banget!'
)
ON DUPLICATE KEY UPDATE id=id;

INSERT INTO ulasan (produk_id, nama_pengulas, rating, komentar)
VALUES (
    2, 
    'Siti Rahma', 
    5, 
    'Beli Canon IXY di BimzCam kondisinya bagus sekali seperti baru! Tombol responsif dan layarnya jernih. Memang vintage digicam andalan Solo!'
)
ON DUPLICATE KEY UPDATE id=id;
