import pandas as pd
import os

print("="*50)
print("🔍 BUSCADOR DE POSTS EN EXCEL")
print("="*50)

# 1. Buscar el archivo CSV más reciente
archivos_csv = [f for f in os.listdir('.') if f.startswith('posts_') and f.endswith('.csv')]

if not archivos_csv:
    print("❌ No encontré ningún archivo de posts.")
    print("   Ejecuta 'guardar_posts.py' primero para generar el archivo.")
    exit()

# Tomar el archivo más reciente (por nombre, que incluye la fecha)
archivo_reciente = sorted(archivos_csv)[-1]
print(f"📂 Cargando: {archivo_reciente}")

try:
    # 2. Cargar el archivo CSV
    df = pd.read_csv(archivo_reciente)
    print(f"✅ Cargados {len(df)} posts desde el archivo.")
    
    while True:
        print("\n" + "-"*50)
        palabra = input("🔎 Buscar posts que contengan (escribe 'salir' para terminar): ").strip()
        
        if palabra.lower() == 'salir':
            print("👋 ¡Hasta luego!")
            break
        
        if not palabra:
            print("❌ Escribe una palabra para buscar.")
            continue
            
        # 3. Buscar la palabra en el título o en el contenido
        # Convertir a minúsculas para buscar sin importar mayúsculas
        mascara = df['title'].str.lower().str.contains(palabra.lower(), na=False) | \
                  df['body'].str.lower().str.contains(palabra.lower(), na=False)
        
        resultados = df[mascara]
        
        if len(resultados) == 0:
            print(f"❌ No encontré ningún post con '{palabra}'")
        else:
            print(f"\n✅ Encontré {len(resultados)} posts con '{palabra}':")
            print("="*50)
            
            # Mostrar los primeros 10 resultados
            for i, row in resultados.head(10).iterrows():
                print(f"\n📌 POST #{row['id']} (Usuario: {row['userId']})")
                print(f"📝 Título: {row['title']}")
                print(f"📄 Contenido: {row['body'][:100]}..." if len(row['body']) > 100 else f"📄 Contenido: {row['body']}")
                print("-"*30)
            
            if len(resultados) > 10:
                print(f"... y {len(resultados) - 10} resultados más.")
                guardar = input("¿Quieres guardar los resultados en un archivo? (s/n): ")
                if guardar.lower() == 's':
                    nombre_guardado = f"resultados_{palabra}.csv"
                    resultados.to_csv(nombre_guardado, index=False, encoding='utf-8')
                    print(f"✅ Guardado en: {nombre_guardado}")
        
except FileNotFoundError:
    print("❌ No encontré el archivo. Asegúrate de haber ejecutado 'guardar_posts.py' primero.")
except Exception as e:
    print(f"❌ Error inesperado: {e}")