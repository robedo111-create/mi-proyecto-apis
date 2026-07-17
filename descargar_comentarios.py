import requests
import pandas as pd
from datetime import datetime
import time

print("="*50)
print("💬 DESCARGANDO COMENTARIOS DE POSTS")
print("="*50)

BASE_URL = "https://jsonplaceholder.typicode.com"

try:
    # 1. Descargar todos los posts primero
    print("\n🔄 Descargando posts...")
    respuesta_posts = requests.get(f"{BASE_URL}/posts")
    
    if respuesta_posts.status_code != 200:
        print("❌ Error al descargar posts")
        exit()
    
    posts = respuesta_posts.json()
    print(f"✅ Descargados {len(posts)} posts")
    
    # 2. Descargar comentarios de cada post
    print("\n🔄 Descargando comentarios de cada post...")
    
    todos_los_comentarios = []
    posts_sin_comentarios = 0
    
    for i, post in enumerate(posts, 1):
        # Mostrar progreso
        if i % 10 == 0:
            print(f"   Procesando post {i}/{len(posts)}...")
        
        # Descargar comentarios de este post
        respuesta_comentarios = requests.get(f"{BASE_URL}/posts/{post['id']}/comments")
        
        if respuesta_comentarios.status_code == 200:
            comentarios = respuesta_comentarios.json()
            
            if comentarios:
                # Agregar el post_id a cada comentario para poder unirlos después
                for comentario in comentarios:
                    comentario['post_id'] = post['id']
                    comentario['post_title'] = post['title']
                    comentario['post_userId'] = post['userId']
                    todos_los_comentarios.append(comentario)
            else:
                posts_sin_comentarios += 1
        else:
            print(f"   ⚠️ Error al descargar comentarios del post {post['id']}")
        
        # Pequeña pausa para no sobrecargar la API
        time.sleep(0.05)
    
    print(f"\n✅ Descargados {len(todos_los_comentarios)} comentarios en total")
    print(f"ℹ️  {posts_sin_comentarios} posts no tienen comentarios")
    
    # 3. Crear DataFrame con los comentarios
    if todos_los_comentarios:
        df_comentarios = pd.DataFrame(todos_los_comentarios)
        
        # 4. Mostrar vista previa
        print("\n📋 Vista previa de comentarios:")
        print("-" * 50)
        print(df_comentarios[['post_id', 'name', 'email', 'body']].head())
        
        # 5. Estadísticas
        print("\n📊 Estadísticas de comentarios:")
        print("-" * 50)
        print(f"💬 Total de comentarios: {len(df_comentarios)}")
        print(f"📝 Posts con comentarios: {df_comentarios['post_id'].nunique()}")
        print(f"👤 Usuarios que comentaron: {df_comentarios['email'].nunique()}")
        
        # 6. Posts con más comentarios
        print("\n📊 Top 5 posts con más comentarios:")
        print("-" * 50)
        top_posts = df_comentarios.groupby('post_id').size().sort_values(ascending=False).head(5)
        for post_id, cantidad in top_posts.items():
            # Obtener el título del post (tomamos el primero de ese post_id)
            titulo = df_comentarios[df_comentarios['post_id'] == post_id]['post_title'].iloc[0]
            print(f"📌 Post #{post_id}: {cantidad} comentarios - {titulo[:50]}...")
        
        # 7. Guardar en archivos
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Guardar todos los comentarios
        nombre_csv = f"comentarios_{timestamp}.csv"
        df_comentarios.to_csv(nombre_csv, index=False, encoding='utf-8')
        print(f"\n✅ Comentarios guardados en: {nombre_csv}")
        
        # Guardar en Excel
        try:
            nombre_excel = f"comentarios_{timestamp}.xlsx"
            df_comentarios.to_excel(nombre_excel, index=False, sheet_name='Comentarios')
            print(f"✅ Comentarios guardados en Excel: {nombre_excel}")
        except Exception as e:
            print(f"ℹ️  No se pudo guardar en Excel: {e}")
        
        # 8. Crear resumen por post
        print("\n📊 Creando resumen por post...")
        resumen = df_comentarios.groupby('post_id').agg({
            'id': 'count',  # Número de comentarios
            'email': lambda x: list(x)[:3]  # Primeros 3 emails
        }).rename(columns={'id': 'total_comentarios'})
        
        # Unir con los datos de posts
        df_posts = pd.DataFrame(posts)
        df_resumen = df_posts.merge(resumen, left_on='id', right_on='post_id', how='left')
        df_resumen['total_comentarios'] = df_resumen['total_comentarios'].fillna(0).astype(int)
        df_resumen['email'] = df_resumen['email'].apply(lambda x: x if isinstance(x, list) else [])
        
        # Guardar resumen
        nombre_resumen = f"resumen_posts_{timestamp}.csv"
        df_resumen[['id', 'userId', 'title', 'total_comentarios']].to_csv(
            nombre_resumen, index=False, encoding='utf-8'
        )
        print(f"✅ Resumen guardado en: {nombre_resumen}")
        
        print("\n" + "="*50)
        print("🎉 ¡PROCESO COMPLETADO!")
        print(f"📊 Archivos generados:")
        print(f"   - {nombre_csv} (todos los comentarios)")
        print(f"   - {nombre_resumen} (resumen por post)")
        if 'nombre_excel' in locals():
            print(f"   - {nombre_excel} (versión Excel)")
        print("="*50)
        
    else:
        print("❌ No se descargaron comentarios")
        
except requests.exceptions.ConnectionError:
    print("❌ Error de conexión. Revisa tu internet.")
except Exception as e:
    print(f"❌ Error inesperado: {e}")