from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from typing import List
import os  # <--- NUEVO: Para obtener la ruta de la base de datos

app = FastAPI(title="Mi API con Base de Datos")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Configurar la Base de Datos ---
# Usamos la ruta absoluta para que funcione en cualquier entorno
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'posts.db')
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        body TEXT NOT NULL,
        userId INTEGER NOT NULL
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

# --- ENDPOINTS ---
@app.get("/", tags=["Root"])
def root():
    return {"mensaje": "¡API funcionando! Ve a /docs para probarla"}

@app.get("/posts", response_model=List[PostResponse])
def obtener_posts():
    cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()
    return [{"id": row[0], "title": row[1], "body": row[2], "userId": row[3]} for row in posts]

@app.get("/posts/{post_id}", response_model=PostResponse)
def obtener_post(post_id: int):
    cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    return {"id": post[0], "title": post[1], "body": post[2], "userId": post[3]}

@app.post("/posts", response_model=PostResponse, status_code=201)
def crear_post(post: PostCreate):
    cursor.execute(
        "INSERT INTO posts (title, body, userId) VALUES (?, ?, ?)",
        (post.title, post.body, post.userId)
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    return {"id": nuevo_id, "title": post.title, "body": post.body, "userId": post.userId}

@app.delete("/posts/{post_id}")
def eliminar_post(post_id: int):
    cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    return {"mensaje": f"Post {post_id} eliminado"}

@app.put("/posts/{post_id}", response_model=PostResponse)
def actualizar_post(post_id: int, post: PostCreate):
    cursor.execute(
        "UPDATE posts SET title = ?, body = ?, userId = ? WHERE id = ?",
        (post.title, post.body, post.userId, post_id)
    )
    conn.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    return {"id": post_id, "title": post.title, "body": post.body, "userId": post.userId}

# Para ejecutar localmente (opcional)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)