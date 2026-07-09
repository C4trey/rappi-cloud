# 📱 Rappi Cloud API - Documentación Completa

## 🎯 Descripción del Proyecto

**Rappi Cloud** es un sistema backend simulador de Rappi (plataforma de entregas) construido con **FastAPI**. El proyecto implementa una API REST que permite la creación y gestión de pedidos, autenticación de usuarios con JWT, roles de usuario (cliente y repartidor), y sincronización con AWS para el procesamiento de pedidos en la nube.

### Características Principales
- ✅ Autenticación y autorización con JWT
- ✅ Sistema de roles (cliente y repartidor)
- ✅ Gestión de pedidos completa
- ✅ Sincronización en tiempo real con AWS
- ✅ Base de datos SQLite local
- ✅ CORS habilitado para integraciones frontend
- ✅ Docker listo para producción

---

## 🏗️ Arquitectura del Proyecto

```
rappi-cloud/
├── main.py                    # Punto de entrada de la aplicación
├── requirements.txt           # Dependencias del proyecto
├── dockerfile                 # Configuración para contenedor Docker
├── .env                       # Variables de entorno
├── rappi.db                   # Base de datos SQLite
├── app/
│   ├── __init__.py
│   ├── api/                   # Rutas de la API
│   │   ├── auth.py           # Autenticación y registro
│   │   ├── orders.py         # Gestión de pedidos
│   │   └── driver.py         # Funcionalidades del repartidor
│   ├── core/                 # Configuración central
│   │   ├── database.py       # Conexión a BD
│   │   ├── security.py       # Funciones de seguridad (JWT, Hash)
│   │   └── config.py         # Configuración (vacío)
│   ├── models/               # Modelos Pydantic y SQLAlchemy
│   │   ├── user.py          # Modelos Pydantic de usuario
│   │   ├── user_db.py       # Modelo SQLAlchemy de usuario
│   │   ├── order.py         # Modelos Pydantic de pedido
│   │   └── order_db.py      # Modelo SQLAlchemy de pedido
│   └── services/             # Lógica de negocio
│       ├── auth_service.py  # Servicios de autenticación
│       └── order_service.py # Servicios de pedidos (vacío)
└── venv/                      # Entorno virtual Python
```

---

## 📚 Librerías Utilizadas

### Backend & Framework
| Librería | Versión | Propósito |
|----------|---------|----------|
| **fastapi** | 0.136.1 | Framework web moderno y rápido |
| **uvicorn** | 0.46.0 | Servidor ASGI para ejecutar FastAPI |
| **starlette** | 1.0.0 | Framework ASGI (base de FastAPI) |

### Autenticación & Seguridad
| Librería | Versión | Propósito |
|----------|---------|----------|
| **python-jose** | 3.5.0 | Manejo de tokens JWT |
| **bcrypt** | 5.0.0 | Hashing seguro de contraseñas |
| **passlib** | 1.7.4 | Gestión de contraseñas |
| **cryptography** | 49.0.0 | Operaciones criptográficas |

### Base de Datos & ORM
| Librería | Versión | Propósito |
|----------|---------|----------|
| **sqlalchemy** | (implícita) | ORM para BD relacional |

### Validación de Datos
| Librería | Versión | Propósito |
|----------|---------|----------|
| **pydantic** | 2.13.3 | Validación y serialización de datos |
| **pydantic_core** | 2.46.3 | Core de Pydantic v2 |
| **annotated-types** | 0.7.0 | Tipos anotados para Pydantic |
| **annotated-doc** | 0.0.4 | Documentación en anotaciones |

### HTTP & Comunicación
| Librería | Versión | Propósito |
|----------|---------|----------|
| **requests** | 2.34.2 | Cliente HTTP para llamadas a AWS |
| **httpx** | 0.28.1 | Cliente HTTP async |
| **httpcore** | 1.0.9 | Núcleo de HTTP |

