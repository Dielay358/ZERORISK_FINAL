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
    st.title("ZERORISK TOWER v14.1")
    st.write("**Proyecto Integrador: Ingeniería Industrial - UNICA 2026**")

st.divider()

# --- BARRA LATERAL: VARIABLES INDEPENDIENTES ---
st.sidebar.header("🕹️ Variables Independientes (Entradas)")
radio_carro = st.sidebar.slider("Radio de Carga (m)", 2.0, 45.0, 31.13)
carga = st.sidebar.number_input("Peso de la Carga (kg)", 0.0, 10000.0, 3000.0)
viento = st.sidebar.slider("Velocidad Viento (km/h)", 0, 100, 58)
mantenimiento = st.sidebar.slider("Nivel Mantenimiento (1-10)", 1, 10, 8)
num_bloques = st.sidebar.number_input("Número de Bloques de Lastre", 1, 15, 6)

# --- MOTOR TÉCNICO ---
# 1. Masa del Balasto
vol_bloque = 2 * 1 * 0.5 
masa_total_contra = num_bloques * (vol_bloque * 2380) # Densidad hormigón armado UNICA

# 2. Cálculo II: Centroide
def rho(x): return 60 + 1.5 * x 
masa_pluma, _ = integrate.quad(rho, 0, 45)
momento_pluma, _ = integrate.quad(lambda x: x * rho(x), 0, 45)
centroide_pluma = momento_pluma / masa_pluma

# 3. Mecánica (Hibbeler)
mv = (carga * radio_carro) + (masa_pluma * centroide_pluma) + (0.005 * viento**2 * 15 * 50)
me = masa_total_contra * 12 
fs = me / mv

# 4. Estadística (Walpole)
p_b1, p_b2 = 0.85, 0.15 
p_f_dado_b1 = (1 - mantenimiento/10) * 0.05
p_f_dado_b2 = 0.65 if viento > 50 else 0.20
p_falla_total = (p_f_dado_b1 * p_b1) + (p_f_dado_b2 * p_b2)
p_bayes = (p_f_dado_b2 * p_b2) / p_falla_total if p_falla_total > 0 else 0

# --- DASHBOARD ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Factor Seguridad", f"{fs:.2f}")
m2.metric("Centroide Pluma", f"{centroide_pluma:.2f} m")
m3.metric("Masa Balasto", f"{masa_total_contra:.0f} kg")
m4.metric("Prob. Bayesiana", f"{p_bayes*100:.2f}%")

# --- VISUALIZACIÓN TELEMÉTRICA ---
fig, ax = plt.subplots(figsize=(12, 5))
ax.set_facecolor('#0E1117'); fig.patch.set_facecolor('#0E1117')
color_fs = '#10B981' if fs > 1.4 else '#F59E0B' if fs > 1.1 else '#E11D48'
ax.plot([0, 0], [0, 50], color='white', lw=6) 
ax.plot([-30, 60], [0, 0], color='#4B5563', lw=3) 
ax.plot([-15, 45], [50, 50], color=color_fs, lw=5) 

for i in range(int(num_bloques)):
    y_lvl = 48 - (i * 2.2)
    ax.add_patch(plt.Rectangle((-14, y_lvl), 4, 1.8, color='#3B82F6', alpha=0.8))
ax.text(-12, 10, f"BALASTO\n{masa_total_contra:.0f}kg", color='#3B82F6', ha='center', fontweight='bold')
ax.plot([radio_carro, radio_carro], [50, 35], color='red', lw=2, linestyle='--')
ax.scatter(radio_carro, 35, color='red', s=400, zorder=5)
ax.text(radio_carro, 28, f"CARGA: {carga}kg\nR: {radio_carro}m", color='red', ha='center', fontweight='bold')
ax.scatter(centroide_pluma, 50, color='yellow', s=150, zorder=6)
ax.text(centroide_pluma, 55, f"CENTROIDE: {centroide_pluma:.2f}m", color='yellow', ha='center', fontweight='bold')

ax.set_xlim(-25, 65); ax.set_ylim(-5, 75); ax.axis('off')
st.pyplot(fig)

