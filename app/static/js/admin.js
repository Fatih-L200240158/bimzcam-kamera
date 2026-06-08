/**
 * Script Frontend untuk Halaman Admin & CRUD BimzCam Digicam & Aksesoris
 * Menggunakan Native JS dengan Fetch API untuk integrasi penuh Express/Flask Server.
 */

document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("login-form");
  const authError = document.getElementById("auth-error");

  // ==========================================
  // 1. HALAMAN LOGIN ADMIN CLIENT FLOW
  // ==========================================
  if (loginForm) {
    loginForm.addEventListener("submit", (e) => {
      e.preventDefault();

      const usernameVal = document.getElementById("username").value;
      const passwordVal = document.getElementById("password").value;

      if (!usernameVal || !passwordVal) {
        showError("Username dan Password wajib diisi!");
        return;
      }

      fetch("/api/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username: usernameVal, password: passwordVal }),
      })
        .then((res) => {
          if (!res.ok) {
            return res.json().then((data) => {
              throw new Error(data.error || "Gagal masuk. Periksa kembali akun Anda.");
            });
          }
          return res.json();
        })
        .then((data) => {
          // Success
          window.location.href = "/admin.html";
        })
        .catch((err) => {
          showError(err.message);
        });
    });

    function showError(msg) {
      if (authError) {
        authError.style.display = "block";
        authError.textContent = msg;
      }
    }
  }


  // ==========================================
  // 2. PANEL ADMIN & OPERATIONS FLOW
  // ==========================================
  const adminLayout = document.querySelector(".admin-layout");
  if (adminLayout) {
    // Check session first
    fetch("/api/check-session")
      .then((res) => res.json())
      .then((data) => {
        if (!data.loggedIn) {
          window.location.href = "/login.html";
        } else {
          initAdminPanel();
        }
      })
      .catch((err) => {
        console.error("Gagal memeriksa sesi admin: ", err);
        window.location.href = "/login.html";
      });
  }

  function initAdminPanel() {
    let listCategories = [];
    let listProducts = [];
    let isEditMode = false;
    let currentEditProductId = null;

    const profileModal = document.getElementById('profile-modal');
    const btnMenuProfil = document.getElementById('menu-pengaturan-profil');
    const closeProfileModal = document.getElementById('close-profile-modal');
    const btnCancelProfile = document.getElementById('btn-cancel-profile');
    const profileForm = document.getElementById('profile-form');

    // 1. Fungsi Membuka Modal (Mengatasi Tombol Statis)
    if (btnMenuProfil && profileModal) {
        btnMenuProfil.addEventListener('click', () => {
            profileModal.classList.add('show');
            // Isi default username ke input saat modal terbuka
            const usernameInput = document.getElementById('profile-username');
            if (usernameInput) usernameInput.value = "admin"; 
        });
    }

    // 2. Fungsi Menutup Modal
    if (profileModal) {
        const closeModal = () => {
            profileModal.classList.remove('show');
            if (profileForm) profileForm.reset();
        };
        if (closeProfileModal) closeProfileModal.addEventListener('click', closeModal);
        if (btnCancelProfile) btnCancelProfile.addEventListener('click', closeModal);
    }

    // 3. Fungsi Kirim Data ke route/admin.py via Fetch PUT
    if (profileForm) {
        profileForm.addEventListener('submit', (e) => {
            e.preventDefault(); // Mencegah halaman reload

            const usernameValue = document.getElementById('profile-username').value;
            const passwordValue = document.getElementById('profile-password').value;

            // Membentuk payload JSON sesuai kebutuhan data.get() di Python
            const payload = {
                username: usernameValue,
                password: passwordValue
            };

            // Menembak endpoint @admin_bp.route('/api/admin/profile/update')
            fetch('/api/admin/profile/update', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json' // Wajib agar request.get_json() di Flask tidak None
                },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    alert("Gagal: " + data.error);
                } else {
                    alert("Profil admin berhasil diperbarui!");
                    profileModal.classList.remove('show');
                    profileForm.reset();
                    window.location.reload(); // Refresh halaman agar session baru terbaca
                }
            })
            .catch(err => {
                console.error("Error updating profile:", err);
                alert("Terjadi kesalahan koneksi ke server!");
            });
        });
    }
    
    // Load Metrics
    const loadMetrics = () => {
      fetch("/api/admin/summary")
        .then((res) => res.json())
        .then((sum) => {
          document.getElementById("metrics-products-count").textContent = sum.totalProduk;
          document.getElementById("metrics-reviews-count").textContent = sum.totalUlasan;
          document.getElementById("metrics-categories-count").textContent = sum.totalKategori;
        })
        .catch((err) => console.error("Error loading metrics: ", err));
    };

    // Helper for formatting Currency (IDR)
    const formatIDRVal = (num) => {
      return new Intl.NumberFormat("id-ID", {
        style: "currency",
        currency: "IDR",
        minimumFractionDigits: 0
      }).format(num);
    };

    // Load categories for dropdown selection
    const loadCategoriesDropdown = () => {
      fetch("/api/kategori")
        .then((res) => res.json())
        .then((cats) => {
          listCategories = cats;
          const selectElement = document.getElementById("form-kategori");
          if (selectElement) {
            selectElement.innerHTML = `<option value="">-- Pilih Kategori --</option>`;
            cats.forEach((cat) => {
              const opt = document.createElement("option");
              opt.value = cat.id;
              opt.textContent = cat.nama_kategori;
              selectElement.appendChild(opt);
            });
          }
        })
        .catch((err) => console.error("Error loading categories dropdown: ", err));
    };

    // Load & Render Products Table
    const loadProductsTable = () => {
      fetch("/api/produk")
        .then((res) => res.json())
        .then((prods) => {
          listProducts = prods;
          const tbody = document.getElementById("admin-products-tbody");
          if (!tbody) return;

          if (prods.length === 0) {
            tbody.innerHTML = `
              <tr>
                <td colspan="7" class="text-center" style="padding: 2rem;">
                  Belum ada data barang katalog. Klik '+ Tambah Katalog Baru' untuk mulai mengisinya.
                </td>
              </tr>
            `;
            return;
          }

          tbody.innerHTML = "";
          prods.forEach((prod, idx) => {
            const tr = document.createElement("tr");
            
            const isSewa = (prod.tipe !== "Jual");
            const tipeLabel = isSewa ? "SEWA" : "JUAL";
            const tipeClass = isSewa ? "badge-sewa" : "badge-jual";
            
            // Format pricing column label based on state
            const pricingLabel = isSewa 
              ? `${formatIDRVal(prod.harga_per_hari)}<span style="font-size:0.75rem; color:var(--text-secondary)">/hari</span>`
              : formatIDRVal(prod.harga_per_hari);

            tr.innerHTML = `
              <td style="font-family: var(--font-mono); font-size: 0.85rem;">${idx + 1}</td>
              <td><img src="${prod.gambar_url}" class="td-img" alt="${prod.nama_produk}" referrerPolicy="no-referrer"></td>
              <td><strong style="color: var(--text-primary); font-size: 0.95rem;">${prod.nama_produk}</strong></td>
              <td><span class="card-cat-badge ${tipeClass}" style="position:static; padding: 0.2rem 0.5rem; font-size: 0.7rem; font-weight:700;">${tipeLabel}</span></td>
              <td><span class="card-cat-badge" style="position:static; padding: 0.2rem 0.5rem; font-size: 0.7rem; opacity:0.8;">${prod.nama_kategori}</span></td>
              <td class="td-price">${pricingLabel}</td>
              <td>
                <div class="td-actions">
                  <button class="btn-action-edit" data-id="${prod.id}">Edit</button>
                  <button class="btn-action-delete" data-id="${prod.id}">Hapus</button>
                </div>
              </td>
            `;
            tbody.appendChild(tr);
          });

          // Mount event listeners for Edit & Delete inside table body
          tbody.querySelectorAll(".btn-action-edit").forEach((btn) => {
            btn.addEventListener("click", (e) => {
              const targetId = parseInt(e.target.getAttribute("data-id"));
              openEditModal(targetId);
            });
          });

          tbody.querySelectorAll(".btn-action-delete").forEach((btn) => {
            btn.addEventListener("click", (e) => {
              const targetId = parseInt(e.target.getAttribute("data-id"));
              if (confirm("Apakah Anda yakin ingin menghapus unit katalog ini dari database BimzCam?")) {
                deleteProduct(targetId);
              }
            });
          });
        })
        .catch((err) => console.error("Error loading products table: ", err));
    };

    // Init actions
    loadMetrics();
    loadCategoriesDropdown();
    loadProductsTable();

    // ==========================================
    // CRUD Operations Modals & Submissions
    // ==========================================
    const modal = document.getElementById("crud-modal");
    const modalTitle = document.getElementById("modal-title");
    const crudForm = document.getElementById("crud-form");
    const btnAddProduct = document.getElementById("btn-add-product");
    const btnCloseModal = document.querySelector(".btn-close-modal");
    const btnCancelModal = document.getElementById("btn-cancel-modal");

    if (btnAddProduct) {
      btnAddProduct.addEventListener("click", () => {
        isEditMode = false;
        currentEditProductId = null;
        modalTitle.textContent = "Tambah Produk/Katalog Baru";
        
        // Reset Form Fields
        crudForm.reset();
        document.getElementById("existing-gambar-url").value = "";
        document.getElementById("form-tipe").value = "Sewa";
        
        modal.classList.add("active");
      });
    }

    const closeModal = () => {
      modal.classList.remove("active");
      crudForm.reset();
    };

    if (btnCloseModal) btnCloseModal.addEventListener("click", closeModal);
    if (btnCancelModal) btnCancelModal.addEventListener("click", closeModal);

    // Open Edit Modal
    const openEditModal = (id) => {
      const prod = listProducts.find(p => p.id === id);
      if (!prod) return;

      isEditMode = true;
      currentEditProductId = prod.id;
      modalTitle.textContent = `Edit Unit: ${prod.nama_produk}`;

      // Populate Inputs
      document.getElementById("form-nama").value = prod.nama_produk;
      document.getElementById("form-tipe").value = prod.tipe || "Sewa";
      document.getElementById("form-kategori").value = prod.kategori_id;
      document.getElementById("form-deskripsi").value = prod.deskripsi;
      document.getElementById("form-harga").value = prod.harga_per_hari;
      document.getElementById("existing-gambar-url").value = prod.gambar_url;

      modal.classList.add("active");
    };

    // CRUD Form Submit Handler (Multipart for upload)
    if (crudForm) {
      crudForm.addEventListener("submit", (e) => {
        e.preventDefault();

        const nama = document.getElementById("form-nama").value;
        const tipe = document.getElementById("form-tipe").value;
        const kategori_id = document.getElementById("form-kategori").value;
        const deskripsi = document.getElementById("form-deskripsi").value;
        const harga = document.getElementById("form-harga").value;

        if (!nama || !tipe || !kategori_id || !deskripsi || !harga) {
          alert("Silakan lengkapi semua kolom wajib!");
          return;
        }

        const formData = new FormData();
        formData.append("nama_produk", nama);
        formData.append("tipe", tipe);
        formData.append("kategori_id", kategori_id);
        formData.append("deskripsi", deskripsi);
        formData.append("harga_per_hari", harga);
        
        const gambarInput = document.getElementById("form-gambar");
        if (gambarInput && gambarInput.files.length > 0) {
          formData.append("gambar", gambarInput.files[0]);
        } else {
          // Send existing fallback URL
          const existing = document.getElementById("existing-gambar-url").value;
          formData.append("existing_gambar", existing);
        }

        // Determine destination endpoint & method
        const url = isEditMode ? `/api/admin/produk/${currentEditProductId}` : "/api/admin/produk";
        const method = isEditMode ? "PUT" : "POST";

        // Flask matches standard method-override or standard multi-part methods
        // Flask can take PUT or POST method directly depending on configuration
        // In clean API blueprints, PUT /api/admin/produk/<id> accepts form-data parameters natively
        fetch(url, {
          method: method,
          body: formData,
        })
          .then((res) => {
            if (!res.ok) {
              return res.json().then((data) => {
                throw new Error(data.error || "Gagal memproses data unit!");
              });
            }
            return res.json();
          })
          .then((data) => {
            closeModal();
            loadProductsTable();
            loadMetrics();
          })
          .catch((err) => {
            alert("Error: " + err.message);
          });
      });
    }

    // Delete Product
    const deleteProduct = (id) => {
      fetch(`/api/admin/produk/${id}`, {
        method: "DELETE",
      })
        .then((res) => {
          if (!res.ok) {
            throw new Error("Gagal menghapus produk!");
          }
          return res.json();
        })
        .then((data) => {
          loadProductsTable();
          loadMetrics();
        })
        .catch((err) => {
          alert(err.message);
        });
    };

    // Logout Action
    const logoutBtn = document.getElementById("btn-admin-logout");
    if (logoutBtn) {
      logoutBtn.addEventListener("click", () => {
        if (confirm("Apakah Anda yakin ingin keluar dari panel admin BimzCam?")) {
          fetch("/api/logout", {
            method: "POST"
          })
            .then(() => {
              window.location.href = "/login.html";
            })
            .catch(() => {
              window.location.href = "/login.html";
            });
        }
      });
    }
  }
});


  // 1. Mobile Menu Burger Navigation
  const burgerMenu = document.getElementById("burger-menu");
  const navLinks = document.getElementById("nav-links");

  if (burgerMenu) {
    burgerMenu.addEventListener("click", () => {
      navLinks.classList.toggle("active");
      
      // Burger icon animation
      const spans = burgerMenu.querySelectorAll("span");
      spans.forEach((span, idx) => {
        if (navLinks.classList.contains("active")) {
          if (idx === 0) span.style.transform = "rotate(45deg) translate(5px, 5px)";
          if (idx === 1) span.style.opacity = "0";
          if (idx === 2) span.style.transform = "rotate(-45deg) translate(6px, -6px)";
        } else {
          span.style.transform = "none";
          span.style.opacity = "1";
        }
      });
    });
  }

  //tema
