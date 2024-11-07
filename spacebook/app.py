from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb
import bcrypt

app = Flask(__name__)
app.config.from_object('config.Config')

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Satyavan12@'
app.config['MYSQL_DB'] = 'spacebook'

mysql = MySQL(app)

# Routes
@app.route('/')
def index():
    return render_template('index.html')



@app.route('/home')
def home():
    if 'user_id' in session:
        return redirect(url_for('profile'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_username = request.form['email_or_username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s OR username=%s", (email_or_username, email_or_username))
        user = cur.fetchone()
        cur.close()
        if user:
            if bcrypt.checkpw(password.encode('utf-8'), user[8].encode('utf-8')):  # user[8] is the password column
                session['user_id'] = user[0]
                session['role'] = user[7]  # Store the role (user/admin)
                flash("Login successful!", "success")
                return redirect(url_for('profile'))
            else:
                flash('Invalid credentials, please try again.', 'danger')
                return render_template('login.html')
        else:
            flash("Invalid username/email or password", "danger")
            return render_template('login.html')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        profession = request.form['profession']
        bio = request.form['bio']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, age, gender, profession, bio, email, username, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (name, age, gender, profession, bio, email, username, hashed_password))
        mysql.connection.commit()
        cur.close()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/post', methods=['POST'])
def post():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    content = request.form['content']
    
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO posts (user_id, content) VALUES (%s, %s)", (user_id, content))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('profile'))

@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM posts WHERE user_id = %s", (user_id,))
    cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
    mysql.connection.commit()
    cur.close()

    session.clear()
    flash('Your account has been deleted successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'is_admin' in session and session['is_admin']:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Execute queries
        cur.execute("SELECT COUNT(*) AS total_users FROM users;")
        total_users = cur.fetchone()['total_users']

        cur.execute("SELECT COUNT(*) AS male_users FROM users WHERE gender = 'male';")
        male_users = cur.fetchone()['male_users']

        cur.execute("SELECT COUNT(*) AS female_users FROM users WHERE gender = 'female';")
        female_users = cur.fetchone()['female_users']

        cur.execute("SELECT COUNT(*) AS total_posts FROM posts;")
        total_posts = cur.fetchone()['total_posts']

        cur.execute("""
            SELECT u.username, COUNT(p.id) AS post_count
            FROM users u
            LEFT JOIN posts p ON u.id = p.user_id
            GROUP BY u.id;
        """)
        user_posts = cur.fetchall()

        cur.close()

        return render_template(
            'dashboard.html', 
            total_users=total_users, 
            male_users=male_users, 
            female_users=female_users, 
            total_posts=total_posts, 
            user_posts=user_posts
        )
    else:
        flash('Unauthorized access')
        return redirect(url_for('index'))


@app.route('/logout')
def logout():
    # Clear the session to log the user out
    session.clear()  # This will clear all session data

    # Redirect to the homepage after logging out
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    cur = mysql.connection.cursor()
    
    # Get user info
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    
    # Get posts by this user
    cur.execute("SELECT * FROM posts WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    posts = cur.fetchall()
    cur.close()

    # Set session data to display user info in the profile
    session['username'] = user[7]  # username
    session['name'] = user[1]  # name
    session['age'] = user[2]  # age
    session['gender'] = user[3]  # gender
    session['profession'] = user[4]  # profession
    session['bio'] = user[5]  # bio

    return render_template('profile.html', posts=posts)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the entered credentials match MySQL root credentials
        if username == 'root' and password == 'Satyavan12@':
            session['username'] = username
            session['is_admin'] = True  # Set an admin flag in the session
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid admin credentials')
    
    return render_template('admin_login.html')

@app.route('/admin_logout')
def admin_logout():
    session.clear()  # Clears all session data
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
