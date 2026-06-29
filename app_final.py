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
    st.title("ZERORISK TOWER v14.2")
    st.write("**Simulación de Ingeniería Avanzada: Mecánica, Estadística y Cálculo II**")

st.divider()

# --- BARRA LATERAL: VARIABLES INDEPENDIENTES (ENTRADAS) ---
st.sidebar.header("🕹️ Variables Independientes (Input)")
radio_carro = st.sidebar.slider("Radio de Carga (m)", 2.0, 45.0, 31.13)
carga = st.sidebar.number_input("Peso de la Carga (kg)", 0.0, 10000.0, 3000.0)
viento = st.sidebar.slider("Velocidad Viento (km/h)", 0, 100, 58)
mantenimiento = st.sidebar.slider("Nivel Mantenimiento (1-10)", 1, 10, 8)
num_bloques = st.sidebar.number_input("Número de Bloques de Lastre", 1, 15, 6)

# --- MOTOR TÉCNICO ---
# 1. Masa del Balasto (Prismas Rectangulares)
vol_bloque = 2 * 1 * 0.5 
masa_total_contra = num_bloques * (vol_bloque * 2380) 

# 2. Motor de Cálculo II: Centroide de la Pluma
def rho(x): return 60 + 1.5 * x 
masa_pluma, _ = integrate.quad(rho, 0, 45)
momento_pluma, _ = integrate.quad(lambda x: x * rho(x), 0, 45)
centroide_pluma = momento_pluma / masa_pluma

# 3. Motor de Mecánica (Hibbeler)
mv = (carga * radio_carro) + (masa_pluma * centroide_pluma) + (0.005 * viento**2 * 15 * 50)
me = masa_total_contra * 12 
fs = me / mv

# 4. Motor de Estadística (Walpole)
p_b1, p_b2 = 0.85, 0.15 # B1: Viento Seguro, B2: Viento Fuerte
p_f_dado_b1 = (1 - mantenimiento/10) * 0.05
p_f_dado_b2 = 0.65 if viento > 50 else 0.20
p_falla_total = (p_f_dado_b1 * p_b1) + (p_f_dado_b2 * p_b2)
p_bayes = (p_f_dado_b2 * p_b2) / p_falla_total if p_falla_total > 0 else 0

# --- DASHBOARD DE RESULTADOS ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Factor Seguridad", f"{fs:.2f}")
m2.metric("Centroide Pluma", f"{centroide_pluma:.2f} m")
m3.metric("Masa Balasto", f"{masa_total_contra:.0f} kg")
m4.metric("Prob. Bayesiana", f"{p_bayes*100:.2f}%")

# --- VISUALIZACIÓN TELEMÉTRICA (CORREGIDA) ---
st.subheader("🏗️ Ilustración Estructural Telemétrica")
fig, ax = plt.subplots(figsize=(12, 6))
ax.set_facecolor('#0E1117'); fig.patch.set_facecolor('#0E1117')
color_fs = '#10B981' if fs > 1.4 else '#E11D48'

# Dibujo estructural
ax.plot([0, 0], [0, 50], color='white', lw=6) # Mástil
ax.plot([-30, 60], [0, 0], color='#4B5563', lw=3) # Suelo
ax.plot([-15, 45], [50, 50], color=color_fs, lw=5) # Pluma

# Lastre/Balasto (Ajuste de posición de texto)
for i in range(int(num_bloques)):
    y_lvl = 48 - (i * 2.2)
    ax.add_patch(plt.Rectangle((-14, y_lvl), 4, 1.8, color='#3B82F6', alpha=0.8))
ax.text(-12, 5, f"BALASTO\n{masa_total_contra:.0f}kg", color='#3B82F6', ha='center', fontweight='bold', fontsize=11)

# Carga (Ajuste de posición para que no se tape)
ax.plot([radio_carro, radio_carro], [50, 35], color='red', lw=2, linestyle='--')
ax.scatter(radio_carro, 35, color='red', s=400, zorder=5)
ax.text(radio_carro + 2, 30, f"CARGA: {carga:.0f}kg\nR: {radio_carro:.2f}m", color='red', ha='left', fontweight='bold', fontsize=11)

# Centroide (Punto amarillo)
ax.scatter(centroide_pluma, 50, color='yellow', s=150, zorder=6, edgecolors='black')
ax.text(centroide_pluma, 55, f"CENTROIDE: {centroide_pluma:.2f}m", color='yellow', ha='center', fontweight='bold')

ax.set_xlim(-25, 65); ax.set_ylim(-5, 75); ax.axis('off')
st.pyplot(fig)

