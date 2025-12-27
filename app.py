from flask import Flask, render_template, request, redirect, url_for, flash, session
import pymysql
import random
import bcrypt
from datetime import datetime
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY') or os.getenv('FLASK_SECRET') or 'dev-secret-change-me'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = (os.getenv('FLASK_ENV', 'development') == 'production')

@app.template_filter('currency')
def currency(value):
    try:
        return f"{float(value):,.0f}"
    except Exception:
        return "0"

# Fungsi untuk koneksi database
def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'bimantara_db'),
        cursorclass=pymysql.cursors.DictCursor
    )

# Fungsi hash password
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(hashed_password, user_password):
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password.encode('utf-8'))

# Fungsi untuk membuat database dan tabel
def init_db():
    # Buat database jika belum ada
    conn = pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', '')
    )
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {os.getenv('DB_NAME', 'bimantara_db')}")
    conn.commit()
    conn.close()

    # Koneksi ke database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Tabel products (sudah ada - JANGAN DIUBAH)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INT PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(255) NOT NULL,
        slug VARCHAR(255) NOT NULL,
        price DECIMAL(10,2) NOT NULL
    )
    """)

    # Tabel orders (ditambah created_at, user_id, status, total_price)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INT PRIMARY KEY AUTO_INCREMENT,
        kd_order VARCHAR(255) NOT NULL,
        product_name VARCHAR(255) NOT NULL,
        quantity INT NOT NULL,
        customer_name VARCHAR(255) NOT NULL,
        address TEXT NOT NULL,
        contact VARCHAR(255) NOT NULL,
        user_id INT,
        status VARCHAR(50) DEFAULT 'pending',
        total_price DECIMAL(10,2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Tabel users (tambahan baru)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        phone VARCHAR(20) NOT NULL,
        address TEXT NOT NULL,
        role ENUM('admin', 'pembeli') DEFAULT 'pembeli',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # (Safety) Tambah kolom jika belum ada (tidak gagal jika sudah ada)
    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN user_id INT")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN status VARCHAR(50) DEFAULT 'pending'")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN total_price DECIMAL(10,2)")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    except:
        pass

    # Cek dan tambah data produk jika belum ada (JANGAN DIUBAH)
    cursor.execute("SELECT COUNT(*) as cnt FROM products")
    if cursor.fetchone()['cnt'] == 0:
        cursor.executemany("INSERT INTO products (name, slug, price) VALUES (%s, %s, %s)", [
            ("Dandang 6kg", "dandang-6kg", 200000),
            ("Dandang 8kg", "dandang-8kg", 300000),
            ("Dandang 10kg", "dandang-10kg", 500000)
        ])
        conn.commit()

    # Cek apakah ada admin
    cursor.execute("SELECT COUNT(*) as cnt FROM users WHERE role = 'admin'")
    if cursor.fetchone()['cnt'] == 0:
        admin_password = hash_password("admin123")
        cursor.execute("""
            INSERT INTO users (name, email, password, phone, address, role) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, ("Administrator", "admin@bimantara.com", admin_password, "081234567890", "Jl. Industri No. 123, Jakarta", "admin"))
        conn.commit()
    cursor.execute("UPDATE users SET role = 'admin' WHERE email = %s", ("admin@bimantara.com",))
    conn.commit()
    conn.close()

# Panggil fungsi untuk inisialisasi database
init_db()

