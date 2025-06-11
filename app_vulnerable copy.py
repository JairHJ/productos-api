from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

app.config['DEBUG'] = True

def init_db():
    conn = sqlite3.connect('vulnerable.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            birthdate DATE,
            status TEXT DEFAULT 'active',
            secret_question TEXT,
            secret_answer TEXT
        )
    ''')

# Insertamos usuarios de prueba
    cursor.execute("INSERT INTO users (username, password, email, birthdate, secret_question, secret_answer) SELECT 'admin', '1234', 'admin@gmail.com', '2000-07-24', '¿Pais donde naciste?', 'Mexico' WHERE NOT EXISTS (SELECT 1 FROM users WHERE username='admin')")
 

    conn.commit()
    conn.close()

@app.route('/user')
def get_user():
    username = request.args.get('username') or ''
    conn = sqlite3.connect('vulnerable.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    user = cursor.fetchone()
    return jsonify({"user": user})



@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Inyeccion SQL + autienticacion insegura
    query =  f"SELECT * from users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)

    user = cursor.fetchone()
    if user:
        return jsonify({"message": "Inicio de sesion exitoso"})
    else:
        return jsonify({"message": "Credenciales invalidas"}), 401
    conn.close()
    
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    birthdate = request.form['birthdate']
    secret_question = request.form['secret_question']
    secret_answer = request.form['secret_answer']

    conn = sqlite3.connect('vulnerable.db')
    cursor = conn.cursor()

    # Inyeccion SQL + autienticacion insegura
    query = f"INSERT INTO users (username, password, email, birthdate, secret_question, secret_answer) VALUES ('{username}', '{password}', '{email}', '{birthdate}', '{secret_question}', '{secret_answer}')"
    cursor.execute(query)
    
    conn.commit()
    conn.close()

    return jsonify({"message": "Usuario registrado exitosamente"})

@app.route('/update_user', methods=['POST'])
def update_user():
    username = request.form['username']
    email = request.form['email']
    birthdate = request.form['birthdate']
    secret_question = request.form['secret_question']
    secret_answer = request.form['secret_answer']

    conn = sqlite3.connect('vulnerable.db')
    cursor = conn.cursor()

    # Inyeccion SQL + autienticacion insegura
    query = f"UPDATE users SET email = '{email}', birthdate = '{birthdate}', secret_question = '{secret_question}', secret_answer = '{secret_answer}' WHERE username = '{username}'"
    cursor.execute(query)
    
    conn.commit()
    conn.close()

    return jsonify({"message": "Usuario actualizado exitosamente"})

@app.route('/delete_user', methods=['POST'])
def delete_user():
    username = request.form['username']

    conn = sqlite3.connect('vulnerable.db')
    cursor = conn.cursor()

    # Inyeccion SQL + autienticacion insegura
    query = f"DELETE FROM users WHERE username = '{username}'"
    cursor.execute(query)
    
    conn.commit()
    conn.close()

    return jsonify({"message": "Usuario eliminado exitosamente"})


@app.route('/admin/data')
def admin_data():
    return jsonify({"data": "Datos confidenciales de admin, Acceso denegado!"})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
    