const themeToggle = document.querySelector('.theme-toggle');

// 1. Cek tema yang tersimpan di localStorage saat halaman pertama dimuat
const currentTheme = localStorage.getItem('theme') || 'dark'; // Default ke dark jika belum ada

// Terapkan tema saat ini ke tag <html>
document.documentElement.setAttribute('data-theme', currentTheme);

// Sesuaikan teks tombol di awal berdasarkan tema aktif
if (currentTheme === 'light') {
    themeToggle.textContent = 'Tema Gelap';
} else {
    themeToggle.textContent = 'Tema Terang';
}

// 2. Logika ketika tombol tema diklik
themeToggle.addEventListener('click', () => {
    let theme = document.documentElement.getAttribute('data-theme');
    
    if (theme === 'dark') {
        // Balik ke Mode Dark
        document.documentElement.setAttribute('data-theme', 'light');
        themeToggle.textContent = 'Tema Gelap';
        localStorage.setItem('theme', 'light');
    } else {
        // Balik ke Mode Light
        document.documentElement.setAttribute('data-theme', 'dark');
        themeToggle.textContent = 'Tema Terang';
        localStorage.setItem('theme', 'dark');
    }
});

// Contoh fungsi saat tombol "Simpan Perubahan" di klik admin
function simpanProfilBaru() {
    const usernameInput = document.getElementById('input-username').value;
    const passwordInput = document.getElementById('input-password').value; // Boleh dikosongkan jika gak mau ganti pw

    fetch('/api/admin/profile/update', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: usernameInput,
            password: passwordInput
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert(data.message);
            window.location.reload(); // Refresh halaman setelah sukses
        } else {
            alert("Error: " + data.error);
        }
    })
    .catch(err => console.error("Gagal koneksi:", err));
}