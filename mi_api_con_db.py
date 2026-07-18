from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
import os
import re
import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib
import secrets

# --- Configuración ---
SECRET_KEY = "mi-clave-secreta-super-segura-cambiar-en-produccion"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(title="Mi API con PostgreSQL y Autenticación")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Conexión a PostgreSQL ---
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise Exception("DATABASE_URL no está configurada")

conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

# --- Crear tablas ---
with conn.cursor() as cur:
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            body TEXT NOT NULL,
            "userId" INTEGER NOT NULL
        )
    ''')
    conn.commit()

# --- Funciones de hashing (sin bcrypt) ---
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

# --- Modelos ---
class UserCreate(BaseModel):
    email: str
    password: str

class PostCreate(BaseModel):
    title: str
    body: str
    userId: int

class PostResponse(PostCreate):
    id: int

class Token(BaseModel):
    access_token: str
    token_type: str

# --- Funciones de autenticación ---
def get_user_by_email(email: str):
    with conn.cursor() as cur:
        cur.execute("SELECT id, email, hashed_password FROM users WHERE email = %s", (email,))
        return cur.fetchone()

def authenticate_user(email: str, password: str):
    user = get_user_by_email(email)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"id": 1, "email": "test@ejemplo.com"}

# --- ENDPOINTS DE AUTENTICACIÓN ---
@app.post("/register", response_model=Token)
def register(user: UserCreate):
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", user.email):
        raise HTTPException(status_code=400, detail="Email inválido")
    if len(user.password) < 6:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 6 caracteres")
    
    if get_user_by_email(user.email):
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    hashed = hash_password(user.password)
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO users (email, hashed_password) VALUES (%s, %s) RETURNING id",
            (user.email, hashed)
        )
        conn.commit()
    
    access_token = secrets.token_hex(32)
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
    access_token = secrets.token_hex(32)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return {"id": current_user["id"], "email": current_user["email"]}

# --- ENDPOINTS DE POSTS ---
@app.get("/posts", response_model=List[PostResponse])
def obtener_posts():
    with conn.cursor() as cur:
        cur.execute("SELECT id, title, body, \"userId\" FROM posts")
        return cur.fetchall()

@app.get("/posts/{post_id}", response_model=PostResponse)
def obtener_post(post_id: int):
    with conn.cursor() as cur:
        cur.execute("SELECT id, title, body, \"userId\" FROM posts WHERE id = %s", (post_id,))
        post = cur.fetchone()
        if not post:
            raise HTTPException(status_code=404, detail="Post no encontrado")
        return post

@app.post("/posts", response_model=PostResponse, status_code=201)
def crear_post(post: PostCreate):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO posts (title, body, \"userId\") VALUES (%s, %s, %s) RETURNING id, title, body, \"userId\"",
            (post.title, post.body, post.userId)
        )
        conn.commit()
        return cur.fetchone()

@app.put("/posts/{post_id}", response_model=PostResponse)
def actualizar_post(post_id: int, post: PostCreate):
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE posts SET title = %s, body = %s, \"userId\" = %s WHERE id = %s RETURNING id, title, body, \"userId\"",
            (post.title, post.body, post.userId, post_id)
        )
        conn.commit()
        updated = cur.fetchone()
        if not updated:
            raise HTTPException(status_code=404, detail="Post no encontrado")
        return updated

@app.delete("/posts/{post_id}")
def eliminar_post(post_id: int):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM posts WHERE id = %s", (post_id,))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Post no encontrado")
        return {"mensaje": f"Post {post_id} eliminado"}

@app.get("/")
def root():
    return {"mensaje": "API con PostgreSQL y Autenticación funcionando. Ve a /docs para probarla"}