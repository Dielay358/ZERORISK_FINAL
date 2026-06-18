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
    st.title("ZERORISK TOWER v12.3")
    st.write("**Sistema Experto de Auditoría Estructural: Mecánica, Estadística y Cálculo II**")

st.divider()

# --- BARRA LATERAL: VARIABLES INDEPENDIENTES (CAUSAS) ---
st.sidebar.header("🕹️ Centro de Control de Variables")
radio = st.sidebar.slider("Radio de Carga (m)", 2.0, 45.0, 31.13)
carga = st.sidebar.number_input("Peso de la Carga (kg)", 0.0, 10000.0, 3000.0)
viento = st.sidebar.slider("Velocidad Viento (km/h)", 0, 100, 58)
mantenimiento = st.sidebar.slider("Nivel Mantenimiento (1-10)", 1, 10, 8)
r_lastre = st.sidebar.slider("Radio Balasto (m)", 0.5, 5.0, 3.77)

# --- MOTOR TÉCNICO: CÁLCULOS II (INTEGRALES) ---
# Procedimiento: Volumen del balasto mediante sólido de revolución (Método del disco)
# Radio constante R = r_lastre, Altura h = 3m
def integrando_volumen(y): return np.pi * (r_lastre**2)
vol_lastre, _ = integrate.quad(integrando_volumen, 0, 3)
masa_contra = vol_lastre * 2400 # kg (Densidad del hormigón)

# --- MOTOR DE MECÁNICA: MOMENTOS (HIBBELER) ---
# Mv = (Carga * Brazo) + (Peso Jib * Brazo_Jib) + Presión Viento
mv = (carga * radio) + (2500 * 22.5) + (0.005 * viento**2 * 15 * 50)
me = masa_contra * 12 # Brazo del contrapeso a 12m
fs = me / mv

# --- MOTOR ESTADÍSTICO: BAYES Y PARTICIÓN (WALPOLE) ---
# Paso 1: Definir Probabilidades a priori (Viento)
p_viento_seguro = 0.85 # P(B1)
p_viento_fuerte = 0.15 # P(B2) - Prior

# Paso 2: Definir Probabilidades Condicionales (Falla | Viento)
p_falla_dado_seguro = (1 - mantenimiento/10) * 0.05 # P(F|B1)
p_falla_dado_fuerte = 0.65 if viento > 50 else 0.20 # P(F|B2)

# Paso 3: Teorema de la Partición (Probabilidad Total de Falla)
p_falla_total = (p_falla_dado_seguro * p_viento_seguro) + (p_falla_dado_fuerte * p_viento_fuerte)

# Paso 4: Teorema de Bayes (Probabilidad de Viento Fuerte dado que hay una Falla detectada)
p_bayes = (p_falla_dado_fuerte * p_viento_fuerte) / p_falla_total if p_falla_total > 0 else 0

# --- DASHBOARD DE RESULTADOS ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Factor Seguridad", f"{fs:.2f}")
m2.metric("Volumen Balasto", f"{vol_lastre:.1f} m³")
m3.metric("P(Falla) Total", f"{p_falla_total*100:.2f}%")
m4.metric("Prob. Bayesiana", f"{p_bayes*100:.3f}%")

# --- VISUALIZACIÓN DINÁMICA CON TELEMETRÍA ---
fig, ax = plt.subplots(figsize=(12, 5))
ax.set_facecolor('#0E1117'); fig.patch.set_facecolor('#0E1117')
color_est = '#10B981' if fs > 1.4 else '#F59E0B' if fs > 1.05 else '#E11D48'

# Dibujo de Grúa
ax.plot([0, 0], [0, 50], color='white', lw=6) # Mástil
ax.plot([-30, 60], [0, 0], color='#334155', lw=2) # Suelo
ax.plot([-15, 45], [50, 50], color=color_est, lw=5) # Pluma

# Balasto Dinámico
balasto_x = [-12 - r_lastre, -12 + r_lastre]
ax.fill_between(balasto_x, 43, 50, color='#3B82F6', alpha=0.9)
ax.text(-12, 38, f"BALASTO\nR: {r_lastre:.2f}m\nM: {masa_contra:.0f}kg", color='#3B82F6', ha='center', fontweight='bold')

# Carga Dinámica
ax.plot([radio, radio], [50, 35], color='red', lw=2, linestyle='--')
ax.scatter(radio, 35, color='red', s=300, zorder=5) 
ax.text(radio, 25, f"CARGA: {carga:.0f}kg\nRadio: {radio:.2f}m", color='red', ha='center', fontweight='bold')

# Viento
ax.text(55, 60, f"🌪️ Viento: {viento} km/h", color='white', ha='right', fontsize=12, fontweight='bold')

ax.set_xlim(-25, 60); ax.set_ylim(-5, 75); ax.axis('off')
st.pyplot(fig)

