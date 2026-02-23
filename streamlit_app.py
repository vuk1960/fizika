import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- FIZIKAI ÁLLANDÓK ---
R = 8.314  

def calc_P(V, T, n): return (n * R * T) / V
def calc_V(P, T, n): return (n * R * T) / P
def calc_T(P, V, n): return (P * V) / (n * R)

st.set_page_config(layout="wide", page_title="Gáz Állapotváltozás Szimulátor")

# --- OLDALSÁV (VEZÉRLÉS) ---
st.sidebar.header("⚙️ Beállítások")

# Mód választó
mode = st.sidebar.radio(
    "Válassz állapotváltozást:",
    ('Szabad', 'Izobár (p állandó)', 'Izoterm (T állandó)', 'Izochor (V állandó)')
)

# Adatbevitel
n_mol = st.sidebar.number_input("Anyagmennyiség (n [mol])", 0.1, 5.0, 1.0, 0.1)

# Alapértékek inicializálása a session_state-ben (hogy ne vesszenek el frissítéskor)
if 'h_V' not in st.session_state:
    st.session_state.h_V, st.session_state.h_P, st.session_state.h_T = [0.0246], [101325.0], [300.0]

# Csúszkák és Beviteli mezők
col1, col2 = st.sidebar.columns(2)
v_in = col1.number_input("V [m³]", 0.005, 0.06, st.session_state.h_V[-1], format="%.4f")
p_in = col2.number_input("p [Pa]", 40000, 250000, int(st.session_state.h_P[-1]))
t_in = st.sidebar.slider("T [Hőmérséklet K]", 150, 650, int(st.session_state.h_T[-1]))

# Logika a módokhoz
curr_V, curr_P, curr_T = v_in, p_in, t_in

if mode == 'Izobár (p állandó)':
    curr_P = p_in
    curr_T = calc_T(curr_P, curr_V, n_mol)
elif mode == 'Izoterm (T állandó)':
    curr_T = t_in
    curr_P = calc_P(curr_V, curr_T, n_mol)
elif mode == 'Izochor (V állandó)':
    curr_V = v_in
    curr_P = calc_P(curr_V, curr_T, n_mol)
else:
    curr_P = calc_P(curr_V, curr_T, n_mol)

# Pont hozzáadása a grafikonhoz
if st.sidebar.button("📍 Pont rögzítése / Rajzolás"):
    st.session_state.h_V.append(curr_V)
    st.session_state.h_P.append(curr_P)
    st.session_state.h_T.append(curr_T)

if st.sidebar.button("🗑️ Grafikon törlése"):
    st.session_state.h_V, st.session_state.h_P, st.session_state.h_T = [curr_V], [curr_P], [curr_T]

# --- VIZUALIZÁCIÓ ---
st.title("🌡️ Interaktív Gázállapot-szimulátor")
st.write(f"**Aktuális állapot:** V = {curr_V:.4f} m³, p = {curr_P:.0f} Pa, T = {curr_T:.1f} K")

fig, axes = plt.subplots(2, 2, figsize=(12, 8))
(ax_pv, ax_vt), (ax_pt, ax_pist) = axes

# Diagramok rajzolása
def draw_plot(ax, x, y, xl, yl, title, xlim, ylim):
    ax.plot(x, y, 'b-', lw=2, alpha=0.6)
    ax.plot(x[-1], y[-1], 'ro', markersize=10)
    ax.set_xlabel(xl); ax.set_ylabel(yl); ax.set_title(title)
    ax.set_xlim(xlim); ax.set_ylim(ylim)
    ax.grid(True, linestyle=':')

draw_plot(ax_pv, st.session_state.h_V, st.session_state.h_P, "V [m³]", "p [Pa]", "p-V Diagram", (0.005, 0.065), (30000, 260000))
draw_plot(ax_vt, st.session_state.h_T, st.session_state.h_V, "T [K]", "V [m³]", "V-T Diagram", (140, 660), (0.005, 0.065))
draw_plot(ax_pt, st.session_state.h_T, st.session_state.h_P, "T [K]", "p [Pa]", "p-T Diagram", (140, 660), (30000, 260000))

# Dugattyú grafika
ax_pist.set_xlim(0, 0.08); ax_pist.set_ylim(-0.02, 0.02); ax_pist.axis('off')
ax_pist.plot([0, 0.06, 0.06, 0], [0.015, 0.015, -0.015, -0.015], 'k-', lw=4) 
ax_pist.add_patch(plt.Rectangle((0, -0.015), curr_V, 0.03, color='skyblue', alpha=0.5))
ax_pist.axvline(curr_V, ymin=0.3, ymax=0.7, color='black', lw=6)
ax_pist.plot([curr_V, curr_V + 0.03], [0, 0], color='gray', lw=8) # Rúd
# Hőmérő
ax_pist.plot([0.075, 0.075], [-0.015, 0.015], 'k-', lw=2)
ax_pist.plot([0.075, 0.075], [-0.015, (curr_T/650)*0.03 - 0.015], 'r-', lw=10)

st.pyplot(fig)
