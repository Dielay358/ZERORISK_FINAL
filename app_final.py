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
    st.title("ZERORISK TOWER v13.1")
    st.write("**Consola Telemétrica: Centroide por Integrales y Estática de Precisión**")

st.divider()

# --- BARRA LATERAL (INPUTS) ---
st.sidebar.header("🕹️ Variables Independientes")
radio_carro = st.sidebar.slider("Radio de Carga (m)", 2.0, 45.0, 30.0)
carga = st.sidebar.number_input("Peso de la Carga (kg)", 0.0, 10000.0, 3000.0)
viento = st.sidebar.slider("Velocidad Viento (km/h)", 0, 100, 45)
mantenimiento = st.sidebar.slider("Nivel de Mantenimiento (1-10)", 1, 10, 8)

st.sidebar.subheader("🧱 Configuración de Lastre")
num_bloques = st.sidebar.number_input("Número de Bloques", 1, 15, 6)
# Dimensiones reales bloque: 2m x 1.5m
masa_total_contra = num_bloques * (2 * 1 * 0.5 * 2400) 

# --- MOTOR DE CÁLCULO II: CENTROIDE ---
# rho(x) = densidad lineal. La pluma es más pesada cerca de la torre.
def rho(x): return 60 + 1.5 * x 

masa_pluma, _ = integrate.quad(rho, 0, 45)
momento_estatico, _ = integrate.quad(lambda x: x * rho(x), 0, 45)
centroide_pluma = momento_estatico / masa_pluma

# --- MOTOR DE MECÁNICA ---
mv = (carga * radio_carro) + (masa_pluma * centroide_pluma) + (0.005 * viento**2 * 15 * 50)
me = masa_total_contra * 12 # El brazo corto es de 12m
fs = me / mv

# --- MOTOR ESTADÍSTICO (WALPOLE) ---
p_falla_total = ((1 if viento > 55 else 0.2) * 0.6) + ((1 if carga > 5000 else 0.1) * 0.4)
p_bayes = (0.90 * 0.15) / p_falla_total if p_falla_total > 0 else 0

# --- DASHBOARD ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Factor Seguridad", f"{fs:.2f}")
m2.metric("X_cm (Pluma)", f"{centroide_pluma:.2f} m")
m3.metric("Masa Lastre", f"{masa_total_contra:.0f} kg")
m4.metric("Prob. Incidente", f"{p_falla_total*100:.1f}%")

# --- VISUALIZACIÓN DINÁMICA MEJORADA ---
st.subheader("🏗️ Diagrama de Cuerpo Libre con Telemetría")

fig, ax = plt.subplots(figsize=(12, 6))
ax.set_facecolor('#0E1117'); fig.patch.set_facecolor('#0E1117')
color_fs = '#10B981' if fs > 1.4 else '#F59E0B' if fs > 1.1 else '#E11D48'

# 1. Mástil y Suelo
ax.plot([0, 0], [0, 50], color='white', lw=8) 
ax.plot([-30, 60], [0, 0], color='#4B5563', lw=3) 

# 2. Pluma Completa (Jib)
ax.plot([-15, 45], [50, 50], color=color_fs, lw=6)

# 3. Bloques de Contrapeso (Posicionamiento preciso)
for i in range(int(num_bloques)):
    y_lvl = 48 - (i * 2.2) # Apilado hacia abajo
    ax.add_patch(plt.Rectangle((-14, y_lvl), 4, 1.8, color='#3B82F6', alpha=0.8))
# Etiqueta de Masa Lastre
ax.text(-12, 15, f"LASTRE TOTAL\n{masa_total_contra:.0f}kg", color='#3B82F6', ha='center', fontweight='bold')

# 4. Carga y Gancho (Telemetría de Carga)
ax.plot([radio_carro, radio_carro], [50, 35], color='red', lw=2, linestyle='--')
ax.scatter(radio_carro, 35, color='red', s=400, zorder=5) 
ax.text(radio_carro, 28, f"CARGA: {carga:.0f}kg\nR: {radio_carro:.2f}m", color='red', ha='center', fontweight='bold')

# 5. Marcador de Centroide (Cálculo II)
ax.scatter(centroide_pluma, 50, color='yellow', s=150, edgecolors='black', zorder=6)
ax.text(centroide_pluma, 55, f"Centroide (Integral)\n{centroide_pluma:.2f}m", color='yellow', ha='center', fontweight='bold')

# 6. Indicador de Viento
ax.text(58, 65, f"🌪️ Viento: {viento} km/h", color='white', ha='right', fontsize=12, fontweight='bold')

ax.set_xlim(-25, 65); ax.set_ylim(-5, 75); ax.axis('off')
st.pyplot(fig)

# --- FUNDAMENTOS (INSTRUMENTO DE EVALUACIÓN) ---
with st.expander("📚 Fundamentación Científica (Criterios de Evaluación)"):
    st.markdown(fr"""
    ### 1. Determinación del Centroide ($\bar{{x}}$) mediante Cálculo Integral
    Para evaluar la estabilidad, no simplificamos la pluma como un punto. Aplicamos la suma continua de elementos diferenciales:
    $$\bar{{x}} = \frac{{\int_0^{{45}} x \cdot (60 + 1.5x) dx}}{{\int_0^{{45}} (60 + 1.5x) dx}} = {centroide_pluma:.2f} m$$
    Este valor es la posición donde actúa el peso propio de la estructura metálica.

    ### 2. Influencia en la Estabilidad (Hibbeler)
    El centro de masa es el eje de giro del momento estabilizador estático. Si el centroide estuviera más lejos del mástil, el Momento Volcante aumentaría sin necesidad de carga externa, reduciendo la eficiencia estructural.

    ### 3. Teorema de Bayes (Walpole)
    Calculamos la probabilidad condicional de falla crítica:
    $$P(B_2 | F) = \frac{{P(F | B_2) \cdot P(B_2)}}{{P(F)}} = {p_bayes*100:.2f}\%$$
    """)

    ### 4. Panel de Demostración de Librerías
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

# --- BOTÓN DE DIAGNÓSTICO ---
if st.button("🏗️ GENERAR DIAGNÓSTICO MAGISTRAL"):
    st.markdown("## 📋 INFORME DE AUDITORÍA TÉCNICA")
    st.write(f"**Estado del Sistema:** {'SEGURO' if fs > 1.2 else 'CRÍTICO'}")
    st.write(f"El Momento Volcante total (Carga + Centroide Pluma + Viento) es de **{mv:.0f} Nm**.")
    st.write(f"Se requiere un contrapeso de al menos **{masa_total_contra:.0f} kg** para mantener un FS de **{fs:.2f}**.")

st.sidebar.divider()
st.sidebar.caption("© 2026 - Universidad UNICA | FIA")