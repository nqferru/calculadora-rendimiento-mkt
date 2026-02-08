import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Analizador de Impacto Social", layout="wide")

st.title("📊 Calculadora de Eficiencia de Contenido")
st.markdown("""
Esta herramienta calcula el **Z-Score** de tu post actual comparándolo con el rendimiento histórico.
*No mide vanidad (likes), mide anomalías estadísticas de eficiencia.*
""")

# --- BARRA LATERAL: CONFIGURACIÓN ---
with st.sidebar:
    st.header("⚙️ Configuración de Pesos")
    st.info("Define cuánto vale cada interacción según tu estrategia.")
    w_like = st.number_input("Peso Like", value=1.0)
    w_save = st.number_input("Peso Guardado", value=2.0)
    w_share = st.number_input("Peso Compartido", value=3.0)
    w_comment = st.number_input("Peso Comentario", value=4.0)

# --- LÓGICA DE CÁLCULO ---
def calcular_wer(row):
    """Calcula Weighted Engagement Rate sobre Alcance"""
    try:
        interaction_score = (
            (row['Likes'] * w_like) +
            (row['Guardados'] * w_save) +
            (row['Compartidos'] * w_share) +
            (row['Comentarios'] * w_comment)
        )
        if row['Alcance'] == 0:
            return 0
        return (interaction_score / row['Alcance']) * 100
    except:
        return 0

# --- INTERFAZ PRINCIPAL ---

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("1. Post a Analizar")
    cur_reach = st.number_input("Alcance (Reach)", min_value=1, value=15000)
    cur_likes = st.number_input("Likes", min_value=0, value=450)
    cur_saves = st.number_input("Guardados", min_value=0, value=45)
    cur_shares = st.number_input("Compartidos", min_value=0, value=20)
    cur_comments = st.number_input("Comentarios", min_value=0, value=15)

with col2:
    st.subheader("2. Historial (Últimos 10 Posts)")
    st.markdown("Edita los valores o **copia y pega desde Excel**.")
    
    # Datos iniciales de ejemplo (para que no esté vacío)
    data_inicial = {
        'Alcance': [12000, 13500, 11000, 45000, 12500, 11800, 14000, 12200, 13000, 12100],
        'Likes': [300, 320, 290, 800, 310, 305, 330, 295, 315, 300],
        'Guardados': [20, 25, 15, 100, 22, 18, 28, 19, 24, 20],
        'Compartidos': [5, 8, 4, 50, 6, 5, 10, 6, 7, 5],
        'Comentarios': [8, 10, 5, 60, 9, 7, 12, 6, 11, 8]
    }
    df_history = pd.DataFrame(data_inicial)
    
    # Widget de tabla editable
    edited_df = st.data_editor(df_history, num_rows="dynamic")

# --- BOTÓN DE ANÁLISIS ---
st.divider()

if st.button("🚀 ANALIZAR RENDIMIENTO", type="primary"):
    
    # 1. Calcular WER del Historial
    edited_df['WER'] = edited_df.apply(calcular_wer, axis=1)
    
    media_hist = edited_df['WER'].mean()
    std_hist = edited_df['WER'].std()
    mediana_hist = edited_df['WER'].median()
    
    # 2. Calcular WER Actual
    datos_actuales = {
        'Likes': cur_likes, 'Guardados': cur_saves, 
        'Compartidos': cur_shares, 'Comentarios': cur_comments, 
        'Alcance': cur_reach
    }
    wer_actual = calcular_wer(datos_actuales)
    
    # 3. Calcular Z-Score
    if std_hist == 0:
        z_score = 0
    else:
        z_score = (wer_actual - media_hist) / std_hist
        
    # --- RESULTADOS VISUALES ---
    
    # Métricas grandes
    m1, m2, m3 = st.columns(3)
    m1.metric("WER Actual", f"{wer_actual:.2f}%", delta=f"{wer_actual - media_hist:.2f}% vs Promedio")
    m2.metric("Promedio Histórico", f"{media_hist:.2f}%")
    m3.metric("Z-Score (Anomalía)", f"{z_score:.2f}", delta_color="normal" if z_score > 0 else "inverse")
    
    st.subheader("Diagnóstico Técnico")
    
    if z_score >= 2.0:
        st.success(f"🔥 **OUTLIER POSITIVO DETECTADO (Z={z_score:.2f})**: Este contenido es una anomalía de éxito. Rompió el patrón histórico. **ACCIÓN: Replicar formato inmediatamente.**")
    elif 1.0 <= z_score < 2.0:
        st.success(f"✅ **ALTO RENDIMIENTO (Z={z_score:.2f})**: Supera el ruido normal de la cuenta. Muy buen trabajo.")
    elif -1.0 < z_score < 1.0:
        st.warning(f"😐 **RENDIMIENTO ESTÁNDAR (Z={z_score:.2f})**: Dentro de la variabilidad normal. El contenido cumplió pero no destacó.")
    else:
        st.error(f"📉 **BAJO RENDIMIENTO (Z={z_score:.2f})**: El contenido tuvo un rendimiento significativamente menor a lo esperado para el alcance obtenido.")

    # Mostrar tabla de cálculos para transparencia
    with st.expander("Ver desglose de datos históricos"):
        st.dataframe(edited_df.style.format("{:.2f}", subset="WER"))