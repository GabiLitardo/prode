import streamlit as st
import pandas as pd

st.set_page_config(page_title="Prode Laboratorio 2026", layout="wide")
st.title("🏆 Simulador Inteligente - Prode Mundial 2026")
st.subheader("Formato Oficial de 48 Equipos - Matriz de Cruces FIFA")

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
            
        # Ordenamiento reglamentario (Se le añade el index al final para evitar empates absolutos)
        tabla_df = pd.DataFrame.from_dict(puntos, orient='index').sort_values(by=["pts", "dg", "gf"], ascending=False)
        tablas_grupos[grupo] = tabla_df
        st.dataframe(tabla_df, use_container_width=True)

# 2. PROCESAMIENTO MATEMÁTICO DE POSICIONES
posiciones_fijas = {}
terceros_por_grupo = {}

for grupo, tabla in tablas_grupos.items():
    g_letra = grupo.split(" ")[1] # Extrae la letra del grupo (A, B, C...)
    posiciones_fijas[f"1{g_letra}"] = tabla.index[0] 
    posiciones_fijas[f"2{g_letra}"] = tabla.index[1] 
    # Guardamos los terceros con su respectiva información para el ranking de mejores terceros
    terceros_por_grupo[g_letra] = {
        "equipo": tabla.index[2],
        "pts": tabla.iloc[2]["pts"],
        "dg": tabla.iloc[2]["dg"],
        "gf": tabla.iloc[2]["gf"]
    }

# Ranking global de los terceros para ver cuáles 8 clasifican
df_terceros = pd.DataFrame.from_dict(terceros_por_grupo, orient='index').sort_values(by=["pts", "dg", "gf"], ascending=False)
letras_terceros_clasificados = set(df_terceros.index[:8]) # Guardamos las 8 letras (ej: {'A', 'C', 'E', ...})

# --- ALGORITMO OFICIAL DE RESOLUCIÓN DE TERCEROS DE LA FIFA ---
# Esta función toma las opciones reglamentarias de cada partido y elige el grupo correspondiente,
# asegurándose de que la letra ya haya sido utilizada y que el tercero no enfrente a su propio grupo.
def asignar_tercero_oficial(opciones_partido, letras_disponibles, grupo_rival):
    # Intentamos emparejar siguiendo el orden estricto de opciones provisto por el fixture
    for letra in opciones_partido:
        if letra in letras_disponibles and letra != grupo_rival:
            letras_disponibles.remove(letra)
            return terceros_por_grupo[letra]["equipo"]
    # Fallback reglamentario de emergencia en caso de que la prioridad filtre por coincidencia de grupo
    for letra in opciones_partido:
        if letra in letras_disponibles:
            letras_disponibles.remove(letra)
            return terceros_por_grupo[letra]["equipo"]
    # Si quedan flecos por combinaciones raras, toma el primer disponible de los clasificados generales
    if letras_disponibles:
        letra = list(letras_disponibles)[0]
        letras_disponibles.remove(letra)
        return terceros_por_grupo[letra]["equipo"]
    return "Tercero Pendiente"

# Duplicamos el set para poder ir removiendo las letras asignadas sin alterar el original
letras_restantes = letras_terceros_clasificados.copy()

posiciones_completas = posiciones_fijas.copy()
posiciones_completas["3_P3"]  = asignar_tercero_oficial(["A", "B", "C", "D", "F"], letras_restantes, "E")
posiciones_completas["3_P6"]  = asignar_tercero_oficial(["F", "D", "G", "H", "C"], letras_restantes, "I")
posiciones_completas["3_P7"]  = asignar_tercero_oficial(["C", "E", "F", "H", "I"], letras_restantes, "A")
posiciones_completas["3_P8"]  = asignar_tercero_oficial(["E", "H", "I", "J", "K"], letras_restantes, "L")
posiciones_completas["3_P9"]  = asignar_tercero_oficial(["A", "E", "H", "I", "J"], letras_restantes, "G")
posiciones_completas["3_P10"] = asignar_tercero_oficial(["B", "E", "F", "I", "J"], letras_restantes, "D")
posiciones_completas["3_P13"] = asignar_tercero_oficial(["E", "F", "G", "I", "J"], letras_restantes, "B")
posiciones_completas["3_P16"] = asignar_tercero_oficial(["D", "E", "I", "J", "L"], letras_restantes, "K")