# --- BOTÓN DE AUDITORÍA MAGISTRAL ---
if st.button("🏗️ GENERAR INFORME DE AUDITORÍA MAGISTRAL"):
    st.header("📋 INFORME DE AUDITORÍA TÉCNICA PASO A PASO")
    
    # 1. CÁLCULO II (CORREGIDO EL ERROR DE AR{X})
    st.subheader("1. Determinación del Centroide mediante Cálculo Integral")
    st.write("Determinamos el centro de masa de la pluma mediante la integración de la densidad lineal:")
    st.markdown(fr"""
    **Paso A: Definir la Función de Densidad Lineal $\rho(x)$:**  
    $\rho(x) = 60 + 1.5x$.  
    
    **Paso B: Cálculo del Momento Estático ($M_x$):**  
    $M_x = \int_0^{{45}} x \cdot (60 + 1.5x) dx = {momento_pluma:.2f}$
    
    **Paso C: Cálculo de la Masa Total ($M$):**  
    $M = \int_0^{{45}} (60 + 1.5x) dx = {masa_pluma:.2f} kg$
    
    **Paso D: Resultado Final:**  
    $\bar{{x}} = \frac{{M_x}}{{M}} = \frac{{{momento_pluma:.2f}}}{{{masa_pluma:.2f}}} = {centroide_pluma:.2f} m$
    """)

    # --- 2. ESTADÍSTICA DESGLOSADA ---
    st.subheader("2. Análisis de Riesgo Bayesiano (Walpole)")
    st.write("Aplicamos el Teorema de Bayes para actualizar la probabilidad de fallo bajo evidencia de viento.")
    st.markdown(fr"""
    **Paso A: Probabilidad Total (Teorema de Partición):**  
    Dividimos el riesgo en dos escenarios: Viento Seguro ($B_1$) y Viento Fuerte ($B_2$).  
    $$P(F) = [P(F|B_1) \cdot P(B_1)] + [P(F|B_2) \cdot P(B_2)]$$
    $$P(F) = [{p_f_dado_b1:.3f} \cdot {p_b1}] + [{p_f_dado_b2:.2f} \cdot {p_b2}] = {p_falla_total:.4f}$$
    
    **Paso B: Aplicación de Bayes:**  
    $$P(B_2|F) = \frac{{P(F|B_2) \cdot P(B_2)}}{{P(F)}} = \frac{{{p_f_dado_b2} \cdot {p_b2}}}{{{p_falla_total:.4f}}} = {p_bayes*100:.2f}\%$$
    *Objetivo: Cuantificar qué tanto influye el viento en la probabilidad de colapso actual.*
    """)

    # --- 3. MASA DEL BALASTO ---
    st.subheader("3. Cálculo de Masa del Balasto")
    st.markdown(fr"""
    Para evitar la inestabilidad de figuras cilíndricas, usamos bloques rectangulares modulares:
    *   **Volumen por bloque:** $2m \cdot 1m \cdot 0.5m = 1.0 m^3$.
    *   **Masa por bloque:** $1.0 m^3 \cdot 2380 kg/m^3 = 2380 kg$.
    *   **Masa Total ({num_bloques} bloques):** **{masa_total_contra:.0f} kg**.
    """)

    # 4. PANEL DE LIBRERÍAS
    st.subheader("4. Panel de Demostración de Librerías")
    df_lib = pd.DataFrame({
        "Librería": ["SciPy (Integrate)", "SciPy (Stats)", "NumPy", "Matplotlib", "Streamlit"],
        "Función": ["Integral de Centroide", "Teoremas de Walpole", "Álgebra de Hibbeler", "DCL Dinámico", "Interfaz Web"],
        "Resultado Real": [f"{centroide_pluma:.2f} m", f"{p_falla_total:.4f}", f"{mv:.0f} Nm", "Telemetría Activa", "Online"]
    })
    st.table(df_lib)

    # 5. CONCLUSIÓN INTEGRADORA PARA FERIA
    st.subheader("5. Conclusión y Veredicto Estructural")
    veredicto = "OPERACIÓN SEGURA" if fs > 1.4 else "ALTO RIESGO / ABORTAR"
    st.markdown(f"""
    **Síntesis de Ingeniería:**  
    El sistema se encuentra en un estado de **{veredicto}** con un **Factor de Seguridad de {fs:.2f}**. 
    
    La integración de **Cálculo II** nos permitió ubicar con precisión el peso estructural ({centroide_pluma:.2f}m), lo que optimiza la **Mecánica** de la grúa al balancear las cargas. Finalmente, la **Estadística** de Walpole nos otorga la capacidad predictiva: sabemos que hay un **{p_falla_total*100:.1f}%** de riesgo total, del cual el **{p_bayes*100:.1f}%** es atribuible exclusivamente a las ráfagas de viento actuales.
    
    **Impacto:** Este proyecto demuestra cómo la programación permite aplicar la teoría avanzada para salvar vidas y recursos en la industria.
    """)

st.sidebar.divider()
st.sidebar.caption("© 2026 - Universidad UNICA | FIA")