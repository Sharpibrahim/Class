from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database setup (SQLite)
def init_db():
    conn = sqlite3.connect('sharp_class.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT,
                        role TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS posts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        content TEXT,
                        video_url TEXT,
                        audio_url TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS comments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        post_id INTEGER,
                        username TEXT,
                        comment TEXT,
                        FOREIGN KEY(post_id) REFERENCES posts(id))''')
    conn.commit()
    conn.close()

# Initialize DB
init_db()

# Homepage route
@app.route('/')
def home():
    return render_template('index.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        hashed_password = generate_password_hash(password, method='sha256')

        conn = sqlite3.connect('sharp_class.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       (username, hashed_password, role))
        conn.commit()
        conn.close()

        return redirect(url_for('login'))

    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('sharp_class.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['username'] = user[1]
            session['role'] = user[3]
            if user[3] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            return 'Invalid username or password'

    return render_template('login.html')

# Admin Dashboard route
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    conn = sqlite3.connect('sharp_class.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()
    conn.close()

    return render_template('admin_dashboard.html', posts=posts)

# Student Dashboard route
@app.route('/student_dashboard')
def student_dashboard():
    if 'username' not in session or session['role'] != 'student':
        return redirect(url_for('login'))

    conn = sqlite3.connect('sharp_class.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()
    conn.close()

    return render_template('student_dashboard.html', posts=posts)

# Post a new message
@app.route('/post', methods=['POST'])
def post():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    content = request.form['content']
    video_url = request.form['video_url']
    audio_url = request.form['audio_url']

    conn = sqlite3.connect('sharp_class.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO posts (content, video_url, audio_url) VALUES (?, ?, ?)",
                   (content, video_url, audio_url))
    conn.commit()
    conn.close()

    return redirect(url_for('admin_dashboard'))

# Add a comment to a post
@app.route('/comment', methods=['POST'])
def comment():
    if 'username' not in session or session['role'] != 'student':
        return redirect(url_for('login'))

    post_id = request.form['post_id']
    comment = request.form['comment']
    username = session['username']

    conn = sqlite3.connect('sharp_class.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO comments (post_id, username, comment) VALUES (?, ?, ?)",
                   (post_id, username, comment))
    conn.commit()
    conn.close()

    return redirect(url_for('student_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)