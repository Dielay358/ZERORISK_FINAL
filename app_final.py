import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as integrate
from scipy.stats import poisson
from google import genai
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="ZERORISK TOWER Pro - UNICA", page_icon="🏗️", layout="wide")
LLAVE_MAESTRA = "AQ.Ab8RN6Iw_5HmYf8ygdEX_Ve4IHufxzZRZAz6fQjsqGxXt_PwXQ"
client = genai.Client(api_key=LLAVE_MAESTRA)

# --- CABECERA ---
col_logo, col_tit = st.columns([1, 4])
with col_logo:
    if os.path.exists("logo_unica.png"): 
        st.image("logo_unica.png", width=120)
with col_tit:
    st.title("ZERORISK TOWER v9.1")
    st.write("**Simulación de Ingeniería: Estática, Cálculo II e Inferencia Bayesiana**")

# --- BARRA LATERAL ---
st.sidebar.header("🕹️ Variables Independientes")
radio = st.sidebar.slider("Radio de Carga (m)", 2.0, 45.0, 20.0)
cap_max = 8000 if radio <= 16.5 else 8000 * (16.5 / radio)
carga = st.sidebar.number_input("Peso de la Carga (kg)", 0.0, 10000.0, 2000.0)
viento = st.sidebar.slider("Velocidad del Viento (km/h)", 0, 100, 20)
mantenimiento = st.sidebar.slider("Mantenimiento (1-10)", 1, 10, 8)
r_lastre = st.sidebar.slider("Radio Balasto (m)", 0.5, 5.0, 2.5)

# --- MOTOR DE CÁLCULO II (INTEGRALES) ---
vol_lastre, _ = integrate.quad(lambda y: np.pi * r_lastre**2, 0, 3)
masa_contra = vol_lastre * 2400 
# Integral para longitud de arco del tirante
long_cable, _ = integrate.quad(lambda x: np.sqrt(1 + (0.01 * x)**2), 0, radio)

# --- MOTOR DE MECÁNICA (HIBBELER) ---
mv = (carga * radio) + (2500 * 22.5) + (0.005 * viento**2 * 15 * 50)
me = masa_contra * 12 
fs = me / mv

# --- MOTOR DE ESTADÍSTICA (WALPOLE) ---
p_falla_mecanica = (1 - poisson.pmf(0, (12 - mantenimiento) / 12))
p_viento_alto = 1 if viento > 50 else 0.2
p_sobrecarga = 1 if carga > cap_max else 0.1
p_falla_total = (p_viento_alto * 0.6) + (p_sobrecarga * 0.4)
p_colapso_previo = 0.001 
p_viento_dado_colapso = 0.90
p_viento_general = 0.15
p_bayes = (p_viento_dado_colapso * p_colapso_previo) / p_viento_general

# --- DASHBOARD ---
st.subheader("📊 Resultados Técnicos")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Factor Seguridad", f"{fs:.2f}")
m2.metric("Volumen Lastre", f"{vol_lastre:.1f} m³")
m3.metric("Riesgo Mecánico", f"{p_falla_mecanica*100:.1f}%")
m4.metric("Prob. Bayesiana", f"{p_bayes*100:.4f}%")

# --- VISUALIZACIÓN DINÁMICA (CORREGIDA) ---
st.subheader("🏗️ Ilustración Técnica")

fig, ax = plt.subplots(figsize=(10, 5))
ax.set_facecolor('#0E1117') 
fig.patch.set_facecolor('#0E1117')

color_est = '#10B981' if fs > 1.4 else '#F59E0B' if fs > 1.1 else '#E11D48'

# 1. Dibujar Mástil y Suelo
ax.plot([0, 0], [0, 50], color='white', lw=6) 
ax.plot([-25, 55], [0, 0], color='#334155', lw=2) # Suelo

# 2. Dibujar Pluma (Derecha) y Contrapluma (Izquierda)
ax.plot([-12, 45], [50, 50], color=color_est, lw=5)

