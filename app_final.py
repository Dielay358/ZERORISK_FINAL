import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as integrate
from scipy.stats import poisson
import pandas as pd
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="ZERORISK TOWER Pro - UNICA", page_icon="🏗️", layout="wide")

# --- CABECERA ---
col_logo, col_tit = st.columns([1, 4])
with col_logo:
    if os.path.exists("logo_unica.png"): st.image("logo_unica.png", width=120)
with col_tit:
    st.title("ZERORISK TOWER v13.0")
    st.write("**Simulación de Integridad: Centroide (Cálculo II), Estática (Hibbeler) y Riesgo (Walpole)**")

st.divider()

# --- BARRA LATERAL: VARIABLES INDEPENDIENTES (INPUTS REALES) ---
st.sidebar.header("🕹️ Centro de Control Local")
radio_carro = st.sidebar.slider("Radio de Carga (m)", 2.0, 45.0, 30.0)
carga = st.sidebar.number_input("Peso de la Carga (kg)", 0.0, 10000.0, 3000.0)
viento = st.sidebar.slider("Velocidad Viento (km/h)", 0, 100, 45)
mantenimiento = st.sidebar.slider("Nivel de Mantenimiento (1-10)", 1, 10, 8)

st.sidebar.subheader("🧱 Configuración de Bloques (Lastre)")
num_bloques = st.sidebar.number_input("Número de Bloques de Concreto", 1, 15, 6)
# Dimensiones reales de un bloque estándar: 2m x 1m x 0.5m
vol_bloque = 2 * 1 * 0.5 
masa_total_contra = num_bloques * (vol_bloque * 2400) # 2400kg/m3 densidad concreto

# --- MOTOR DE CÁLCULO II: CENTROIDE Y CENTRO DE MASA ---
# El objetivo según la rúbrica es fundamentar la suma de elementos diferenciales.
# Modelamos la pluma (45m) como una viga cuya densidad lineal rho(x) aumenta cerca de la torre.
def densidad_pluma(x):
    return 50 + 2 * x  # kg/m (Más reforzada en la base x=0)

# Integral para Masa de la Pluma (M = integral rho(x) dx)
masa_pluma, _ = integrate.quad(densidad_pluma, 0, 45)

# Integral para Centroide de la Pluma (Xcm = 1/M * integral x * rho(x) dx)
momento_pluma, _ = integrate.quad(lambda x: x * densidad_pluma(x), 0, 45)
centroide_pluma = momento_pluma / masa_pluma

# --- MOTOR DE MECÁNICA (HIBBELER) ---
# Sumatoria de Momentos respecto al eje central
m_volcante = (carga * radio_carro) + (masa_pluma * centroide_pluma) + (0.005 * viento**2 * 15 * 50)
m_estabilizador = masa_total_contra * 12 # Contrapeso a 12m fijos
fs = m_estabilizador / m_volcante

# --- MOTOR ESTADÍSTICO (WALPOLE) ---
p_b1, p_b2 = 0.85, 0.15 
p_f_dado_b1 = (1 - mantenimiento/10) * 0.05
p_f_dado_b2 = 0.60 if viento > 55 else 0.20
p_falla_total = (p_f_dado_b1 * p_b1) + (p_f_dado_b2 * p_b2)
p_bayes = (p_f_dado_b2 * p_b2) / p_falla_total if p_falla_total > 0 else 0

# --- DASHBOARD ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Factor Seguridad", f"{fs:.2f}", delta="Criterio Hibbeler")
m2.metric("Centroide Pluma", f"{centroide_pluma:.2f} m", delta="Cálculo II")
m3.metric("Masa Contrapeso", f"{masa_total_contra:.0f} kg", delta="Modular")
m4.metric("Prob. Bayesiana", f"{p_bayes*100:.2f}%", delta="Walpole")

# --- VISUALIZACIÓN TÉCNICA ---
fig, ax = plt.subplots(figsize=(10, 4))
ax.set_facecolor('#0E1117'); fig.patch.set_facecolor('#0E1117')
color_est = '#10B981' if fs > 1.4 else '#F59E0B' if fs > 1.1 else '#E11D48'

ax.plot([0, 0], [0, 50], color='white', lw=6) # Mástil
ax.plot([-15, 45], [50, 50], color=color_est, lw=5) # Pluma

# Dibujar Bloques de Contrapeso Reales (Rectangulares)
for i in range(int(num_bloques)):
    y_pos = 50 - (i * 2) # Apilados hacia abajo
    ax.add_patch(plt.Rectangle((-13, y_pos), 2, 1.5, color='#3B82F6', alpha=0.7))

# Dibujar Carga y Marcador de Centroide
ax.scatter(radio_carro, 45, color='red', s=200)
ax.plot([radio_carro, radio_carro], [50, 45], color='red', lw=2)
ax.scatter(centroide_pluma, 50, color='yellow', s=100, label='Centroide') # Centro de masa de la pluma

ax.set_xlim(-25, 55); ax.set_ylim(-5, 70); ax.axis('off')
st.pyplot(fig)

# --- PANEL DE FUNDAMENTOS (SEGÚN INSTRUMENTO CÁLCULO II) ---
with st.expander("📚 Fundamentación Científica (Criterios de Evaluación)"):
    st.markdown(fr"""
    ### 1. Procedimiento del Centro de Masa (Cálculo II)
    Para determinar el centroide de la pluma, no la tratamos como un objeto puntual, sino como una **distribución continua de masa**.
    Aplicamos la definición integral:
    $$\bar{{x}} = \frac{{\int_0^L x \cdot \rho(x) dx}}{{\int_0^L \rho(x) dx}} = \frac{{{momento_pluma:.2f}}}{{{masa_pluma:.2f}}} = {centroide_pluma:.2f} m$$
    Donde $\rho(x)$ representa la densidad diferencial de la celosía de acero.

    ### 2. Influencia del Centro de Masa en la Estabilidad
    El centroide calculado es el punto donde se concentra el vector de peso de la estructura. Según **Hibbeler**, este punto actúa como el pivote del Momento Estático. Si el centroide se desplaza por deformación o mala distribución, el Factor de Seguridad cae drásticamente.

    ### 3. Geometría y Distribución
    El uso de **bloques rectangulares modulares** permite una distribución de masa uniforme y predecible, facilitando el transporte y asegurando que el centro de gravedad del contrapeso sea constante y no ruede.

    ### 4. Fundamentación Conceptual de la Integral
    La integral nos permite modelar la grúa como una **suma infinita de elementos diferenciales**. Cada centímetro de la pluma tiene un peso; la integral suma todos esos pesos individuales para darnos una propiedad macroscópica: la **Masa Total** y su **Ubicación Exacta**.
    """)

# --- DIAGNÓSTICO MAESTRO ---
if st.button("🏗️ GENERAR DIAGNÓSTICO MAGISTRAL"):
    st.markdown("## 📋 INFORME DE AUDITORÍA TÉCNICA")
    st.write(f"**Análisis de Estática:** El centro de masa de la pluma está a **{centroide_pluma:.2f}m** de la torre. El Momento Volcante total es de **{m_volcante:.0f} Nm**.")
    st.write(f"**Análisis de Riesgo:** Según el Teorema de Bayes, hay una probabilidad del **{p_bayes*100:.2f}%** de colapso por ráfagas de viento de {viento}km/h.")

st.sidebar.divider()
st.sidebar.caption("© 2026 - Proyecto Integrador UNICA")