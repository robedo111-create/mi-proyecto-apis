import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import os
from datetime import datetime

# Configurar matplotlib para mostrar gráficos en la terminal (no necesitas ventana)
matplotlib.use('Agg')

print("="*50)
print("📊 DASHBOARD DE POSTS Y COMENTARIOS")
print("="*50)

# 1. Buscar los archivos más recientes
archivos_comentarios = [f for f in os.listdir('.') if f.startswith('comentarios_') and f.endswith('.csv')]
archivos_resumen = [f for f in os.listdir('.') if f.startswith('resumen_posts_') and f.endswith('.csv')]

if not archivos_comentarios or not archivos_resumen:
    print("❌ No encontré los archivos de comentarios.")
    print("   Ejecuta 'descargar_comentarios.py' primero.")
    exit()

archivo_comentarios = sorted(archivos_comentarios)[-1]
archivo_resumen = sorted(archivos_resumen)[-1]

print(f"\n📂 Cargando comentarios: {archivo_comentarios}")
df_comentarios = pd.read_csv(archivo_comentarios)

print(f"📂 Cargando resumen: {archivo_resumen}")
df_resumen = pd.read_csv(archivo_resumen)

print(f"✅ Datos cargados correctamente")

# 2. Crear figura con 4 gráficos
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle('📊 Dashboard de Posts y Comentarios', fontsize=16, fontweight='bold')

# Gráfico 1: Posts por usuario
ax1 = axes[0, 0]
posts_por_usuario = df_resumen.groupby('userId').size()
ax1.bar(posts_por_usuario.index, posts_por_usuario.values, color='skyblue')
ax1.set_title('📝 Posts por Usuario')
ax1.set_xlabel('ID del Usuario')
ax1.set_ylabel('Número de Posts')
ax1.grid(True, alpha=0.3)

# Gráfico 2: Comentarios por usuario
ax2 = axes[0, 1]
comentarios_por_usuario = df_comentarios.groupby('post_userId').size()
ax2.bar(comentarios_por_usuario.index, comentarios_por_usuario.values, color='lightcoral')
ax2.set_title('💬 Comentarios por Usuario')
ax2.set_xlabel('ID del Usuario')
ax2.set_ylabel('Número de Comentarios')
ax2.grid(True, alpha=0.3)

# Gráfico 3: Top 10 posts con más comentarios
ax3 = axes[1, 0]
top_posts = df_resumen.nlargest(10, 'total_comentarios')[['id', 'total_comentarios']]
ax3.barh(top_posts['id'], top_posts['total_comentarios'], color='lightgreen')
ax3.set_title('🏆 Top 10 Posts con Más Comentarios')
ax3.set_xlabel('Número de Comentarios')
ax3.set_ylabel('ID del Post')
ax3.grid(True, alpha=0.3)

# Gráfico 4: Distribución de comentarios por post
ax4 = axes[1, 1]
distribucion = df_resumen['total_comentarios'].value_counts().sort_index()
ax4.bar(distribucion.index, distribucion.values, color='plum')
ax4.set_title('📊 Distribución de Comentarios por Post')
ax4.set_xlabel('Número de Comentarios')
ax4.set_ylabel('Cantidad de Posts')
ax4.grid(True, alpha=0.3)

# Ajustar layout
plt.tight_layout()

# Guardar el dashboard
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
nombre_imagen = f'dashboard_{timestamp}.png'
plt.savefig(nombre_imagen, dpi=150, bbox_inches='tight')
print(f"\n✅ Dashboard guardado como: {nombre_imagen}")

# Mostrar estadísticas
print("\n" + "="*50)
print("📊 ESTADÍSTICAS DEL DASHBOARD")
print("="*50)

print(f"\n📝 POSTS:")
print(f"   • Total de posts: {len(df_resumen)}")
print(f"   • Usuarios distintos: {df_resumen['userId'].nunique()}")
print(f"   • Usuario con más posts: {posts_por_usuario.idxmax()} ({posts_por_usuario.max()} posts)")

print(f"\n💬 COMENTARIOS:")
print(f"   • Total de comentarios: {len(df_comentarios)}")
print(f"   • Usuarios que comentaron: {df_comentarios['post_userId'].nunique()}")
print(f"   • Usuario con más comentarios: {comentarios_por_usuario.idxmax()} ({comentarios_por_usuario.max()} comentarios)")

print(f"\n📊 PROMEDIOS:")
print(f"   • Promedio de comentarios por post: {df_resumen['total_comentarios'].mean():.1f}")
print(f"   • Post con más comentarios: ID {df_resumen.loc[df_resumen['total_comentarios'].idxmax(), 'id']} ({df_resumen['total_comentarios'].max()} comentarios)")

print(f"\n✅ ¡Dashboard completado! Abre {nombre_imagen} para ver los gráficos.")

print("\n" + "="*50)
print("🎉 ¡PROCESO COMPLETADO!")
print("="*50)