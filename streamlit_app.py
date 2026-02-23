import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- FIZIKAI SZÁMÍTÁSOK ---
R = 8.314  
def calc_P(V, T, n): return (n * R * T) / V
def calc_V(P, T, n): return (n * R * T) / P
def calc_T(P, V, n): return (P * V) / (n * R)

st.set_page_config(layout="wide", page_title="Gáz Szimulátor")

# --- MEMÓRIA (Session State) ---
if 'V' not in st.session_state:
    st.session_state.V = 0.0246
    st.session_state.P = 101325.0
    st.session_state.T = 300.0
    st.session_state.n = 1.0
    st.session_state.history = {'V': [0.0246], 'P': [101325.0], 'T': [300.0]}

# --- OLDALSÁV (Vezérlők) ---
with st.sidebar:
    st.header("⚙️ Beállítások")
    mode = st.radio("Állapotváltozás típusa:", 
                   ('Szabad', 'Izobár (p állandó)', 'Izoterm (T állandó)', 'Izochor (V állandó)'))
    
    st.markdown("---")
    new_n = st.number_input("n [mol]", 0.1, 5.0, float(st.session_state.n), 0.1)
    
    # Csúszka + Mező szinkronizált kezelése
    st.write("**V [m³]**")
    v_val = st.slider("V_slider", 0.005, 0.065, float(st.session_state.V), 0.001, label_visibility="collapsed")
    v_val = st.number_input("V_num", 0.005, 0.065, v_val, format="%.4f", label_visibility="collapsed")
    
    st.write("**p [10⁵ Pa]**")
    p_val_105 = st.slider("P_slider", 0.4, 2.8, float(st.session_state.P/1e5), 0.1, label_visibility="collapsed")
    p_val_105 = st.number_input("P_num", 0.4, 2.8, p_val_105, format="%.2f", label_visibility="collapsed")
    
    st.write("**T [K]**")
    t_val = st.slider("T_slider", 100.0, 750.0, float(st.session_state.T), 1.0, label_visibility="collapsed")
    t_val = st.number_input("T_num", 100.0, 750.0, t_val, format="%.1f", label_visibility="collapsed")
    
    if st.button("🗑️ Grafikon törlése", use_container_width=True):
        st.session_state.history = {'V': [st.session_state.V], 'P': [st.session_state.P], 'T': [st.session_state.T]}
        st.rerun()

# --- FIZIKAI LOGIKA ---
temp_V, temp_P, temp_T = v_val, p_val_105 * 1e5, t_val
is_drawing = True

# Változás figyelése
v_ch = not np.isclose(temp_V, st.session_state.V)
p_ch = not np.isclose(temp_P, st.session_state.P)
t_ch = not np.isclose(temp_T, st.session_state.T)

if mode == 'Izobár (p állandó)':
    if p_ch: is_drawing = False; temp_T = calc_T(temp_P, temp_V, new_n)
    else: temp_T = np.clip(calc_T(st.session_state.P, temp_V, new_n), 100, 750); temp_P = st.session_state.P
elif mode == 'Izoterm (T állandó)':
    if t_ch: is_drawing = False; temp_P = calc_P(temp_V, temp_T, new_n)
    else: temp_P = np.clip(calc_P(temp_V, st.session_state.T, new_n), 30000, 300000); temp_T = st.session_state.T
elif mode == 'Izochor (V állandó)':
    if v_ch: is_drawing = False; temp_P = calc_P(temp_V, temp_T, new_n)
    else: temp_P = np.clip(calc_P(st.session_state.V, temp_T, new_n), 30000, 300000); temp_V = st.session_state.V
else:
    temp_P = calc_P(temp_V, temp_T, new_n)

# Frissítés
if v_ch or p_ch or t_ch or new_n != st.session_state.n:
    if not is_drawing or new_n != st.session_state.n:
        st.session_state.history = {'V': [temp_V], 'P': [temp_P], 'T': [temp_T]}
    else:
        st.session_state.history['V'].append(temp_V)
        st.session_state.history['P'].append(temp_P)
        st.session_state.history['T'].append(temp_T)
    st.session_state.V, st.session_state.P, st.session_state.T, st.session_state.n = temp_V, temp_P, temp_T, new_n

# --- MEGJELENÍTÉS ---
st.title("🌡️ Gáz Állapotváltozás Szimulátor")
m1, m2, m3 = st.columns(3)
m1.metric("V térfogat", f"{st.session_state.V:.4f} m³")
m2.metric("p nyomás", f"{st.session_state.P/1e5:.2f} · 10⁵ Pa")
m3.metric("T hőmérséklet", f"{st.session_state.T:.1f} K")

fig, axes = plt.subplots(2, 2, figsize=(10, 7))
(ax_pv, ax_vt), (ax_pt, ax_pist) = axes
h = st.session_state.history

def plot_it(ax, x, y, xl, yl, title, xlim, ylim, sc_y=1):
    ax.plot(np.array(x), np.array(y)*sc_y, 'b-', alpha=0.6, lw=2)
    ax.plot(x[-1], y[-1]*sc_y, 'ro', markersize=6)
    ax.set_xlabel(xl, fontsize=8); ax.set_ylabel(yl, fontsize=8)
    ax.set_title(title, fontsize=10, fontweight='bold')
    ax.set_xlim(xlim); ax.set_ylim(ylim); ax.grid(True, ls=':', alpha=0.4)

plot_it(ax_pv, h['V'], h['P'], "V [m³]", "p [10⁵ Pa]", "p-V diagram", (0.005, 0.07), (0.3, 2.9), sc_y=1/1e5)
plot_it(ax_vt, h['T'], h['V'], "T [K]", "V [m³]", "V-T diagram", (100, 750), (0.005, 0.07))
plot_it(ax_pt, h['T'], h['P'], "T [K]", "p [10⁵ Pa]", "p-T diagram", (100, 750), (0.3, 2.9), sc_y=1/1e5)

# Dugattyú rajzolása
ax_pist.set_xlim(0, 0.08); ax_pist.set_ylim(-0.02, 0.02); ax_pist.axis('off')
ax_pist.plot([0, 0.06, 0.06, 0], [0.015, 0.015, -0.015, -0.015], 'k-', lw=2)
ax_pist.add_patch(plt.Rectangle((0, -0.015), st.session_state.V, 0.03, color='skyblue', alpha=0.4))
ax_pist.axvline(st.session_state.V, ymin=0.3, ymax=0.7, color='black', lw=4)
# JAVÍTOTT DUGATTYÚRÚD
ax_pist.plot([st.session_state.V, st.session_state.V + 0.025], [0, 0], color='gray', lw=6)
# HŐMÉRŐ
ax_pist.plot([0.07, 0.07], [-0.01, 0.01], 'k-', lw=1.5)
ax_pist.plot([0.07, 0.07], [-0.01, (st.session_state.T/750)*0.02 - 0.01], 'r-', lw=6)

plt.tight_layout()
st.pyplot(fig)
