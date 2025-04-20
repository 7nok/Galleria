import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from PIL import Image

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a secure random key in production

# Configuration
UPLOAD_FOLDER = 'static/uploads'
THUMBNAIL_FOLDER = 'static/thumbnails'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
DATABASE = 'users.db'

# Ensure upload and thumbnail folders exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(THUMBNAIL_FOLDER):
    os.makedirs(THUMBNAIL_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (username TEXT PRIMARY KEY, password TEXT, is_admin INTEGER)''')
        # Create default admin user if not exists
        c.execute('''INSERT OR IGNORE INTO users (username, password, is_admin)
                     VALUES (?, ?, ?)''', 
                     ('admin', generate_password_hash('admin123'), 1))
        conn.commit()

def generate_thumbnail(original_path, thumbnail_path, size=(200, 200)):
    try:
        with Image.open(original_path) as img:
            img.thumbnail(size)
            img.save(thumbnail_path)
    except Exception as e:
        print(f"Error generating thumbnail: {e}")

@app.route('/')
def index():
    init_db()
    images = [f for f in os.listdir(UPLOAD_FOLDER) if allowed_file(f)]
    is_admin = session.get('is_admin', False)
    return render_template('index.html', images=images, is_admin=is_admin)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            c.execute('SELECT password, is_admin FROM users WHERE username = ?', (username,))
            user = c.fetchone()
            
            if user and check_password_hash(user[0], password):
                session['username'] = username
                session['is_admin'] = bool(user[1])
                flash('Login successful!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid credentials', 'error')
                
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('is_admin', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
def upload_file():
    if not session.get('is_admin'):
        flash('Admin access required', 'error')
        return redirect(url_for('index'))
        
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(request.url)
        
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(request.url)
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        thumbnail_path = os.path.join(THUMBNAIL_FOLDER, filename)
        file.save(file_path)
        generate_thumbnail(file_path, thumbnail_path)
        flash('File uploaded successfully', 'success')
        return redirect(url_for('index'))
        
    flash('Invalid file type', 'error')
    return redirect(request.url)

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    if not session.get('is_admin'):
        flash('Admin access required', 'error')
        return redirect(url_for('index'))
        
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    thumbnail_path = os.path.join(THUMBNAIL_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
        flash('File deleted successfully', 'success')
    else:
        flash('File not found', 'error')
    return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)