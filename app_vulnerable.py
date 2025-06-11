from flask import Flask, request, jsonify
import sqlite3
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mi_clave_123'

def init_db():
    conn = sqlite3.connect('vulnerable.db')
    cursor = conn.cursor()
    
    # Tabla de usuarios
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

    # Tabla de productos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            fecha_creacion DATE DEFAULT CURRENT_DATE,
            precio_llegada REAL NOT NULL,
            precio_menudeo REAL NOT NULL,
            precio_mayoreo REAL NOT NULL
        )
    ''')

    # Insertamos usuarios de prueba
    cursor.execute("INSERT INTO users (username, password, email, birthdate, secret_question, secret_answer) SELECT 'admin', '1234', 'admin@gmail.com', '2000-07-24', '¿Pais donde naciste?', 'Mexico' WHERE NOT EXISTS (SELECT 1 FROM users WHERE username='admin')")
    
    # Insertamos productos de prueba
    cursor.execute("INSERT INTO productos (nombre, descripcion, precio_llegada, precio_menudeo, precio_mayoreo) SELECT 'Laptop HP', 'Laptop para oficina', 8000.00, 10000.00, 9500.00 WHERE NOT EXISTS (SELECT 1 FROM productos WHERE nombre='Laptop HP')")
    cursor.execute("INSERT INTO productos (nombre, descripcion, precio_llegada, precio_menudeo, precio_mayoreo) SELECT 'Mouse Logitech', 'Mouse inalambrico', 200.00, 300.00, 250.00 WHERE NOT EXISTS (SELECT 1 FROM productos WHERE nombre='Mouse Logitech')")

    conn.commit()
    conn.close()

# Funcion para verificar token
def verificar_token(f):
    @wraps(f)
    def decorador(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'No hay token'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except:
            return jsonify({'message': 'Token no valido'}), 401
        
        return f(*args, **kwargs)
    return decorador

@app.route('/user')
def get_user():
    username = request.args.get('username') or ''
    conn = sqlite3.connect('vulnerable.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()
    return jsonify({"user": user})

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    conn = sqlite3.connect('vulnerable.db')
    cursor = conn.cursor()

    query = f"SELECT * from users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)

    user = cursor.fetchone()
    if user:
        # Crear token que dura 5 minutos
        token = jwt.encode({
            'username': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
        }, app.config['SECRET_KEY'])
        
        conn.close()
        return jsonify({"message": "Login exitoso", "token": token})
    else:
        conn.close()
        return jsonify({"message": "Credenciales invalidas"}), 401

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

    query = f"INSERT INTO users (username, password, email, birthdate, secret_question, secret_answer) VALUES ('{username}', '{password}', '{email}', '{birthdate}', '{secret_question}', '{secret_answer}')"
    cursor.execute(query)
    
    conn.commit()
    conn.close()

    return jsonify({"message": "Usuario registrado exitosamente"})

@app.route('/update_user', methods=['POST'])
@verificar_token
def update_user():
    username = request.form['username']
    email = request.form['email']
    birthdate = request.form['birthdate']
    secret_question = request.form['secret_question']
    secret_answer = request.form['secret_answer']

    conn = sqlite3.connect('vulnerable.db')
    cursor = conn.cursor()

    query = f"UPDATE users SET email = '{email}', birthdate = '{birthdate}', secret_question = '{secret_question}', secret_answer = '{secret_answer}' WHERE username = '{username}'"
    cursor.execute(query)
    
    conn.commit()
    conn.close()

    return jsonify({"message": "Usuario actualizado exitosamente"})

@app.route('/delete_user', methods=['POST'])
@verificar_token
def delete_user():
    username = request.form['username']

    conn = sqlite3.connect('vulnerable.db')
    cursor = conn.cursor()

    query = f"DELETE FROM users WHERE username = '{username}'"
    cursor.execute(query)
    
    conn.commit()
    conn.close()

    return jsonify({"message": "Usuario eliminado exitosamente"})

# APIs para productos

@app.route('/productos', methods=['GET'])
@verificar_token
def obtener_productos():
    conn = sqlite3.connect('vulnerable.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    conn.close()
    
    lista_productos = []
    for p in productos:
        lista_productos.append({
            'id': p[0],
            'nombre': p[1],
            'descripcion': p[2],
            'fecha_creacion': p[3],
            'precio_llegada': p[4],
            'precio_menudeo': p[5],
            'precio_mayoreo': p[6]
        })
    
    return jsonify({"productos": lista_productos})

@app.route('/producto/<int:id>', methods=['GET'])
@verificar_token
def obtener_producto(id):
    conn = sqlite3.connect('vulnerable.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM productos WHERE id = {id}")
    producto = cursor.fetchone()
    conn.close()
    
    if producto:
        return jsonify({
            "producto": {
                'id': producto[0],
                'nombre': producto[1],
                'descripcion': producto[2],
                'fecha_creacion': producto[3],
                'precio_llegada': producto[4],
                'precio_menudeo': producto[5],
                'precio_mayoreo': producto[6]
            }
        })
    else:
        return jsonify({"message": "No encontrado"}), 404

@app.route('/productos', methods=['POST'])
@verificar_token
def crear_producto():
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio_llegada = request.form['precio_llegada']
    precio_menudeo = request.form['precio_menudeo']
    precio_mayoreo = request.form['precio_mayoreo']

    conn = sqlite3.connect('vulnerable.db')
    cursor = conn.cursor()
    query = f"INSERT INTO productos (nombre, descripcion, precio_llegada, precio_menudeo, precio_mayoreo) VALUES ('{nombre}', '{descripcion}', {precio_llegada}, {precio_menudeo}, {precio_mayoreo})"
    cursor.execute(query)
    conn.commit()
    conn.close()

    return jsonify({"message": "Producto agregado"})

@app.route('/producto/<int:id>', methods=['PUT'])
@verificar_token
def actualizar_producto(id):
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio_llegada = request.form['precio_llegada']
    precio_menudeo = request.form['precio_menudeo']
    precio_mayoreo = request.form['precio_mayoreo']

    conn = sqlite3.connect('vulnerable.db')
    cursor = conn.cursor()
    query = f"UPDATE productos SET nombre = '{nombre}', descripcion = '{descripcion}', precio_llegada = {precio_llegada}, precio_menudeo = {precio_menudeo}, precio_mayoreo = {precio_mayoreo} WHERE id = {id}"
    cursor.execute(query)
    conn.commit()
    conn.close()

    return jsonify({"message": "Producto actualizado"})

@app.route('/producto/<int:id>', methods=['DELETE'])
@verificar_token
def borrar_producto(id):
    conn = sqlite3.connect('vulnerable.db')
    cursor = conn.cursor()
    query = f"DELETE FROM productos WHERE id = {id}"
    cursor.execute(query)
    conn.commit()
    conn.close()

    return jsonify({"message": "Producto borrado"})

@app.route('/admin/data')
@verificar_token
def admin_data():
    return jsonify({"data": "Datos de admin"})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)