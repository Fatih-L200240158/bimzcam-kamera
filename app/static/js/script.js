/**
 * Script Frontend untuk Halaman Publik BimzCam Digicam & Aksesoris
 * Menggunakan Native JavaScript murni untuk DOM Manipulation, Fetch API, dan Double Filtering (Kategori & Tipe).
 */

document.addEventListener("DOMContentLoaded", () => {
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

  // 2. Fetch Profil data & Populate
  let whatsappNumber = "6285158801421"; // default fallback

  fetch("/api/profil")
    .then((res) => res.json())
    .then((data) => {
      if (data) {
        whatsappNumber = data.whatsapp || "6285158801421";
        
        // Update elements
        document.querySelectorAll(".rental-nama").forEach(el => el.textContent = data.nama);
        document.getElementById("rental-tentang").textContent = data.tentang;
        document.getElementById("rental-alamat").textContent = data.alamat;

        // Render Syarat & Ketentuan (Split by newline into steps)
        const skContainer = document.getElementById("rental-sku-list");
        if (skContainer && data.syarat_sewa) {
          skContainer.innerHTML = "";
          const rules = data.syarat_sewa.split("\n");
          rules.forEach((rule) => {
            if (rule.trim()) {
              const firstDotIdx = rule.indexOf(".");
              let num = "✓";
              let text = rule;
              if (firstDotIdx !== -1 && firstDotIdx < 4) {
                num = rule.substring(0, firstDotIdx).trim();
                text = rule.substring(firstDotIdx + 1).trim();
              }

              const item = document.createElement("div");
              item.className = "sku-item";
              item.innerHTML = `
                <span class="sku-num">${num}</span>
                <p>${text}</p>
              `;
              skContainer.appendChild(item);
            }
          });
        }

        // Set WhatsApp links
        document.querySelectorAll(".contact-wa-link").forEach((link) => {
          link.href = `https://wa.me/${whatsappNumber}`;
        });

        // Set OpenStreetMap map iframe src
        const mapIframe = document.getElementById("rental-map-iframe");
        if (mapIframe && data.map_iframe) {
          mapIframe.src = data.map_iframe;
        }
      }
    })
    .catch((err) => console.error("Gagal memuat profil BimzCam: ", err));

  // 3. Helper Function to Format Currency (IDR)
  const formatIDR = (num) => {
    return new Intl.NumberFormat("id-ID", {
      style: "currency",
      currency: "IDR",
      minimumFractionDigits: 0
    }).format(num);
  };

  // 4. Fetch Products & Categories with Dual Filter State
  let allProducts = [];
  let activeCategory = "all";
  let activeType = "all";

  const renderProducts = () => {
    const grid = document.getElementById("catalog-grid");
    if (!grid) return;

    // Filter based on activeCategory AND activeType state
    const filteredProducts = allProducts.filter((prod) => {
      const categoryMatch = (activeCategory === "all" || prod.kategori_id.toString() === activeCategory);
      const typeMatch = (activeType === "all" || (prod.tipe || "Sewa") === activeType);
      return categoryMatch && typeMatch;
    });

    if (filteredProducts.length === 0) {
      grid.innerHTML = `
        <div style="grid-column: 1/-1; text-align: center; color: var(--text-secondary); padding: 4rem 0;">
          <p>Belum ada produk yang cocok dengan pilihan filter Anda.</p>
        </div>
      `;
      return;
    }

    grid.innerHTML = "";
    filteredProducts.forEach((prod) => {
      const card = document.createElement("div");
      card.className = "product-card";
      card.setAttribute("data-category-id", prod.kategori_id);
      
      const isForRent = (prod.tipe !== "Jual"); // default is rent
      const formattedPrice = formatIDR(prod.harga_per_hari);
      const typeBadgeClass = isForRent ? "badge-sewa" : "badge-jual";
      const typeBadgeLabel = isForRent ? "SEWA / RENTAL" : "DIJUAL / MILIKI";
      
      // WhatsApp message encoding based on type
      let encodedMsg = "";
      if (isForRent) {
        encodedMsg = encodeURIComponent(
          `Halo BimzCam!\n\nSaya ingin menyewa unit digicam/aksesoris berikut:\n` +
          `- *Unit*: ${prod.nama_produk}\n` +
          `- *Kategori*: ${prod.nama_kategori}\n` +
          `- *Durasi*: Harian (24 Jam)\n` +
          `- *Tarif*: ${formattedPrice}/hari\n\n` +
          `Apakah unit ini tersedia untuk disewa dalam waktu dekat? Terima kasih.`
        );
      } else {
        encodedMsg = encodeURIComponent(
          `Halo BimzCam!\n\nSaya tertarik untuk membeli unit berikut:\n` +
          `- *Unit*: ${prod.nama_produk}\n` +
          `- *Kategori*: ${prod.nama_kategori}\n` +
          `- *Harga*: ${formattedPrice}\n\n` +
          `Apakah unit ini masih ready stock dan siap dikirim? Terima kasih.`
        );
      }
      
      const waUrl = `https://wa.me/${whatsappNumber}?text=${encodedMsg}`;
      const actionButtonLabel = isForRent ? "Sewa Sekarang" : "Beli Sekarang / Tanya";

      card.innerHTML = `
        <div class="card-img-wrapper">
          <img src="${prod.gambar_url}" alt="${prod.nama_produk}" referrerPolicy="no-referrer">
          <span class="card-cat-badge">${prod.nama_kategori}</span>
          <span class="card-tipe-badge ${typeBadgeClass}">${typeBadgeLabel}</span>
        </div>
        <div class="product-details">
          <h3 style="margin-top: 0.25rem;">${prod.nama_produk}</h3>
          <p style="min-height: 50px;">${prod.deskripsi}</p>
          <div class="product-footer">
            <div class="price-box">
              <span class="price-title">${isForRent ? "Tarif Sewa" : "Harga Jual"}</span>
              <span class="price-value">${formattedPrice}${isForRent ? '<span class="price-unit">/hari</span>' : ""}</span>
            </div>
            <a href="${waUrl}" target="_blank" rel="noopener noreferrer" class="btn-rent-wa" id="rent-btn-${prod.id}">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
              </svg>
              ${actionButtonLabel}
            </a>
          </div>
        </div>
      `;
      grid.appendChild(card);
    });
  };

  // Fetch Categories & setup category filters
  fetch("/api/kategori")
    .then((res) => res.json())
    .then((categories) => {
      const filters = document.getElementById("catalog-filters");
      if (!filters) return;

      filters.innerHTML = `
        <button class="filter-btn active" data-category="all">Semua Kategori</button>
      `;

      categories.forEach((cat) => {
        const btn = document.createElement("button");
        btn.className = "filter-btn";
        btn.setAttribute("data-category", cat.id);
        btn.textContent = cat.nama_kategori;
        filters.appendChild(btn);
      });

      // Category toggle event handler
      filters.addEventListener("click", (e) => {
        if (e.target.classList.contains("filter-btn")) {
          filters.querySelectorAll(".filter-btn").forEach((btn) => btn.classList.remove("active"));
          e.target.classList.add("active");

          activeCategory = e.target.getAttribute("data-category");
          renderProducts();
        }
      });
    })
    .catch((err) => console.error("Gagal memuat kategori: ", err));

  // Handle Type Filter Event Toggle
  const typeFilters = document.getElementById("catalog-type-filters");
  if (typeFilters) {
    typeFilters.addEventListener("click", (e) => {
      if (e.target.classList.contains("filter-btn")) {
        typeFilters.querySelectorAll(".filter-btn").forEach((btn) => btn.classList.remove("active"));
        e.target.classList.add("active");

        activeType = e.target.getAttribute("data-type");
        renderProducts();
      }
    });
  }

  // Load Products and Render
  const loadProductCatalog = () => {
    fetch("/api/produk")
      .then((res) => res.json())
      .then((products) => {
        allProducts = products;
        renderProducts();
      })
      .catch((err) => console.error("Gagal memuat katalog produk: ", err));
  };
  loadProductCatalog();

  // 5. Fetch Reviews & Render
  fetch("/api/ulasan")
    .then((res) => res.json())
    .then((reviews) => {
      const reviewContainer = document.getElementById("reviews-grid");
      if (!reviewContainer) return;

      if (reviews.length === 0) {
        reviewContainer.innerHTML = `<p style="grid-column:1/-1; text-align:center; color:var(--text-secondary);">Belum ada ulasan.</p>`;
        return;
      }

      reviewContainer.innerHTML = "";
      reviews.forEach((rev) => {
        let starsStr = "";
        for (let i = 1; i <= 5; i++) {
          starsStr += (i <= rev.rating) ? "★" : "☆";
        }

        const reviewCard = document.createElement("div");
        reviewCard.className = "review-card";
        reviewCard.innerHTML = `
          <div class="review-header">
            <span class="reviewer-name">${rev.nama_pengulas}</span>
            <span class="rating-stars">${starsStr}</span>
          </div>
          <p class="review-comment">"${rev.komentar}"</p>
          <span class="reviewed-product">${rev.nama_produk || "Pembelian/Penyewaan Alat"}</span>
        `;
        reviewContainer.appendChild(reviewCard);
      });
    })
    .catch((err) => console.error("Gagal memuat ulasan pelanggan: ", err));
});


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