### Cloud & AWS
| Librería | Versión | Propósito |
|----------|---------|----------|
| **boto3** | 1.43.2 | SDK de AWS para Python |
| **botocore** | 1.43.2 | Núcleo de AWS SDK |
| **s3transfer** | 0.17.0 | Transferencias a S3 |

### Configuración & Utilities
| Librería | Versión | Propósito |
|----------|---------|----------|
| **python-dotenv** | 1.2.2 | Carga de variables de entorno |
| **click** | 8.3.3 | CLI utilities |
| **colorama** | 0.4.6 | Colores en terminal |

### Soporte & Dependencias
| Librería | Versión | Propósito |
|----------|---------|----------|
| **anyio** | 4.13.0 | Abstracción async |
| **idna** | 3.13 | Codificación IDNA |
| **certifi** | 2026.4.22 | Certificados SSL |
| **urllib3** | 2.6.3 | HTTP avanzado |
| **charset-normalizer** | 3.4.7 | Normalización de charset |
| **jmespath** | 1.1.0 | Consultas JSON |
| **python-dateutil** | 2.9.0 | Utilidades de fechas |
| **rsa** | 4.9.1 | Criptografía RSA |
| **pyasn1** | 0.6.3 | Soporte ASN.1 |
| **ecdsa** | 0.19.2 | Algoritmo ECDSA |
| **pycparser** | 3.0 | Parser de C |
| **cffi** | 2.0.0 | Interface C extranjera |
| **six** | 1.17.0 | Compatibilidad Python 2/3 |
| **typing-inspection** | 0.4.2 | Inspección de tipos |
| **typing_extensions** | 4.15.0 | Extensiones de typing |
| **h11** | 0.16.0 | HTTP/1.1 |

---

## 🔐 Modelos de Datos

### Usuario (DBUser)
```python
class DBUser(Base):
    __tablename__ = "users"
    
    id: int              # ID único
    username: str        # Usuario único
    email: str          # Correo único
    hashed_password: str # Contraseña hasheada con bcrypt
    role: str           # "customer" o "driver"
```

### Pedido (DBOrder)
```python
class DBOrder(Base):
    __tablename__ = "orders"
    
    id: str             # ID del pedido (sincronizado con AWS)
    username: str       # Usuario que hizo el pedido
    driver_username: str # Repartidor asignado (nullable)
    total_price: float  # Precio total
    delivery_address: str # Dirección de entrega
    status: str         # Estado del pedido
```

### Estados de Pedido
- `RECEIVED` - Pedido recibido
- `WAITING_DELIVER` - Esperando a repartidor
- `ON_THE_WAY` - En camino
- `WAITING_RECEIVE` - Esperando confirmación del cliente
- `COMPLETED` - Completado

---

## 🔌 API Endpoints

### 🔑 AUTENTICACIÓN (auth.py)

#### 1. **Registro de Usuario**
```http
POST /api/register
Content-Type: application/json

{
  "username": "juan123",
  "email": "juan@example.com",
  "password": "Password123",
  "role": "customer"  // "customer" o "driver"
}
```
**Respuesta (201):**
```json
{
  "message": "Usuario juan123 registrado exitosamente"
}
```