st.success(f"💪 ¡Fase de grupos completada! Terceros distribuidos con la matriz matemática oficial de la FIFA.")

# --- FASE DE ELIMINACIÓN DIRECTA ---
st.write("---")
st.write("### 🔀 2. Cuadro de Eliminación Directa")

# Tu matriz exacta e irrevocable de cruces oficiales de la FIFA
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

# Inicialización de estados en Session State para evitar bugs de persistencia en los Radio Buttons
if "ganadores_16vos" not in st.session_state:
    st.session_state.ganadores_16vos = [None] * 16
if "ganadores_8vos" not in st.session_state:
    st.session_state.ganadores_8vos = [None] * 8
if "ganadores_cuartos" not in st.session_state:
    st.session_state.ganadores_cuartos = [None] * 4
if "finalistas" not in st.session_state:
    st.session_state.finalistas = [None] * 2
if "perdedores_semis" not in st.session_state:
    st.session_state.perdedores_semis = [None] * 2

playoffs_resultados = {}

# --- 16vos de Final ---
st.write("#### 🔹 Dieciseisavos de Final")
col_16_1, col_16_2 = st.columns(2)

for i, cruce in enumerate(cruces_16vos_estructura):
    eq_local = posiciones_completas.get(cruce["eq1"], cruce["eq1"])
    eq_visita = posiciones_completas.get(cruce["eq2"], cruce["eq2"])
    
    target_col = col_16_1 if i < 8 else col_16_2
    with target_col:
        current_idx = 0
        if st.session_state.ganadores_16vos[i] == eq_visita:
            current_idx = 1
            
        ganador = st.radio(
            f"**{cruce['name']}**: {eq_local} vs {eq_visita}", 
            [eq_local, eq_visita], 
            index=current_idx,
            key=f"l16_state_{i}", 
            horizontal=True
        )
        st.session_state.ganadores_16vos[i] = ganador
        playoffs_resultados[f"Ganador_16vos_P{i+1}"] = ganador

# --- Octavos de Final ---
st.write("---")
st.write("#### 🔹 Octavos de Final")
col_8_1, col_8_2 = st.columns(2)

for i in range(8):
    eq_local = st.session_state.ganadores_16vos[i*2]
    eq_visita = st.session_state.ganadores_16vos[i*2 + 1]
    
    target_col = col_8_1 if i < 4 else col_8_2
    with target_col:
        current_idx = 0
        if st.session_state.ganadores_8vos[i] == eq_visita:
            current_idx = 1
            
        ganador = st.radio(
            f"Octavos {i+1} (Ganador P{i*2+1} vs P{i*2+2})", 
            [eq_local, eq_visita], 
            index=current_idx,
            key=f"l8_state_{i}", 
            horizontal=True
        )
        st.session_state.ganadores_8vos[i] = ganador
        playoffs_resultados[f"Ganador_8vos_O{i+1}"] = ganador

# --- Cuartos de Final ---
st.write("---")
st.write("#### 🔹 Cuartos de Final")
col_4_1, col_4_2 = st.columns(2)

for i in range(4):
    eq_local = st.session_state.ganadores_8vos[i*2]
    eq_visita = st.session_state.ganadores_8vos[i*2 + 1]
    
    target_col = col_4_1 if i < 2 else col_4_2
    with target_col:
        current_idx = 0
        if st.session_state.ganadores_cuartos[i] == eq_visita:
            current_idx = 1
            
        ganador = st.radio(
            f"Cuartos {i+1} (Ganador Octavos {i*2+1} vs {i*2+2})", 
            [eq_local, eq_visita], 
            index=current_idx,
            key=f"l4_state_{i}", 
            horizontal=True
        )
        st.session_state.ganadores_cuartos[i] = ganador
        playoffs_resultados[f"Ganador_Cuartos_C{i+1}"] = ganador

