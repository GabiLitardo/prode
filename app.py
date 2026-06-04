import streamlit as st
import pandas as pd

st.set_page_config(page_title="Prode Laboratorio 2026", layout="wide")
st.title("🏆 Simulador Inteligente - Prode Mundial 2026")
st.subheader("Formato Oficial de 48 Equipos - Matriz de Cruces FIFA")

# ==============================================================================
# CARGA DE MATRIZ OFICIAL DESDE CSV EXTERNO
# ==============================================================================
@st.cache_data
def cargar_matriz_fifa():
    try:
        df = pd.read_csv("matriz_fifa_2026.csv", dtype=str)
        df.columns = df.columns.str.strip()
        df["combo"] = df["combo"].astype(str).str.strip().str.upper()
        for col in ["P3", "P6", "P7", "P8", "P9", "P10", "P13", "P16"]:
            df[col] = df[col].astype(str).str.strip().str.upper()
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["combo", "P3", "P6", "P7", "P8", "P9", "P10", "P13", "P16"])

df_matriz_oficial = cargar_matriz_fifa()

# Base de datos oficial de equipos
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

def asignar_tercero_fallback(opciones_partido, letras_disponibles, grupo_rival, terceros_dict):
    for letra in opciones_partido:
        if letra in letras_disponibles and letra != grupo_rival:
            letras_disponibles.remove(letra)
            return terceros_dict[letra]["equipo"]
    for letra in opciones_partido:
        if letra in letras_disponibles:
            letras_disponibles.remove(letra)
            return terceros_dict[letra]["equipo"]
    if letras_disponibles:
        letra = list(letras_disponibles)[0]
        letras_disponibles.remove(letra)
        return terceros_dict[letra]["equipo"]
    return "Tercero Pendiente"

st.write("### ⚽ 1. Carga los resultados de la Fase de Grupos")
st.caption("Coloca los goles. El sistema calculará las tablas e identificará los 8 mejores terceros de forma automática.")

tablas_grupos = {}
posiciones_fijas = {}
terceros_por_grupo = {}

# Diccionario para almacenar TODOS los goles de la fase de grupos para el CSV
goles_fase_grupos_csv = {}

cols_pestanas = st.columns(3)
for idx_g, (grupo, equipos) in enumerate(grupos_data.items()):
    g_letra = grupo.split(" ")[1]
    
    with cols_pestanas[idx_g % 3]:
        with st.expander(f"📅 Partidos {grupo}"):
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
                
                # Guardamos goles en el diccionario estructurado para exportación (Ej: "G_A_Mexico_vs_Corea": "2-1")
                goles_fase_grupos_csv[f"G_{g_letra}_{eq1}_vs_{eq2}"] = f"{g1}-{g2}"
                
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
                
            tabla_df = pd.DataFrame.from_dict(puntos, orient='index').reset_index()
            tabla_df.columns = ["Equipo", "pts", "gf", "gc", "dg"]
            tabla_df = tabla_df.sort_values(by=["pts", "dg", "gf", "Equipo"], ascending=[False, False, False, True]).set_index("Equipo")
            
            tablas_grupos[grupo] = tabla_df
            st.dataframe(tabla_df, use_container_width=True)
            
            posiciones_fijas[f"1{g_letra}"] = tabla_df.index[0]
            posiciones_fijas[f"2{g_letra}"] = tabla_df.index[1]
            terceros_por_grupo[g_letra] = {
                "equipo": tabla_df.index[2], "pts": tabla_df.iloc[2]["pts"], "dg": tabla_df.iloc[2]["dg"], "gf": tabla_df.iloc[2]["gf"]
            }

# ==============================================================================
# 📊 RANKING VISUAL DE MEJORES TERCEROS
# ==============================================================================
st.write("---")
st.write("### 🏅 Ranking de Mejores Terceros")
df_terceros = pd.DataFrame.from_dict(terceros_por_grupo, orient='index').sort_values(by=["pts", "dg", "gf"], ascending=False)
combo_terceros = "".join(sorted(list(df_terceros.index[:8])))
mejores_8_terceros = [terceros_por_grupo[l]["equipo"] for l in df_terceros.index[:8]]