# Middleware untuk check login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu!', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu!', 'danger')
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('Akses ditolak! Halaman untuk admin saja.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROUTE PUBLIC ====================

# Route untuk halaman utama
@app.route("/")
def index():
    return render_template("index.html")

# Route untuk halaman login
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Jika sudah login dan role admin saat GET -> redirect ke dashboard
    if 'user_id' in session and request.method == 'GET' and session.get('role') == 'admin':
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Email dan password wajib diisi!', 'danger')
            return render_template('login.html')

        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if not user:
                flash('Email atau password salah!', 'danger')
                return render_template('login.html')

            try:
                valid = check_password(user['password'], password)
            except Exception as e:
                print("Error saat verifikasi password:", e)
                flash('Terjadi kesalahan saat verifikasi password. Cek log server.', 'danger')
                return render_template('login.html')

            if valid:
                # Ganti session (bersihkan session lama jika ada)
                session.clear()
                session['user_id'] = user['id']
                session['name'] = user.get('name')
                session['email'] = user.get('email')
                session['role'] = user.get('role')
                session['phone'] = user.get('phone')
                session['address'] = user.get('address')
                session.modified = True

                flash('Login berhasil!', 'success')

                if user.get('role') == 'admin':
                    return redirect(url_for('dashboard'))
                else:
                    return redirect(url_for('index'))
            else:
                flash('Email atau password salah!', 'danger')
                return render_template('login.html')

        except Exception as e:
            print("Exception pada login:", e)
            flash('Terjadi kesalahan server saat login. Cek log terminal.', 'danger')
            return render_template('login.html')
        finally:
            if conn:
                conn.close()

    return render_template('login.html')

# Route untuk halaman register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        phone = request.form['phone']
        address = request.form['address']
        
        # Validasi
        if len(password) < 6:
            flash('Password minimal 6 karakter!', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Password tidak cocok!', 'danger')
            return render_template('register.html')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Cek apakah email sudah terdaftar
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            flash('Email sudah terdaftar!', 'danger')
            conn.close()
            return render_template('register.html')
        
        # Hash password dan simpan user
        hashed_password = hash_password(password)
        cursor.execute("""
            INSERT INTO users (name, email, password, phone, address, role) 
            VALUES (%s, %s, %s, %s, %s, 'pembeli')
        """, (name, email, hashed_password, phone, address))
        conn.commit()
        
        # Ambil user yang baru dibuat
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        new_user = cursor.fetchone()
        conn.close()
        
        # Auto login setelah register
        session['user_id'] = new_user['id']
        session['name'] = new_user['name']
        session['email'] = new_user['email']
        session['role'] = new_user['role']
        session['phone'] = new_user['phone']
        session['address'] = new_user['address']
        
        flash('Registrasi berhasil! Selamat datang ' + name, 'success')
        return redirect(url_for('index'))
    
    return render_template('register.html')

# Route untuk logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Logout berhasil!', 'success')
    return redirect(url_for('index'))

# Route untuk halaman produk (public)
@app.route('/product')
def product():
    # Jika admin, redirect ke dashboard section products
    if session.get('role') == 'admin':
        return redirect(url_for('dashboard') + '#section-products')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()

    return render_template('products.html', products=products)

# Route untuk checkout produk individual
@app.route('/checkout/<produk>')
@login_required
def checkout(produk):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE slug = %s", (produk,))
    product = cursor.fetchone()
    conn.close()

    if not product:
        flash('Produk tidak ditemukan!', 'danger')
        return redirect(url_for('product'))

    return render_template('checkout.html', product=product)

# Tambah item ke keranjang (POST)
@app.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    slug = request.form.get('slug')
    try:
        quantity = int(request.form.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE slug = %s", (slug,))
    product = cursor.fetchone()
    conn.close()

    if not product:
        flash('Produk tidak ditemukan.', 'danger')
        return redirect(request.referrer or url_for('product'))

    cart = session.get('cart', {})
    if slug in cart:
        cart[slug]['quantity'] += quantity
    else:
        cart[slug] = {
            'name': product['name'],
            'price': float(product['price']),
            'quantity': quantity,
            'slug': product['slug']
        }

    session['cart'] = cart
    flash(f"{product['name']} ditambahkan ke keranjang.", 'success')
    return redirect(request.referrer or url_for('product'))

# Lihat keranjang
@app.route('/cart')
@login_required
def view_cart():
    return redirect(url_for('profile'))

# Hapus item dari keranjang (POST)
@app.route('/cart/remove', methods=['POST'])
@login_required
def remove_from_cart():
    slug = request.form.get('slug')
    cart = session.get('cart', {})
    if slug in cart:
        cart.pop(slug, None)
        session['cart'] = cart
        flash('Item dihapus dari keranjang.', 'success')
    # redirect back to profile where embedded cart is shown
    return redirect(url_for('profile'))

# Checkout seluruh keranjang (membuat invoice_data untuk payment)
@app.route('/checkout/cart', methods=['GET', 'POST'])
@login_required
def checkout_cart():
    cart = session.get('cart', {})
    if not cart:
        flash('Keranjang kosong!', 'danger')
        return redirect(url_for('product'))

    # Buat ringkasan invoice di session (bisa dikembangkan untuk menyimpan multi-item)
    items = []
    total_price = 0
    for slug, it in cart.items():
        items.append({
            'slug': slug,
            'name': it['name'],
            'quantity': it['quantity'],
            'price': it['price'],
            'line_total': it['price'] * it['quantity']
        })
        total_price += it['price'] * it['quantity']

    session['invoice_data'] = {
        'cart_items': items,
        'total_price': total_price,
        'order_date': datetime.now().strftime('%d/%m/%Y %H:%M')
    }

    # Setelah men-setup invoice_data kita redirect ke page checkout
    return render_template('checkout.html', cart_items=items, total_price=total_price)

# Route untuk menangani pemesanan
@app.route("/place_order", methods=["POST"])
@login_required
def place_order():
    kd_order = random.randint(10000, 99999)
    product_name = request.form["product_name"]
    try:
        quantity = int(request.form["quantity"])
    except:
        flash("Jumlah tidak valid!", "danger")
        return redirect(url_for("product"))
    customer_name = request.form["customer_name"]
    address = request.form["address"]
    contact = request.form["contact"]
    try:
        price = float(request.form["price"])
    except:
        flash("Harga tidak valid!", "danger")
        return redirect(url_for("product"))
    slug = request.form.get("slug", "")
    total_price = quantity * price

    if not product_name or not quantity or not customer_name or not address or not contact:
        flash("Semua kolom harus diisi!", "danger")
        return redirect(url_for("checkout", produk=slug))

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO orders (kd_order, product_name, quantity, customer_name, address, contact, user_id, status, total_price)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (kd_order, product_name, quantity, customer_name, address, contact, session['user_id'], 'pending', total_price))
    
    conn.commit()
    conn.close()

    session["invoice_data"] = {
        "kd_order": kd_order,
        "product_name": product_name,
        "quantity": quantity,
        "customer_name": customer_name,
        "address": address,
        "contact": contact,
        "price": price,
        "total_price": total_price,
        "order_date": datetime.now().strftime('%d/%m/%Y %H:%M')
    }
    
    return redirect(url_for("payment"))

# Route untuk menangani pemesanan dari keranjang (multiple items)
@app.route("/place_cart_order", methods=["POST"])
@login_required
def place_cart_order():
    cart = session.get('cart', {})
    if not cart:
        flash("Keranjang kosong!", "danger")
        return redirect(url_for("product"))

    customer_name = request.form["customer_name"]
    address = request.form["address"]
    contact = request.form["contact"]

    if not customer_name or not address or not contact:
        flash("Semua kolom harus diisi!", "danger")
        return redirect(url_for("checkout_cart"))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Hitung total keseluruhan
    total_price = sum(it['price'] * it['quantity'] for it in cart.values())

    # Buat satu order untuk semua item di keranjang
    kd_order = random.randint(10000, 99999)
    # Gabungkan nama produk untuk product_name
    product_names = [it['name'] + f" (x{it['quantity']})" for it in cart.values()]
    product_name_combined = ", ".join(product_names)

    cursor.execute("""
        INSERT INTO orders (kd_order, product_name, quantity, customer_name, address, contact, user_id, status, total_price)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (kd_order, product_name_combined, 1, customer_name, address, contact, session['user_id'], 'pending', total_price))

    conn.commit()
    conn.close()

    # Buat invoice_data dengan detail item
    items = []
    for slug, it in cart.items():
        items.append({
            'slug': slug,
            'name': it['name'],
            'quantity': it['quantity'],
            'price': it['price'],
            'line_total': it['price'] * it['quantity']
        })

    session["invoice_data"] = {
        "kd_order": kd_order,
        "product_name": product_name_combined,
        "quantity": 1,  # Karena satu order untuk semua
        "customer_name": customer_name,
        "address": address,
        "contact": contact,
        "price": total_price,
        "total_price": total_price,
        "order_date": datetime.now().strftime('%d/%m/%Y %H:%M'),
        "cart_items": items  # Tambahkan detail item
    }

    return redirect(url_for("payment"))

# Route untuk halaman pembayaran
@app.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    payment_data = session.get("invoice_data")
    
    if not payment_data:
        flash('Tidak ada data pembayaran!', 'danger')
        return redirect(url_for('product'))
    
    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        
        # Simpan metode pembayaran ke session (bisa ditambahkan ke database jika perlu)
        session['payment_method'] = payment_method
        
        flash('Pembayaran berhasil! Pesanan Anda sedang diproses.', 'success')
        return redirect(url_for('invoice'))
    
    return render_template('payment.html', payment_data=payment_data)

# Route untuk halaman invoice
@app.route('/invoice')
@login_required
def invoice():
    invoice_data = session.get("invoice_data")
    
    if not invoice_data:
        flash('Tidak ada data invoice!', 'danger')
        return redirect(url_for('profile') + '#section-orders')
    
    # Hapus cart dari session setelah ditampilkan
    session.pop('cart', None)  # <-- Tambah baris ini untuk kosongkan keranjang
    session.modified = True  # Pastikan session diupdate
    
    flash("Pesanan berhasil dibuat!", "success")
    return render_template('invoice.html', invoice_data=invoice_data)

# Orders routes removed — orders are shown inside the `profile` page.

# Route untuk update profil
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        # Update profil user
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        
        cursor.execute("""
            UPDATE users SET name = %s, phone = %s, address = %s 
            WHERE id = %s
        """, (name, phone, address, session['user_id']))
        conn.commit()
        
        # Update session
        session['name'] = name
        session['phone'] = phone
        session['address'] = address
        
        flash('Profil berhasil diperbarui!', 'success')
        conn.close()
        return redirect(url_for('profile'))
    
    # Ambil data user
    cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()
    
    # Ambil daftar pesanan user (sesuai yang dipesan setelah pembayaran)
    cursor.execute("""
        SELECT * FROM orders 
        WHERE user_id = %s 
        ORDER BY created_at DESC
    """, (session['user_id'],))
    orders = cursor.fetchall()
    
    # Hitung total pesanan
    total_orders = len(orders) if orders else 0
    
    conn.close()
    # Include cart from session so embedded cart section can render
    cart = session.get('cart', {})
    subtotal = sum(item['price'] * item['quantity'] for item in cart.values()) if cart else 0

    return render_template('profile.html', user=user, orders=orders, total_orders=total_orders, cart=cart, subtotal=subtotal)

# ==================== ROUTE ADMIN ====================

# Route untuk dashboard admin
@app.route('/dashboard')
@admin_required
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Hitung statistik
    cursor.execute("SELECT COUNT(*) as total_orders FROM orders")
    total_orders_row = cursor.fetchone()
    total_orders = total_orders_row['total_orders'] if total_orders_row and total_orders_row.get('total_orders') else 0
    
    cursor.execute("SELECT COUNT(*) as total_users FROM users")
    total_users_row = cursor.fetchone()
    total_users = total_users_row['total_users'] if total_users_row and total_users_row.get('total_users') else 0
    
    cursor.execute("SELECT COUNT(*) as total_products FROM products")
    total_products_row = cursor.fetchone()
    total_products = total_products_row['total_products'] if total_products_row and total_products_row.get('total_products') else 0
    
    # Hitung total pendapatan dari orders yang sudah selesai
    cursor.execute("SELECT SUM(total_price) as total_revenue FROM orders WHERE status = 'completed'")
    revenue_result = cursor.fetchone()
    total_revenue = 0
    if revenue_result and revenue_result.get('total_revenue') is not None:
        total_revenue = revenue_result['total_revenue']
    
    cursor.execute("""
        SELECT 
            o.*, 
            u.name as customer_name,
            COALESCE(o.total_price, 0) as total_price_fixed,
            DATE_FORMAT(o.created_at, '%d/%m/%Y %H:%i') as formatted_date
        FROM orders o 
        LEFT JOIN users u ON o.user_id = u.id 
        ORDER BY o.id DESC LIMIT 10
    """)
    recent_orders = cursor.fetchall()
    
    # Ambil produk
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    # Ambil semua users untuk section users
    cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
    all_users = cursor.fetchall()

    # Ambil semua pesanan untuk section orders
    cursor.execute("""
        SELECT o.*, u.name as customer_name, u.email, u.phone
        FROM orders o
        LEFT JOIN users u ON o.user_id = u.id
        ORDER BY o.id DESC
    """)
    all_orders = cursor.fetchall()

    # Statistik pesanan per status
    cursor.execute("""
        SELECT
            status,
            COUNT(*) as count
        FROM orders
        GROUP BY status
    """)
    status_stats = cursor.fetchall()

    conn.close()

    return render_template('dashboard.html',
                         total_orders=total_orders,
                         total_users=total_users,
                         total_products=total_products,
                         total_revenue=total_revenue,
                         recent_orders=recent_orders,
                         products=products,
                         all_users=all_users,
                         all_orders=all_orders,
                         status_stats=status_stats)

# Route untuk manajemen produk (admin only)
@app.route("/kelola-products")
@admin_required
def kelola_products():
    return redirect(url_for('dashboard') + '#section-products')

# Route untuk tambah produk (admin only)
@app.route("/kelola/products/kelola", methods=['GET', 'POST'])
@admin_required
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        slug = request.form['slug']
        price = float(request.form['price'])

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (name, slug, price)
            VALUES (%s, %s, %s)
        """, (name, slug, price))
        conn.commit()
        conn.close()

        flash('Produk berhasil ditambahkan!', 'success')
        return redirect(url_for('dashboard') + '#section-products')

    return redirect(url_for('dashboard') + '#section-products')

# Route untuk edit produk (admin only)
@app.route("/admin/products/edit/<int:product_id>", methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        slug = request.form['slug']
        price = float(request.form['price'])

        cursor.execute("""
            UPDATE products SET name = %s, slug = %s, price = %s
            WHERE id = %s
        """, (name, slug, price, product_id))
        conn.commit()
        conn.close()

        flash('Produk berhasil diupdate!', 'success')
        return redirect(url_for('dashboard') + '#section-products')

    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    conn.close()

    if not product:
        flash('Produk tidak ditemukan!', 'danger')
        return redirect(url_for('dashboard') + '#section-products')

    return redirect(url_for('dashboard') + '#section-products')

# Route untuk hapus produk (admin only)
@app.route("/admin/products/delete/<int:product_id>")
@admin_required
def delete_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Ambil produk dulu berdasarkan id
    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    if not product:
        flash('Produk tidak ditemukan!', 'danger')
        conn.close()
        return redirect(url_for('dashboard') + '#section-products')

    # Cek apakah produk ada di order berdasarkan nama produk
    cursor.execute("SELECT COUNT(*) as count FROM orders WHERE product_name = %s", (product['name'],))
    order_count_row = cursor.fetchone()
    order_count = order_count_row['count'] if order_count_row and order_count_row.get('count') else 0

    if order_count > 0:
        flash('Produk tidak dapat dihapus karena sudah ada dalam pesanan!', 'danger')
    else:
        cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
        conn.commit()
        flash('Produk berhasil dihapus!', 'success')

    conn.close()
    return redirect(url_for('dashboard') + '#section-products')



# Route untuk update status pesanan (admin only)
@app.route("/admin/orders/update_status/<int:order_id>", methods=['POST'])
@admin_required
def update_order_status(order_id):
    status = request.form['status']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Update status order
    cursor.execute("UPDATE orders SET status = %s WHERE id = %s", (status, order_id))
    conn.commit()
    conn.close()
    
    flash('Status pesanan berhasil diupdate!', 'success')
    return redirect(url_for('dashboard') + '#section-orders')

# Route untuk manajemen user (admin only)
@app.route("/admin/users")
@admin_required
def admin_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
    users = cursor.fetchall()
    conn.close()
    
    return render_template("admin_users.html", users=users)

# Route untuk update role user (admin only)
@app.route("/admin/users/update_role/<int:user_id>", methods=['POST'])
@admin_required
def update_user_role(user_id):
    role = request.form['role']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET role = %s WHERE id = %s", (role, user_id))
    conn.commit()
    conn.close()

    flash('Role user berhasil diupdate!', 'success')
    return redirect(url_for('dashboard') + '#section-users')





# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# ==================== RUN APP ====================

if __name__ == "__main__":
    app.run(debug=True, port=5000)
