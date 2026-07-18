from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
import os
import re
import psycopg2  # ✅ CORRECTO (con 'psy')
from psycopg2.extras import RealDictCursor  # ✅ CORRECTO (con 'psy')

# --- Configuración JWT ---
SECRET_KEY = "mi-clave-secreta-super-segura-cambiar-en-produccion"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Seguridad ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
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

# --- CONEXIÓN A POSTGRESQL ---
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ADVERTENCIA: La variable DATABASE_URL no está configurada.")
    raise Exception("DATABASE_URL no está configurada")

conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

# --- Crear tablas si no existen ---
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
            "userId" INTEGER NOT NULL,
            CONSTRAINT fk_user FOREIGN KEY("userId") REFERENCES users(id)
        )
    ''')
    conn.commit()

# --- Modelos Pydantic ---
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

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

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
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", user.email):
        raise HTTPException(status_code=400, detail="Email inválido")
    if len(user.password) < 6:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 6 caracteres")
    
    if get_user_by_email(user.email):
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    hashed = get_password_hash(user.password)
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO users (email, hashed_password) VALUES (%s, %s) RETURNING id",
            (user.email, hashed)
        )
        conn.commit()
    
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
    with conn.cursor() as cur:
        cur.execute("SELECT id, title, body, \"userId\" FROM posts")
        return cur.fetchall()

@app.get("/posts/{post_id}", response_model=PostResponse)
def obtener_post(post_id: int, current_user: dict = Depends(get_current_user)):
    with conn.cursor() as cur:
        cur.execute("SELECT id, title, body, \"userId\" FROM posts WHERE id = %s", (post_id,))
        post = cur.fetchone()
        if not post:
            raise HTTPException(status_code=404, detail="Post no encontrado")
        return post

@app.post("/posts", response_model=PostResponse, status_code=201)
def crear_post(post: PostCreate, current_user: dict = Depends(get_current_user)):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO posts (title, body, \"userId\") VALUES (%s, %s, %s) RETURNING id, title, body, \"userId\"",
            (post.title, post.body, post.userId)
        )
        conn.commit()
        return cur.fetchone()

@app.put("/posts/{post_id}", response_model=PostResponse)
def actualizar_post(post_id: int, post: PostCreate, current_user: dict = Depends(get_current_user)):
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
def eliminar_post(post_id: int, current_user: dict = Depends(get_current_user)):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM posts WHERE id = %s", (post_id,))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Post no encontrado")
        return {"mensaje": f"Post {post_id} eliminado"}

@app.get("/")
def root():
    return {"mensaje": "API con PostgreSQL y Autenticación funcionando. Ve a /docs para probarla"}