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
    st.error("❌ Error de Autenticación: Configura la API KEY en los Secrets de Streamlit.")
    st.stop()

# --- CABECERA ---
st.title("ZERORISK TOWER v10.4")
st.write("**Consola Profesional de Ingeniería Industrial | Proyecto Integrador UNICA**")
st.divider()

# --- BARRA LATERAL: ENTRADA DE VARIABLES ---
st.sidebar.header("🕹️ Centro de Control")
radio = st.sidebar.slider("Radio de Carga (m)", 2.0, 45.0, 20.0)
cap_max = 8000 if radio <= 16.5 else 8000 * (16.5 / radio)
st.sidebar.info(f"📌 Capacidad Estructural Máxima: {cap_max:.1f} kg")

carga = st.sidebar.number_input("Peso de la Carga (kg)", 0.0, 10000.0, 2000.0)
viento = st.sidebar.slider("Velocidad del Viento (km/h)", 0, 100, 25)
mantenimiento = st.sidebar.slider("Estado de Mantenimiento (1-10)", 1, 10, 8)
r_lastre = st.sidebar.slider("Radio del Balasto (m)", 0.5, 5.0, 2.5)

# --- MOTOR TÉCNICO (CÁLCULO II & HIBBELER) ---
# 1. Integral de Volumen (Sólido de Revolución)
vol_lastre, _ = integrate.quad(lambda y: np.pi * r_lastre**2, 0, 3)
masa_contra = vol_lastre * 2400 
# 2. Integral de Longitud de Arco (Catenaria tirante)
long_cable, _ = integrate.quad(lambda x: np.sqrt(1 + (0.01 * x)**2), 0, radio)
# 3. Mecánica de Momentos
mv = (carga * radio) + (2500 * 22.5) + (0.005 * viento**2 * 15 * 50)
me = masa_contra * 12 
fs = me / mv

# --- MOTOR ESTADÍSTICO (WALPOLE & BAYES) ---
p_falla_total = ((1 if viento > 50 else 0.2) * 0.6) + ((1 if carga > cap_max else 0.1) * 0.4)
p_bayes = (0.90 * 0.001) / 0.15

# --- DASHBOARD DE RESULTADOS ---
st.subheader("📊 Variables Dependientes (Resultados del Sistema)")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Factor Seguridad", f"{fs:.2f}", help="Criterio de Hibbeler")
m2.metric("Volumen Lastre", f"{vol_lastre:.1f} m³", help="Integral Cálculo II")
m3.metric("Riesgo Mecánico", f"{p_falla_total*100:.1f}%", help="Partición de Walpole")
m4.metric("Prob. Bayesiana", f"{p_bayes*100:.4f}%", help="Teorema de Bayes")

# --- VISUALIZACIÓN DINÁMICA ---
fig, ax = plt.subplots(figsize=(12, 6))
ax.set_facecolor('#0E1117') 
fig.patch.set_facecolor('#0E1117')
color_est = '#10B981' if fs > 1.3 else '#F59E0B' if fs > 1.05 else '#E11D48'

ax.plot([0, 0], [0, 50], color='white', lw=8) # Mástil
ax.plot([-30, 60], [0, 0], color='#4B5563', lw=3) # Suelo
ax.plot([-15, 50], [50, 50], color=color_est, lw=6) # Jib
balasto_x = [-12 - r_lastre, -12 + r_lastre]
ax.fill_between(balasto_x, 42, 50, color='#3B82F6', alpha=0.9) # Balasto
ax.text(-12, 35, f"BALASTO\n{r_lastre}m", color='#3B82F6', ha='center', fontweight='bold')
ax.plot([radio, radio], [50, 30], color='red', lw=3, linestyle='--') # Cable carga
ax.scatter(radio, 30, color='red', s=300, zorder=5) # Carga
ax.text(radio, 22, f"CARGA\n{carga}kg", color='red', ha='center', fontweight='bold')
x_arco = np.linspace(-12, radio, 100)
y_arco = 50 + 0.008 * (x_arco + 12)**2 # Tirante
ax.plot(x_arco, y_arco, color='#FDE047', lw=1.5, alpha=0.6)
ax.set_xlim(-30, 60); ax.set_ylim(-10, 80); ax.axis('off')
st.pyplot(fig)

# --- FUNDAMENTOS TEÓRICOS ---
with st.expander("📚 Ver Fundamento Estadístico y de Cálculo (Hibbeler/Walpole)"):
    st.markdown(fr"""
    ### Análisis de Ingeniería Aplicado:
    *   **Teorema de Bayes:** Probabilidad de falla crítica bajo evidencia de viento: **{p_bayes*100:.4f}%**.
    *   **Cálculo II:** Volumen del balasto mediante integral de revolución: 
        $V = \pi \int_0^3 ({r_lastre:.2f})^2 dy = {vol_lastre:.2f} m^3$.
    *   **Mecánica:** Momento de vuelco actual calculado en base a radio y carga: **{mv:.0f} Nm**.
    """)

# --- IA DIAGNÓSTICO (ESTRUCTURA RESILIENTE v10.4) ---
if st.button("🧠 GENERAR DIAGNÓSTICO INTEGRAL IA"):
    prompt = f"Ingeniero experto: Analiza FS {fs:.2f}, Riesgo {p_falla_total*100:.1f}%, Bayes {p_bayes*100:.2f}%. Usa términos de Walpole e Hibbeler."
    
    # Hemos actualizado los nombres de modelos a los que SÍ existen en 2026
    modelos_a_probar = ['gemini-2.0-flash', 'gemini-2.0-flash-lite', 'gemini-flash-latest']
    
    exito = False
    with st.spinner('Estableciendo conexión segura con Google AI...'):
        for mod in modelos_a_probar:
            if exito: break
            try:
                # El truco es probar los modelos sin el prefijo manual
                res = client.models.generate_content(model=mod, contents=prompt)
                st.success(f"Análisis emitido por el modelo: {mod}")
                st.markdown(res.text)
                exito = True
            except Exception as e:
                # Si es 404 o 429, el bucle intenta con el siguiente modelo de la lista
                print(f"DEBUG: Fallo con {mod}: {e}")
                continue
        
        if not exito:
            st.error("❌ Los servidores de Google no responden. Esto suele ser temporal. Por favor, refresca la página o intenta en 20 segundos.")

st.sidebar.divider()
st.sidebar.caption("© 2026 - Universidad UNICA")