import streamlit as st
import pandas as pd


st.set_page_config(page_title="Prode Laboratorio 2026", layout="wide")
st.title("🏆 Simulador Inteligente - Prode Mundial 2026")
st.subheader("Formato Oficial de 48 Equipos - Llave Completa")

# 1. Base de datos oficial aportada por el usuario
grupos_data = {
    "Grupo A": ["México", "Corea", "Chequia", "Sudáfrica"],
    "Grupo B": ["Suiza", "Bosnia", "Canada", "Qatar"],
    "Grupo C": ["Brasil", "Marruecos", "Haití", "Escocia"],
    "Grupo D": ["EEUU", "Paraguay", "Australia", "Turquía"],
    "Grupo E": ["Alemania", "Curazao", "Costa de Marfil", "Ecuador"],
    "Grupo F": ["Países Bajos", "Japón", "Suecia", "Túnez"],
    "Grupo G": ["Bélgica", "Egipto", "Irán", "Nueva Zelanda"],
    "Grupo H": ["España", "Cabo Verde", "Arabia Saudita", "Uruguay"],
    "Grupo I": ["Francia", "Senegal", "Irak", "Noruega"],
    "Grupo J": ["Argentina", "Argelia", "Austria", "Jordania"],
    "Grupo K": ["Portugal", "RD Congo", "Uzbekistán", "Colombia"],
    "Grupo L": ["Inglaterra", "Croacia", "Ghana", "Panamá"]
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

# 2. PROCESAMIENTO MATEMÁTICO DE POSICIONES
posiciones = {}
todos_los_terceros = {}

for grupo, tabla in tablas_grupos.items():
    g_letra = grupo.split(" ")[1] # Extrae la letra del grupo
    posiciones[f"1{g_letra}"] = tabla.index[0] 
    posiciones[f"2{g_letra}"] = tabla.index[1] 
    todos_los_terceros[tabla.index[2]] = {**tabla.iloc[2].to_dict(), "equipo": tabla.index[2]}

# Ranking de mejores terceros
mejores_terceros_df = pd.DataFrame.from_dict(todos_los_terceros, orient='index').sort_values(by=["pts", "dg", "gf"], ascending=False)
mejores_8_terceros = list(mejores_terceros_df["equipo"].iloc[:8])

# Asignar los 8 mejores terceros de forma secuencial a los casilleros del fixture reglamentario
terceros_mapeo = ["3_P3", "3_P6", "3_P7", "3_P8", "3_P9", "3_P10", "3_P13", "3_P16"]
for idx, ter_nom in enumerate(mejores_8_terceros):
    posiciones[terceros_mapeo[idx]] = ter_nom

# Relleno de seguridad
for c_ter in terceros_mapeo:
    if c_ter not in posiciones:
        posiciones[c_ter] = f"Tercero ({c_ter.split('_')[1]})"

st.success(f"💪 ¡Fase de grupos completada con éxito! Se armaron los cruces oficiales de la FIFA.")

# --- FASE DE ELIMINACIÓN DIRECTA ---
st.write("---")
st.write("### 🔀 2. Cuadro de Eliminación Directa")

playoffs_resultados = {}

# Tu matriz exacta de cruces oficiales para los 16 partidos de 16vos
cruces_16vos_estructura = [
    {"name": "Partido 1", "eq1": "2A", "eq2": "2B"},
    {"name": "Partido 2", "eq1": "1C", "eq2": "2F"},
    {"name": "Partido 3", "eq1": "1E", "eq2": "3_P3"},
    {"name": "Partido 4", "eq1": "1F", "eq2": "2C"},
    {"name": "Partido 5", "eq1": "2E", "eq2": "2I"},
    {"name": "Partido 6", "eq1": "1I", "eq2": "3_P6"},
    {"name": "Partido 7", "eq1": "1A", "eq2": "3_P7"},
    {"name": "Partido 8", "eq1": "1L", "eq2": "3_P8"},
    {"name": "Partido 9", "eq1": "1G", "eq2": "3_P9"},
    {"name": "Partido 10", "eq1": "1D", "eq2": "3_P10"},
    {"name": "Partido 11", "eq1": "1H", "eq2": "2J"},
    {"name": "Partido 12", "eq1": "2K", "eq2": "2L"},
    {"name": "Partido 13", "eq1": "1B", "eq2": "3_P13"},
    {"name": "Partido 14", "eq1": "2D", "eq2": "2G"},
    {"name": "Partido 15", "eq1": "1J", "eq2": "2H"},
    {"name": "Partido 16", "eq1": "1K", "eq2": "3_P16"}
]

# --- 16vos de Final ---
st.write("#### 🔹 Dieciseisavos de Final")
ganadores_16vos = []
col_16_1, col_16_2 = st.columns(2)

for i, cruce in enumerate(cruces_16vos_estructura):
    eq_local = posiciones.get(cruce["eq1"], cruce["eq1"])
    eq_visita = posiciones.get(cruce["eq2"], cruce["eq2"])
    
    target_col = col_16_1 if i < 8 else col_16_2
    with target_col:
        ganador = st.radio(f"**{cruce['name']}**: {eq_local} vs {eq_visita}", [eq_local, eq_visita], key=f"l16_{i}", horizontal=True)
        ganadores_16vos.append(ganador)
        playoffs_resultados[f"Ganador_16vos_P{i+1}"] = ganador

# --- Octavos de Final (P1 vs P2, P3 vs P4...) ---
st.write("---")
st.write("#### 🔹 Octavos de Final")
ganadores_8vos = []
col_8_1, col_8_2 = st.columns(2)

for i in range(8):
    eq_local = ganadores_16vos[i*2]
    eq_visita = ganadores_16vos[i*2 + 1]
    
    target_col = col_8_1 if i < 4 else col_8_2
    with target_col:
        ganador = st.radio(f"Octavos {i+1} (Ganador P{i*2+1} vs Ganador P{i*2+2})", [eq_local, eq_visita], key=f"l8_{i}", horizontal=True)
        ganadores_8vos.append(ganador)
        playoffs_resultados[f"Ganador_8vos_O{i+1}"] = ganador

# --- Cuartos de Final (O1 vs O2, O3 vs O4...) ---
st.write("---")
st.write("#### 🔹 Cuartos de Final")
ganadores_cuartos = []
col_4_1, col_4_2 = st.columns(2)

for i in range(4):
    eq_local = ganadores_8vos[i*2]
    eq_visita = ganadores_8vos[i*2 + 1]
    
    target_col = col_4_1 if i < 2 else col_4_2
    with target_col:
        ganador = st.radio(f"Cuartos {i+1} (Ganador Octavos {i*2+1} vs {i*2+2})", [eq_local, eq_visita], key=f"l4_{i}", horizontal=True)
        ganadores_cuartos.append(ganador)
        playoffs_resultados[f"Ganador_Cuartos_C{i+1}"] = ganador

# --- Semifinales ---
st.write("---")
st.write("#### 🔹 Semifinales")
finalistas = []
perdedores_semis = []
col_semi = st.columns(2)

for i in range(2):
    eq_local = ganadores_cuartos[i*2]
    eq_visita = ganadores_cuartos[i*2 + 1]
    
    with col_semi[i]:
        ganador = st.radio(f"Semifinal {i+1} (Ganador Cuartos {i*2+1} vs {i*2+2})", [eq_local, eq_visita], key=f"lsemi_{i}", horizontal=True)
        finalistas.append(ganador)
        perdedor = eq_visita if ganador == eq_local else eq_local
        perdedores_semis.append(perdedor)
        playoffs_resultados[f"Ganador_Semi_{i+1}"] = ganador

# --- Tercer Puesto y Gran Final ---
st.write("---")
col_finales = st.columns(2)

with col_finales[0]:
    st.write("#### 🥉 Partido por el Tercer Puesto")
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

datos_prode_usuario = {
    "Usuario": nombre_usuario,
    "Clasificados_Grupos": ",".join(list(posiciones.values())[:24] + mejores_8_terceros),
    **playoffs_resultados
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
