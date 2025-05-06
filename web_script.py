from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import hashlib

app = Flask(__name__)


# Подключение к базе данных
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def weak_hash_md5(password):
    return hashlib.md5(password.encode()).hexdigest()


@app.route('/', methods=['GET', 'POST'])
def logins():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM admins WHERE login = ?', (login,)).fetchall()
        conn.close()
        if user:
            if weak_hash_md5(password) == user[0][2]:
                return redirect(url_for('locations'))
        return render_template('login.html', error="Неверное имя пользователя или пароль")
    return render_template('login.html')


@app.route('/locations')
def locations():
    conn = get_db_connection()
    locations = conn.execute('SELECT * FROM Locations').fetchall()
    locations_with_users = []
    for location in locations:
        user = conn.execute('SELECT * FROM Users WHERE id = ?', (location['id_user'],)).fetchall()
        locations_with_users.append({'location': location, 'user': user[0]})
    conn.close()
    return render_template('locations.html', locations=locations_with_users)


@app.route('/offices')
def offices():
    conn = get_db_connection()
    offices = conn.execute('SELECT * FROM Offices').fetchall()
    conn.close()
    return render_template('offices.html', offices=offices)


@app.route('/admin')
def admin():
    return render_template('admin.html', offices=offices)


if __name__ == '__main__':
    app.run(debug=True)
