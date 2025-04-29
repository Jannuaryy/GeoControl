from flask import Flask, render_template, redirect, url_for
import sqlite3

app = Flask(__name__)


# Подключение к базе данных
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    return redirect(url_for('locations'))


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
