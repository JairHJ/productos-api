## Version Python
3.10.0

## Dependences to install
See requeriments.txt

## Steps to run
## 1. Instalación
Instalar Flask y PyJWT:
bashpip install -r requirements.txt

## 2. Ejecución
bashpython app.py

## 3. EndPoints
Endpoints
Login

POST /login - Iniciar sesión

username: admin
password: admin123

## Productos (necesitan token)

GET /productos - Ver todos los productos
GET /productos/<id> - Ver un producto
POST /productos - Crear producto
PUT /productos/<id> - Actualizar producto
DELETE /productos/<id> - Eliminar producto

## Campos de Producto

id: Número único
nombre: Texto obligatorio
descripcion: Texto opcional
fecha_creacion: Se pone automático
precio_llegada: Número obligatorio
precio_menudeo: Número obligatorio
precio_mayoreo: Número obligatorio

## Uso

Hacer login para obtener token
Usar token en header: Authorization: Bearer <token>
Token dura 5 minutos