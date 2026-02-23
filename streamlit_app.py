import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- FIZIKAI ÁLLANDÓK ---
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

# --- OLDALSÁV VEZÉRLÉS ---
st.sidebar.header("⚙️ Beállítások")

mode = st.sidebar.radio("Állapotváltozás típusa:", 
    ('Szabad', 'Izobár (p állandó)', 'Izoterm (T állandó)', 'Izochor (V állandó)'))

# Értékek beolvasása a csúszkákról
n_val = st.sidebar.number_input("n [mol]", 0.1, 5.0, float(st.session_state.n), 0.1)
v_slider = st.sidebar.slider("V [m³]", 0.008, 0.060, float(st.session_state.V), 0.001)
p_slider = st.sidebar.slider("p [10⁵ Pa]", 0.4, 2.5, float(st.session_state.P/1e5), 0.1)
t_slider = st.sidebar.slider("T [K]", 150.0, 650.0, float(st.session_state.T), 1.0)

# FIZIKAI LOGIKA FRISSÍTÉSE
new_V, new_P, new_T = v_slider, p_slider * 1e5, t_slider

# Mi változott? (Hogy tudjuk, mit kell újraszámolni)
if n_val != st.session_state.n:
    st.session_state.n = n_val
    new_P = calc_P(new_V, new_T, n_val)

if mode == 'Izobár (p állandó)':
    # Ha a P-t bántjuk -> Alappont váltás (törlés)
    if not np.isclose(new_P, st.session_state.P):
        st.session_state.history = {'V': [new_V], 'P': [new_P], 'T': [calc_T(new_P, new_V, n_val)]}
    new_T = calc_T(new_P, new_V, n_val)
elif mode == 'Izoterm (T állandó)':
    if not np.isclose(new_T, st.session_state.T):
        st.session_state.history = {'V': [new_V], 'P': [new_P], 'T': [new_T]}
    new_P = calc_P(new_V, new_T, n_val)
elif mode == 'Izochor (V állandó)':
    if not np.isclose(new_V, st.session_state.V):
        st.session_state.history = {'V': [new_V], 'P': [new_P], 'T': [new_T]}
    new_P = calc_P(new_V, new_T, n_val)
else:
    new_P = calc_P(new_V, new_T, n_val)

# Előzmények mentése (ha változott valami)
if new_V != st.session_state.V or new_P != st.session_state.P or new_T != st.session_state.T:
    st.session_state.V, st.session_state.P, st.session_state.T = new_V, new_P, new_T
    st.session_state.history['V'].append(new_V)
    st.session_state.history['P'].append(new_P)
    st.session_state.history['T'].append(new_T)

if st.sidebar.button("🗑️ Grafikon törlése"):
    st.session_state.history = {'V': [new_V], 'P': [new_P], 'T': [new_T]}
    st.rerun()

# --- MEGJELENÍTÉS ---
st.title("🌡️ Gáz Állapotváltozás Szimulátor")
c1, c2, c3 = st.columns(3)
c1.metric("V [m³]", f"{st.session_state.V:.4f}")
c2.metric("p [Pa]", f"{st.session_state.P:.0f}")
c3.metric("T [K]", f"{st.session_state.T:.1f}")

fig, axes = plt.subplots(2, 2, figsize=(12, 8))
(ax_pv, ax_vt), (ax_pt, ax_pist) = axes
h = st.session_state.history

def plot_it(ax, x, y, xl, yl, title, xlim, ylim):
    ax.plot(x, y, 'b-', alpha=0.4, lw=2)
    ax.plot(x[-1], y[-1], 'ro')
    ax.set_xlabel(xl); ax.set_ylabel(yl); ax.set_title(title)
    ax.set_xlim(xlim); ax.set_ylim(ylim); ax.grid(True, ls=':')

plot_it(ax_pv, h['V'], h['P'], "V", "p", "p-V", (0.005, 0.065), (30000, 260000))
plot_it(ax_vt, h['T'], h['V'], "T", "V", "V-T", (140, 660), (0.005, 0.065))
plot_it(ax_pt, h['T'], h['P'], "T", "p", "p-T", (140, 660), (30000, 260000))

# Dugattyú
ax_pist.set_xlim(0, 0.08); ax_pist.set_ylim(-0.02, 0.02); ax_pist.axis('off')
ax_pist.plot([0, 0.06, 0.06, 0], [0.015, 0.015, -0.015, -0.015], 'k-', lw=3)
ax_pist.add_patch(plt.Rectangle((0, -0.015), st.session_state.V, 0.03, color='skyblue', alpha=0.5))
ax_pist.axvline(st.session_state.V, ymin=0.3, ymax=0.7, color='black', lw=5)
ax_pist.plot([0.07, 0.07], [-0.01, 0.01], 'k-', lw=2)
ax_pist.plot([0.07, 0.07], [-0.01, (st.session_state.T/660)*0.02 - 0.01], 'r-', lw=8)

st.pyplot(fig)