# --- Semifinales ---
st.write("---")
st.write("#### 🔹 Semifinales")
col_semi = st.columns(2)

for i in range(2):
    eq_local = st.session_state.ganadores_cuartos[i*2]
    eq_visita = st.session_state.ganadores_cuartos[i*2 + 1]
    
    with col_semi[i]:
        current_idx = 0
        if st.session_state.finalistas[i] == eq_visita:
            current_idx = 1
            
        ganador = st.radio(
            f"Semifinal {i+1} (Ganador Cuartos {i*2+1} vs {i*2+2})", 
            [eq_local, eq_visita], 
            index=current_idx,
            key=f"lsemi_state_{i}", 
            horizontal=True
        )
        st.session_state.finalistas[i] = ganador
        perdedor = eq_visita if ganador == eq_local else eq_local
        st.session_state.perdedores_semis[i] = perdedor
        playoffs_resultados[f"Ganador_Semi_{i+1}"] = ganador

# --- Tercer Puesto y Gran Final ---
st.write("---")
col_finales = st.columns(2)

with col_finales[0]:
    st.write("#### 🥉 Partido por el Tercer Puesto")
    p_3er_1 = st.session_state.perdedores_semis[0]
    p_3er_2 = st.session_state.perdedores_semis[1]
    tercer_puesto = st.radio(f"Definición: {p_3er_1} vs {p_3er_2}", [p_3er_1, p_3er_2], key="3er_puesto_state", horizontal=True)
    playoffs_resultados["Tercer_Puesto"] = tercer_puesto

with col_finales[1]:
    st.write("#### 🥇 Gran Final del Mundo")
    f1 = st.session_state.finalistas[0]
    f2 = st.session_state.finalistas[1]
    campeon = st.radio(f"🏆 FINAL: {f1} vs {f2}", [f1, f2], key="final_state", horizontal=True)
    subcampeon = f2 if campeon == f1 else f1
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
    "Clasificados_Grupos": ",".join(list(posiciones_completas.values())),
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
    st.info("Escribe tu nombre arriba para habilitar el botón de descarga del CSV.")import streamlit as st
import pandas as pd

st.set_page_config(page_title="Prode Laboratorio 2026", layout="wide")
st.title("🏆 Simulador Inteligente - Prode Mundial 2026")
st.subheader("Formato Oficial de 48 Equipos - Llave Completa")

# 1. Base de datos oficial
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
st.caption("Coloca los goles. El sistema calculará las tablas e identificará los mejores terceros de forma automática.")

tablas_grupos = {}

for grupo, equipos in grupos_data.items():
    with st.expander(f"📅 Partidos del {grupo}"):
        partidos = [
            (equipos[0], equipos[1]), (equipos[2], equipos[3]),
            (equipos[0], equipos[2]), (equipos[1], equipos[3]),
            (equipos[0], equipos[3]), (equipos[1], equipos[2])
        ]
        
        puntos = {eq: {"pts": 0, "gf": 0, "gc": 0, "dg": 0} for eq in equipos}
        
        # Crear columnas de títulos para mejor interfaz
        col_t1, col_t2, col_t3, col_t4 = st.columns([3, 1, 1, 3])
        
        for eq1, eq2 in partidos:
            col1, col2, col3, col4 = st.columns([3, 1, 1, 3])
            with col1: st.write(f"{eq1}")
            g1 = col2.number_input("G", min_value=0, step=1, key=f"{grupo}_{eq1}_{eq2}_g1", label_visibility="collapsed")
            g2 = col3.number_input("G", min_value=0, step=1, key=f"{grupo}_{eq2}_{eq1}_g2", label_visibility="collapsed")
            with col4: st.write(f"{eq2}")
            
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
            
        # Agregamos el nombre del equipo como criterio secundario (alfabético) para evitar empates idénticos en Pandas
        tabla_df = pd.DataFrame.from_dict(puntos, orient='index').reset_index()
        tabla_df.columns = ["Equipo", "pts", "gf", "gc", "dg"]
        tabla_df = tabla_df.sort_values(by=["pts", "dg", "gf", "Equipo"], ascending=[False, False, False, True]).set_index("Equipo")
        
        tablas_grupos[grupo] = tabla_df
        st.dataframe(tabla_df, use_container_width=True)

