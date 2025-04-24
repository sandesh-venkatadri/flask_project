from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'

    def init_db():
        conn = sqlite3.connect('users.db')
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL)''')
        conn.close()

    init_db()

    @app.route('/')
    def home():
        return redirect(url_for('login'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            password = generate_password_hash(request.form['password'])

            try:
                with sqlite3.connect('users.db') as conn:
                    conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                flash("Registered successfully! Please login.", "success")
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash("Username already exists!", "danger")

        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password_input = request.form['password']

            with sqlite3.connect('users.db') as conn:
                user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

            if user and check_password_hash(user[2], password_input):
                session['username'] = username
                flash("Login successful!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid credentials", "danger")

        return render_template('login.html')

    @app.route('/dashboard')
    def dashboard():
        if 'username' not in session:
            flash("Please login first!", "warning")
            return redirect(url_for('login'))
        return render_template('dashboard.html', username=session['username'])

    @app.route('/logout')
    def logout():
        session.pop('username', None)
        flash("Logged out successfully!", "info")
        return redirect(url_for('login'))

    return app

# For Vercel handler
app = create_app()
