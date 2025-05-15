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

    def is_valid_location(loc_str):
        try:
            parts = loc_str.split()
            if len(parts) != 2:
                return False
            lat, lon = map(float, parts)
            return -90 <= lat <= 90 and -180 <= lon <= 180
        except ValueError:
            return False

    if request.method == 'POST':
        for key, value in request.form.items():
            if '_' in key:
                field, office_id = key.split('_')[:2]
                if field in ['location', 'name'] and office_id.isdigit():
                    current_location = request.form.get(f'location_{office_id}', '').strip()
                    current_name = request.form.get(f'name_{office_id}', '').strip()
                    if not current_location and not current_name:
                        conn.execute('DELETE FROM Offices WHERE id = ?', (office_id,))
                        conn.commit()
                    else:
                        if field == 'name' and not current_name:
                            error_message = 'Некорректный ввод: введите строку в формате: широта долгота название'
                            break
                        if field == 'location' and not current_location and not is_valid_location(current_location):
                            error_message = 'Некорректный ввод: введите строку в формате: широта долгота название'
                            break
                        original = conn.execute(f'SELECT {field} FROM Offices WHERE id = ?', (office_id,)).fetchone()
                        if original and original[0] != value:
                            conn.execute(f'UPDATE Offices SET {field} = ? WHERE id = ?', (value, office_id))
                            error_message = 'Некорректный ввод: введите строку в формате: широта долгота название'
        new_location = request.form.get('new_location', '').strip()
        new_name = request.form.get('new_name', '').strip()

        if error_message or (new_location and not new_name) or (
                not new_location and new_name):
            error_message = 'Ошибка: для нового офиса нужно указать и координаты и название'
        else:
            if new_location and new_name:
                if not is_valid_location(new_location):
                    error_message = 'Ошибка: неверный формат координат для нового офиса'
                else:
                    conn.execute('INSERT INTO Offices (location, name) VALUES (?, ?)', (new_location, new_name))

            if not error_message:
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