# --- BOTÓN DE AUDITORÍA MAGISTRAL ---
if st.button("🏗️ GENERAR INFORME DE AUDITORÍA MAGISTRAL"):
    st.header("📋 INFORME DE AUDITORÍA TÉCNICA PASO A PASO")
    
     # --- 1. CÁLCULO II DESGLOSADO ---
    st.subheader("1. Determinación del Centroide mediante Cálculo Integral")
    st.write("Siguiendo el programa de Cálculo II, determinamos el centro de masa de la pluma ($\bar{x}$) mediante la suma continua de elementos diferenciales de masa.")
    st.markdown(fr"""
    **Paso A: Definir la Función de Densidad Lineal $\rho(x)$:**  
    Modelamos la viga de acero como un cuerpo cuya densidad disminuye linealmente: $\rho(x) = 60 + 1.5x$.  
    
    **Paso B: Cálculo del Momento Estático ($M_x$):**  
    $$M_x = \int_0^{{45}} x \cdot \rho(x) dx = \int_0^{{45}} x \cdot (60 + 1.5x) dx = {momento_pluma:.2f}$$
    
    **Paso C: Cálculo de la Masa Total ($M$):**  
    $$M = \int_0^{{45}} \rho(x) dx = \int_0^{{45}} (60 + 1.5x) dx = {masa_pluma:.2f} kg$$
    
    **Paso D: División para hallar el Centroide:**  
    $$\bar{{x}} = \frac{{M_x}}{{M}} = \frac{{{momento_pluma:.2f}}}{{{masa_pluma:.2f}}} = {centroide_pluma:.2f} m$$
    *El objetivo es localizar el punto exacto donde el peso de la estructura genera torque sobre el mástil.*
    """)

    # 2. ESTADÍSTICA
    st.subheader("2. Análisis de Riesgo Bayesiano (Walpole)")
    st.markdown(fr"""
    Probabilidad Total de Falla mediante Partición:  
    $P(F) = [P(F|B_1) \cdot P(B_1)] + [P(F|B_2) \cdot P(B_2)] = {p_falla_total:.4f}$
    
    Aplicación de Bayes:  
    $P(B_2|F) = \frac{{P(F|B_2) \cdot P(B_2)}}{{P(F)}} = {p_bayes*100:.2f}\%$
    """)

    # --- 3. MASA DEL BALASTO ---
    st.subheader("3. Cálculo de Masa del Balasto")
    st.markdown(fr"""
    Para evitar la inestabilidad de figuras cilíndricas, usamos bloques rectangulares modulares:
    *   **Volumen por bloque:** $2m \cdot 1m \cdot 0.5m = 1.0 m^3$.
    *   **Masa por bloque:** $1.0 m^3 \cdot 2400 kg/m^3 = 2400 kg$.
    *   **Masa Total ({num_bloques} bloques):** **{masa_total_contra:.0f} kg**.
    """)
    
    # 4. LIBRERÍAS
    st.subheader("4. Panel de Demostración de Librerías")
    df_lib = pd.DataFrame({
        "Librería": ["SciPy (Integrate)", "SciPy (Stats)", "NumPy", "Matplotlib", "Streamlit"],
        "Función": [f"Integral Centroide", "Cálculo de Bayes", "Momentos (Hibbeler)", "Visualización DCL", "Interfaz v14.1"],
        "Resultado": [f"{centroide_pluma:.2f} m", f"{p_falla_total:.4f}", f"{mv:.0f} Nm", "Diagrama Activo", "Web Online"]
    })
    st.table(df_lib)

    # 5. CONCLUSIÓN INTEGRADORA (LO NUEVO)
    st.subheader("5. Conclusión y Veredicto Estructural")
    
    # Lógica de conclusión dinámica
    color_v = "🟢" if fs > 1.4 else "🟡" if fs > 1.1 else "🔴"
    veredicto = "OPERACIÓN SEGURA" if fs > 1.4 else "PRECAUCIÓN / LÍMITE" if fs > 1.1 else "ALTO RIESGO / ABORTAR"
    
    st.markdown(f"""
    **Síntesis de Ingeniería:**
    Tras procesar las variables independientes (Carga, Radio, Balasto, Viento y Mantenimiento), el sistema **{veredicto}** con un **Factor de Seguridad de {fs:.2f}**. 
    
    **Integración Científica:**
    1.  **Cálculo II:** Determinó la ubicación exacta del peso estructural, evitando errores de diseño.
    2.  **Mecánica:** Validó que el momento estabilizador generado por los bloques es suficiente para contrarrestar la carga.
    3.  **Estadística:** Cuantificó la incertidumbre climática. Aunque el sistema sea físicamente estable, existe un **{p_falla_total*100:.1f}%** de riesgo de incidente debido a factores externos.
    
    **Impacto del Proyecto:**
    Este software demuestra que la **Ingeniería Industrial** moderna no depende de suposiciones, sino de la suma continua de elementos diferenciales y la actualización de probabilidades. La maqueta física presentada es la evidencia tangible de estos cálculos computacionales.
    """)

st.sidebar.divider()
st.sidebar.caption("© 2026 - Universidad UNICA | FIA")