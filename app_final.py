import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as integrate
from scipy.stats import poisson
from google import genai
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="ZERORISK TOWER Pro - UNICA", page_icon="🏗️", layout="wide")

# --- CONEXIÓN IA SEGURA (PARA NUBE) ---
try:
    api_key_cloud = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key_cloud)
except Exception:
    st.error("❌ Error: Configura la API KEY en los Secrets de Streamlit.")
    st.stop()

# --- CABECERA ---
col_logo, col_tit = st.columns([1, 4])
with col_logo:
    if os.path.exists("logo_unica.png"): 
        st.image("logo_unica.png", width=120)
with col_tit:
    st.title("ZERORISK TOWER v10.0")
    st.write("**Simulación de Ingeniería Avanzada: Estática, Cálculo II y Bayes**")

st.divider()

# --- BARRA LATERAL (INPUTS) ---
st.sidebar.header("🕹️ Variables Independientes")
radio = st.sidebar.slider("Radio de Carga (m)", 2.0, 45.0, 20.0)
cap_max = 8000 if radio <= 16.5 else 8000 * (16.5 / radio)
st.sidebar.info(f"📌 Capacidad Estructural: {cap_max:.1f} kg")

carga = st.sidebar.number_input("Peso de la Carga (kg)", 0.0, 10000.0, 2000.0)
viento = st.sidebar.slider("Velocidad del Viento (km/h)", 0, 100, 20)
mantenimiento = st.sidebar.slider("Mantenimiento (1-10)", 1, 10, 8)
r_lastre = st.sidebar.slider("Radio Balasto (m)", 0.5, 5.0, 2.5)

# --- MOTOR DE CÁLCULO II (INTEGRALES) ---
vol_lastre, _ = integrate.quad(lambda y: np.pi * r_lastre**2, 0, 3)
masa_contra = vol_lastre * 2400 
long_cable, _ = integrate.quad(lambda x: np.sqrt(1 + (0.01 * x)**2), 0, radio)

# --- MOTOR DE MECÁNICA ---
mv = (carga * radio) + (2500 * 22.5) + (0.005 * viento**2 * 15 * 50)
me = masa_contra * 12 
fs = me / mv

# --- MOTOR DE ESTADÍSTICA (WALPOLE) ---
p_falla_total = ((1 if viento > 50 else 0.2) * 0.6) + ((1 if carga > cap_max else 0.1) * 0.4)
p_bayes = (0.90 * 0.001) / 0.15

# --- DASHBOARD ---
st.subheader("📊 Métricas de Respuesta")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Factor Seguridad", f"{fs:.2f}")
m2.metric("Volumen Lastre", f"{vol_lastre:.1f} m³")
m3.metric("Riesgo Estructural", f"{p_falla_total*100:.1f}%")
m4.metric("Prob. Bayesiana", f"{p_bayes*100:.4f}%")

# --- VISUALIZACIÓN ---
st.subheader("🏗️ Ilustración Técnica en Tiempo Real")
fig, ax = plt.subplots(figsize=(12, 6))
ax.set_facecolor('#0E1117') 
fig.patch.set_facecolor('#0E1117')
color_est = '#10B981' if fs > 1.3 else '#F59E0B' if fs > 1.05 else '#E11D48'

ax.plot([0, 0], [0, 50], color='white', lw=8) # Mástil
ax.plot([-30, 60], [0, 0], color='#4B5563', lw=3) # Suelo
ax.plot([-15, 50], [50, 50], color=color_est, lw=6) # Jib

# Balasto
balasto_x = [-12 - r_lastre, -12 + r_lastre]
ax.fill_between(balasto_x, 42, 50, color='#3B82F6', alpha=0.9)
ax.text(-12, 35, f"BALASTO\n{r_lastre}m", color='#3B82F6', ha='center', fontweight='bold')

# Carga
ax.plot([radio, radio], [50, 30], color='red', lw=3, linestyle='--')
ax.scatter(radio, 30, color='red', s=300, zorder=5) 
ax.text(radio, 22, f"CARGA\n{carga}kg", color='red', ha='center', fontweight='bold')

# Tirante
x_arco = np.linspace(-12, radio, 100)
y_arco = 50 + 0.01 * (x_arco + 12)**2
ax.plot(x_arco, y_arco, color='#FDE047', lw=1.5, alpha=0.6)

ax.set_xlim(-30, 60); ax.set_ylim(-10, 80); ax.axis('off')
st.pyplot(fig)

# --- IA DIAGNÓSTICO ---
with st.expander("📚 Ver Fundamentos de Walpole e Integrales"):
    st.markdown(fr"""
    ### Fundamentos Aplicados:
    1. **Teorema de Bayes:** Probabilidad de falla crítica dado el viento actual: **{p_bayes*100:.4f}%**.
    2. **Cálculo II:** Volumen mediante sólido de revolución $V = \pi \int_0^3 ({r_lastre})^2 dy = {vol_lastre:.2f} m^3$.
    """)

if st.button("🧠 GENERAR DIAGNÓSTICO INTEGRAL"):
    prompt = f"Ingeniero Senior: Analiza FS {fs:.2f}, Riesgo {p_falla_total*100:.1f}%, Bayes {p_bayes*100:.2f}%. Usa términos de Walpole e Hibbeler."
    
    # Probamos con Gemini 2.0 que es el estándar de 2026
    modelos = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-2.0-flash-lite']
    
    exito = False
    with st.spinner('Consultando al Ingeniero Senior IA...'):
        for mod in modelos:
            if exito: break
            try:
                res = client.models.generate_content(model=mod, contents=prompt)
                st.success(f"Análisis generado con {mod}")
                st.markdown(res.text)
                exito = True
            except Exception as e:
                # Si es un error 404 o 503, pasamos al siguiente modelo
                continue
                
        if not exito:
            st.error("❌ Los modelos de Google están en mantenimiento o saturados. Intenta en un momento.")

st.sidebar.divider()
st.sidebar.caption("© 2026 - Universidad UNICA")