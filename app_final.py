import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as integrate
from scipy.stats import poisson
from google import genai
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="ZERORISK TOWER Pro - UNICA", page_icon="🏗️", layout="wide")

# --- CONEXIÓN IA SEGURA (USANDO SECRETS) ---
try:
    # Esta línea busca la llave en la configuración de la nube de Streamlit
    api_key_cloud = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key_cloud)
except Exception:
    st.error("❌ Configura la 'GEMINI_API_KEY' en el panel de Secrets de Streamlit.")
    st.stop()

# --- CABECERA ---
col_logo, col_tit = st.columns([1, 4])
with col_logo:
    if os.path.exists("logo_unica.png"): 
        st.image("logo_unica.png", width=120)
with col_tit:
    st.title("ZERORISK TOWER v9.5")
    st.write("**Simulación de Ingeniería: Estática (Hibbeler), Cálculo II e Inferencia Bayesiana (Walpole)**")

st.divider()

# --- BARRA LATERAL: VARIABLES INDEPENDIENTES (CAUSAS) ---
st.sidebar.header("🕹️ Variables Independientes")
radio = st.sidebar.slider("Radio de Carga (m)", 2.0, 45.0, 20.0, help="Distancia horizontal del carro")
cap_max = 8000 if radio <= 16.5 else 8000 * (16.5 / radio)
st.sidebar.info(f"📌 Capacidad Estructural Máxima a {radio:.1f}m: {cap_max:.1f} kg")

carga = st.sidebar.number_input("Peso de la Carga (kg)", 0.0, 10000.0, 2000.0)
viento = st.sidebar.slider("Velocidad del Viento (km/h)", 0, 100, 20)
mantenimiento = st.sidebar.slider("Nivel de Mantenimiento (1-10)", 1, 10, 8)
r_lastre = st.sidebar.slider("Radio Balasto (m)", 0.5, 5.0, 2.5, help="Cambia visualmente el tamaño del contrapeso")

# --- MOTOR DE CÁLCULO II (INTEGRALES) ---
# 1. Volumen del Balasto (Sólido de Revolución)
vol_lastre, _ = integrate.quad(lambda y: np.pi * r_lastre**2, 0, 3)
masa_contra = vol_lastre * 2400 # Densidad del hormigón kg/m3

# 2. Longitud de Arco (Catenaria del tirante superior)
long_cable, _ = integrate.quad(lambda x: np.sqrt(1 + (0.01 * x)**2), 0, radio)

# --- MOTOR DE MECÁNICA (MOMENTOS DE HIBBELER) ---
mv = (carga * radio) + (2500 * 22.5) + (0.005 * viento**2 * 15 * 50)
me = masa_contra * 12 # Brazo del contrapeso fijo a 12m
fs = me / mv

# --- MOTOR DE ESTADÍSTICA (WALPOLE & BAYES) ---
p_b1 = 0.85 # Clima Seguro
p_b2 = 0.15 # Viento Fuerte
p_f_dado_b1 = (1 - mantenimiento/10) * 0.05
p_f_dado_b2 = 0.50 if viento > 50 else 0.15
p_falla_total = (p_f_dado_b1 * p_b1) + (p_f_dado_b2 * p_b2)
p_bayes = (p_f_dado_b2 * p_b2) / p_falla_total if p_falla_total > 0 else 0

# --- DASHBOARD DE VARIABLES DEPENDIENTES (EFECTOS) ---
st.subheader("📊 Métricas de Respuesta (Resultados)")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Factor Seguridad", f"{fs:.2f}", delta="Crítico" if fs < 1.15 else "Estable")
m2.metric("Volumen Balasto", f"{vol_lastre:.1f} m³")
m3.metric("Riesgo Estructural", f"{p_falla_total*100:.1f}%")
m4.metric("Prob. Bayesiana", f"{p_bayes*100:.3f}%")

# --- VISUALIZACIÓN DINÁMICA ---
st.subheader("🏗️ Ilustración Técnica en Tiempo Real")
fig, ax = plt.subplots(figsize=(10, 5))
ax.set_facecolor('#0E1117') 
fig.patch.set_facecolor('#0E1117')
color_est = '#10B981' if fs > 1.3 else '#F59E0B' if fs > 1.05 else '#E11D48'

# Dibujo de estructura
ax.plot([0, 0], [0, 50], color='white', lw=6) # Mástil
ax.plot([-30, 60], [0, 0], color='#4B5563', lw=2) # Suelo
ax.plot([-12, 45], [50, 50], color=color_est, lw=5) # Jib

# Balasto dinámico (Basado en r_lastre)
balasto_x = [-12 - r_lastre, -12 + r_lastre]
ax.fill_between(balasto_x, 43, 50, color='#3B82F6', alpha=0.9)
ax.text(-12, 38, f"BALASTO\n{r_lastre}m", color='#3B82F6', ha='center', fontweight='bold')

# Carga dinámica
ax.plot([radio, radio], [50, 30], color='red', lw=2, linestyle='--')
ax.scatter(radio, 30, color='red', s=carga/5, alpha=0.8, edgecolors='white', zorder=5)
ax.text(radio, 23, f"CARGA\n{carga}kg", color='red', ha='center', fontweight='bold')

# Tirante de Cálculo II
x_arco = np.linspace(-12, radio, 100)
y_arco = 50 + 0.006 * (x_arco + 12)**2
ax.plot(x_arco, y_arco, color='#FDE047', lw=1.5, alpha=0.5)

ax.set_xlim(-25, 55); ax.set_ylim(-5, 75); ax.axis('off')
st.pyplot(fig)

# --- FUNDAMENTOS TEÓRICOS ---
with st.expander("📚 Ver Fundamento Estadístico y de Cálculo (Hibbeler/Walpole)"):
    st.markdown(fr"""
    ### Análisis de Ingeniería Aplicado:
    *   **Teorema de Bayes:** Calculamos la probabilidad revisada de falla crítica dado el viento actual: 
        $$P(B_2 | F) = \frac{{P(F|B_2) \cdot P(B_2)}}{{P(F)}}$$
    *   **Cálculo II:** Volumen del balasto mediante integral de revolución: 
        $V = \pi \int_0^3 ({r_lastre:.2f})^2 dy = {vol_lastre:.2f} m^3$.
    *   **Mecánica de Cuerpos Rígidos:** Momento de vuelco actual: **{mv:.0f} Nm**.
    """)

# --- IA DIAGNÓSTICO (ALTA DISPONIBILIDAD) ---
if st.button("🧠 GENERAR DIAGNÓSTICO INTEGRAL IA"):
    prompt = f"Como Ingeniero Senior, analiza: FS {fs:.2f}, Riesgo Total {p_falla_total*100:.1f}%, Bayes {p_bayes*100:.2f}%. Usa terminología de Walpole e Hibbeler."
    modelos = ['gemini-1.5-flash', 'gemini-2.0-flash-lite']
    exito = False
    with st.spinner('Analizando integridad estructural...'):
        for mod in modelos:
            if exito: break
            try:
                res = client.models.generate_content(model=mod, contents=prompt)
                st.success(f"Diagnóstico emitido por {mod}")
                st.markdown(res.text)
                exito = True
            except: continue
        if not exito: st.error("Servidores ocupados. Intenta en 30 segundos.")

st.sidebar.divider()
st.sidebar.caption("© 2026 - Universidad UNICA")