# --- PANEL DE ARQUITECTURA Y DEMOSTRACIÓN DE LIBRERÍAS ---
with st.expander("🛠️ Arquitectura de Software y Demostración de Librerías"):
    st.markdown("### Justificación del Stack Tecnológico")
    df_lib = pd.DataFrame({
        "Librería": ["SciPy (Stats)", "SciPy (Integrate)", "NumPy", "Matplotlib", "Streamlit"],
        "Demostración de Aplicación": [
            f"Cálculo de Poisson y Bayes: P(F) = {p_falla_total:.4f}",
            f"Integral de volumen: integrate.quad() = {vol_lastre:.2f}",
            f"np.pi * {r_lastre:.2f}**2 y álgebra lineal de momentos.",
            f"ax.fill_between() para el balasto y ax.plot() para la estructura.",
            "st.sidebar.slider() para el control dinámico de variables."
        ],
        "Referencia Académica": ["Walpole (Probabilidad)", "Cálculo II (Integrales)", "Hibbeler (Estática)", "Ingeniería Gráfica", "Software de Ingeniería"]
    })
    st.table(df_lib)

# --- INFORME TÉCNICO CON PROCEDIMIENTOS DESGLOSADOS ---
def generar_informe_maestro():
    st.markdown("## 📋 INFORME MAGISTRAL DE AUDITORÍA TÉCNICA")
    
    # 1. ESTADÍSTICA
    st.header("1. Procedimiento Estadístico (Teorema de Bayes)")
    st.write("El objetivo es actualizar la probabilidad de fallo basándonos en la partición del espacio muestral climático.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(fr"""
        **Datos Iniciales (Priors):**
        *   **P(Viento Fuerte) $P(B_2)$**: {p_b2}
        *   **P(Falla | Viento Fuerte) $P(F|B_2)$**: {p_f_dado_b2}
        *   **P(Viento Seguro) $P(B_1)$**: {p_b1}
        *   **P(Falla | Viento Seguro) $P(F|B_1)$**: {p_f_dado_b1:.3f}
        """)
    with col2:
        st.markdown(fr"""
        **Cálculo de Probabilidad Total $P(F)$:**
        $$P(F) = \sum P(F|B_i)P(B_i)$$
        $$P(F) = ({p_f_dado_b1:.3f} \cdot {p_b1}) + ({p_f_dado_b2} \cdot {p_b2}) = {p_falla_total:.4f}$$
        """)
    
    st.markdown(fr"""
    **Aplicación del Teorema de Bayes:**
    $$P(B_2|F) = \frac{{P(F|B_2) \cdot P(B_2)}}{{P(F)}} = \frac{{{p_f_dado_b2} \cdot {p_b2}}}{{{p_falla_total:.4f}}} = {p_bayes*100:.4f}\%$$
    *   **Objetivo de Bayes:** Evaluar qué tan responsable es el viento de la inestabilidad actual.
    """)

    # 2. CÁLCULO II
    st.header("2. Procedimiento de Cálculo II (Sólido de Revolución)")
    st.write("El objetivo es determinar la masa estabilizadora exacta mediante el Método del Disco.")
    
    st.markdown(fr"""
    **Paso 1: Definición de la Integral**
    Consideramos el balasto como un cilindro generado por la rotación del radio $R = {r_lastre:.2f}$ m desde $y=0$ hasta $y=3$.
    $$V = \int_0^3 \pi \cdot [R]^2 dy = \pi \cdot ({r_lastre:.2f})^2 \int_0^3 dy$$
    
    **Paso 2: Resolución**
    $$V = \pi \cdot {r_lastre**2:.2f} \cdot [y]_0^3 = \pi \cdot {r_lastre**2:.2f} \cdot 3 = {vol_lastre:.2f} m^3$$
    
    **Paso 3: Obtención de la Masa**
    Multiplicamos por la densidad del hormigón ($\rho = 2400 kg/m^3$):
    $$Masa = {vol_lastre:.2f} m^3 \cdot 2400 kg/m^3 = {masa_contra:.0f} kg$$
    *   **Objetivo de la Variable R:** Es la variable independiente que define la inercia del sistema. A mayor radio, mayor volumen y, por tanto, mayor Momento Estabilizador.
    """)

    # 3. MECÁNICA
    st.header("3. Análisis Mecánico de Cuerpos Rígidos")
    st.write("El objetivo es verificar la Segunda Condición de Equilibrio de Hibbeler ($\sum M = 0$).")
    st.info(f"""
    *   **Momento Volcante ({mv:.0f} Nm):** Representa la tendencia al giro de la pluma por la carga y el viento.
    *   **Momento Estabilizador ({me:.0f} Nm):** Representa la resistencia al giro proporcionada por la masa del balasto calculada.
    *   **Factor de Seguridad ({fs:.2f}):** El cociente que garantiza la integridad estructural.
    """)

if st.button("🏗️ GENERAR INFORME DE AUDITORÍA MAGISTRAL"):
    generar_informe_maestro()

st.sidebar.divider()
st.sidebar.caption("© 2026 - Universidad UNICA | Ingeniería Industrial")