df_visual_terceros = df_terceros.copy()
df_visual_terceros.index.name = "Grupo"
df_visual_terceros.columns = ["Equipo Tercero", "Pts", "DG", "GF"]

def destacar_clasificados(row):
    if row.name in df_terceros.index[:8]: return ['background-color: rgba(40, 167, 69, 0.2)'] * len(row)
    return ['background-color: rgba(220, 53, 69, 0.2)'] * len(row)

st.dataframe(df_visual_terceros.style.apply(destacar_clasificados, axis=1), use_container_width=True)

posiciones_completas = posiciones_fijas.copy()
fila_oficial = df_matriz_oficial[df_matriz_oficial["combo"] == combo_terceros]

if not fila_oficial.empty:
    posiciones_completas["3_P3"]  = terceros_por_grupo[fila_oficial["P3"].values[0]]["equipo"]
    posiciones_completas["3_P6"]  = terceros_por_grupo[fila_oficial["P6"].values[0]]["equipo"]
    posiciones_completas["3_P7"]  = terceros_por_grupo[fila_oficial["P7"].values[0]]["equipo"]
    posiciones_completas["3_P8"]  = terceros_por_grupo[fila_oficial["P8"].values[0]]["equipo"]
    posiciones_completas["3_P9"]  = terceros_por_grupo[fila_oficial["P9"].values[0]]["equipo"]
    posiciones_completas["3_P10"] = terceros_por_grupo[fila_oficial["P10"].values[0]]["equipo"]
    posiciones_completas["3_P13"] = terceros_por_grupo[fila_oficial["P13"].values[0]]["equipo"]
    posiciones_completas["3_P16"] = terceros_por_grupo[fila_oficial["P16"].values[0]]["equipo"]
    st.success(f"💪 ¡Fase de grupos completada! Terceros distribuidos mediante Matriz Oficial FIFA.")
else:
    letras_restantes = set(df_terceros.index[:8])
    posiciones_completas["3_P3"]  = asignar_tercero_fallback(["A", "B", "C", "D", "F"], letras_restantes, "E", terceros_por_grupo)
    posiciones_completas["3_P6"]  = asignar_tercero_fallback(["F", "D", "G", "H", "C"], letras_restantes, "I", terceros_por_grupo)
    posiciones_completas["3_P7"]  = asignar_tercero_fallback(["C", "E", "F", "H", "I"], letras_restantes, "A", terceros_por_grupo)
    posiciones_completas["3_P8"]  = asignar_tercero_fallback(["E", "H", "I", "J", "K"], letras_restantes, "L", terceros_por_grupo)
    posiciones_completas["3_P9"]  = asignar_tercero_fallback(["A", "E", "H", "I", "J"], letras_restantes, "G", terceros_por_grupo)
    posiciones_completas["3_P10"] = asignar_tercero_fallback(["B", "E", "F", "I", "J"], letras_restantes, "D", terceros_por_grupo)
    posiciones_completas["3_P13"] = asignar_tercero_fallback(["E", "F", "G", "I", "J"], letras_restantes, "B", terceros_por_grupo)
    posiciones_completas["3_P16"] = asignar_tercero_fallback(["D", "E", "I", "J", "L"], letras_restantes, "K", terceros_por_grupo)
    st.warning(f"⚠️ Combo '{combo_terceros}' no hallado en el CSV. Activado algoritmo de emergencia.")

# ==============================================================================
# FASE DE ELIMINACIÓN DIRECTA (CON GOLES Y FUNCIÓN DE PENALES INTEGRADA)
# ==============================================================================
st.write("---")
st.write("### 🔀 2. Cuadro de Eliminación Directa")
st.caption("Introduce los goles reglamentarios. Si hay empate, se abrirá automáticamente el casillero de Penales.")

