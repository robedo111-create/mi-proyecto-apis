from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import re

# --- Configuración JWT ---
SECRET_KEY = "mi-clave-secreta-super-segura-cambiar-en-produccion"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Configuración de seguridad ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(title="Mi API con Autenticación")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Base de datos SQLite ---
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'posts.db')
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# Crear tablas si no existen
cursor.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        body TEXT NOT NULL,
        userId INTEGER NOT NULL
    )
''')

# Tabla de usuarios
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL
    )
''')
conn.commit()

# --- Modelos ---
class PostCreate(BaseModel):
    title: str
    body: str
    userId: int

class PostResponse(PostCreate):
    id: int

class UserCreate(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- Funciones de autenticación ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user_by_email(email: str):
    cursor.execute("SELECT id, email, hashed_password FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    if user:
        return {"id": user[0], "email": user[1], "hashed_password": user[2]}
    return None

def authenticate_user(email: str, password: str):
    user = get_user_by_email(email)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

# --- ENDPOINTS DE AUTENTICACIÓN ---

@app.post("/register", response_model=Token)
def register(user: UserCreate):
    # Validar email
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", user.email):
        raise HTTPException(status_code=400, detail="Email inválido")
    if len(user.password) < 6:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 6 caracteres")
    
    # Verificar si el usuario ya existe
    if get_user_by_email(user.email):
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    # Crear usuario
    hashed = get_password_hash(user.password)
    cursor.execute(
        "INSERT INTO users (email, hashed_password) VALUES (?, ?)",
        (user.email, hashed)
    )
    conn.commit()
    
    # Crear token
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return {"id": current_user["id"], "email": current_user["email"]}

# --- ENDPOINTS DE POSTS (protegidos) ---

@app.get("/posts", response_model=List[PostResponse])
def obtener_posts(current_user: dict = Depends(get_current_user)):
    cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()
    return [{"id": row[0], "title": row[1], "body": row[2], "userId": row[3]} for row in posts]

@app.get("/posts/{post_id}", response_model=PostResponse)
def obtener_post(post_id: int, current_user: dict = Depends(get_current_user)):
    cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    return {"id": post[0], "title": post[1], "body": post[2], "userId": post[3]}

@app.post("/posts", response_model=PostResponse, status_code=201)
def crear_post(post: PostCreate, current_user: dict = Depends(get_current_user)):
    cursor.execute(
        "INSERT INTO posts (title, body, userId) VALUES (?, ?, ?)",
        (post.title, post.body, post.userId)
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    return {"id": nuevo_id, "title": post.title, "body": post.body, "userId": post.userId}

@app.put("/posts/{post_id}", response_model=PostResponse)
def actualizar_post(post_id: int, post: PostCreate, current_user: dict = Depends(get_current_user)):
    cursor.execute(
        "UPDATE posts SET title = ?, body = ?, userId = ? WHERE id = ?",
        (post.title, post.body, post.userId, post_id)
    )
    conn.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    return {"id": post_id, "title": post.title, "body": post.body, "userId": post.userId}

@app.delete("/posts/{post_id}")
def eliminar_post(post_id: int, current_user: dict = Depends(get_current_user)):
    cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    return {"mensaje": f"Post {post_id} eliminado"}

# --- Endpoint raíz ---
@app.get("/")
def root():
    return {"mensaje": "API con autenticación funcionando. Ve a /docs para probarla"}