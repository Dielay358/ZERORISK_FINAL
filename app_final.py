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
    st.title("ZERORISK TOWER v12.4")
    st.write("**Informe Magistral de Ingeniería: Auditoría y Simulación Dinámica**")

st.divider()

# --- BARRA LATERAL (VARIABLES INDEPENDIENTES) ---
st.sidebar.header("🕹️ Centro de Control de Variables")
radio = st.sidebar.slider("Radio de Carga (m)", 2.0, 45.0, 31.13)
carga = st.sidebar.number_input("Peso de la Carga (kg)", 0.0, 10000.0, 3000.0)
viento = st.sidebar.slider("Velocidad Viento (km/h)", 0, 100, 58)
mantenimiento = st.sidebar.slider("Nivel Mantenimiento (1-10)", 1, 10, 8)
r_lastre = st.sidebar.slider("Radio Balasto (m)", 0.5, 5.0, 3.77)

# --- MOTOR TÉCNICO (CÁLCULOS CENTRALIZADOS) ---
# Cálculo II
vol_lastre, _ = integrate.quad(lambda y: np.pi * (r_lastre**2), 0, 3)
masa_contra = vol_lastre * 2400 

# Mecánica
mv = (carga * radio) + (2500 * 22.5) + (0.005 * viento**2 * 15 * 50)
me = masa_contra * 12 
fs = me / mv

# Estadística (Walpole)
p_b1, p_b2 = 0.85, 0.15 
p_f_dado_b1 = (1 - mantenimiento/10) * 0.05 
p_f_dado_b2 = 0.65 if viento > 50 else 0.20 
p_falla_total = (p_f_dado_b1 * p_b1) + (p_f_dado_b2 * p_b2) 
p_bayes = (p_f_dado_b2 * p_b2) / p_falla_total if p_falla_total > 0 else 0

# --- DASHBOARD ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Factor Seguridad", f"{fs:.2f}")
m2.metric("Volumen Lastre", f"{vol_lastre:.1f} m³")
m3.metric("P(Falla) Total", f"{p_falla_total*100:.2f}%")
m4.metric("Prob. Bayesiana", f"{p_bayes*100:.3f}%")

# --- VISUALIZACIÓN ---
fig, ax = plt.subplots(figsize=(12, 5))
ax.set_facecolor('#0E1117'); fig.patch.set_facecolor('#0E1117')
color_est = '#10B981' if fs > 1.4 else '#F59E0B' if fs > 1.05 else '#E11D48'

ax.plot([0, 0], [0, 50], color='white', lw=6) # Mástil
ax.plot([-30, 60], [0, 0], color='#334155', lw=2) # Suelo
ax.plot([-15, 45], [50, 50], color=color_est, lw=5) # Pluma

# Balasto Dinámico
balasto_x = [-12 - r_lastre, -12 + r_lastre]
ax.fill_between(balasto_x, 43, 50, color='#3B82F6', alpha=0.9)
# CORRECCIÓN POSICIÓN: Se bajó de 38 a 22 para evitar solapamiento
ax.text(-12, 22, f"BALASTO\nR: {r_lastre:.2f}m\nM: {masa_contra:.0f}kg", 
        color='#3B82F6', ha='center', fontweight='bold', fontsize=10)

# Carga Dinámica
ax.plot([radio, radio], [50, 35], color='red', lw=2, linestyle='--')
ax.scatter(radio, 35, color='red', s=300, zorder=5) 
ax.text(radio, 25, f"CARGA: {carga:.0f}kg\nDist: {radio:.2f}m", color='red', ha='center', fontweight='bold')

ax.set_xlim(-25, 60); ax.set_ylim(-5, 75); ax.axis('off')
st.pyplot(fig)

# --- PANEL DE LIBRERÍAS ---
with st.expander("🛠️ Arquitectura de Software y Demostración de Librerías"):
    df_lib = pd.DataFrame({
        "Librería": ["SciPy (Stats)", "SciPy (Integrate)", "NumPy", "Matplotlib", "Streamlit"],
        "Demostración de Aplicación": [
            f"Distribución de Poisson y Bayes: P(F) = {p_falla_total:.4f}",
            f"Integral Definida de Volumen: {vol_lastre:.2f} m3",
            f"Cálculo de Torque: {mv:.0f} Nm",
            "DCL Dinámico: ax.fill_between() y ax.text()",
            "Interfaz reactiva: st.sidebar y st.metric()"
        ],
        "Referencia": ["Walpole", "Cálculo II", "Hibbeler", "Gráfica", "Software"]
    })
    st.table(df_lib)

# --- FUNCIÓN DE INFORME (CORREGIDA: Ahora recibe las variables) ---
def generar_informe_maestro(p_b1, p_b2, p_f1, p_f2, p_tot, pb, vl, mc, rl, mv_val, me_val, fs_val):
    st.markdown("## 📋 INFORME MAGISTRAL DE AUDITORÍA TÉCNICA")
    
    st.header("1. Procedimiento Estadístico (Walpole)")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(fr"""
        **Priors y Prob. Condicional:**
        *   $P(Viento \ Fuerte) [P(B_2)]$: **{p_b2}**
        *   $P(Falla | Viento \ F.) [P(F|B_2)]$: **{p_f2}**
        *   $P(Viento \ Seguro) [P(B_1)]$: **{p_b1}**
        *   $P(Falla | Viento \ S.) [P(F|B_1)]$: **{p_f1:.3f}**
        """)
    with col2:
        st.markdown(fr"""
        **Probabilidad Total $P(F)$:**
        $$P(F) = (P(F|B_1) \cdot P(B_1)) + (P(F|B_2) \cdot P(B_2))$$
        $$P(F) = ({p_f1:.3f} \cdot {p_b1}) + ({p_f2} \cdot {p_b2}) = {p_tot:.4f}$$
        """)
    
    st.markdown(fr"""
    **Aplicación del Teorema de Bayes:**
    $$P(B_2|F) = \frac{{P(F|B_2) \cdot P(B_2)}}{{P(F)}} = \frac{{{p_f2} \cdot {p_b2}}}{{{p_tot:.4f}}} = {pb*100:.4f}\%$$
    """)

    st.header("2. Procedimiento de Cálculo II")
    st.markdown(fr"""
    **Sólido de Revolución (Método del Disco):**
    $$V = \pi \int_0^3 ({rl:.2f})^2 dy = \pi \cdot {rl**2:.2f} \cdot 3 = {vl:.2f} m^3$$
    **Masa Final:** $M = {vl:.2f} \cdot 2400 kg/m^3 = {mc:.0f} kg$.
    """)

    st.header("3. Estática (Hibbeler)")
    st.info(f"FS: {fs_val:.2f} | M. Volcante: {mv_val:.0f} Nm | M. Estabilizador: {me_val:.0f} Nm")

# --- BOTÓN DE EJECUCIÓN ---
if st.button("🏗️ GENERAR INFORME DE AUDITORÍA MAGISTRAL"):
    generar_informe_maestro(p_b1, p_b2, p_f_dado_b1, p_f_dado_b2, p_falla_total, p_bayes, vol_lastre, masa_contra, r_lastre, mv, me, fs)

st.sidebar.divider()
st.sidebar.caption("© 2026 - Universidad UNICA")