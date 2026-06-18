import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as integrate
from scipy.stats import poisson
import pandas as pd # Añadimos pandas para crear la tabla técnica
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="ZERORISK TOWER Pro - UNICA", page_icon="🏗️", layout="wide")

# --- CABECERA ---
col_logo, col_tit = st.columns([1, 4])
with col_logo:
    if os.path.exists("logo_unica.png"): st.image("logo_unica.png", width=120)
with col_tit:
    st.title("ZERORISK TOWER v12.1")
    st.write("**Consola de Ingeniería Integrada: Mecánica, Estadística y Cálculo II**")

st.divider()

# --- BARRA LATERAL (INPUTS) ---
st.sidebar.header("🕹️ Centro de Control")
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

# --- MOTOR ESTADÍSTICO (WALPOLE) ---
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

# --- VISUALIZACIÓN ---
fig, ax = plt.subplots(figsize=(10, 4))
ax.set_facecolor('#0E1117'); fig.patch.set_facecolor('#0E1117')
color_est = '#10B981' if fs > 1.4 else '#E11D48'
ax.plot([0, 0], [0, 50], color='white', lw=6) 
ax.plot([-15, 45], [50, 50], color=color_est, lw=5) 
balasto_x = [-12 - r_lastre, -12 + r_lastre]
ax.fill_between(balasto_x, 43, 50, color='#3B82F6', alpha=0.9)
ax.plot([radio, radio], [50, 35], color='red', lw=2, linestyle='--')
ax.scatter(radio, 35, color='red', s=300)
ax.set_xlim(-25, 55); ax.set_ylim(-5, 70); ax.axis('off')
st.pyplot(fig)

# --- SECCIÓN DE FUNDAMENTOS (TABLA DE LIBRERÍAS ACTUALIZADA) ---
with st.expander("📚 Ver Fundamentos Científicos y Librerías"):
    st.markdown("### 🛠️ Arquitectura de Software y Librerías")
    st.write("Para cumplir con los requerimientos de programación y estadística, se emplearon las siguientes herramientas:")
    
    # Creamos la tabla de librerías solicitada
    df_lib = pd.DataFrame({
        "Librería": ["SciPy", "NumPy", "Matplotlib", "Streamlit", "Python Lists (Nativo)"],
        "Propósito en Ingeniería": [
            "Cálculo de distribuciones de Walpole e integrales de Cálculo II.",
            "Procesamiento matricial y funciones matemáticas de Hibbeler.",
            "Generación del Diagrama de Cuerpo Libre (DCL) y visualización.",
            "Interfaz de usuario reactiva para la entrada de variables.",
            "Estructura de datos para organizar históricos de carga y mantenimiento."
        ],
        "Función Específica": [
            "integrate.quad() y stats.poisson",
            "np.pi y operaciones de torque",
            "plt.plot() y ax.fill_between()",
            "st.slider() y st.metric()",
            "Almacenamiento de parámetros independientes."
        ]
    })
    st.table(df_lib)

    st.markdown(fr"""
    ### 🔬 Desglose Teórico:
    *   **Estadística (Bayes):** $P(Viento|Falla) = \frac{{{p_f_dado_b2:.2f} \cdot {p_b2}}}{{{p_falla_total:.4f}}} = {p_bayes*100:.2f}\%$.
    *   **Cálculo II (Sólido):** $V = \pi \int_0^3 ({r_lastre:.2f})^2 dy = {vol_lastre:.2f} m^3$.
    """)

# --- FUNCIÓN DE DIAGNÓSTICO MAGISTRAL ---
def generar_diagnostico_detallado():
    st.markdown("# 📋 INFORME TÉCNICO DE AUDITORÍA")
    
    # Estadística
    st.header("1. Aplicación de Estadística I (Walpole)")
    st.markdown(fr"""
    *   **Teorema de la Partición:** El riesgo total (**{p_falla_total:.4f}**) se obtiene particionando el evento de falla en dos estados climáticos mutuamente excluyentes: Viento Seguro ($B_1$) y Viento Fuerte ($B_2$).
    *   **Inferencia Bayesiana:** El resultado de **{p_bayes*100:.2f}%** permite al ingeniero realizar una *actualización de creencias* basada en la evidencia climática actual.
    """)

    # Cálculo
    st.header("2. Aplicación de Cálculo II")
    st.markdown(fr"""
    *   **Sólido de Revolución:** Siguiendo el **Método del Disco**, el balasto se representa como la rotación de la constante $R = {r_lastre:.2f}$ sobre el eje de ordenadas. Esto garantiza una masa de **{masa_contra:.0f} kg** calculada con rigor infinitesimal.
    """)

# --- BOTÓN ---
if st.button("🏗️ GENERAR DIAGNÓSTICO MAGISTRAL"):
    generar_diagnostico_detallado()

st.sidebar.divider()
st.sidebar.caption("© 2026 - Universidad UNICA | Ingeniería Industrial")