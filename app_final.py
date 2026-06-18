import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as integrate
from scipy.stats import poisson
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="ZERORISK TOWER Pro - UNICA", page_icon="🏗️", layout="wide")

# --- CABECERA ---
col_logo, col_tit = st.columns([1, 4])
with col_logo:
    if os.path.exists("logo_unica.png"): 
        st.image("logo_unica.png", width=120)
with col_tit:
    st.title("ZERORISK TOWER v11.9")
    st.write("**Sistema de Ingeniería: Integración Dinámica de Variables y Fórmulas**")

st.divider()

# --- BARRA LATERAL: VARIABLES INDEPENDIENTES ---
st.sidebar.header("🕹️ Centro de Control Local")
radio = st.sidebar.slider("Radio de Carga (m)", 2.0, 45.0, 29.57)
cap_max = 8000 if radio <= 16.5 else 8000 * (16.5 / radio)
st.sidebar.info(f"📌 Capacidad Estructural Máxima: {cap_max:.1f} kg")

carga = st.sidebar.number_input("Peso de la Carga (kg)", 0.0, 10000.0, 3000.0)
viento = st.sidebar.slider("Velocidad del Viento (km/h)", 0, 100, 58)
mantenimiento = st.sidebar.slider("Nivel de Mantenimiento (1-10)", 1, 10, 8)
r_lastre = st.sidebar.slider("Radio Balasto (m)", 0.5, 5.0, 3.77)

# --- MOTOR TÉCNICO (CÁLCULO II Y MECÁNICA) ---
vol_lastre, _ = integrate.quad(lambda y: np.pi * r_lastre**2, 0, 3)
masa_contra = vol_lastre * 2400 
mv = (carga * radio) + (2500 * 22.5) + (0.005 * viento**2 * 15 * 50)
me = masa_contra * 12 
fs = me / mv

# --- MOTOR ESTADÍSTICO (WALPOLE & BAYES) ---
p_b1, p_b2 = 0.85, 0.15 
p_f_dado_b1 = (1 - mantenimiento/10) * 0.05
p_f_dado_b2 = 0.55 if viento > 50 else 0.15
p_falla_total = (p_f_dado_b1 * p_b1) + (p_f_dado_b2 * p_b2)
p_bayes = (p_f_dado_b2 * p_b2) / p_falla_total if p_falla_total > 0 else 0

# --- DASHBOARD DE RESULTADOS ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Factor Seguridad", f"{fs:.2f}")
m2.metric("Volumen Lastre", f"{vol_lastre:.1f} m³")
m3.metric("Riesgo Estructural", f"{p_falla_total*100:.1f}%")
m4.metric("Prob. Bayesiana", f"{p_bayes*100:.3f}%")

# --- VISUALIZACIÓN DINÁMICA CON ETIQUETAS ---
st.subheader("🏗️ Ilustración Técnica Reactiva")

fig, ax = plt.subplots(figsize=(12, 6))
ax.set_facecolor('#0E1117')
fig.patch.set_facecolor('#0E1117')

# Color dinámico de seguridad
color_est = '#10B981' if fs > 1.4 else '#F59E0B' if fs > 1.1 else '#E11D48'

# Dibujo estructural
ax.plot([0, 0], [0, 50], color='white', lw=8) # Mástil
ax.plot([-30, 60], [0, 0], color='#4B5563', lw=3) # Suelo
ax.plot([-15, 50], [50, 50], color=color_est, lw=6) # Pluma

# Balasto Dinámico (Cambia ancho según r_lastre)
balasto_x = [-12 - r_lastre, -12 + r_lastre]
ax.fill_between(balasto_x, 42, 50, color='#3B82F6', alpha=0.9)
ax.text(-12, 35, f"BALASTO\n{r_lastre:.2f}m", color='#3B82F6', ha='center', fontweight='bold')

# Carga Dinámica (Cambia posición según radio)
ax.plot([radio, radio], [50, 30], color='red', lw=3, linestyle='--')
ax.scatter(radio, 30, color='red', s=400, zorder=5) 
ax.text(radio, 22, f"CARGA\n{carga:.0f}kg\nDist: {radio:.2f}m", color='red', ha='center', fontweight='bold')

# Límites de cámara fijos para estabilidad visual
ax.set_xlim(-25, 55); ax.set_ylim(-5, 75); ax.axis('off')
st.pyplot(fig)

# --- FUNCIÓN DE DIAGNÓSTICO CON FÓRMULAS DINÁMICAS ---
def generar_diagnostico_profesional():
    st.markdown("## 📋 DIAGNÓSTICO CLÍNICO DE INTEGRIDAD")
    
    # 1. Estado de Seguridad
    if fs < 1.0:
        st.error(f"🔴 **ESTADO CRÍTICO:** El Factor de Seguridad ({fs:.2f}) es inferior a la unidad. Colapso estructural inminente.")
    elif fs < 1.5:
        st.warning(f"🟡 **ALERTA PREVENTIVA:** FS de {fs:.2f} es marginal. Se recomienda reducir el radio o aumentar el contrapeso.")
    else:
        st.success(f"🟢 **ESTADO OPERATIVO:** Sistema estable bajo normas Hibbeler con un FS de {fs:.2f}.")

    # 2. Fundamentos Aplicados (Lo que pediste: Fórmulas con variables reales)
    st.markdown("### 📚 Fundamentos de Walpole e Integrales (Cálculo II)")
    
    # Aquí insertamos los valores de los sliders dentro de las fórmulas LaTeX
    st.markdown(fr"""
    *   **Teorema de Bayes:** 
        $$P(Viento | Falla) = \frac{{P(Falla | Viento) \cdot P(Viento)}}{{P(Falla)}} = \frac{{{p_f_dado_b2:.2f} \cdot {p_b2:.2f}}}{{{p_falla_total:.4f}}} = {p_bayes*100:.4f}\%$$
    *   **Cálculo II (Sólido de Revolución):** 
        $$V = \pi \int_0^3 ({r_lastre:.2f})^2 dy = {vol_lastre:.2f} m^3$$
    *   **Mecánica (Momento de Hibbeler):** 
        Sumatoria de momentos respecto al eje: $\sum M = 0 \rightarrow$ Momento Volcante: **{mv:.0f} Nm** vs Momento Estabilizador: **{me:.0f} Nm**.
    """)

    # 3. Plan de Acción
    st.info(f"### 🛠️ PLAN DE ACCIÓN\n- **Viento:** Con {viento} km/h, se debe monitorear ráfagas.\n- **Carga:** Opera al {(carga/cap_max*100):.1f}% de la capacidad del radio actual.")

# --- BOTÓN DE EJECUCIÓN ---
if st.button("🏗️ GENERAR INFORME TÉCNICO"):
    generar_diagnostico_profesional()

with st.expander("📖 Glosario de Términos"):
    st.write("Cuerpo Rígido, Momento Volcante, Probabilidad Condicional, Catenaria.")

st.sidebar.divider()
st.sidebar.caption("© 2026 - Universidad UNICA")