import streamlit as st
import pandas as pd

st.set_page_config(page_title="Prode Laboratorio 2026", layout="wide")
st.title("🏆 Simulador Inteligente - Prode Mundial 2026")
st.subheader("Formato Oficial de 48 Equipos - Llave Completa")

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
    clasificados_directos.append(tabla.index[0]) 
    clasificados_directos.append(tabla.index[1]) 
    todos_los_terceros[tabla.index[2]] = tabla.iloc[2].to_dict() 

mejores_terceros_df = pd.DataFrame.from_dict(todos_los_terceros, orient='index').sort_values(by=["pts", "dg", "gf"], ascending=False)
mejores_8_terceros = list(mejores_terceros_df.index[:8])

lista_32_clasificados = clasificados_directos + mejores_8_terceros

st.success(f"💪 ¡Fase de grupos completada! Se detectaron los 32 clasificados.")

# --- FASE DE ELIMINACIÓN DIRECTA ---
st.write("---")
st.write("### 🔀 2. Cuadro de Eliminación Directa")

# Diccionario para guardar todas las elecciones del usuario y exportarlas
playoffs_resultados = {}

# --- 16vos de Final (32 equipos -> 16 ganadores) ---
st.write("#### 🔹 Dieciseisavos de Final")
ganadores_16vos = []
col_16_1, col_16_2 = st.columns(2)

for i in range(16):
    eq_local = lista_32_clasificados[i]
    eq_visita = lista_32_clasificados[31 - i]
    
    target_col = col_16_1 if i < 8 else col_16_2
    with target_col:
        ganador = st.radio(f"Llave {i+1}: {eq_local} vs {eq_visita}", [eq_local, eq_visita], key=f"l16_{i}", horizontal=True)
        ganadores_16vos.append(ganador)
        playoffs_resultados[f"Ganador_16vos_L{i+1}"] = ganador

# --- Octavos de Final (16 equipos -> 8 ganadores) ---
st.write("---")
st.write("#### 🔹 Octavos de Final")
ganadores_8vos = []
col_8_1, col_8_2 = st.columns(2)

for i in range(8):
    eq_local = ganadores_16vos[i*2]
    eq_visita = ganadores_16vos[i*2 + 1]
    
    target_col = col_8_1 if i < 4 else col_8_2
    with target_col:
        ganador = st.radio(f"Octavos {i+1}: {eq_local} vs {eq_visita}", [eq_local, eq_visita], key=f"l8_{i}", horizontal=True)
        ganadores_8vos.append(ganador)
        playoffs_resultados[f"Ganador_8vos_L{i+1}"] = ganador

# --- Cuartos de Final (8 equipos -> 4 ganadores) ---
st.write("---")
st.write("#### 🔹 Cuartos de Final")
ganadores_cuartos = []
col_4_1, col_4_2 = st.columns(2)

for i in range(4):
    eq_local = ganadores_8vos[i*2]
    eq_visita = ganadores_8vos[i*2 + 1]
    
    target_col = col_4_1 if i < 2 else col_4_2
    with target_col:
        ganador = st.radio(f"Cuartos {i+1}: {eq_local} vs {eq_visita}", [eq_local, eq_visita], key=f"l4_{i}", horizontal=True)
        ganadores_cuartos.append(ganador)
        playoffs_resultados[f"Ganador_Cuartos_L{i+1}"] = ganador

# --- Semifinales (4 equipos -> 2 finalistas + 2 al 3er puesto) ---
st.write("---")
st.write("#### 🔹 Semifinales")
finalistas = []
perdedores_semis = []
col_semi = st.columns(2)

for i in range(2):
    eq_local = ganadores_cuartos[i*2]
    eq_visita = ganadores_cuartos[i*2 + 1]
    
    with col_semi[i]:
        ganador = st.radio(f"Semifinal {i+1}: {eq_local} vs {eq_visita}", [eq_local, eq_visita], key=f"lsemi_{i}", horizontal=True)
        finalistas.append(ganador)
        perdedor = eq_visita if ganador == eq_local else eq_local
        perdedores_semis.append(perdedor)
        playoffs_resultados[f"Ganador_Semi_{i+1}"] = ganador

# --- Tercer Puesto y Gran Final ---
st.write("---")
col_finales = st.columns(2)

with col_finales[0]:
    st.write("#### 🥉 Tercer Puesto")
    tercer_puesto = st.radio(f"Definición: {perdedores_semis[0]} vs {perdedores_semis[1]}", [perdedores_semis[0], perdedores_semis[1]], key="3er_puesto", horizontal=True)
    playoffs_resultados["Tercer_Puesto"] = tercer_puesto

with col_finales[1]:
    st.write("#### 🥇 Gran Final del Mundo")
    campeon = st.radio(f"🏆 FINAL: {finalistas[0]} vs {finalistas[1]}", [finalistas[0], finalistas[1]], key="final", horizontal=True)
    subcampeon = finalistas[1] if campeon == finalistas[0] else finalistas[0]
    playoffs_resultados["Campeon"] = campeon
    playoffs_resultados["Subcampeon"] = subcampeon

# --- Goleador ---
st.write("---")
st.write("### 👟 3. Premios Extra")
goleador = st.text_input("¿Quién creés que será el Bota de Oro (Goleador del Torneo)?:")
playoffs_resultados["Goleador"] = goleador

# 5. EXPORTACIÓN A CSV LIMPIO
st.write("---")
st.write("### 📊 4. Guardar y Exportar Predicción")

nombre_usuario = st.text_input("Introduce tu nombre o apodo del laboratorio para el archivo:")

# Consolidar toda la información en una sola fila para el DataFrame
datos_prode_usuario = {
    "Usuario": nombre_usuario,
    "Clasificados_Grupos": ",".join(lista_32_clasificados),
    **playoffs_resultados # Suma todos los ganadores de las llaves dinámicamente
}

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
