import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as integrate
from scipy.stats import poisson
import pandas as pd
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="ZERORISK TOWER Pro - UNICA", page_icon="🏗️", layout="wide")
LLAVE_MAESTRA = "AQ.Ab8RN6Iw_5HmYf8ygdEX_Ve4IHufxzZRZAz6fQjsqGxXt_PwXQ"
client = genai.Client(api_key=LLAVE_MAESTRA) if 'genai' in globals() else None

# --- CABECERA ---
col_logo, col_tit = st.columns([1, 4])
with col_logo:
    if os.path.exists("logo_unica.png"): st.image("logo_unica.png", width=120)
with col_tit:
    st.title("ZERORISK TOWER v12.2")
    st.write("**Consola de Monitoreo con Telemetría Visual en Tiempo Real**")

st.divider()

# --- BARRA LATERAL ---
st.sidebar.header("🕹️ Variables Independientes")
radio = st.sidebar.slider("Radio de Carga (m)", 2.0, 45.0, 31.13)
carga = st.sidebar.number_input("Peso de la Carga (kg)", 0.0, 10000.0, 3000.0)
viento = st.sidebar.slider("Velocidad Viento (km/h)", 0, 100, 58)
mantenimiento = st.sidebar.slider("Nivel Mantenimiento (1-10)", 1, 10, 8)
r_lastre = st.sidebar.slider("Radio Balasto (m)", 0.5, 5.0, 3.77)

# --- MOTOR TÉCNICO ---
vol_lastre, _ = integrate.quad(lambda y: np.pi * r_lastre**2, 0, 3)
masa_contra = vol_lastre * 2400 
mv = (carga * radio) + (2500 * 22.5) + (0.005 * viento**2 * 15 * 50)
me = masa_contra * 12 
fs = me / mv

# --- MOTOR ESTADÍSTICO ---
p_b1, p_b2 = 0.85, 0.15 
p_f_dado_b1 = (1 - mantenimiento/10) * 0.05 
p_f_dado_b2 = 0.65 if viento > 50 else 0.20 
p_falla_total = (p_f_dado_b1 * p_b1) + (p_f_dado_b2 * p_b2) 
p_bayes = (p_f_dado_b2 * p_b2) / p_falla_total 

# --- DASHBOARD ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Factor Seguridad", f"{fs:.2f}")
m2.metric("Volumen Lastre", f"{vol_lastre:.1f} m³")
m3.metric("Riesgo Estructural", f"{p_falla_total*100:.1f}%")
m4.metric("Prob. Bayesiana", f"{p_bayes*100:.3f}%")

# --- VISUALIZACIÓN DINÁMICA CON ETIQUETAS (TELEMÉTRICA) ---
st.subheader("🏗️ Diagrama de Cuerpo Libre con Telemetría")

fig, ax = plt.subplots(figsize=(12, 6))
ax.set_facecolor('#0E1117')
fig.patch.set_facecolor('#0E1117')

# Color de alerta
color_est = '#10B981' if fs > 1.4 else '#F59E0B' if fs > 1.1 else '#E11D48'

# 1. Dibujar Estructura Base
ax.plot([0, 0], [0, 50], color='white', lw=6) # Mástil
ax.plot([-30, 60], [0, 0], color='#334155', lw=2) # Suelo
ax.plot([-15, 45], [50, 50], color=color_est, lw=5) # Pluma

# 2. ETIQUETA DE VIENTO (Dinámica arriba)
ax.text(45, 60, f"🌪️ Viento: {viento} km/h", color='white', fontsize=12, fontweight='bold', ha='right')

# 3. BALASTO DINÁMICO CON ETIQUETA
balasto_x = [-12 - r_lastre, -12 + r_lastre]
ax.fill_between(balasto_x, 43, 50, color='#3B82F6', alpha=0.9)
# Etiqueta que cambia con el radio del balasto
ax.text(-12, 35, f"BALASTO\nRadio: {r_lastre:.2f}m\nMasa: {masa_contra:.0f}kg", 
        color='#3B82F6', ha='center', fontweight='bold', fontsize=10)

# 4. CARGA DINÁMICA CON ETIQUETA
ax.plot([radio, radio], [50, 35], color='red', lw=2, linestyle='--')
ax.scatter(radio, 35, color='red', s=300, zorder=5) 
# Etiqueta que persigue a la bola roja
ax.text(radio, 25, f"CARGA: {carga:.0f}kg\nDistancia: {radio:.2f}m", 
        color='red', ha='center', fontweight='bold', fontsize=10)

# 5. INDICADOR DE FACTOR DE SEGURIDAD EN EL DIBUJO
ax.text(0, 55, f"ESTADO: {'SEGURO' if fs > 1.1 else 'PELIGRO'}\nFS: {fs:.2f}", 
        color=color_est, fontsize=14, fontweight='bold', ha='center')

ax.set_xlim(-25, 55); ax.set_ylim(-5, 75); ax.axis('off')
st.pyplot(fig)

# --- SECCIÓN DE FUNDAMENTOS ---
with st.expander("📚 Ver Fundamentos Científicos y Librerías"):
    st.markdown("### 🛠️ Arquitectura de Software y Librerías")
    df_lib = pd.DataFrame({
        "Librería": ["SciPy", "NumPy", "Matplotlib", "Streamlit", "Python Lists"],
        "Propósito": ["Probabilidades e Integrales", "Motor Matemático", "Visualización DCL", "Interfaz Web", "Organización de datos"],
        "Aplicación": ["Bayes/Volumen", "Momentos", "Gráfico 2D", "Sliders/Botones", "Variables Independientes"]
    })
    st.table(df_lib)

    st.markdown(fr"""
    ### 🔬 Desglose Teórico:
    *   **Teorema de Bayes:** $P(Viento|Falla) = \frac{{{p_f_dado_b2:.2f} \cdot {p_b2}}}{{{p_falla_total:.4f}}} = {p_bayes*100:.2f}\%$.
    *   **Cálculo II (Sólido):** $V = \pi \int_0^3 ({r_lastre:.2f})^2 dy = {vol_lastre:.2f} m^3$.
    """)

# --- FUNCIÓN DE DIAGNÓSTICO ---
def generar_diagnostico_detallado():
    st.markdown("# 📋 INFORME TÉCNICO DE AUDITORÍA")
    st.header("1. Análisis de Ingeniería (Hibbeler)")
    st.write(f"El Momento Volcante es de **{mv:.0f} Nm**, compensado por un Momento Estabilizador de **{me:.0f} Nm**. Esto resulta en un Factor de Seguridad de **{fs:.2f}**.")
    
    st.header("2. Aplicación de Estadística (Walpole)")
    st.markdown(f"Bajo el Teorema de Bayes, la probabilidad de que el viento sea la causa de un fallo es del **{p_bayes*100:.2f}%**. El riesgo total particionado es de **{p_falla_total*100:.2f}%**.")

if st.button("🏗️ GENERAR DIAGNÓSTICO MAGISTRAL"):
    generar_diagnostico_detallado()

st.sidebar.divider()
st.sidebar.caption("© 2026 - Universidad UNICA | Ingeniería Industrial")