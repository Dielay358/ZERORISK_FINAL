import customtkinter as ctk
import os
import sys
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.stats import poisson
from google import genai
import scipy.integrate as integrate

# --- CONFIGURACIÓN DE SEGURIDAD ---
LLAVE_MAESTRA = "AQ.Ab8RN6Iw_5HmYf8ygdEX_Ve4IHufxzZRZAz6fQjsqGxXt_PwXQ"
client = genai.Client(api_key=LLAVE_MAESTRA)

def resource_path(relative_path):
    try: base_path = sys._MEIPASS
    except Exception: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class ZeroRiskTowerFinal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ZERORISK TOWER v8.1 - Professional Edition")
        self.geometry("1200x850")
        
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)
        self.pantalla_portada()

    def pantalla_portada(self):
        for w in self.container.winfo_children(): w.destroy()
        frame = ctk.CTkFrame(self.container, fg_color="#0F172A")
        frame.pack(fill="both", expand=True)

        try:
            img = ctk.CTkImage(Image.open(resource_path("logo_unica.png")), size=(180, 240))
            ctk.CTkLabel(frame, image=img, text="").pack(pady=20)
        except: pass

        ctk.CTkLabel(frame, text="ZERORISK TOWER", font=("Helvetica", 60, "bold"), text_color="#E11D48").pack()
        ctk.CTkButton(frame, text="EJECUTAR CONSOLA TÉCNICA", command=self.pantalla_consola, 
                       fg_color="#E11D48", height=55, width=300, font=("Helvetica", 16, "bold")).pack(pady=40)

    def pantalla_consola(self):
        for w in self.container.winfo_children(): w.destroy()
        self.frame_consola = ctk.CTkFrame(self.container)
        self.frame_consola.pack(fill="both", expand=True)
        self.frame_consola.grid_columnconfigure(1, weight=1)

        # 1. BARRA LATERAL (CONTROLES)
        self.sidebar = ctk.CTkScrollableFrame(self.frame_consola, width=320)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(self.sidebar, text="CONFIGURACIÓN", font=("Helvetica", 20, "bold"), text_color="#E11D48").pack(pady=15)

        self.sld_distancia = self.crear_control("Radio del Carro (m)", 2, 45, 20)
        self.sld_carga = self.crear_control("Carga a Izar (kg)", 0, 8000, 1000)
        self.sld_radio_lastre = self.crear_control("Radio del Balasto (m)", 1, 5, 2)
        self.sld_viento = self.crear_control("Viento (km/h)", 0, 100, 0)
        self.sld_mant = self.crear_control("Mantenimiento (1-10)", 1, 10, 10)

        ctk.CTkButton(self.sidebar, text="🧠 DIAGNÓSTICO IA", command=self.analisis_ia_pro, fg_color="#10B981", height=45).pack(pady=30, padx=20, fill="x")
        ctk.CTkButton(self.sidebar, text="← Volver Inicio", command=self.pantalla_portada, fg_color="transparent", border_width=1).pack(side="bottom", pady=20)

        # 2. PANEL CENTRAL (GRÁFICO)
        self.main_view = ctk.CTkFrame(self.frame_consola)
        self.main_view.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # AJUSTE VITAL: Crear la figura con fondo que combine con la app
        plt.close('all') # Limpiar memorias anteriores
        self.fig, self.ax = plt.subplots(figsize=(5, 4), facecolor='#2B2B2B')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_view)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True, padx=10, pady=10)

        self.txt_ia = ctk.CTkTextbox(self.main_view, height=250, font=("Helvetica", 13), border_width=2, border_color="#1E293B")
        self.txt_ia.pack(fill="x", padx=10, pady=10)

        # 3. PANEL DERECHO (MÉTRICAS)
        self.metrics = ctk.CTkFrame(self.frame_consola, width=220)
        self.metrics.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(self.metrics, text="MÉTRICAS", font=("Helvetica", 16, "bold")).pack(pady=20)
        self.lbl_fs = self.crear_metric_box("FACTOR SEGURIDAD")
        self.lbl_vol = self.crear_metric_box("VOLUMEN LASTRE")
        self.lbl_cable = self.crear_metric_box("LONGITUD CABLE")

        # Iniciar primer cálculo
        self.actualizar_todo()

    def crear_control(self, title, min_v, max_v, init):
        ctk.CTkLabel(self.sidebar, text=title, font=("Helvetica", 12, "bold")).pack(pady=(10, 0))
        sld = ctk.CTkSlider(self.sidebar, from_=min_v, to=max_v, command=self.actualizar_todo)
        sld.set(init)
        sld.pack(padx=20, pady=5)
        # Etiqueta de valor
        lbl_val = ctk.CTkLabel(self.sidebar, text=f"{init}", text_color="#64B5F6")
        lbl_val.pack()
        # Guardamos referencia para actualizar el texto
        if "Radio" in title: self.val_dist = lbl_val
        elif "Carga" in title: self.val_carga = lbl_val
        elif "Balasto" in title: self.val_lastre = lbl_val
        elif "Viento" in title: self.val_viento = lbl_val
        elif "Mantenimiento" in title: self.val_mant = lbl_val
        return sld

    def crear_metric_box(self, title):
        frame = ctk.CTkFrame(self.metrics, fg_color="#1E293B")
        frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(frame, text=title, font=("Helvetica", 9), text_color="#94A3B8").pack(pady=5)
        lbl = ctk.CTkLabel(frame, text="--", font=("Helvetica", 24, "bold"), text_color="#10B981")
        lbl.pack(pady=5)
        return lbl

    def actualizar_todo(self, event=None):
        try:
            d, c, r_l, v, m = self.sld_distancia.get(), self.sld_carga.get(), self.sld_radio_lastre.get(), self.sld_viento.get(), self.sld_mant.get()
            
            # Actualizar textos de sliders
            self.val_dist.configure(text=f"{d:.1f} m")
            self.val_carga.configure(text=f"{c:.0f} kg")
            self.val_lastre.configure(text=f"{r_l:.1f} m")
            self.val_viento.configure(text=f"{v:.1f} km/h")
            self.val_mant.configure(text=f"{int(m)}")

            # Cálculos de Ingeniería (Cálculo II e Hibbeler)
            vol_lastre, _ = integrate.quad(lambda y: np.pi * r_l**2, 0, 3)
            masa_contra = vol_lastre * 2400 
            long_cable, _ = integrate.quad(lambda x: np.sqrt(1 + (0.01 * x)**2), 0, d)
            fs = (masa_contra * 12) / ((c * d) + (2500 * 22.5) + (0.005 * v**2 * 15 * 50))

            # Actualizar métricas
            self.lbl_fs.configure(text=f"{fs:.2f}", text_color="#10B981" if fs > 1.3 else "#E11D48")
            self.lbl_vol.configure(text=f"{vol_lastre:.1f} m³")
            self.lbl_cable.configure(text=f"{long_cable:.2f} m")

            # Redibujar Grúa
            self.dibujar_grua(d, fs)
        except Exception as e:
            print(f"Error en actualización: {e}")

    def dibujar_grua(self, d, fs):
        self.ax.clear()
        self.ax.set_facecolor('#2B2B2B')
        color = '#10B981' if fs > 1.3 else '#F59E0B' if fs > 1.05 else '#E11D48'
        
        self.ax.plot([0, 0], [0, 50], color='white', lw=5) # Torre
        self.ax.plot([-12, 45], [50, 50], color=color, lw=4) # Pluma
        self.ax.plot([d, d], [50, 40], color='red', lw=2) # Cable izaje
        self.ax.scatter(d, 40, color='red', s=150) # Carga
        self.ax.plot([-12, -12], [50, 45], color='#3B82F6', lw=8) # Contrapeso
        
        self.ax.set_xlim(-20, 50); self.ax.set_ylim(0, 60); self.ax.axis('off')
        self.canvas.draw() # <--- DIBUJAR CAMBIOS

    def analisis_ia_pro(self):
        self.txt_ia.delete("1.0", "end")
        self.txt_ia.insert("end", "⌛ Conectando con Ingeniero Senior IA...\n")
        self.update()
        prompt = f"Analiza para ZERORISK TOWER: FS {self.lbl_fs.cget('text')}, Vol Lastre {self.lbl_vol.cget('text')}, Viento {self.val_viento.cget('text')}. Estado Estructural y Plan de Accion."
        try:
            res = client.models.generate_content(model='gemini-flash-latest', contents=prompt)
            clean_res = res.text.encode('latin-1', 'ignore').decode('latin-1')
            self.txt_ia.delete("1.0", "end")
            self.txt_ia.insert("end", clean_res)
        except Exception as e:
            self.txt_ia.insert("end", f"\n❌ Error de red: {str(e)[:40]}")

if __name__ == "__main__":
    app = ZeroRiskTowerFinal()
    app.mainloop()