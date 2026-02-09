import streamlit as st
import pandas as pd
import numpy as np
import io

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Analizador de Impacto", layout="wide")
st.title("📊 Calculadora de Eficiencia de Contenido")

# --- BARRA LATERAL: PESOS ---
with st.sidebar:
    st.header("⚙️ Configuración")
    w_like = st.number_input("Peso Like", value=1.0)
    w_save = st.number_input("Peso Guardado", value=2.0)
    w_share = st.number_input("Peso Compartido", value=3.0)
    w_comment = st.number_input("Peso Comentario", value=4.0)

# --- FUNCIÓN DE CÁLCULO ---
def calcular_wer(row):
    try:
        score = (row['Likes'] * w_like) + (row['Guardados'] * w_save) + \
                (row['Compartidos'] * w_share) + (row['Comentarios'] * w_comment)
        return (score / row['Alcance']) * 100 if row['Alcance'] > 0 else 0
    except: return 0

# --- INTERFAZ ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("1. Post Actual")
    cur_reach = st.number_input("Alcance", value=15000)
    cur_likes = st.number_input("Likes", value=450)
    cur_saves = st.number_input("Guardados", value=45)
    cur_shares = st.number_input("Compartidos", value=20)
    cur_comments = st.number_input("Comentarios", value=15)

with col2:
    st.subheader("2. Historial (Excel)")
    st.info("Selecciona en Excel SOLO los números de los últimos 10 posts (sin encabezados). Copia y pega aquí.")
    
    # Instrucción visual de las columnas esperadas
    st.markdown("**Orden de columnas en Excel:** `Alcance` | `Likes` | `Guardados` | `Compartidos` | `Comentarios`")
    
    # EL CAMBIO CLAVE: Un área de texto simple en lugar de tabla
    texto_pegado = st.text_area("Pega aquí los datos (Ctrl+V o Cmd+V):", height=200,
                                placeholder="Ejemplo:\n12000\t300\t20\t5\t8\n13500\t320\t25\t8\t10...")

# --- PROCESAMIENTO ---
if st.button("🚀 ANALIZAR AHORA", type="primary"):
    if not texto_pegado:
        st.error("⚠️ Por favor pega los datos del historial primero.")
    else:
        try:
            # Magia: Convertir texto tabulado de Excel a DataFrame
            df = pd.read_csv(io.StringIO(texto_pegado), sep='\t', header=None)
            
            # Asignar nombres a las columnas automáticamente
            # Si pegó más columnas, cortamos a las primeras 5
            df = df.iloc[:, :5]
            df.columns = ['Alcance', 'Likes', 'Guardados', 'Compartidos', 'Comentarios']
            
            # Cálculo
            df['WER'] = df.apply(calcular_wer, axis=1)
            
            media = df['WER'].mean()
            std = df['WER'].std()
            
            # Post Actual
            actual_row = {'Alcance': cur_reach, 'Likes': cur_likes, 'Guardados': cur_saves, 
                          'Compartidos': cur_shares, 'Comentarios': cur_comments}
            wer_actual = calcular_wer(actual_row)
            
            z_score = (wer_actual - media) / std if std > 0 else 0

            # --- RESULTADOS ---
            st.divider()
            m1, m2, m3 = st.columns(3)
            m1.metric("WER Actual", f"{wer_actual:.2f}%")
            m2.metric("Promedio Histórico", f"{media:.2f}%")
            m3.metric("Z-Score", f"{z_score:.2f}", delta_color="normal" if z_score > 0 else "inverse")
            
            if z_score >= 2.0:
                st.success(f"🔥 **OUTLIER POSITIVO (Z={z_score:.2f})**: Éxito total.")
            elif z_score <= -1.0:
                st.error(f"📉 **BAJO RENDIMIENTO (Z={z_score:.2f})**: Revisar contenido.")
            else:
                st.info(f"✅ **NORMAL (Z={z_score:.2f})**: Rendimiento estándar.")
                
            with st.expander("Ver datos interpretados"):
                st.dataframe(df)

        except Exception as e:
            st.error(f"Error al leer los datos. Asegúrate de copiar solo números. Detalle: {e}")
