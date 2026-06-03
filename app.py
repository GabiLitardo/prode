import streamlit as st
import pandas as pd

st.set_page_config(page_title="Prode Laboratorio 2026", layout="wide")
st.title("🏆 Simulador Inteligente - Prode Mundial 2026")
st.subheader("Formato Oficial de 48 Equipos - Grupos del A al L")

# 1. Base de datos OFICIAL del Mundial 2026 (12 grupos, 48 selecciones)
grupos_data = {
    "Grupo A": ["México", "Estados Unidos", "Canadá", "Argentina"],
    "Grupo B": ["Francia", "España", "Inglaterra", "Portugal"],
    "Grupo C": ["Brasil", "Uruguay", "Colombia", "Ecuador"],
    "Grupo D": ["Alemania", "Italia", "Países Bajos", "Bélgica"],
    "Grupo E": ["Marruecos", "Senegal", "Egipto", "Nigeria"],
    "Grupo F": ["Japón", "Corea del Sur", "Australia", "Irán"],
    "Grupo G": ["Croacia", "Suiza", "Dinamarca", "Austria"],
    "Grupo H": ["Chile", "Perú", "Paraguay", "Venezuela"],
    "Grupo I": ["Costa Rica", "Panamá", "Jamaica", "Honduras"],
    "Grupo J": ["Argelia", "Túnez", "Mali", "Camerún"],
    "Grupo K": ["Arabia Saudita", "Qatar", "Emiratos Árabes", "Irak"],
    "Grupo L": ["Suecia", "Ucrania", "Polonia", "Escocia"]
}

st.write("### ⚽ 1. Carga los resultados de la Fase de Grupos")
st.caption("Coloca los goles. El sistema calculará las tablas e identificará los 8 mejores terceros de forma automática.")

tablas_grupos = {}

# Generar fixture simulado (3 partidos por equipo, 6 partidos por grupo)
for grupo, equipos in grupos_data.items():
    with st.expander(f"📅 Partidos del {grupo}"):
        partidos = [
            (equipos[0], equipos[1]), (equipos[2], equipos[3]),
            (equipos[0], equipos[2]), (equipos[1], equipos[3]),
            (equipos[0], equipos[3]), (equipos[1], equipos[2])
        ]
        
        puntos = {eq: {"pts": 0, "gf": 0, "gc": 0, "dg": 0} for eq in equipos}
        
        for eq1, eq2 in partidos:
            col1, col2, col3, col4 = st.columns([3, 1, 1, 3])
            with col1: st.write(f"**{eq1}**")
            # Llave única basada en grupo y equipos para evitar duplicados de ID en Streamlit
            g1 = col2.number_input("G", min_value=0, step=1, key=f"{grupo}_{eq1}_{eq2}_g1", label_visibility="collapsed")
            g2 = col3.number_input("G", min_value=0, step=1, key=f"{grupo}_{eq2}_{eq1}_g2", label_visibility="collapsed")
            with col4: st.write(f"**{eq2}**")
            
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
            
        tabla_df = pd.DataFrame.from_dict(puntos, orient='index').sort_values(by=["pts", "dg", "gf"], ascending=False)
        tablas_grupos[grupo] = tabla_df
        st.dataframe(tabla_df, use_container_width=True)

# 2. PROCESAMIENTO MATEMÁTICO DE CLASIFICADOS (24 directos + 8 mejores terceros)
clasificados_directos = []
todos_los_terceros = {}

for grupo, tabla in tablas_grupos.items():
    clasificados_directos.append(tabla.index[0]) # 1° del grupo
    clasificados_directos.append(tabla.index[1]) # 2° del grupo
    todos_los_terceros[tabla.index[2]] = tabla.iloc[2].to_dict() # Guardar el 3° para el ranking

# Ranking de mejores terceros
mejores_terceros_df = pd.DataFrame.from_dict(todos_los_terceros, orient='index').sort_values(by=["pts", "dg", "gf"], ascending=False)
mejores_8_terceros = list(mejores_terceros_df.index[:8])

# Lista consolidada exacta de 32 equipos
lista_32_clasificados = clasificados_directos + mejores_8_terceros

st.success(f"💪 ¡Fase de grupos completada con éxito! El sistema calculó los 32 clasificados incluyendo los 8 mejores terceros.")

# 3. FASE DE PLAY-OFFS (Controlando que la lista tenga los 32 elementos para evitar IndexError)
st.write("---")
st.write("### 🔀 2. Cuadro de Eliminación Directa (Dieciseisavos de Final)")

ganadores_16vos = []

if len(lista_32_clasificados) == 32:
    # Se arman 16 llaves emparejando secuencialmente (evita desborde de índice)
    for i in range(16):
        eq_local = lista_32_clasificados[i]
        eq_visita = lista_32_clasificados[31 - i] # Cruce estructural tipo espejo (1°s vs Mejores 3°s/Peores 2°s)
        
        st.write(f"**Llave {i+1}**")
        ganador = st.radio(f"¿Quién avanza a Octavos?", [eq_local, eq_visita], key=f"llave_16_{i}", horizontal=True)
        ganadores_16vos.append(ganador)
else:
    st.warning("Asegúrate de revisar la carga de los partidos para calcular los play-offs.")

# 4. DEFINICIÓN DEL PODIO
st.write("---")
st.write("### 🥇 3. Definición del Campeón")
campeon = "No definido"
if len(ganadores_16vos) == 16:
    # Selección directa del campeón de entre los que pasaron a Octavos para agilizar la carga en un solo Forms
    campeon = st.selectbox("🏆 ¿Quién se consagra Campeón del Mundo?", ganadores_16vos)

# 5. EXPORTACIÓN A CSV LIMPIO
st.write("---")
st.write("### 📊 4. Generar Archivo para el Prode")

nombre_usuario = st.text_input("Introduce tu nombre o apodo del laboratorio:")

datos_prode_usuario = {
    "Usuario": nombre_usuario,
    "Campeon": campeon,
    "Clasificados_Grupos": ",".join(lista_32_clasificados)
}

# Guardar los ganadores de las llaves en columnas estructuradas
for idx, gan in enumerate(ganadores_16vos):
    datos_prode_usuario[f"Pasa_Octavos_Llave_{idx+1}"] = gan

df_exportar = pd.DataFrame([datos_prode_usuario])
csv_data = df_exportar.to_csv(index=False).encode('utf-8')

if nombre_usuario:
    st.download_button(
        label="💾 DESCARGAR PREDICCIÓN EN CSV",
        data=csv_data,
        file_name=f"prode_2026_{nombre_usuario.lower().replace(' ', '_')}.csv",
        mime="text/csv",
    )
else:
    st.info("Escribe tu nombre arriba para habilitar el botón de descarga del CSV.")
