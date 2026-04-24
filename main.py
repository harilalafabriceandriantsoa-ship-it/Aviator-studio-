import streamlit as st
import hashlib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
from pathlib import Path

# ================= CONFIGURATION =================
st.set_page_config(page_title="AVIATOR ANDR V1", layout="wide")

# ================= PERSISTENCE (Data Saving) =================
try:
    DATA_DIR = Path(__file__).parent / "aviator_andr_data"
except:
    DATA_DIR = Path.cwd() / "aviator_andr_data"
DATA_DIR.mkdir(exist_ok=True)
HISTORY_FILE = DATA_DIR / "history_v1.json"

def save_data(data):
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except: pass

def load_data():
    try:
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
    except: pass
    return []

# ================= CSS PREMIUM ULTRA STYLÉ =================
# ... (existing CSS code) ...

# ================= SESSION STATE =================
if "auth" not in st.session_state:
    st.session_state.auth = False
if "history" not in st.session_state:
    st.session_state.history = load_data()
if "last_res" not in st.session_state:
    st.session_state.last_res = None

# ================= LOGIN SYSTEM =================
if not st.session_state.auth:
    st.markdown("<h1 class='main-title'>AVIATOR ANDR V1</h1>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 1.2, 1])
    with col_b:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        pw = st.text_input("🔑 PASSWORD", type="password", placeholder="AVIATOR2026")
        if st.button("ACTIVATE SYSTEM", use_container_width=True):
            if pw == "AVIATOR2026":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Access Denied")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ================= ENGINE V1 (250K SIMS) =================
def run_engine_andr(sha5, heure, last_cote):
    sha5 = sha5.strip().lower()[:5]
    combined = f"{sha5}{heure}{last_cote}"
    h_hex = hashlib.sha256(combined.encode()).hexdigest()
    seed = int(h_hex[:12], 16)
    np.random.seed(seed % (2**32))
    
    # Logic simulation
    base = 2.10 - (last_cote * 0.005) if last_cote > 2 else 2.18
    sims = np.random.lognormal(np.log(base), 0.22, 250_000)
    
    prob_x3 = round(float(np.mean(sims >= 3.0)) * 100, 2)
    strength = round(max(30, min(99, prob_x3 * 1.8)), 2)
    
    # Entry time
    try:
        h, m = map(int, heure.split(':'))
        base_t = datetime.now().replace(hour=h, minute=m, second=0)
    except:
        st.error("Veuillez entrer l'heure au format HH:MM")
        return None
    
    # Vérifier si l'heure est dans le futur
    if base_t < datetime.now():
        base_t = base_t.replace(day=base_t.day + 1)
    
    shift = 45 + (seed % 35)
    entry_t = (base_t + timedelta(seconds=shift)).strftime("%H:%M:%S")
    
    res = {
        "id": h_hex[:6],
        "entry": entry_t,
        "prob": prob_x3,
        "strength": strength,
        "min": max(2.00, round(float(np.percentile(sims, 25)), 2)),
        "moy": max(2.60, round(float(np.percentile(sims, 55)), 2)),
        "max": max(3.10, round(float(np.percentile(sims, 88)), 2)),
        "status": "PENDING"
    }
    return res

# ================= SIDEBAR STATS =================
with st.sidebar:
    st.markdown("### 📊 V1 PERFORMANCE")
    if st.session_state.history:
        total = len(st.session_state.history)
        wins = sum(1 for x in st.session_state.history if x.get('status') == 'WIN ✅')
        st.metric("WIN RATE", f"{round(wins/total*100, 1)}%" if total > 0 else "0%")
    st.markdown("---")
    if st.button("🗑️ RESET HISTORY"):
        st.session_state.history = []
        save_data([])
        st.rerun()

# ================= MAIN UI =================
st.markdown("<h1 class='main-title'>AVIATOR ANDR V1</h1>", unsafe_allow_html=True)

col_in, col_out = st.columns([1, 2.2], gap="medium")

with col_in:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📥 INPUT")
    sha_in = st.text_input("SHA512 (5 voalohany)", placeholder="Ex: ac50e")
    time_in = st.text_input("TIME (HH:MM)", placeholder="Ex: 14:05")
    cote_in = st.number_input("LAST COTE", value=1.80, step=0.01)
    
    if st.button("🚀 ANALYSER", use_container_width=True):
        if sha_in and time_in:
            with st.spinner("Simulating 250k rounds..."):
                result = run_engine_andr(sha_in, time_in, cote_in)
                if result:
                    st.session_state.last_res = result
                    st.session_state.history.append(result)
                    save_data(st.session_state.history[-50:])
                    st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with col_out:
    r = st.session_state.last_res
    if r:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#00ffcc;'>▸ NEXT ENTRY TIME</p>", unsafe_allow_html=True)
        st.markdown(f"<div class='entry-display'>{r['entry']}</div>", unsafe_allow_html=True)
        
        st.markdown(f"<h1 style='text-align:center; color:#00ffcc; font-size:4rem;'>{r['prob']}%</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#ffffff66;'>PROBABILITÉ X3+</p>", unsafe_allow_html=True)
        
        # Targets
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"<div class='target-container'>SAFE<br><span class='val-target' style='color:#00ffcc;'>{r['min']}x</span></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='target-container'>MOYEN<br><span class='val-target' style='color:#ffd700;'>{r['moy']}x</span></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='target-container'>ULTRA<br><span class='val-target' style='color:#ff0066;'>{r['max']}x</span></div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        # --- WIN / LOSS BUTTONS ---
        bw, bl = st.columns(2)
        with bw:
            if st.button("🎯 WIN", use_container_width=True):
                st.session_state.history[-1]['status'] = 'WIN ✅'
                save_data(st.session_state.history)
                st.rerun()
        with bl:
            if st.button("❌ LOSS", use_container_width=True):
                st.session_state.history[-1]['status'] = 'LOSS ❌'
                save_data(st.session_state.history)
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='glass-card' style='height:400px; display:flex; align-items:center; justify-content:center;'><h3 style='color:#ffffff22;'>EN ATTENTE DE DONNÉES...</h3></div>", unsafe_allow_html=True)

# ================= HISTORY =================
if st.session_state.history:
    st.markdown("---")
    st.markdown("### 📜 LOGS (10 DERNIERS)")
    df = pd.DataFrame(st.session_state.history[-10:][::-1])
    st.dataframe(df[['entry', 'prob', 'status']], use_container_width=True, hide_index=True)
