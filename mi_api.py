from fastapi import FastAPI

# Crear la aplicación
app = FastAPI()

# Nuestra "base de datos" falsa
posts = [
    {"id": 1, "title": "Mi primer post", "body": "Contenido del post 1", "userId": 1},
    {"id": 2, "title": "Mi segundo post", "body": "Contenido del post 2", "userId": 1},
]

# GET - Obtener todos los posts
@app.get("/posts")
def obtener_posts():
    return posts

# GET - Obtener un post por ID
@app.get("/posts/{post_id}")
def obtener_post(post_id: int):
    for post in posts:
        if post["id"] == post_id:
            return post
    return {"error": "Post no encontrado"}

# GET - Contar posts
@app.get("/posts/count")
def contar_posts():
    return {"total": len(posts)}