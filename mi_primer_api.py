import requests

print("🚀 INICIANDO PRUEBA DE API...")

# La URL de la "Base de Datos" falsa
BASE_URL = "https://jsonplaceholder.typicode.com/posts"

# --------------------------------------------------
# 1. PETICIÓN GET (Buscar y traer datos)
# --------------------------------------------------
print("\n" + "="*50)
print("--- 1. GET: Cargar todos los posts ---")
print("="*50)

try:
    respuesta = requests.get(BASE_URL)
    print(f"✅ Código de respuesta: {respuesta.status_code}")
    
    if respuesta.status_code == 200:
        posts = respuesta.json()
        print(f"✅ ¡Traje {len(posts)} posts! El primero es:")
        print("-" * 30)
        primer_post = posts[0]
        print(f"ID: {primer_post['id']}")
        print(f"Título: {primer_post['title']}")
        print(f"Cuerpo: {primer_post['body'][:50]}...")
    else:
        print(f"❌ Error: Código {respuesta.status_code}")
        
except Exception as e:
    print(f"❌ Error en la conexión: {e}")

# --------------------------------------------------
# 2. GET con búsqueda específica (Buscar por ID)
# --------------------------------------------------
print("\n" + "="*50)
print("--- 2. GET: Buscar el post con ID 5 ---")
print("="*50)

try:
    respuesta = requests.get(f"{BASE_URL}/5")
    print(f"✅ Código de respuesta: {respuesta.status_code}")
    
    if respuesta.status_code == 200:
        post = respuesta.json()
        print(f"✅ Título del post 5: {post['title']}")
        print(f"   Cuerpo: {post['body'][:50]}...")
    else:
        print(f"❌ Error: Código {respuesta.status_code}")
        
except Exception as e:
    print(f"❌ Error en la conexión: {e}")

# --------------------------------------------------
# 3. PETICIÓN POST (Crear/Añadir un nuevo dato)
# --------------------------------------------------
print("\n" + "="*50)
print("--- 3. POST: Crear un nuevo post ---")
print("="*50)

try:
    nuevo_post = {
        "title": "Mi primer post desde Python",
        "body": "Esto es una prueba de POST en VS Code",
        "userId": 1
    }
    
    respuesta = requests.post(BASE_URL, json=nuevo_post)
    print(f"✅ Código de respuesta: {respuesta.status_code}")
    
    if respuesta.status_code == 201:
        creado = respuesta.json()
        print(f"✅ ¡Creado con éxito!")
        print(f"   ID asignado: {creado['id']}")
        print(f"   Título: {creado['title']}")
    else:
        print(f"❌ Error al crear: Código {respuesta.status_code}")
        
except Exception as e:
    print(f"❌ Error en la conexión: {e}")

# --------------------------------------------------
# 4. PETICIÓN PUT (Actualizar todo un dato)
# --------------------------------------------------
print("\n" + "="*50)
print("--- 4. PUT: Actualizar el post 1 ---")
print("="*50)

try:
    datos_actualizados = {
        "id": 1,
        "title": "¡TÍTULO ACTUALIZADO!",
        "body": "Este texto fue modificado con PUT",
        "userId": 1
    }
    
    respuesta = requests.put(f"{BASE_URL}/1", json=datos_actualizados)
    print(f"✅ Código de respuesta: {respuesta.status_code}")
    
    if respuesta.status_code == 200:
        actualizado = respuesta.json()
        print(f"✅ Actualizado correctamente")
        print(f"   Nuevo título: {actualizado['title']}")
    else:
        print(f"❌ Error al actualizar: Código {respuesta.status_code}")
        
except Exception as e:
    print(f"❌ Error en la conexión: {e}")

# --------------------------------------------------
# 5. PETICIÓN DELETE (Eliminar un dato)
# --------------------------------------------------
print("\n" + "="*50)
print("--- 5. DELETE: Eliminar el post 1 ---")
print("="*50)

try:
    respuesta = requests.delete(f"{BASE_URL}/1")
    print(f"✅ Código de respuesta: {respuesta.status_code}")
    
    if respuesta.status_code == 200:
        print("✅ ¡Post eliminado exitosamente! (simulación)")
    else:
        print(f"❌ Error al eliminar: Código {respuesta.status_code}")
        
except Exception as e:
    print(f"❌ Error en la conexión: {e}")

print("\n" + "="*50)
print("🎉 ¡TODAS LAS PRUEBAS COMPLETADAS!")
print("="*50)