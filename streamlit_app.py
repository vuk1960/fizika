import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- FIZIKAI SZÁMÍTÁSOK ---
R = 8.314  
def calc_P(V, T, n): return (n * R * T) / V
def calc_V(P, T, n): return (n * R * T) / P
def calc_T(P, V, n): return (P * V) / (n * R)

st.set_page_config(layout="wide", page_title="Gáz Szimulátor")

# --- MEMÓRIA ---
if 'V' not in st.session_state:
    st.session_state.V = 0.0246
    st.session_state.P = 101325.0
    st.session_state.T = 300.0
    st.session_state.n = 1.0
    st.session_state.history = {'V': [0.0246], 'P': [101325.0], 'T': [300.0]}

st.title("🌡️ Interaktív Gázállapot Szimulátor")

# --- FŐ PANEL: DIAGRAMOK ---
c1, c2, c3 = st.columns(3)
c1.metric("Térfogat (V)", f"{st.session_state.V:.4f} m³")
c2.metric("Nyomás (p)", f"{st.session_state.P/1e5:.2f} · 10⁵ Pa")
c3.metric("Hőmérséklet (T)", f"{st.session_state.T:.1f} K")

fig, axes = plt.subplots(2, 2, figsize=(10, 6))
(ax_pv, ax_vt), (ax_pt, ax_pist) = axes
h = st.session_state.history

def plot_it(ax, x, y, xl, yl, title, xlim, ylim, sc_y=1):
    ax.plot(np.array(x), np.array(y)*sc_y, 'b-', alpha=0.6, lw=2)
    ax.plot(x[-1], y[-1]*sc_y, 'ro', markersize=6)
    ax.set_xlabel(xl, fontsize=8); ax.set_ylabel(yl, fontsize=8)
    ax.set_title(title, fontsize=9, fontweight='bold')
    ax.set_xlim(xlim); ax.set_ylim(ylim); ax.grid(True, ls=':', alpha=0.4)

plot_it(ax_pv, h['V'], h['P'], "V [m³]", "p [10⁵ Pa]", "p-V", (0.005, 0.065), (0.4, 2.8), sc_y=1/1e5)
plot_it(ax_vt, h['T'], h['V'], "T [K]", "V [m³]", "V-T", (100, 750), (0.005, 0.065))
plot_it(ax_pt, h['T'], h['P'], "T [K]", "p [10⁵ Pa]", "p-T", (100, 750), (0.4, 2.8), sc_y=1/1e5)

# Dugattyú
ax_pist.set_xlim(0, 0.08); ax_pist.set_ylim(-0.02, 0.02); ax_pist.axis('off')
ax_pist.plot([0, 0.06, 0.06, 0], [0.015, 0.015, -0.015, -0.015], 'k-', lw=2)
ax_pist.add_patch(plt.Rectangle((0, -0.015), st.session_state.V, 0.03, color='skyblue', alpha=0.4))
ax_pist.axvline(st.session_state.V, ymin=0.3, ymax=0.7, color='black', lw=4)
ax_pist.plot([st.session_state.V, st.session_state.V + 0.025], [0, 0], color='gray', lw=6)
ax_pist.plot([0.07, 0.07], [-0.01, 0.01], 'k-', lw=1.5)
ax_pist.plot([0.07, 0.07], [-0.01, (st.session_state.T/750)*0.02 - 0.01], 'r-', lw=6)

st.pyplot(fig)

# --- VEZÉRLŐK A DIAGRAMOK ALATT ---
st.write("---")
ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns([2, 1, 1, 1])

mode = ctrl_col1.radio("Állapotváltozás típusa:", ('Szabad', 'Izobár (p állandó)', 'Izoterm (T állandó)', 'Izochor (V állandó)'), horizontal=True)
new_n = ctrl_col1.number_input("n [mol]", 0.1, 5.0, float(st.session_state.n), 0.1)

# Beviteli mezők (ezek mozgatják a grafikont)
v_in = ctrl_col2.number_input("V [m³]", 0.005, 0.065, float(st.session_state.V), 0.001, format="%.4f")
p_in_105 = ctrl_col3.number_input("p [10⁵ Pa]", 0.4, 2.8, float(st.session_state.P/1e5), 0.1)
t_in = ctrl_col4.number_input("T [K]", 100.0, 750.0, float(st.session_state.T), 1.0)

# --- LOGIKA ---
temp_V, temp_P, temp_T = v_in, p_in_105 * 1e5, t_in
is_drawing = True

if mode == 'Izobár (p állandó)':
    if not np.isclose(temp_P, st.session_state.P): is_drawing = False
    temp_T = calc_T(temp_P, temp_V, new_n)
elif mode == 'Izoterm (T állandó)':
    if not np.isclose(temp_T, st.session_state.T): is_drawing = False
    temp_P = calc_P(temp_V, temp_T, new_n)
elif mode == 'Izochor (V állandó)':
    if not np.isclose(temp_V, st.session_state.V): is_drawing = False
    temp_P = calc_P(temp_V, temp_T, new_n)
else:
    temp_P = calc_P(temp_V, temp_T, new_n)

# Frissítés és Rajzolás
if not np.isclose(temp_V, st.session_state.V) or not np.isclose(temp_P, st.session_state.P) or not np.isclose(temp_T, st.session_state.T) or new_n != st.session_state.n:
    if not is_drawing or new_n != st.session_state.n:
        st.session_state.history = {'V': [temp_V], 'P': [temp_P], 'T': [temp_T]}
    else:
        st.session_state.history['V'].append(temp_V)
        st.session_state.history['P'].append(temp_P)
        st.session_state.history['T'].append(temp_T)
    
    st.session_state.V, st.session_state.P, st.session_state.T, st.session_state.n = temp_V, temp_P, temp_T, new_n
    st.rerun()

if st.button("🗑️ Grafikon törlése"):
    st.session_state.history = {'V': [st.session_state.V], 'P': [st.session_state.P], 'T': [st.session_state.T]}
    st.rerun()