cruces_16vos_estructura = [
    {"name": "Partido 1", "eq1": "2A", "eq2": "2B"}, {"name": "Partido 2", "eq1": "1C", "eq2": "2F"},
    {"name": "Partido 3", "eq1": "1E", "eq2": "3_P3"}, {"name": "Partido 4", "eq1": "1F", "eq2": "2C"},
    {"name": "Partido 5", "eq1": "2E", "eq2": "2I"}, {"name": "Partido 6", "eq1": "1I", "eq2": "3_P6"},
    {"name": "Partido 7", "eq1": "1A", "eq2": "3_P7"}, {"name": "Partido 8", "eq1": "1L", "eq2": "3_P8"},
    {"name": "Partido 9", "eq1": "1G", "eq2": "3_P9"}, {"name": "Partido 10", "eq1": "1D", "eq2": "3_P10"},
    {"name": "Partido 11", "eq1": "1H", "eq2": "2J"}, {"name": "Partido 12", "eq1": "2K", "eq2": "2L"},
    {"name": "Partido 13", "eq1": "1B", "eq2": "3_P13"}, {"name": "Partido 14", "eq1": "2D", "eq2": "2G"},
    {"name": "Partido 15", "eq1": "1J", "eq2": "2H"}, {"name": "Partido 16", "eq1": "1K", "eq2": "3_P16"}
]

if "ganadores_16vos" not in st.session_state: st.session_state.ganadores_16vos = [None] * 16
if "ganadores_8vos" not in st.session_state: st.session_state.ganadores_8vos = [None] * 8
if "ganadores_cuartos" not in st.session_state: st.session_state.ganadores_cuartos = [None] * 4
if "finalistas" not in st.session_state: st.session_state.finalistas = [None] * 2
if "perdedores_semis" not in st.session_state: st.session_state.perdedores_semis = [None] * 2

playoffs_goles_y_ganadores = {}

# --- FUNCIÓN CONTROLADORA DE PARTIDOS DE ELIMINACIÓN DIRECTA (UX SUPREMA) ---
def render_partido_eliminacion(etiqueta, eq_l, eq_v, key_prefijo):
    st.write(f"**{etiqueta}**")
    c1, c2, c3, c4 = st.columns([3, 1, 1, 3])
    with c1: st.write(eq_l)
    g_l = c2.number_input("G", min_value=0, step=1, key=f"{key_prefijo}_gl", label_visibility="collapsed")
    g_v = c3.number_input("G", min_value=0, step=1, key=f"{key_prefijo}_gv", label_visibility="collapsed")
    with c4: st.write(eq_v)
    
    ganador_partido = None
    string_marcador = f"{g_l}-{g_v}"
    
    if g_l > g_v:
        ganador_partido = eq_l
    elif g_v > g_l:
        ganador_partido = eq_v
    else:
        # CASO EMPATE: Se despliega la tanda de penales
        st.caption(f"☘️ Definición por Penales para {etiqueta}:")
        cp1, cp2, cp3 = st.columns([3, 2, 3])
        with cp1: p_l = st.number_input(f"Penales {eq_l}", min_value=0, step=1, key=f"{key_prefijo}_pl")
        with cp3: p_v = st.number_input(f"Penales {eq_v}", min_value=0, step=1, key=f"{key_prefijo}_pv")
        
        string_marcador += f" ({p_l}-{p_v} Pen)"
        ganador_partido = eq_l if p_l >= p_v else eq_v
        
    # Guardamos los goles estructurados y el ganador de forma explícita
    playoffs_goles_y_ganadores[f"Goles_{key_prefijo}"] = string_marcador
    playoffs_goles_y_ganadores[f"Ganador_{key_prefijo}"] = ganador_partido
    return ganador_partido

