import requests

# La URL de la "Base de Datos" falsa
BASE_URL = "https://jsonplaceholder.typicode.com/posts"


print("="*50)
print("🔍 BUSCADOR DE POSTS")
print("="*50)

while True:
    print("\n" + "-"*30)
    
    # Pedir al usuario el número del post
    try:
        entrada = input("📝 ¿Qué post quieres ver? (1-100) o escribe 'salir' para terminar: ")
        
        # Opción para salir del programa
        if entrada.lower() == 'salir':
            print("👋 ¡Hasta luego!")
            break
        
        # Convertir a número
        post_id = int(entrada)
        
        # Verificar que esté en rango válido (1-100)
        if post_id < 1 or post_id > 100:
            print("❌ El número debe estar entre 1 y 100")
            continue
            
        # Hacer la petición GET a la API
        print(f"🔎 Buscando el post #{post_id}...")
        respuesta = requests.get(f"{BASE_URL}/{post_id}")
        
        # Verificar si el post existe
        if respuesta.status_code == 200:
            post = respuesta.json()
            
            # Mostrar la información del post
            print("\n" + "="*40)
            print(f"📌 POST #{post['id']}")
            print("="*40)
            print(f"📝 Título: {post['title']}")
            print("-"*40)
            print(f"📄 Contenido: {post['body']}")
            print("="*40)
            print(f"👤 Usuario ID: {post['userId']}")
            
        elif respuesta.status_code == 404:
            print(f"❌ No existe ningún post con el número {post_id}")
        else:
            print(f"❌ Error {respuesta.status_code}: No se pudo obtener el post")
            
    except ValueError:
        print("❌ Por favor, escribe un número válido")
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión. Revisa tu internet.")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")