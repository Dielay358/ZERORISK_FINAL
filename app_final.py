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
    st.title("ZERORISK TOWER v11.8")
    st.write("**Sistema Experto de Ingeniería: Estática, Cálculo II e Inferencia de Walpole**")

st.divider()

# --- BARRA LATERAL: ENTRADA DE VARIABLES ---
st.sidebar.header("🕹️ Centro de Control Local")
radio = st.sidebar.slider("Radio de Carga (m)", 2.0, 45.0, 20.0)
cap_max = 8000 if radio <= 16.5 else 8000 * (16.5 / radio)
st.sidebar.info(f"📌 Capacidad Estructural Máxima: {cap_max:.1f} kg")

carga = st.sidebar.number_input("Peso de la Carga (kg)", 0.0, 10000.0, 2000.0)
viento = st.sidebar.slider("Velocidad del Viento (km/h)", 0, 100, 25)
mantenimiento = st.sidebar.slider("Nivel de Mantenimiento (1-10)", 1, 10, 8)
r_lastre = st.sidebar.slider("Radio Balasto (m)", 0.5, 5.0, 2.5)

# --- MOTOR TÉCNICO (INTEGRALES Y MECÁNICA) ---
vol_lastre, _ = integrate.quad(lambda y: np.pi * r_lastre**2, 0, 3)
masa_contra = vol_lastre * 2400 
long_cable, _ = integrate.quad(lambda x: np.sqrt(1 + (0.01 * x)**2), 0, radio)
mv = (carga * radio) + (2500 * 22.5) + (0.005 * viento**2 * 15 * 50)
me = masa_contra * 12 
fs = me / mv

# --- MOTOR ESTADÍSTICO (WALPOLE & BAYES) ---
p_b1, p_b2 = 0.85, 0.15 # Probabilidades de clima
p_f_dado_b1 = (1 - mantenimiento/10) * 0.05
p_f_dado_b2 = 0.50 if viento > 50 else 0.15
p_falla_total = (p_f_dado_b1 * p_b1) + (p_f_dado_b2 * p_b2)
p_bayes = (p_f_dado_b2 * p_b2) / p_falla_total if p_falla_total > 0 else 0

# --- DASHBOARD ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Factor Seguridad", f"{fs:.2f}")
m2.metric("Volumen Lastre", f"{vol_lastre:.1f} m³")
m3.metric("Riesgo Mecánico", f"{p_falla_total*100:.1f}%")
m4.metric("Prob. Bayesiana", f"{p_bayes*100:.3f}%")

# --- VISUALIZACIÓN ---
fig, ax = plt.subplots(figsize=(12, 5))
ax.set_facecolor('#0E1117'); fig.patch.set_facecolor('#0E1117')
color_est = '#10B981' if fs > 1.4 else '#F59E0B' if fs > 1.1 else '#E11D48'
ax.plot([0, 0], [0, 50], color='white', lw=8) 
ax.plot([-30, 60], [0, 0], color='#4B5563', lw=3) 
ax.plot([-12, 45], [50, 50], color=color_est, lw=6) 
balasto_x = [-12 - r_lastre, -12 + r_lastre]
ax.fill_between(balasto_x, 42, 50, color='#3B82F6', alpha=0.9)
ax.plot([radio, radio], [50, 30], color='red', lw=3, linestyle='--')
ax.scatter(radio, 30, color='red', s=300, zorder=5) 
ax.set_xlim(-25, 55); ax.set_ylim(-5, 75); ax.axis('off')
st.pyplot(fig)

# --- NUEVA FUNCIÓN: SISTEMA EXPERTO DE DIAGNÓSTICO (REEMPLAZA A LA IA) ---
def generar_diagnostico_experto(fs, pf, pb, v, c, cap_max):
    diag = "### 📋 DIAGNÓSTICO CLÍNICO DE INTEGRIDAD\n"
    
    # 1. Análisis de Estática (Hibbeler)
    if fs < 1.0:
        diag += f"🔴 **ESTADO CRÍTICO:** Factor de Seguridad ({fs:.2f}) indica colapso inminente. El Momento Volcante supera la capacidad de balance del balasto.\n\n"
    elif fs < 1.4:
        diag += f"🟡 **ALERTA PREVENTIVA:** FS de {fs:.2f} es marginal para operaciones dinámicas. Se requiere reducción de radio de carga.\n\n"
    else:
        diag += f"🟢 **ESTADO OPERATIVO:** Sistema estable bajo normas de seguridad industrial.\n\n"

    # 2. Análisis Estadístico (Walpole)
    diag += "### 📊 Evaluación de Riesgos (Modelo de Walpole)\n"
    diag += f"* **Probabilidad de Falla:** {pf:.1f}%. El nivel de mantenimiento actual genera una incertidumbre operativa considerable.\n"
    diag += f"* **Inferencia Bayesiana:** Existe un **{pb*100:.2f}%** de probabilidad de que el viento sea el factor dominante de inestabilidad en este momento.\n\n"

    # 3. Plan de Acción (Ingeniería Industrial)
    diag += "### 🛠️ PLAN DE ACCIÓN SUGERIDO\n"
    if v > 50:
        diag += "- **CONTROL CLIMÁTICO:** Viento superior a 50km/h. Activar modo 'Veleta' y suspender rotación.\n"
    if c > cap_max:
        diag += f"- **REDUCCIÓN DE CARGA:** Exceso de carga detectado. Bajar masa a menos de {cap_max:.0f} kg.\n"
    if fs < 1.5:
        diag += "- **ESTABILIZACIÓN:** Incrementar el radio del balasto o reducir el radio del carro.\n"
    
    return diag

# --- BOTÓN DE DIAGNÓSTICO (LOCAL Y SEGURO) ---
if st.button("🏗️ GENERAR DIAGNÓSTICO TÉCNICO"):
    with st.spinner('Procesando lógica estructural...'):
        resultado = generar_diagnostico_experto(fs, p_falla_total, p_bayes, viento, carga, cap_max)
        st.markdown(resultado)

with st.expander("📚 Ver Fundamentos de Walpole e Integrales"):
    st.markdown(fr"""
    *   **Teorema de Bayes:** $P(Viento|Falla) = \frac{{P(Falla|Viento)P(Viento)}}{{P(Falla)}}$ = **{p_bayes*100:.4f}%**.
    *   **Cálculo II:** Volumen $V = \pi \int_0^3 ({r_lastre})^2 dy = {vol_lastre:.2f} m^3$.
    """)

st.sidebar.divider()
st.sidebar.caption("© 2026 - Universidad UNICA")