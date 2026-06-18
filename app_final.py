import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as integrate
from scipy.stats import poisson
from google import genai
import os
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="ZERORISK TOWER Pro - UNICA", page_icon="🏗️", layout="wide")

# --- CONEXIÓN IA SEGURA (STREAMLIT CLOUD) ---
try:
    api_key_cloud = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key_cloud)
except Exception:
    st.error("❌ Error: Configura la API KEY en los Secrets de Streamlit.")
    st.stop()

# --- CABECERA ---
st.title("ZERORISK TOWER v11.4")
st.write(f"**Fecha de Operación: {st.session_state.get('date', '18/06/2026')}**")
st.write("*Simulación de Ingeniería Avanzada: Estática de Hibbeler e Inferencia de Walpole*")
st.divider()

# --- BARRA LATERAL: VARIABLES INDEPENDIENTES ---
st.sidebar.header("🕹️ Centro de Mando")
radio = st.sidebar.slider("Radio de Carga (m)", 2.0, 45.0, 20.0)
cap_max = 8000 if radio <= 16.5 else 8000 * (16.5 / radio)
st.sidebar.info(f"📌 Capacidad Estructural Máxima: {cap_max:.1f} kg")

carga = st.sidebar.number_input("Peso de la Carga (kg)", 0.0, 12000.0, 2000.0)
viento = st.sidebar.slider("Velocidad del Viento (km/h)", 0, 100, 25)
mantenimiento = st.sidebar.slider("Estado de Mantenimiento (1-10)", 1, 10, 8)
r_lastre = st.sidebar.slider("Radio del Balasto (m)", 0.5, 5.0, 2.5)

# --- MOTOR TÉCNICO (INTEGRALES Y MECÁNICA) ---
vol_lastre, _ = integrate.quad(lambda y: np.pi * r_lastre**2, 0, 3)
masa_contra = vol_lastre * 2400 
long_cable, _ = integrate.quad(lambda x: np.sqrt(1 + (0.01 * x)**2), 0, radio)
mv = (carga * radio) + (2500 * 22.5) + (0.005 * viento**2 * 15 * 50)
me = masa_contra * 12 
fs = me / mv

p_falla_total = ((1 if viento > 50 else 0.2) * 0.6) + ((1 if carga > cap_max else 0.1) * 0.4)
p_bayes = (0.90 * 0.001) / 0.15

# --- DASHBOARD ---
st.subheader("📊 Resultados Técnicos (Variables Dependientes)")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Factor Seguridad", f"{fs:.2f}")
m2.metric("Volumen Lastre", f"{vol_lastre:.1f} m³")
m3.metric("Riesgo Estructural", f"{p_falla_total*100:.1f}%")
m4.metric("Prob. Bayesiana", f"{p_bayes*100:.4f}%")

# --- VISUALIZACIÓN DINÁMICA ---
fig, ax = plt.subplots(figsize=(12, 6))
ax.set_facecolor('#0E1117'); fig.patch.set_facecolor('#0E1117')
color_est = '#10B981' if fs > 1.3 else '#F59E0B' if fs > 1.1 else '#E11D48'

ax.plot([0, 0], [0, 50], color='white', lw=8) 
ax.plot([-30, 60], [0, 0], color='#4B5563', lw=3) 
ax.plot([-12, 45], [50, 50], color=color_est, lw=6) 
balasto_x = [-12 - r_lastre, -12 + r_lastre]
ax.fill_between(balasto_x, 42, 50, color='#3B82F6', alpha=0.9)
ax.text(-12, 35, f"BALASTO\n{r_lastre}m", color='#3B82F6', ha='center', fontweight='bold')
ax.plot([radio, radio], [50, 30], color='red', lw=3, linestyle='--')
ax.scatter(radio, 30, color='red', s=300, zorder=5) 
x_arco = np.linspace(-12, radio, 100)
y_arco = 50 + 0.008 * (x_arco + 12)**2
ax.plot(x_arco, y_arco, color='#FDE047', lw=1.5, alpha=0.6)
ax.set_xlim(-30, 60); ax.set_ylim(-10, 80); ax.axis('off')
st.pyplot(fig)

# --- FUNDAMENTOS ---
with st.expander("📚 Ver Fundamentos Estadísticos y de Cálculo (Hibbeler/Walpole)"):
    st.markdown(fr"""
    *   **Teorema de Bayes:** Probabilidad actualizada de falla: **{p_bayes*100:.4f}%**.
    *   **Cálculo II:** Volumen del balasto mediante integral de revolución: **{vol_lastre:.2f} m³**.
    """)

# --- IA DIAGNÓSTICO: MOTOR DINÁMICO (SOLUCIÓN AL ERROR 404) ---
if st.button("🧠 GENERAR DIAGNÓSTICO INTEGRAL IA"):
    prompt = f"Ingeniero experto: Analiza FS {fs:.2f}, Riesgo {p_falla_total*100:.1f}%, Bayes {p_bayes*100:.2f}%. Usa términos de Walpole e Hibbeler."
    
    with st.spinner('Buscando modelos activos en el servidor de Google (2026)...'):
        try:
            # 1. Obtenemos la lista real de modelos que tu cuenta tiene permitidos hoy
            available_models = list(client.models.list())
            
            # 2. Buscamos el modelo más reciente que soporte generación de contenido
            # Filtramos los que NO son para imágenes o embebidos
            generation_models = [m.name for m in available_models if 'generateContent' in m.supported_methods]
            
            if not generation_models:
                st.error("No se encontraron modelos de generación activos en tu cuenta de Google Cloud.")
            else:
                # 3. Tomamos el primero de la lista (Google suele poner el más moderno arriba)
                # O buscamos uno que diga 'flash' por eficiencia
                final_model = next((m for m in generation_models if 'flash' in m), generation_models[0])
                
                res = client.models.generate_content(model=final_model, contents=prompt)
                st.success(f"Diagnóstico emitido exitosamente por: {final_model}")
                st.markdown(res.text)
                
        except Exception as e:
            st.error(f"Fallo en la comunicación técnica: {str(e)}")
            st.info("Sugerencia: Verifica que tu API KEY en Secrets sea la correcta y que el pago esté activo.")

st.sidebar.divider()
st.sidebar.caption("© 2026 - Universidad UNICA")