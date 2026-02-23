import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- FIZIKAI ÁLLANDÓK ---
R = 8.314  

def calc_P(V, T, n): return (n * R * T) / V
def calc_V(P, T, n): return (n * R * T) / P
def calc_T(P, V, n): return (P * V) / (n * R)

st.set_page_config(layout="wide", page_title="Gáz Szimulátor Pro")

# --- MEMÓRIA (Session State) ---
if 'V' not in st.session_state:
    st.session_state.V = 0.0246
    st.session_state.P = 101325.0
    st.session_state.T = 300.0
    st.session_state.n = 1.0
    st.session_state.history = {'V': [0.0246], 'P': [101325.0], 'T': [300.0]}

# --- OLDALSÁV VEZÉRLÉS ---
st.sidebar.header("⚙️ Beállítások")

mode = st.sidebar.radio("Állapotváltozás típusa:", 
    ('Szabad', 'Izobár (p állandó)', 'Izoterm (T állandó)', 'Izochor (V állandó)'))

# Mólszám (csak mező)
new_n = st.sidebar.number_input("n [mol]", 0.1, 5.0, float(st.session_state.n), 0.1)

# V, P, T kezelése (Csúszka + Mező párosítás)
st.sidebar.markdown("---")
# Térfogat
st.sidebar.label = "Térfogat (V)"
col_v1, col_v2 = st.sidebar.columns([3, 2])
v_sl = col_v1.slider("V [m³]", 0.008, 0.060, float(st.session_state.V), 0.001, label_visibility="collapsed")
v_num = col_v2.number_input("V [m³]", 0.008, 0.060, v_sl, format="%.4f", label_visibility="collapsed")

# Nyomás (10^5 skálázás)
st.sidebar.label = "Nyomás (p)"
col_p1, col_p2 = st.sidebar.columns([3, 2])
p_sl = col_p1.slider("p [10⁵ Pa]", 0.4, 2.5, float(st.session_state.P/1e5), 0.1, label_visibility="collapsed")
p_num = col_v2.number_input("p [Pa]", 40000.0, 250000.0, p_sl*100000.0, step=100.0, label_visibility="collapsed")

# Hőmérséklet
st.sidebar.label = "Hőmérséklet (T)"
col_t1, col_t2 = st.sidebar.columns([3, 2])
t_sl = col_t1.slider("T [K]", 150.0, 650.0, float(st.session_state.T), 1.0, label_visibility="collapsed")
t_num = col_t2.number_input("T [K]", 150.0, 650.0, t_sl, step=1.0, label_visibility="collapsed")

# Értékek összefésülése (prioritás a számmezőnek, ha változott)
temp_V, temp_P, temp_T = v_num, p_num, t_num

# FIZIKAI LOGIKA
if new_n != st.session_state.n:
    st.session_state.n = new_n
    temp_P = calc_P(temp_V, temp_T, new_n)

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

# Memória frissítése
if not np.isclose(temp_V, st.session_state.V) or not np.isclose(temp_P, st.session_state.P) or not np.isclose(temp_T, st.session_state.T):
    if not is_drawing:
        st.session_state.history = {'V': [temp_V], 'P': [temp_P], 'T': [temp_T]}
    else:
        st.session_state.history['V'].append(temp_V)
        st.session_state.history['P'].append(temp_P)
        st.session_state.history['T'].append(temp_T)
    st.session_state.V, st.session_state.P, st.session_state.T = temp_V, temp_P, temp_T

if st.sidebar.button("🗑️ Grafikon törlése"):
    st.session_state.history = {'V': [temp_V], 'P': [temp_P], 'T': [temp_T]}
    st.rerun()

# --- MEGJELENÍTÉS ---
st.title("🌡️ Gáz Állapotváltozás Szimulátor")
c1, c2, c3 = st.columns(3)
c1.metric("Térfogat (V)", f"{st.session_state.V:.4f} m³")
c2.metric("Nyomás (p)", f"{st.session_state.P:.0f} Pa")
c3.metric("Hőmérséklet (T)", f"{st.session_state.T:.1f} K")

fig, axes = plt.subplots(2, 2, figsize=(12, 9))
(ax_pv, ax_vt), (ax_pt, ax_pist) = axes
h = st.session_state.history

def plot_it(ax, x, y, xl, yl, title, xlim, ylim):
    ax.plot(x, y, 'b-', alpha=0.5, lw=2.5)
    ax.plot(x[-1], y[-1], 'ro', markersize=8)
    ax.set_xlabel(xl, fontsize=10); ax.set_ylabel(yl, fontsize=10); ax.set_title(title, fontweight='bold')
    ax.set_xlim(xlim); ax.set_ylim(ylim); ax.grid(True, ls=':', alpha=0.6)

plot_it(ax_pv, h['V'], h['P'], "V [m³]", "p [Pa]", "Nyomás - Térfogat (p-V)", (0.005, 0.065), (30000, 260000))
plot_it(ax_vt, h['T'], h['V'], "T [K]", "V [m³]", "Térfogat - Hőmérséklet (V-T)", (140, 660), (0.005, 0.065))
plot_it(ax_pt, h['T'], h['P'], "T [K]", "p [Pa]", "Nyomás - Hőmérséklet (p-T)", (140, 660), (30000, 260000))

# Dugattyú (Javított grafika)
ax_pist.set_xlim(0, 0.08); ax_pist.set_ylim(-0.02, 0.02); ax_pist.axis('off')
# Hengerfalak
ax_pist.plot([0, 0.06, 0.06, 0], [0.015, 0.015, -0.015, -0.015], 'k-', lw=3)
# Gáz (skyblue)
ax_pist.add_patch(plt.Rectangle((0, -0.015), st.session_state.V, 0.03, color='skyblue', alpha=0.4))
# Dugattyúfej
ax_pist.axvline(st.session_state.V, ymin=0.3, ymax=0.7, color='black', lw=6)
# Dugattyúrúd (vízszintes)
ax_pist.plot([st.session_state.V, st.session_state.V + 0.025], [0, 0], color='gray', lw=10)
# Hőmérő (piros higany)
ax_pist.plot([0.07, 0.07], [-0.01, 0.01], 'k-', lw=2)
ax_pist.plot([0.07, 0.07], [-0.01, (st.session_state.T/660)*0.02 - 0.01], 'r-', lw=8)
ax_pist.text(0.07, 0.015, "T", ha='center', fontsize=10, fontweight='bold')

plt.tight_layout()
st.pyplot(fig)
