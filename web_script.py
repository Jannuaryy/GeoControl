from flask import Flask, render_template, request, redirect, url_for
import hashlib
from db_connection import *

app = Flask(__name__)


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
        office = conn.execute('SELECT * FROM Offices WHERE id = ?', (location['id_office'],)).fetchall()
        locations_with_users.append({'location': location, 'user': user[0], 'office': next(iter(office), {'name': 'None'})})
    conn.close()
    return render_template('locations.html', locations=locations_with_users)


@app.route('/offices', methods=['GET', 'POST'])
def offices():
    conn = get_db_connection()
    error_message = None
    if request.method == 'POST':
        has_empty_cells = False
        for key, value in request.form.items():
            if key.startswith('location_') or key.startswith('name_'):
                if not value.strip():
                    has_empty_cells = True
                    break
        new_location = request.form.get('new_location', '').strip()
        new_name = request.form.get('new_name', '').strip()
        if (has_empty_cells or (new_location and not new_name) or (not new_location and new_name)) and not (
                not new_location and not new_name):
            error_message = 'Некорректный ввод: введите строку в формате: широта, долгота название'
        else:
            for key, value in request.form.items():
                parts = key.split('_')
                what, office_id = parts
                if what == 'location':
                    value = value.strip()
                    if value:
                        try:
                            lat, lon = value.split()
                            lat = lat.strip(',') # очистить запятую, если пользователь скопировал точку из карт, а там через запятую
                            lon = lon.strip(',')
                            value = '{} {}'.format(lat, lon)
                        except:
                            pass
                    conn.execute('UPDATE Offices SET location = ? WHERE id = ?', (value, office_id))
                elif what == 'name':
                    conn.execute('UPDATE Offices SET name = ? WHERE id = ?', (value, office_id))
            if new_location and new_name:
                new_location = new_location.strip()
                if new_location:
                    try:
                        lat, lon = new_location.split()
                        lat = lat.strip(',') # очистить запятую, если пользователь скопировал точку из карт, а там через запятую
                        lon = lon.strip(',')
                        new_location = '{} {}'.format(lat, lon)
                    except:
                        pass
                conn.execute('INSERT INTO Offices (location, name) VALUES (?, ?)', (new_location, new_name))
            conn.execute(
                'DELETE FROM Offices WHERE (location = "" OR location IS NULL) AND (name = "" OR name IS NULL)')
            conn.commit()
            return redirect(url_for('offices'))
    offices = conn.execute('SELECT * FROM Offices').fetchall()
    conn.close()
    return render_template('offices.html', offices=offices, error_message=error_message)


@app.route('/admin')
def admin():
    return render_template('admin.html', offices=offices)


if __name__ == '__main__':
    app.run(debug=True)
