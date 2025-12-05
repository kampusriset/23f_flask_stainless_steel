from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'secretkey123' 

USERNAME = 'admin'
PASSWORD = '12345'


@app.route('/')
def home():
    """Halaman utama - redirect ke dashboard jika sudah login"""
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Halaman dan proses login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == USERNAME and password == PASSWORD:
            session['username'] = username
            flash('Login berhasil!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Username atau password salah', 'error')
            return redirect(url_for('login'))
    
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    """Halaman dashboard - hanya bisa diakses setelah login"""
    if 'username' not in session:
        flash('Silakan login terlebih dahulu', 'error')
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', username=session['username'])


@app.route('/logout')
def logout():
    """Proses logout"""
    session.pop('username', None)
    flash('Anda telah logout', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)