#### 2. **Login / Obtener Token JWT**
```http
POST /api/login
Content-Type: application/x-www-form-urlencoded

username=juan123&password=Password123
```
**Respuesta (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 3. **Logout**
```http
POST /api/logout
Authorization: Bearer {token}
```
**Respuesta (200):**
```json
{
  "message": "Logout exitoso para el usuario juan123.",
  "instruction": "Por favor, elimina el token guardado en tu aplicación cliente."
}
```

---

### 📦 GESTIÓN DE PEDIDOS (orders.py)

#### 4. **Crear Pedido**
```http
POST /api/orders
Authorization: Bearer {token}
Content-Type: application/json

{
  "items": [
    {
      "product_id": "1",
      "name": "Pizza Margherita",
      "quantity": 2,
      "price": 15.99
    },
    {
      "product_id": "2",
      "name": "Coca Cola",
      "quantity": 1,
      "price": 2.99
    }
  ],
  "total_price": 34.97,
  "delivery_address": "Calle 123 #456, Apto 7"
}
```
**Respuesta (201):**
```json
{
  "message": "Pedido registrado",
  "order_id": "uuid-del-pedido-aws"
}
```

#### 5. **Obtener Estado del Pedido**
```http
GET /api/orders/{order_id}
Authorization: Bearer {token}
```
**Respuesta (200):**
```json
{
  "order_id": "uuid-del-pedido",
  "total": 34.97,
  "status": "ON_THE_WAY"
}
```

#### 6. **Confirmar Recepción del Pedido**
```http
POST /api/orders/{order_id}/confirm
Authorization: Bearer {token}
```
**Respuesta (200):**
```json
{
  "message": "Has confirmado la recepción."
}
```

#### 7. **Actualizar Estado desde AWS** (Webhook)
```http
POST /api/estado
Content-Type: application/json
X-Rappi-Secret: un-secreto-largo

{
  "tenant_id": "madamtusan",
  "order_id": "uuid-del-pedido",
  "status": "WAITING_DELIVER",
  "step": "ready",
  "worker_id": null,
  "timestamp": "2024-07-09T22:30:00Z"
}
```
**Respuesta (200):**
```json
{
  "message": "Estado actualizado exitosamente"
}
```

---

### 🚗 FUNCIONES DE REPARTIDOR (driver.py)

#### 8. **Listar Pedidos Disponibles**
```http
GET /api/driver/orders
Authorization: Bearer {token}  // Token de repartidor
```
**Respuesta (200):**
```json
[
  {
    "id": "uuid-1",
    "username": "juan123",
    "driver_username": null,
    "total_price": 34.97,
    "delivery_address": "Calle 123 #456",
    "status": "WAITING_DELIVER"
  }
]
```

#### 9. **Aceptar Pedido**
```http
POST /api/driver/orders/{order_id}/accept
Authorization: Bearer {token}  // Token de repartidor
```
**Respuesta (200):**
```json
{
  "message": "Has aceptado el pedido uuid-1. ¡Ve a entregarlo!"
}
```

#### 10. **Marcar Pedido como Entregado**
```http
POST /api/driver/orders/{order_id}/delivered
Authorization: Bearer {token}  // Token de repartidor
```
**Respuesta (200):**
```json
{
  "message": "Has entregado el pedido. Esperando confirmación del cliente."
}
```

---

## 🔄 Flujo de un Pedido

```
1. Cliente se registra        → POST /api/register
                ↓
2. Cliente inicia sesión      → POST /api/login (obtiene JWT)
                ↓
3. Cliente crea pedido        → POST /api/orders (sincroniza con AWS)
                ↓
4. AWS procesa & actualiza    → POST /api/estado (webhook)
                ↓
5. Repartidor ve pedidos      → GET /api/driver/orders
                ↓
6. Repartidor acepta          → POST /api/driver/orders/{id}/accept
                ↓
7. Repartidor entrega         → POST /api/driver/orders/{id}/delivered
                ↓
8. Cliente confirma recepción → POST /api/orders/{id}/confirm
                ↓
9. Pedido completado          ✅
```

---

## 🔐 Seguridad

### Autenticación JWT
- **Algoritmo**: HS256
- **Expiración**: 120 minutos
- **Método**: OAuth2 con Bearer Token

### Hashing de Contraseñas
- **Librería**: bcrypt
- **Salt**: Generado automáticamente
- **Verificación**: Segura mediante `bcrypt.checkpw()`

### Roles y Autorización
- **Customer**: Puede crear pedidos y confirmar entregas
- **Driver**: Puede ver pedidos disponibles, aceptarlos y marcar como entregados

---

## 🌐 Configuración de CORS

La API está configurada para aceptar solicitudes desde cualquier origen:
```python
CORSMiddleware(
    allow_origins=["*"],        # Permite cualquier origen
    allow_credentials=True,
    allow_methods=["*"],        # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],
)
```

---

## 📋 Variables de Entorno (.env)

```env
# AWS
AWS_API_GATEWAY_URL="https://2sockss934.execute-api.us-east-1.amazonaws.com"
RAPPI_SHARED_SECRET="un-secreto-largo"

# Entorno
ENVIRONMENT="development"

# JWT
SECRET_KEY="7YQX8vM4q2KpJf9LrN3dTzA6HsWcE1xB5yVuGmR8nPfKkC4Z"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=120
```

---

## 🚀 Instalación y Ejecución

### Requisitos
- Python 3.8+
- pip

### Pasos

1. **Clonar el repositorio**
```bash
git clone https://github.com/C4trey/rappi-cloud.git
cd rappi-cloud
```

2. **Crear entorno virtual**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Ejecutar la aplicación**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

5. **Acceder a la API**
- Docs Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- API: http://localhost:8000

---

## 🐳 Docker

### Construir imagen
```bash
docker build -t rappi-cloud:latest .
```

### Ejecutar contenedor
```bash
docker run -p 8000:8000 --env-file .env rappi-cloud:latest
```

---

## 📊 Base de Datos

La aplicación usa **SQLite** con la siguiente estructura:

### Tabla: users
| Columna | Tipo | Constraints |
|---------|------|-------------|
| id | INTEGER | PRIMARY KEY |
| username | STRING | UNIQUE, INDEX |
| email | STRING | UNIQUE, INDEX |
| hashed_password | STRING | - |
| role | STRING | DEFAULT: "customer" |

### Tabla: orders
| Columna | Tipo | Constraints |
|---------|------|-------------|
| id | STRING | PRIMARY KEY |
| username | STRING | INDEX |
| driver_username | STRING | NULLABLE |
| total_price | FLOAT | - |
| delivery_address | STRING | - |
| status | STRING | DEFAULT: "RECEIVED" |

---

## 🧪 Ejemplo de Uso Completo

```bash
# 1. Registrar usuario
curl -X POST "http://localhost:8000/api/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "carlos",
    "email": "carlos@email.com",
    "password": "Password123",
    "role": "customer"
  }'

# 2. Login
TOKEN=$(curl -X POST "http://localhost:8000/api/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=carlos&password=Password123" | jq -r '.access_token')

# 3. Crear pedido
curl -X POST "http://localhost:8000/api/orders" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [{"product_id": "1", "name": "Pizza", "quantity": 1, "price": 15.99}],
    "total_price": 15.99,
    "delivery_address": "Calle Principal 123"
  }'

# 4. Obtener estado del pedido
curl -X GET "http://localhost:8000/api/orders/ORDER_ID" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🐛 Troubleshooting

### Error: "No se pudieron validar las credenciales"
- Verifica que el token JWT sea válido y no haya expirado
- Usa el formato correcto: `Authorization: Bearer {token}`

### Error: "Usuario ya existe"
- El username o email ya está registrado en la base de datos

### Error: "Acceso denegado"
- Verifica que tu rol sea el correcto (driver vs customer)

### Error: "Error conectando con AWS"
- Verifica que `AWS_API_GATEWAY_URL` sea correcto en `.env`
- Verifica la conectividad a internet

---

## 📝 Notas de Desarrollo

- La BD SQLite se crea automáticamente en `rappi.db`
- Los tokens JWT expiran después de 120 minutos
- Las contraseñas se hashean con bcrypt (irreversible)
- La sincronización con AWS es en tiempo real mediante webhooks

---

## 👨‍💻 Autor

**C4trey** - Proyecto de simulador de Rappi con integración AWS

---

## 📄 Licencia

Este proyecto es de código abierto y disponible en GitHub.

---

## 🔗 Enlaces Útiles

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://www.sqlalchemy.org/)
- [JWT.io](https://jwt.io/)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [AWS API Gateway](https://docs.aws.amazon.com/apigateway/)

---

**Última actualización**: Julio 2026
