import requests
import pandas as pd
from datetime import datetime

print("="*50)
print("📊 GUARDANDO POSTS EN EXCEL")
print("="*50)

# La URL de la "Base de Datos" falsa
BASE_URL = "https://jsonplaceholder.typicode.com/posts"

print("\n🔄 Descargando todos los posts...")

try:
    # 1. Hacer la petición GET para traer todos los posts
    respuesta = requests.get(BASE_URL)
    
    if respuesta.status_code == 200:
        posts = respuesta.json()
        print(f"✅ ¡Descargados {len(posts)} posts!")
        
        # 2. Convertir a DataFrame de pandas
        df = pd.DataFrame(posts)
        
        # 3. Mostrar una vista previa
        print("\n📋 Vista previa (primeros 5 posts):")
        print("-" * 50)
        print(df.head())
        
        # 4. Guardar en archivo CSV
        nombre_archivo = f"posts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(nombre_archivo, index=False, encoding='utf-8')
        print(f"\n✅ Archivo guardado como: {nombre_archivo}")
        
        # 5. Mostrar estadísticas básicas
        print("\n📊 Estadísticas de los posts:")
        print("-" * 50)
        print(f"📝 Total de posts: {len(df)}")
        print(f"👤 Usuarios distintos: {df['userId'].nunique()}")
        print(f"📏 Título más largo: {df['title'].str.len().max()} caracteres")
        print(f"📏 Título más corto: {df['title'].str.len().min()} caracteres")
        
        # 6. Guardar también en formato Excel (opcional)
        try:
            nombre_excel = f"posts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df.to_excel(nombre_excel, index=False, sheet_name='Posts')
            print(f"✅ Archivo Excel guardado como: {nombre_excel}")
        except Exception as e:
            print(f"ℹ️ No se pudo guardar en Excel (puede faltar openpyxl): {e}")
            print("   Instala openpyxl con: pip install openpyxl")
        
        # 7. Mostrar los posts por usuario
        print("\n📊 Posts por usuario:")
        print("-" * 50)
        conteo_usuarios = df['userId'].value_counts().sort_index()
        for usuario, cantidad in conteo_usuarios.items():
            print(f"👤 Usuario {usuario}: {cantidad} posts")
            
    else:
        print(f"❌ Error: Código {respuesta.status_code}")
        
except requests.exceptions.ConnectionError:
    print("❌ Error de conexión. Revisa tu internet.")
except Exception as e:
    print(f"❌ Error inesperado: {e}")

print("\n" + "="*50)
print("🎉 ¡PROCESO COMPLETADO!")
print("="*50)