# --- Dieciseisavos de Final ---
st.write("#### 🔹 Dieciseisavos de Final")
col_16_1, col_16_2 = st.columns(2)
for i, cruce in enumerate(cruces_16vos_estructura):
    eq_local = posiciones_completas.get(cruce["eq1"], cruce["eq1"])
    eq_visita = posiciones_completas.get(cruce["eq2"], cruce["eq2"])
    target_col = col_16_1 if i < 8 else col_16_2
    with target_col:
        win = render_partido_eliminacion(cruce["name"], eq_local, eq_visita, f"16vos_P{i+1}")
        st.session_state.ganadores_16vos[i] = win

# --- Octavos de Final ---
st.write("---")
st.write("#### 🔹 Octavos de Final")
col_8_1, col_8_2 = st.columns(2)
for i in range(8):
    eq_local = st.session_state.ganadores_16vos[i*2]
    eq_visita = st.session_state.ganadores_16vos[i*2 + 1]
    target_col = col_8_1 if i < 4 else col_8_2
    with target_col:
        win = render_partido_eliminacion(f"Octavos {i+1}", eq_local, eq_visita, f"Octavos_O{i+1}")
        st.session_state.ganadores_8vos[i] = win

# --- Cuartos de Final ---
st.write("---")
st.write("#### 🔹 Cuartos de Final")
col_4_1, col_4_2 = st.columns(2)
for i in range(4):
    eq_local = st.session_state.ganadores_8vos[i*2]
    eq_visita = st.session_state.ganadores_8vos[i*2 + 1]
    target_col = col_4_1 if i < 2 else col_4_2
    with target_col:
        win = render_partido_eliminacion(f"Cuartos {i+1}", eq_local, eq_visita, f"Cuartos_C{i+1}")
        st.session_state.ganadores_cuartos[i] = win

# --- Semifinales ---
st.write("---")
st.write("#### 🔹 Semifinales")
col_semi = st.columns(2)
for i in range(2):
    eq_local = st.session_state.ganadores_cuartos[i*2]
    eq_visita = st.session_state.ganadores_cuartos[i*2 + 1]
    with col_semi[i]:
        win = render_partido_eliminacion(f"Semifinal {i+1}", eq_local, eq_visita, f"Semis_S{i+1}")
        st.session_state.finalistas[i] = win
        st.session_state.perdedores_semis[i] = eq_visita if win == eq_local else eq_local

# --- Tercer Puesto y Gran Final ---
st.write("---")
col_finales = st.columns(2)
with col_finales[0]:
    render_partido_eliminacion("🥉 Partido por el Tercer Puesto", st.session_state.perdedores_semis[0], st.session_state.perdedores_semis[1], "Tercer_Puesto")
with col_finales[1]:
    render_partido_eliminacion("🥇 Gran Final del Mundo", st.session_state.finalistas[0], st.session_state.finalistas[1], "Final")

# --- Extras y Exportación ---
st.write("---")
st.write("### 👟 3. Premios Extra")
goleador = st.text_input("¿Quién creés que será el Bota de Oro (Goleador del Torneo)?:")
playoffs_goles_y_ganadores["Goleador"] = goleador

st.write("---")
st.write("### 📊 4. Guardar y Exportar Predicción")
nombre_usuario = st.text_input("Introduce tu nombre o apodo del laboratorio para el archivo:")

if nombre_usuario:
    lista_clasificados = []
    for g in ["A","B","C","D","E","F","G","H","I","J","K","L"]:
        lista_clasificados.append(posiciones_completas[f"1{g}"])
        lista_clasificados.append(posiciones_completas[f"2{g}"])
    for casillero in ["3_P3", "3_P6", "3_P7", "3_P8", "3_P9", "3_P10", "3_P13", "3_P16"]:
        lista_clasificados.append(posiciones_completas[casillero])

    # 🚀 UNIFICACIÓN TOTAL DE DATOS EN EL CSV
    datos_prode_usuario = {
        "Usuario": nombre_usuario,
        "Clasificados_Grupos": ",".join(lista_clasificados),
        **goles_fase_grupos_csv,       # Agrega todos los goles calculados de grupos
        **playoffs_goles_y_ganadores   # Agrega goles, penales y ganadores de playoffs
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
