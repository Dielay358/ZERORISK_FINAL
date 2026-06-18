import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as integrate
from scipy.stats import poisson
from google import genai
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="ZERORISK TOWER Pro - UNICA", page_icon="🏗️", layout="wide")

# --- CONEXIÓN FORZADA POR API KEY (Ignora Google Cloud ADC) ---
try:
    # Usamos explícitamente el argumento api_key para evitar conflictos con Google Cloud Console
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("❌ Error de Secrets: Asegúrate de tener 'GEMINI_API_KEY' en el panel de Streamlit.")
    st.stop()

# --- CABECERA ---
st.title("ZERORISK TOWER v11.1")
st.write("**Simulación Profesional: Estática, Cálculo II e Inferencia Bayesiana**")
st.divider()

# --- BARRA LATERAL (INPUTS) ---
st.sidebar.header("🕹️ Centro de Mando")
radio = st.sidebar.slider("Radio de Carga (m)", 2.0, 45.0, 20.0)
cap_max = 8000 if radio <= 16.5 else 8000 * (16.5 / radio)
st.sidebar.info(f"📌 Capacidad Estructural Máxima: {cap_max:.1f} kg")

carga = st.sidebar.number_input("Peso de la Carga (kg)", 0.0, 10000.0, 2000.0)
viento = st.sidebar.slider("Velocidad del Viento (km/h)", 0, 100, 20)
mantenimiento = st.sidebar.slider("Mantenimiento (1-10)", 1, 10, 8)
r_lastre = st.sidebar.slider("Radio Balasto (m)", 0.5, 5.0, 2.5)

# --- MOTOR TÉCNICO (INTEGRALES) ---
vol_lastre, _ = integrate.quad(lambda y: np.pi * r_lastre**2, 0, 3)
masa_contra = vol_lastre * 2400 
mv = (carga * radio) + (2500 * 22.5) + (0.005 * viento**2 * 15 * 50)
me = masa_contra * 12 
fs = me / mv

p_falla_total = ((1 if viento > 50 else 0.2) * 0.6) + ((1 if carga > cap_max else 0.1) * 0.4)
p_bayes = (0.90 * 0.001) / 0.15

# --- DASHBOARD ---
st.subheader("📊 Resultados Técnicos")
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
ax.text(radio, 22, f"CARGA\n{carga}kg", color='red', ha='center', fontweight='bold')
ax.set_xlim(-25, 55); ax.set_ylim(-5, 75); ax.axis('off')
st.pyplot(fig)

# --- IA DIAGNÓSTICO (ESTABILIZADO) ---
if st.button("🧠 GENERAR DIAGNÓSTICO INTEGRAL IA"):
    prompt = f"Como Ingeniero Senior, analiza Grua: FS {fs:.2f}, Riesgo {p_falla_total*100:.1f}%, Bayes {p_bayes*100:.2f}%. Usa términos de Walpole e Hibbeler."
    
    with st.spinner('Estableciendo conexión prioritaria con Google AI Studio...'):
        try:
            # Forzamos modelos que sabemos que funcionan con API Keys normales
            res = client.models.generate_content(model='gemini-1.5-flash', contents=prompt)
            st.success("Análisis completado")
            st.markdown(res.text)
        except Exception as e:
            st.error(f"Fallo en la comunicación: {str(e)}")
            st.info("Sugerencia: Si el error persiste, genera una API Key nueva en AI Studio y actualiza los Secrets.")

st.sidebar.divider()
st.sidebar.caption("© 2026 - Universidad UNICA")