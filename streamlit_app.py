import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- FIZIKAI SZÁMÍTÁSOK ---
R = 8.314  
def calc_P(V, T, n): return (n * R * T) / V
def calc_V(P, T, n): return (n * R * T) / P
def calc_T(P, V, n): return (P * V) / (n * R)

st.set_page_config(layout="wide", page_title="Gáz Szimulátor Pro")

# --- HATÁRÉRTÉKEK ---
V_MIN, V_MAX = 0.005, 0.070
P_MIN_105, P_MAX_105 = 0.3, 3.0  # 10^5 Pa-ban
T_MIN, T_MAX = 100.0, 800.0      

# --- MEMÓRIA (Session State) ---
if 'V' not in st.session_state:
    st.session_state.V = 0.0246
    st.session_state.P_105 = 1.013
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
    
    # CSÚSZKÁK (Ezek az elsődlegesek)
    st.write("**V [m³]**")
    v_val = st.slider("V_slider", V_MIN, V_MAX, float(st.session_state.V), 0.001, label_visibility="collapsed")
    
    st.write("**p [10⁵ Pa]**")
    p_val_105 = st.slider("P_slider", P_MIN_105, P_MAX_105, float(st.session_state.P_105), 0.1, label_visibility="collapsed")
    
    st.write("**T [K]**")
    t_val = st.slider("T_slider", T_MIN, T_MAX, float(st.session_state.T), 1.0, label_visibility="collapsed")
    
    if st.button("🗑️ Grafikon törlése", use_container_width=True):
        st.session_state.history = {'V': [st.session_state.V], 'P': [st.session_state.P_105 * 1e5], 'T': [st.session_state.T]}
        st.rerun()

# --- FIZIKAI LOGIKA + HIBAVÉDELEM ---
temp_V, temp_P_105, temp_T = v_val, p_val_105, t_val
is_drawing = True

# Változás figyelése a memóriához képest
v_ch = not np.isclose(temp_V, st.session_state.V)
p_ch = not np.isclose(temp_P_105, st.session_state.P_105)
t_ch = not np.isclose(temp_T, st.session_state.T)

if mode == 'Izobár (p állandó)':
    if p_ch: is_drawing = False; temp_T = np.clip(calc_T(temp_P_105*1e5, temp_V, new_n), T_MIN, T_MAX)
    else: temp_T = np.clip(calc_T(st.session_state.P_105*1e5, temp_V, new_n), T_MIN, T_MAX); temp_P_105 = st.session_state.P_105
elif mode == 'Izoterm (T állandó)':
    if t_ch: is_drawing = False; temp_P_105 = np.clip(calc_P(temp_V, temp_T, new_n)/1e5, P_MIN_105, P_MAX_105)
    else: temp_P_105 = np.clip(calc_P(temp_V, st.session_state.T, new_n)/1e5, P_MIN_105, P_MAX_105); temp_T = st.session_state.T
elif mode == 'Izochor (V állandó)':
    if v_ch: is_drawing = False; temp_P_105 = np.clip(calc_P(temp_V, temp_T, new_n)/1e5, P_MIN_105, P_MAX_105)
    else: temp_P_105 = np.clip(calc_P(st.session_state.V, temp_T, new_n)/1e5, P_MIN_105, P_MAX_105); temp_V = st.session_state.V
else: # Szabad
    if v_ch or t_ch: temp_P_105 = np.clip(calc_P(temp_V, temp_T, new_n)/1e5, P_MIN_105, P_MAX_105)
    elif p_ch: temp_T = np.clip(calc_T(temp_P_105*1e5, temp_V, new_n), T_MIN, T_MAX)

# --- MEMÓRIA FRISSÍTÉSE ---
if v_ch or p_ch or t_ch or new_n != st.session_state.n:
    if not is_drawing or new_n != st.session_state.n:
        st.session_state.history = {'V': [temp_V], 'P': [temp_P_105*1e5], 'T': [temp_T]}
    else:
        st.session_state.history['V'].append(temp_V)
        st.session_state.history['P'].append(temp_P_105*1e5)
        st.session_state.history['T'].append(temp_T)
    st.session_state.V, st.session_state.P_105, st.session_state.T, st.session_state.n = temp_V, temp_P_105, temp_T, new_n
    st.rerun()

# --- MEGJELENÍTÉS ---
st.title("🌡️ Gáz Állapotváltozás Szimulátor")
m1, m2, m3 = st.columns(3)
m1.metric("V térfogat", f"{st.session_state.V:.4f} m³")
m2.metric("p nyomás", f"{st.session_state.P_105:.2f} · 10⁵ Pa")
m3.metric("T hőmérséklet", f"{st.session_state.T:.1f} K")

fig, axes = plt.subplots(2, 2, figsize=(10, 7))
(ax_pv, ax_vt), (ax_pt, ax_pist) = axes
h = st.session_state.history

def plot_it(ax, x, y, xl, yl, title, xlim, ylim, sc_y=1):
    ax.plot(np.array(x), np.array(y)*sc_y, 'b-', alpha=0.6, lw=2.5)
    ax.plot(x[-1], y[-1]*sc_y, 'ro', markersize=7)
    ax.set_xlabel(xl); ax.set_ylabel(yl); ax.set_title(title, fontweight='bold')
    ax.set_xlim(xlim); ax.set_ylim(ylim); ax.grid(True, ls=':', alpha=0.4)

plot_it(ax_pv, h['V'], h['P'], "V [m³]", "p [10⁵ Pa]", "p-V diagram", (V_MIN, V_MAX), (P_MIN_105, P_MAX_105), sc_y=1/1e5)
plot_it(ax_vt, h['T'], h['V'], "T [K]", "V [m³]", "V-T diagram", (T_MIN, T_MAX), (V_MIN, V_MAX))
plot_it(ax_pt, h['T'], h['P'], "T [K]", "p [10⁵ Pa]", "p-T diagram", (T_MIN, T_MAX), (P_MIN_105, P_MAX_105), sc_y=1/1e5)

# Dugattyú rajzolása
ax_pist.set_xlim(0, 0.08); ax_pist.set_ylim(-0.02, 0.02); ax_pist.axis('off')
ax_pist.plot([0, 0.06, 0.06, 0], [0.015, 0.015, -0.015, -0.015], 'k-', lw=3)
ax_pist.add_patch(plt.Rectangle((0, -0.015), st.session_state.V, 0.03, color='skyblue', alpha=0.4))
ax_pist.axvline(st.session_state.V, ymin=0.3, ymax=0.7, color='black', lw=6)
ax_pist.plot([st.session_state.V, st.session_state.V + 0.025], [0, 0], color='gray', lw=8)
ax_pist.plot([0.07, 0.07], [-0.01, 0.01], 'k-', lw=2)
ax_pist.plot([0.07, 0.07], [-0.01, (st.session_state.T/T_MAX)*0.02 - 0.01], 'r-', lw=8)
ax_pist.text(0.07, 0.015, "T", ha='center', fontweight='bold')

plt.tight_layout()
st.pyplot(fig)
