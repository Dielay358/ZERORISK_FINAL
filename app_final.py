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

# --- CONEXIÓN IA SEGURA ---
try:
    api_key_cloud = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key_cloud)
except Exception:
    st.error("❌ Error: Configura la API KEY en los Secrets de Streamlit.")
    st.stop()

# --- CABECERA ---
st.title("ZERORISK TOWER v10.3")
st.write("**Consola de Ingeniería Avanzada | Análisis de Riesgos y Estática**")
st.divider()

# --- BARRA LATERAL (INPUTS) ---
st.sidebar.header("🕹️ Centro de Mando")
radio = st.sidebar.slider("Radio de Carga (m)", 2.0, 45.0, 20.0)
cap_max = 8000 if radio <= 16.5 else 8000 * (16.5 / radio)
st.sidebar.info(f"📌 Capacidad Máxima Estructural: {cap_max:.1f} kg")

carga = st.sidebar.number_input("Peso de la Carga (kg)", 0.0, 12000.0, 2000.0)
viento = st.sidebar.slider("Velocidad del Viento (km/h)", 0, 100, 20)
mantenimiento = st.sidebar.slider("Estado de Mantenimiento (1-10)", 1, 10, 8)
r_lastre = st.sidebar.slider("Radio del Balasto (m)", 0.5, 5.0, 2.5)

# --- MOTOR TÉCNICO ---
vol_lastre, _ = integrate.quad(lambda y: np.pi * r_lastre**2, 0, 3)
masa_contra = vol_lastre * 2400 
long_cable, _ = integrate.quad(lambda x: np.sqrt(1 + (0.01 * x)**2), 0, radio)
mv = (carga * radio) + (2500 * 22.5) + (0.005 * viento**2 * 15 * 50)
me = masa_contra * 12 
fs = me / mv

p_falla_total = ((1 if viento > 50 else 0.2) * 0.6) + ((1 if carga > cap_max else 0.1) * 0.4)
p_bayes = (0.90 * 0.001) / 0.15

# --- DASHBOARD ---
st.subheader("📊 Variables Dependientes (Resultados)")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Factor Seguridad", f"{fs:.2f}", help="Criterio de Hibbeler")
m2.metric("Volumen Balasto", f"{vol_lastre:.1f} m³", help="Integral de Revolución")
m3.metric("Riesgo Estructural", f"{p_falla_total*100:.1f}%", help="Teorema Partición")
m4.metric("Prob. Bayesiana", f"{p_bayes*100:.4f}%", help="Walpole Inference")

# --- VISUALIZACIÓN ---
fig, ax = plt.subplots(figsize=(12, 6))
ax.set_facecolor('#0E1117') 
fig.patch.set_facecolor('#0E1117')
color_est = '#10B981' if fs > 1.3 else '#F59E0B' if fs > 1.05 else '#E11D48'

# Dibujo estructural
ax.plot([0, 0], [0, 50], color='white', lw=8) # Mástil
ax.plot([-30, 60], [0, 0], color='#4B5563', lw=3) # Suelo
ax.plot([-15, 50], [50, 50], color=color_est, lw=6) # Jib

# Balasto Dinámico
balasto_x = [-12 - r_lastre, -12 + r_lastre]
ax.fill_between(balasto_x, 42, 50, color='#3B82F6', alpha=0.9)
ax.text(-12, 35, f"BALASTO\n{r_lastre}m", color='#3B82F6', ha='center', fontweight='bold')

# Carga
ax.plot([radio, radio], [50, 30], color='red', lw=3, linestyle='--')
ax.scatter(radio, 30, color='red', s=300, zorder=5) 
ax.text(radio, 22, f"CARGA\n{carga}kg", color='red', ha='center', fontweight='bold')

# Cable Tirante (Cálculo II)
x_arco = np.linspace(-12, radio, 100)
y_arco = 50 + 0.008 * (x_arco + 12)**2
ax.plot(x_arco, y_arco, color='#FDE047', lw=1.5, alpha=0.6)

ax.set_xlim(-30, 60); ax.set_ylim(-10, 80); ax.axis('off')
st.pyplot(fig)

# --- FUNDAMENTOS ---
with st.expander("📚 Ver Fundamentos Estadísticos y de Cálculo"):
    st.markdown(fr"""
    **Teorema de Bayes:** $P(Viento|Falla) = \frac{{P(Falla|Viento)P(Viento)}}{{P(Falla)}}$ = **{p_bayes*100:.4f}%**.
    **Cálculo II:** Volumen $V = \pi \int_0^3 ({r_lastre})^2 dy = {vol_lastre:.2f} m^3$.
    """)

# --- BOTÓN CON PROTOCOLO DE REINTENTO (SOLUCIÓN AL ERROR) ---
if st.button("🧠 GENERAR DIAGNÓSTICO INTEGRAL IA"):
    prompt = f"Ingeniero Senior: Analiza FS {fs:.2f}, Riesgo {p_falla_total*100:.1f}%, Bayes {p_bayes*100:.2f}%. Usa términos de Walpole e Hibbeler."
    
    modelos = ['gemini-1.5-flash', 'gemini-2.0-flash-lite']
    exito = False
    
    with st.spinner('Estableciendo conexión con el servidor de Google...'):
        for mod in modelos:
            if exito: break
            for intento in range(3): # Reintenta 3 veces por cada modelo
                try:
                    res = client.models.generate_content(model=mod, contents=prompt)
                    st.success(f"Diagnóstico generado exitosamente.")
                    st.markdown(res.text)
                    exito = True
                    break
                except Exception as e:
                    if "429" in str(e) or "503" in str(e):
                        time.sleep(3) # Espera 3 segundos si está saturado
                        continue
                    else:
                        st.error(f"Error técnico con {mod}: {str(e)[:50]}")
                        break
        
        if not exito:
            st.error("❌ Los servidores gratuitos de Google están bajo mantenimiento intenso. Por favor, intenta presionar el botón de nuevo en 30 segundos.")

st.sidebar.divider()
st.sidebar.caption("© 2026 - Universidad UNICA")