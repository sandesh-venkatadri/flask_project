import os
import sqlite3
import logging
from flask import Flask, render_template, request, redirect, url_for, session, g

# Enable logging
logging.basicConfig(level=logging.DEBUG)

# Flask app creation
def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'  # Change this for production
    app.debug = True

    # Set DB path relative to root (not api/)
    DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'users.db')

    # Get or create DB connection
    def get_db():
        if 'db' not in g:
            g.db = sqlite3.connect(DB_PATH)
            g.db.row_factory = sqlite3.Row
        return g.db

    # Close DB after request
    @app.teardown_appcontext
    def close_db(error):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    # Initialize DB
    def init_db():
        with app.app_context():
            db = get_db()
            db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            ''')
            db.commit()

    init_db()

    # Home route
    @app.route('/')
    def home():
        return redirect(url_for('login'))

    # Login
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        try:
            if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']
                db = get_db()
                user = db.execute(
                    'SELECT * FROM users WHERE username = ? AND password = ?',
                    (username, password)
                ).fetchone()
                if user:
                    session['user_id'] = user['id']
                    return redirect(url_for('dashboard'))
                else:
                    return render_template('login.html', error='Invalid credentials')
            return render_template('login.html')
        except Exception as e:
            app.logger.error(f"Exception on /login: {e}")
            return "Internal Server Error", 500

    # Register
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        try:
            if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']
                db = get_db()
                try:
                    db.execute(
                        'INSERT INTO users (username, password) VALUES (?, ?)',
                        (username, password)
                    )
                    db.commit()
                    return redirect(url_for('login'))
                except sqlite3.IntegrityError:
                    return render_template('register.html', error='Username already exists')
            return render_template('register.html')
        except Exception as e:
            app.logger.error(f"Exception on /register: {e}")
            return "Internal Server Error", 500

    # Dashboard
    @app.route('/dashboard')
    def dashboard():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return render_template('dashboard.html')

    # Logout
    @app.route('/logout')
    def logout():
        session.pop('user_id', None)
        return redirect(url_for('login'))

    return app


# Global app object for Vercel
app = create_app()
