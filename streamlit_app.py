import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- FIZIKAI ÁLLANDÓK ---
R = 8.314  

def calc_P(V, T, n): return (n * R * T) / V
def calc_V(P, T, n): return (n * R * T) / P
def calc_T(P, V, n): return (P * V) / (n * R)

st.set_page_config(layout="wide", page_title="Gáz Szimulátor Pro")

# --- HATÁRÉRTÉKEK ---
V_MIN, V_MAX = 0.005, 0.070
P_MIN_PA, P_MAX_PA = 30000.0, 300000.0 
T_MIN, T_MAX = 100.0, 800.0      

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

new_n = st.sidebar.number_input("n [mol]", 0.1, 5.0, float(st.session_state.n), 0.1)

st.sidebar.markdown("---")

# Csúszkák és számmezők (Egymás alatt, de logikai kapcsolatban)
v_sl = st.sidebar.slider("V [m³]", V_MIN, V_MAX, float(st.session_state.V), 0.001)
p_sl_105 = st.sidebar.slider("p [10⁵ Pa]", P_MIN_PA/1e5, P_MAX_PA/1e5, float(st.session_state.P/1e5), 0.1)
t_sl = st.sidebar.slider("T [K]", T_MIN, T_MAX, float(st.session_state.T), 1.0)

# Értékek kinyerése
temp_V = v_sl
temp_P_Pa = p_sl_105 * 1e5
temp_T = t_sl

# --- RAJZOLÁSI LOGIKA ---
is_drawing = True

# Ha n változik, töröljük a múltat
if not np.isclose(new_n, st.session_state.n):
    st.session_state.n = new_n
    is_drawing = False

if mode == 'Izobár (p állandó)':
    # Ha a nyomást állítod (alappont), ne rajzoljon
    if not np.isclose(temp_P_Pa, st.session_state.P):
        is_drawing = False
    temp_T = np.clip(calc_T(temp_P_Pa, temp_V, st.session_state.n), T_MIN, T_MAX)
    
elif mode == 'Izoterm (T állandó)':
    # Ha a hőmérsékletet állítod, ne rajzoljon
    if not np.isclose(temp_T, st.session_state.T):
        is_drawing = False
    temp_P_Pa = np.clip(calc_P(temp_V, temp_T, st.session_state.n), P_MIN_PA, P_MAX_PA)

elif mode == 'Izochor (V állandó)':
    # Ha a térfogatot állítod, ne rajzoljon
    if not np.isclose(temp_V, st.session_state.V):
        is_drawing = False
    temp_P_Pa = np.clip(calc_P(temp_V, temp_T, st.session_state.n), P_MIN_PA, P_MAX_PA)

else: # Szabad mód
    temp_P_Pa = np.clip(calc_P(temp_V, temp_T, st.session_state.n), P_MIN_PA, P_MAX_PA)

# --- ÁLLAPOT FRISSÍTÉSE ---
if not np.isclose(temp_V, st.session_state.V) or not np.isclose(temp_P_Pa, st.session_state.P) or not np.isclose(temp_T, st.session_state.T):
    if not is_drawing:
        # Alappont váltás: új lista indítása
        st.session_state.history = {'V': [temp_V], 'P': [temp_P_Pa], 'T': [temp_T]}
    else:
        # Folyamat rajzolása: pontok hozzáadása
        st.session_state.history['V'].append(temp_V)
        st.session_state.history['P'].append(temp_P_Pa)
        st.session_state.history['T'].append(temp_T)
    
    st.session_state.V = temp_V
    st.session_state.P = temp_P_Pa
    st.session_state.T = temp_T

if st.sidebar.button("🗑️ Grafikon törlése"):
    st.session_state.history = {'V': [st.session_state.V], 'P': [st.session_state.P], 'T': [st.session_state.T]}
    st.rerun()

# --- MEGJELENÍTÉS ---
st.title("🌡️ Gáz Állapotváltozás Szimulátor")
c1, c2, c3 = st.columns(3)
c1.metric("Térfogat (V)", f"{st.session_state.V:.4f} m³")
c2.metric("Nyomás (p)", f"{st.session_state.P/1e5:.2f} · 10⁵ Pa")
c3.metric("Hőmérséklet (T)", f"{st.session_state.T:.1f} K")

fig, axes = plt.subplots(2, 2, figsize=(12, 9))
(ax_pv, ax_vt), (ax_pt, ax_pist) = axes
h = st.session_state.history

def plot_it(ax, x, y, xl, yl, title, xlim, ylim, scale_x=1, scale_y=1):
    ax.plot(np.array(x)*scale_x, np.array(y)*scale_y, 'b-', alpha=0.6, lw=2.5)
    ax.plot(x[-1]*scale_x, y[-1]*scale_y, 'ro', markersize=8)
    ax.set_xlabel(xl); ax.set_ylabel(yl); ax.set_title(title, fontweight='bold')
    ax.set_xlim(xlim); ax.set_ylim(ylim); ax.grid(True, ls=':', alpha=0.6)

plot_it(ax_pv, h['V'], h['P'], "V [m³]", "p [10⁵ Pa]", "p-V diagram", (V_MIN, V_MAX), (P_MIN_PA/1e5, P_MAX_PA/1e5), scale_y=1/1e5)
plot_it(ax_vt, h['T'], h['V'], "T [K]", "V [m³]", "V-T diagram", (T_MIN, T_MAX), (V_MIN, V_MAX))
plot_it(ax_pt, h['T'], h['P'], "T [K]", "p [10⁵ Pa]", "p-T diagram", (T_MIN, T_MAX), (P_MIN_PA/1e5, P_MAX_PA/1e5), scale_y=1/1e5)

# --- DUGATTYÚ GRAFIKA ---
ax_pist.set_xlim(0, 0.08); ax_pist.set_ylim(-0.02, 0.02); ax_pist.axis('off')
ax_pist.plot([0, 0.06, 0.06, 0], [0.015, 0.015, -0.015, -0.015], 'k-', lw=3)
ax_pist.add_patch(plt.Rectangle((0, -0.015), st.session_state.V, 0.03, color='skyblue', alpha=0.4))
ax_pist.axvline(st.session_state.V, ymin=0.3, ymax=0.7, color='black', lw=6)
ax_pist.plot([st.session_state.V, st.session_state.V + 0.025], [0, 0], color='gray', lw=10)
ax_pist.plot([0.07, 0.07], [-0.01, 0.01], 'k-', lw=2)
ax_pist.plot([0.07, 0.07], [-0.01, (st.session_state.T/T_MAX)*0.02 - 0.01], 'r-', lw=8)
ax_pist.text(0.07, 0.015, "T", ha='center', fontweight='bold')

plt.tight_layout()
st.pyplot(fig)