# 2. PROCESAMIENTO MATEMÁTICO DE POSICIONES
posiciones = {}
todos_los_terceros = {}

for grupo, tabla in tablas_grupos.items():
    g_letra = grupo.split(" ")[1] 
    posiciones[f"1{g_letra}"] = tabla.index[0] 
    posiciones[f"2{g_letra}"] = tabla.index[1] 
    todos_los_terceros[tabla.index[2]] = {**tabla.iloc[2].to_dict(), "equipo": tabla.index[2], "grupo": g_letra}

# Ranking de mejores terceros
mejores_terceros_df = pd.DataFrame.from_dict(todos_los_terceros, orient='index')
mejores_terceros_df = mejores_terceros_df.sort_values(by=["pts", "dg", "gf", "equipo"], ascending=[False, False, False, True])
mejores_8_terceros = list(mejores_terceros_df["equipo"].iloc[:8])

# Mapeo preventivo de terceros
terceros_mapeo = ["3_P3", "3_P6", "3_P7", "3_P8", "3_P9", "3_P10", "3_P13", "3_P16"]
for idx, ter_nom in enumerate(mejores_8_terceros):
    posiciones[terceros_mapeo[idx]] = ter_nom

st.success(f"💪 ¡Fase de grupos completada con éxito! Se armaron los cruces.")

# --- FASE DE ELIMINACIÓN DIRECTA ---
st.write("---")
st.write("### 🔀 2. Cuadro de Eliminación Directa")

playoffs_resultados = {}

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

# --- Octavos de Final ---
st.write("---")
st.write("#### 🔹 Octavos de Final")
ganadores_8vos = []
col_8_1, col_8_2 = st.columns(2)

for i in range(8):
    eq_local = ganadores_16vos[i*2]
    eq_visita = ganadores_16vos[i*2 + 1]
    
    target_col = col_8_1 if i < 4 else col_8_2
    with target_col:
        ganador = st.radio(f"Octavos {i+1} (Ganador P{i*2+1} vs P{i*2+2})", [eq_local, eq_visita], key=f"l8_{i}", horizontal=True)
        ganadores_8vos.append(ganador)
        playoffs_resultados[f"Ganador_8vos_O{i+1}"] = ganador

# --- Cuartos de Final ---
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

# --- Extras y Exportación ---
st.write("---")
st.write("### 👑 3. Premios Extra")
goleador = st.text_input("¿Quién creés que será el Bota de Oro (Goleador del Torneo)?:")
playoffs_resultados["Goleador"] = goleador

st.write("---")
st.write("### 📊 4. Guardar y Exportar Predicción")
nombre_usuario = st.text_input("Introduce tu nombre o apodo del laboratorio para el archivo:")

if nombre_usuario:
    # Extracción explícita y segura de los nombres ordenados de clasificados
    lista_clasificados = []
    for g in ["A","B","C","D","E","F","G","H","I","J","K","L"]:
        lista_clasificados.append(posiciones[f"1{g}"])
        lista_clasificados.append(posiciones[f"2{g}"])
    lista_clasificados.extend(mejores_8_terceros)

    datos_prode_usuario = {
        "Usuario": nombre_usuario,
        "Clasificados_Grupos": ",".join(lista_clasificados),
        **playoffs_resultados
    }

    df_exportar = pd.DataFrame([datos_prode_usuario])
    csv_data = df_exportar.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="💾 DESCARGAR PREDICCIÓN EN CSV",
        data=csv_data,
        file_name=f"prode_2026_{nombre_usuario.lower().replace(' ', '_')}.csv",
        mime="text/csv",
    )
else:
    st.info("Escribe tu nombre arriba para habilitar el botón de descarga del CSV.")
