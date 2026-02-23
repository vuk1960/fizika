import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- FIZIKAI ÁLLANDÓK ---
R = 8.314  

def calc_P(V, T, n): return (n * R * T) / V
def calc_V(P, T, n): return (n * R * T) / P
def calc_T(P, V, n): return (P * V) / (n * R)

st.set_page_config(layout="wide", page_title="Gáz Szimulátor")

# --- MEMÓRIA INICIALIZÁLÁSA (Session State) ---
if 'V' not in st.session_state:
    st.session_state.V = 0.0246
    st.session_state.P = 101325.0
    st.session_state.T = 300.0
    st.session_state.n = 1.0
    st.session_state.history = {'V': [0.0246], 'P': [101325.0], 'T': [300.0]}

# --- OLDALSÁV (VEZÉRLÉS) ---
st.sidebar.header("⚙️ Beállítások")

mode = st.sidebar.radio("Állapotváltozás:", 
    ('Szabad', 'Izobár (p állandó)', 'Izoterm (T állandó)', 'Izochor (V állandó)'))

# Mólszám (mindig aktív)
n_val = st.sidebar.number_input("n [mol]", 0.1, 5.0, st.session_state.n, 0.1)
if n_val != st.session_state.n:
    st.session_state.n = n_val
    st.session_state.P = calc_P(st.session_state.V, st.session_state.T, st.session_state.n)

# CSÚSZKÁK ÉS MEZŐK SZINKRONIZÁLÁSA
def on_v_change():
    st.session_state.V = st.session_state.v_slider
    update_physics('V')

def on_p_change():
    st.session_state.P = st.session_state.p_slider * 1e5
    update_physics('P')

def on_t_change():
    st.session_state.T = st.session_state.t_slider
    update_physics('T')

def update_physics(triggered):
    V, P, T, n = st.session_state.V, st.session_state.P, st.session_state.T, st.session_state.n
    if mode == 'Izobár (p állandó)':
        if triggered == 'P': st.session_state.T = calc_T(P, V, n); reset_hist()
        else: st.session_state.T = calc_T(P, V, n); add_hist()
    elif mode == 'Izoterm (T állandó)':
        if triggered == 'T': st.session_state.P = calc_P(V, T, n); reset_hist()
        else: st.session_state.P = calc_P(V, T, n); add_hist()
    elif mode == 'Izochor (V állandó)':
        if triggered == 'V': st.session_state.P = calc_P(V, T, n); reset_hist()
        else: st.session_state.P = calc_P(V, T, n); add_hist()
    else:
        st.session_state.P = calc_P(V, T, n); add_hist()

def add_hist():
    st.session_state.history['V'].append(st.session_state.V)
    st.session_state.history['P'].append(st.session_state.P)
    st.session_state.history['T'].append(st.session_state.T)

def reset_hist():
    st.session_state.history = {'V': [st.session_state.V], 'P': [st.session_state.P], 'T': [st.session_state.T]}

# Megjelenítés
st.sidebar.slider("V [m³]", 0.008, 0.06, st.session_state.V, 0.001, key='v_slider', on_change=on_v_change)
st.sidebar.slider("p [10⁵ Pa]", 0.4, 2.5, st.session_state.P/1e5, 0.1, key='p_slider', on_change=on_p_change)
st.sidebar.slider("T [K]", 150, 650, float(st.session_state.T), 1.0, key='t_slider', on_change=on_t_change)

if st.sidebar.button("🗑️ Grafikon törlése"):
    reset_hist()

# --- FŐOLDAL ---
st.title("🌡️ Interaktív Gázállapot Szimulátor")
col_vals = st.columns(3)
col_vals[0].metric("Térfogat (V)", f"{st.session_state.V:.4f} m³")
col_vals[1].metric("Nyomás (p)", f"{st.session_state.P:.0f} Pa")
col_vals[2].metric("Hőmérséklet (T)", f"{st.session_state.T:.1f} K")

# Grafikonok
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
(ax_pv, ax_vt), (ax_pt, ax_pist) = axes

def plot_setup(ax, x, y, xl, yl, title, xlim, ylim):
    ax.plot(x, y, 'b-', lw=2, alpha=0.5)
    ax.plot(x[-1], y[-1], 'ro', markersize=8)
    ax.set_xlabel(xl); ax.set_ylabel(yl); ax.set_title(title)
    ax.set_xlim(xlim); ax.set_ylim(ylim); ax.grid(True, ls=':')

h = st.session_state.history
plot_setup(ax_pv, h['V'], h['P'], "V [m³]", "p [Pa]", "p-V", (0.005, 0.065), (30000, 260000))
plot_setup(ax_vt, h['T'], h['V'], "T [K]", "V [m³]", "V-T", (140, 660), (0.005, 0.065))
plot_setup(ax_pt, h['T'], h['P'], "T [K]", "p [Pa]", "p-T", (140, 660), (30000, 260000))

# Dugattyú
ax_pist.set_xlim(0, 0.08); ax_pist.set_ylim(-0.02, 0.02); ax_pist.axis('off')
ax_pist.plot([0, 0.06, 0.06, 0], [0.015, 0.015, -0.015, -0.015], 'k-', lw=3)
ax_pist.add_patch(plt.Rectangle((0, -0.015), st.session_state.V, 0.03, color='skyblue', alpha=0.5))
ax_pist.axvline(st.session_state.V, ymin=0.3, ymax=0.7, color='black', lw=5)
ax_pist.plot([0.07, 0.07], [-0.01, 0.01], 'k-', lw=2)
ax_pist.plot([0.07, 0.07], [-0.01, (st.session_state.T/650)*0.02 - 0.01], 'r-', lw=8)

st.pyplot(fig)
