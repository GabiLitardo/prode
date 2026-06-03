import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Prode Laboratorio 2026", layout="wide")
st.title("🏆 Simulador Inteligente - Prode Mundial 2026")
st.subheader("Fase de Grupos, Terceros Dinámicos y Play-offs")

# 1. Base de datos de los 12 Grupos (48 equipos oficiales)
# Simplificado para el ejemplo con los grupos principales y placeholders
grupos_data = {
    "Grupo A": ["Estados Unidos", "México", "Canadá", "Argentina"], # Ajustar con el fixture real
    "Grupo B": ["Francia", "Marruecos", "Inglaterra", "Ecuador"],
    "Grupo C": ["Brasil", "Bélgica", "Japón", "Egipto"],
    "Grupo L": ["Uruguay", "Alemania", "Corea del Sur", "Nigeria"]
    # Nota: Expandir a los 12 grupos (A hasta L) con los 48 clasificados reales
}

# Inicializar estado para guardar los resultados del usuario
if "goles" not in st.session_state:
    st.session_state.goles = {}

st.write("### ⚽ 1. Carga los resultados de la Fase de Grupos")
st.caption("Introduce los goles de cada partido. El sistema calculará las tablas automáticamente.")

# Simulación simplificada de partidos por grupo (1 contra todos)
tablas_grupos = {}

for grupo, equipos in grupos_data.items():
    with st.expander(f"📅 Partidos del {grupo}"):
        partidos = [
            (equipos[0], equipos[1]), (equipos[2], equipos[3]),
            (equipos[0], equipos[2]), (equipos[1], equipos[3]),
            (equipos[0], equipos[3]), (equipos[1], equipos[2])
        ]
        
        # Diccionario local para computar los puntos del grupo
        puntos = {eq: {"pts": 0, "gf": 0, "gc": 0, "dg": 0} for eq in equipos}
        
        for eq1, eq2 in partidos:
            col1, col2, col3, col4 = st.columns([3, 1, 1, 3])
            with col1: st.write(f"**{eq1}**")
            with col2: g1 = st.number_input("Goles", min_value=0, step=1, key=f"{grupo}_{eq1}_{eq2}_g1")
            with col3: g2 = st.number_input("Goles", min_value=0, step=1, key=f"{grupo}_{eq2}_{eq1}_g2")
            with col4: st.write(f"**{eq2}**")
            
            # Computar matemática del grupo en tiempo real
            puntos[eq1]["gf"] += g1; puntos[eq1]["gc"] += g2
            puntos[eq2]["gf"] += g2; puntos[eq2]["gc"] += g1
            if g1 > g2:
                puntos[eq1]["pts"] += 3
            elif g2 > g1:
                puntos[eq2]["pts"] += 3
            else:
                puntos[eq1]["pts"] += 1
                puntos[eq2]["pts"] += 1
                
        for eq in equipos:
            puntos[eq]["dg"] = puntos[eq]["gf"] - puntos[eq]["gc"]
            
        # Ordenar tabla del grupo (Puntos -> Diferencia de Gol -> Goles a Favor)
        tabla_df = pd.DataFrame.from_dict(puntos, orient='index').sort_values(by=["pts", "dg", "gf"], ascending=False)
        tablas_grupos[grupo] = tabla_df
        st.write("**Tabla de Posiciones Virtual:**")
        st.dataframe(tabla_df)

# 2. Algoritmo de Selección de Clasificados y los 8 Mejores Terceros
clasificados_directos = []
todos_los_terceros = {}

for grupo, tabla in tablas_grupos.items():
    clasificados_directos.append(tabla.index[0]) # 1ro
    clasificados_directos.append(tabla.index[1]) # 2do
    todos_los_terceros[tabla.index[2]] = tabla.iloc[2].to_dict() # 3ro para comparar

# Tabla comparativa de los mejores terceros
mejores_terceros_df = pd.DataFrame.from_dict(todos_los_terceros, orient='index').sort_values(by=["pts", "dg", "gf"], ascending=False)
mejores_8_terceros = list(mejores_terceros_df.index[:8])

lista_32_clasificados = clasificados_directos + mejores_8_terceros

st.success(f"✅ ¡Fase de grupos procesada! Se detectaron los 8 mejores terceros de forma inteligente.")

# 3. Fase de Play-offs Dinámica
st.write("---")
st.write("### 🔀 2. Cuadro de Eliminación Directa (Dieciseisavos de Final)")
st.caption("Los cruces se armaron automáticamente con tus clasificados de la fase anterior.")

# Nota: El ordenamiento oficial de la FIFA de los terceros cruza grupos (Ej: 1A vs 3C/D/E). 
# Para mantener el script limpio, hacemos cruces indexados directos de los 32 clasificados.
ganadores_16vos = []

for i in range(0, 32, 2):
    eq_local = lista_32_clasificados[i]
    eq_visita = lista_32_clasificados[i+1]
    
    st.write(f"**Llave {i//2 + 1}**")
    ganador = st.radio(f"¿Quién clasifica a Octavos?", [eq_local, eq_visita], key=f"llave_16_{i}")
    ganadores_16vos.append(ganador)

# El proceso se repite idéntico para Octavos, Cuartos, Semis y Final...
st.write("---")
st.write("### 🥇 3. Definición del Podio")
campeon = st.selectbox("🏆 ¿Quién es tu Campeón del Mundo?", ganadores_16vos)

# 4. BOTÓN DE ORO: Exportar a CSV limpio para tu Excel
st.write("---")
st.write("### 📊 4. Envía tus respuestas al administrador del laboratorio")

# Estructurar la predicción final en un diccionario plano para el CSV
datos_prode_usuario = {
    "Usuario": st.text_input("Introduce tu nombre/apellido:"),
    "Campeón": campeon,
    "Clasificados_Totales": ",".join(lista_32_clasificados)
}

# Agregar las elecciones de los playoffs para tener el registro completo
for idx, gan in enumerate(ganadores_16vos):
    datos_prode_usuario[f"Pasa_a_Octavos_Llave_{idx+1}"] = gan

df_exportar = pd.DataFrame([datos_prode_usuario])
csv_data = df_exportar.to_csv(index=False).encode('utf-8')

st.download_button(
    label="💾 DESCARGAR PREDICCIÓN EN CSV",
    data=csv_data,
    file_name=f"prode_mundial_2026.csv",
    mime="text/csv",
)
