import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Simulador de Lanzamiento Vertical", layout="wide")

st.title("🚀 Simulador de Lanzamiento Vertical")
st.markdown("""
Esta aplicación simula el movimiento de un cuerpo lanzado desde un edificio, permitiendo variar
la gravedad según el cuerpo celeste.
""")

# --- 1. BASE DE DATOS DE GRAVEDAD (La "Mecanización") ---
GRAVEDAD_SISTEMA_SOLAR = {
    "Tierra (9.81 m/s²)": 9.81,
    "Luna (1.62 m/s²)": 1.62,
    "Marte (3.72 m/s²)": 3.72,
    "Júpiter (24.79 m/s²)": 24.79,
    "Saturno (10.44 m/s²)": 10.44,
    "Venus (8.87 m/s²)": 8.87,
    "Mercurio (3.7 m/s²)": 3.7,
    "Sol (274 m/s²)": 274.0,
    "Plutón (0.62 m/s²)": 0.62
}

# --- 2. BARRA LATERAL (CONTROLES) ---
with st.sidebar:
    st.header("1. Configuración del Entorno")
    planeta = st.selectbox("Selecciona el lugar:", list(GRAVEDAD_SISTEMA_SOLAR.keys()))
    g = GRAVEDAD_SISTEMA_SOLAR[planeta]
    
    st.divider()
    st.header("2. Variables Iniciales")
    
    # Altura del edificio (di)
    d_i = st.number_input("Altura inicial del edificio (di) [m]", value=50.0, min_value=0.0, step=1.0)
    
    # Velocidad inicial (vi)
    v_i = st.number_input("Velocidad inicial (vi) [m/s]", value=10.0, step=1.0, help="Positivo hacia arriba, negativo hacia abajo")

    # Mostrar tu imagen de referencia si existe
    st.divider()
    st.markdown("**Diagrama de Referencia**")
    if os.path.exists("esquema.jpeg"):
        st.image("esquema.jpeg", caption="Tu boceto original", use_container_width=True)
    else:
        st.info("Sube tu imagen 'esquema.jpeg' al repositorio para verla aquí.")

# --- 3. CÁLCULOS FÍSICOS (MOTOR) ---
# Ecuación de posición: y(t) = di + vi*t - 0.5*g*t^2
# Para encontrar el tiempo total de vuelo, resolvemos cuando y(t) = 0 usando la fórmula general
# 0 = di + vi*t - 0.5*g*t^2  =>  -0.5g*t^2 + vi*t + di = 0

a_quad = -0.5 * g
b_quad = v_i
c_quad = d_i

# Discriminante
discriminante = b_quad**2 - 4*a_quad*c_quad

if discriminante >= 0:
    t1 = (-b_quad + np.sqrt(discriminante)) / (2*a_quad)
    t2 = (-b_quad - np.sqrt(discriminante)) / (2*a_quad)
    t_total = max(t1, t2) # El tiempo positivo es el real
else:
    t_total = 0 # Error físico (no debería pasar con gravedad positiva)

# Velocidad final: vf = vi - g*t
v_f = v_i - g * t_total

# Altura máxima (cuando v = 0, t = vi/g)
if v_i > 0:
    t_max_h = v_i / g
    h_max = d_i + (v_i * t_max_h) - (0.5 * g * t_max_h**2)
else:
    h_max = d_i # Si lanzas hacia abajo, la altura máxima es la inicial

# --- 4. VISUALIZACIÓN GRÁFICA ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Trayectoria Simulada")
    
    # Generamos datos para la gráfica
    t = np.linspace(0, t_total, 200)
    y = d_i + v_i * t - 0.5 * g * t**2
    
    # Truco visual: Creamos una "x" ficticia para que la gráfica se vea como tu dibujo
    # El objeto se aleja del edificio ligeramente mientras avanza el tiempo
    x = np.linspace(0, 5, 200) 

    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 1. Dibujar el Edificio (Rectángulo gris a la izquierda)
    rect = plt.Rectangle((-2, 0), 2, d_i, color='gray', alpha=0.5, label='Edificio')
    ax.add_patch(rect)
    # Plataforma
    plt.plot([0, 0.5], [d_i, d_i], color='black', linewidth=3)
    
    # 2. Dibujar la Trayectoria (Línea punteada como en tu dibujo)
    ax.plot(x, y, linestyle='--', color='black', label='Trayectoria')
    
    # 3. Dibujar vectores (Flechas)
    # Vector Velocidad Inicial (Azul)
    ax.arrow(0, d_i, 0, v_i * 0.5, head_width=0.2, head_length=d_i*0.05, fc='blue', ec='blue', label='Vi')
    plt.text(0.2, d_i + v_i*0.2, r'$v_i$', color='blue', fontsize=12, fontweight='bold')
    
    # Vector Velocidad Final (Rojo) al final de la trayectoria
    ax.arrow(x[-1], y[-1], 0, v_f * 0.5, head_width=0.2, head_length=abs(v_f)*0.05, fc='red', ec='red', label='Vf')
    plt.text(x[-1] + 0.2, y[-1] - 2, r'$v_f$', color='red', fontsize=12, fontweight='bold')

    # Vector Gravedad (Solo indicativo)
    plt.text(4, d_i/2, f'g = {g} m/s²', fontsize=14, color='green')
    ax.arrow(4.5, d_i/2 + 2, 0, -4, head_width=0.1, color='green')

    # Configuración del gráfico
    ax.set_ylim(0, h_max * 1.2) # Dar un poco de aire arriba
    ax.set_xlim(-2.5, 6)
    ax.set_ylabel("Altura (m)")
    ax.set_xlabel("Distancia horizontal (Simulada)")
    ax.axhline(0, color='black', linewidth=1) # Suelo
    ax.grid(True, alpha=0.3, linestyle=':')
    ax.legend(loc='upper right')
    
    st.pyplot(fig)

with col2:
    st.subheader("Resultados Numéricos")
    st.metric("Gravedad Seleccionada (g)", f"{g} m/s²")
    st.metric("Tiempo Total de Vuelo (t)", f"{t_total:.2f} s")
    st.metric("Velocidad Final de Impacto (vf)", f"{v_f:.2f} m/s")
    st.metric("Altura Máxima Alcanzada", f"{h_max:.2f} m")
    
    st.divider()
    st.markdown("### Ecuaciones Utilizadas")
    st.latex(r"y(t) = d_i + v_i t - \frac{1}{2}g t^2")
    st.latex(r"v(t) = v_i - g t")
    st.latex(r"v_f = \sqrt{v_i^2 + 2 g d_i}")

# --- 5. TABLA DE DATOS (OPCIONAL) ---
with st.expander("Ver tabla de datos paso a paso (Tiempo vs Altura)"):
    import pandas as pd
    # Creamos menos puntos para la tabla para que sea legible
    t_tabla = np.linspace(0, t_total, 20)
    y_tabla = d_i + v_i * t_tabla - 0.5 * g * t_tabla**2
    v_tabla = v_i - g * t_tabla
    
    df = pd.DataFrame({
        "Tiempo (s)": t_tabla,
        "Altura (m)": y_tabla,
        "Velocidad (m/s)": v_tabla
    })
    st.dataframe(df)