# 3. DIBUJAR BALASTO (CONTRAPESO AZUL) - ¡DINÁMICO!
# Se ensancha según el radio del balasto
balasto_x = [-12 - r_lastre, -12 + r_lastre]
ax.fill_between(balasto_x, 43, 50, color='#3B82F6', alpha=0.9)
ax.text(-12, 38, f"BALASTO\n{r_lastre}m", color='#3B82F6', ha='center', fontweight='bold')

# 4. Dibujar Carga y Cable de Izaje
ax.plot([radio, radio], [50, 35], color='red', lw=2, linestyle='--')
ax.scatter(radio, 35, color='red', s=200, zorder=5) 
ax.text(radio, 30, f"CARGA\n{carga}kg", color='red', ha='center', fontweight='bold')

# 5. Dibujar Tirante de Tensión (Cálculo II)
x_arco = np.linspace(-12, radio, 100)
y_arco = 50 + 0.005 * (x_arco + 12)**2 # Representación de la curva
ax.plot(x_arco, y_arco, color='yellow', lw=1, alpha=0.4, label='Tirante')

# Ajustes de cámara fijos
ax.set_xlim(-25, 55)
ax.set_ylim(-5, 75)
ax.axis('off')
st.pyplot(fig)

# --- SECCIÓN TEÓRICA ---
with st.expander("📚 Ver Fundamento Estadístico (Teoría de Walpole)"):
    st.markdown(fr"""
    ### Aplicación de Probabilidad y Estadística I (Walpole)
    1. **Probabilidad Simple:** Distribución de Poisson para fallas mecánicas.
    2. **Teorema de la Partición:** El riesgo total (**{p_falla_total*100:.2f}%**) es la suma de particiones climáticas y operativas.
    3. **Teorema de Bayes:** 
       $$P(Viento | Falla) = \frac{{P(Falla | Viento) \cdot P(Viento)}}{{P(Falla \ Total)}}$$
       Probabilidad calculada: **{p_bayes*100:.4f}%**.
    
    ### Aplicación de Cálculo II
    * **Sólido de Revolución:** Volumen de contrapeso: $V = \pi \int_0^3 ({r_lastre})^2 dy = {vol_lastre:.2f} m^3$.
    * **Longitud de Arco:** Longitud real del tirante: $L = \int \sqrt{{1 + [f'(x)]^2}} dx = {long_cable:.2f} m$.
    """)

# --- IA ---
if st.button("🧠 GENERAR DIAGNÓSTICO INTEGRAL"):
    prompt = f"""
    Actúa como Ingeniero Senior. Analiza los resultados:
    - FS: {fs:.2f}, Riesgo: {p_falla_total*100:.1f}%, Bayes: {p_bayes*100:.2f}%.
    - Volumen Balasto (Integral): {vol_lastre:.2f} m3.
    - Longitud Cable (Arco): {long_cable:.2f} m.
    
    Explica el diagnóstico técnico usando términos de Walpole e Hibbeler. 
    Sé directo y profesional.
    """
    
    # Lista de modelos a los que tienes acceso (según tu lista previa)
    modelos_respaldo = ['gemini-1.5-flash', 'gemini-2.0-flash-lite', 'gemini-1.5-pro']
    
    exito = False
    with st.spinner('Consultando a la IA (esto puede tardar si hay alta demanda)...'):
        for nombre_modelo in modelos_respaldo:
            if exito: break
            try:
                # Intentamos con el modelo de la lista
                res = client.models.generate_content(model=nombre_modelo, contents=prompt)
                st.success(f"Análisis generado exitosamente (Modelo: {nombre_modelo})")
                st.markdown(res.text)
                exito = True
            except Exception as e:
                if "503" in str(e):
                    st.warning(f"⚠️ El modelo {nombre_modelo} está saturado. Intentando con otro...")
                    import time
                    time.sleep(2) # Espera técnica
                else:
                    st.error(f"Error con {nombre_modelo}: {str(e)[:50]}")
        
        if not exito:
            st.error("❌ Todos los servidores de Google están ocupados en este momento. Por favor, espera 30 segundos y presiona el botón nuevamente.")

st.sidebar.divider()
st.sidebar.caption("© 2026 - Universidad UNICA")