import streamlit as st
import hashlib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import pytz
import json
from pathlib import Path
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import pickle

# ===================== CONFIGURATION =====================
st.set_page_config(
    page_title="aviator ANDR Ultra V2", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===================== PERSISTENCE =====================
try:
    DATA_DIR = Path(__file__).parent / "aviator_andr_ultra_v2_data"
except:
    DATA_DIR = Path.cwd() / "aviator_andr_ultra_v2_data"

DATA_DIR.mkdir(exist_ok=True, parents=True)
HISTORY_FILE = DATA_DIR / "history.json"
ML_MODEL_FILE = DATA_DIR / "ml_model.pkl"

def save_data(data):
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except: pass

def load_data():
    try:
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except: pass
    return []

def save_ml_model(model, scaler):
    try:
        with open(ML_MODEL_FILE, 'wb') as f:
            pickle.dump({'model': model, 'scaler': scaler}, f)
    except: pass

def load_ml_model():
    try:
        if ML_MODEL_FILE.exists():
            with open(ML_MODEL_FILE, 'rb') as f:
                data = pickle.load(f)
                return data['model'], data['scaler']
    except: pass
    return None, None

# ===================== CSS ULTRA MOBILE-FRIENDLY =====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@600;700&display=swap');
    
    .stApp {
        background: radial-gradient(ellipse at 50% 0%, #1a0033 0%, #000008 60%, #001a1a 100%);
        color: #e0fbfc;
        font-family: 'Rajdhani', sans-serif;
    }
    
    .main-title {
        font-family: 'Orbitron', sans-serif;
        font-size: clamp(2rem, 8vw, 3.5rem);
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #ff0066, #00ffcc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .glass-card {
        background: rgba(10, 0, 25, 0.9);
        border: 2px solid rgba(255, 0, 102, 0.4);
        border-radius: 20px;
        padding: clamp(15px, 5vw, 25px);
        backdrop-filter: blur(12px);
        margin-bottom: 20px;
    }
    
    ::placeholder {
        color: #000000 !important;
        opacity: 1 !important;
        font-weight: bold !important;
    }

    .stTextInput input, .stNumberInput input {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 2px solid rgba(255, 0, 102, 0.6) !important;
        color: #000000 !important;
        border-radius: 12px !important;
        font-size: 1rem !important;
        padding: 12px !important;
        font-weight: bold !important;
    }
    
    .entry-time-mega {
        font-family: 'Orbitron', sans-serif;
        font-size: clamp(3rem, 12vw, 5rem);
        font-weight: 900;
        text-align: center;
        color: #ff0066;
        text-shadow: 0 0 30px #ff0066;
        margin: 20px 0;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #ff0066, #ff3399) !important;
        color: white !important;
        font-weight: 900 !important;
        border-radius: 12px !important;
        height: 55px !important;
        font-size: 1rem !important;
        border: none !important;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ===================== SESSION STATE =====================
if "auth" not in st.session_state:
    st.session_state.auth = False
if "history" not in st.session_state:
    st.session_state.history = load_data()
if "last_res" not in st.session_state:
    st.session_state.last_res = None
if "ml_model" not in st.session_state:
    st.session_state.ml_model, st.session_state.ml_scaler = load_ml_model()

TZ_MG = pytz.timezone("Indian/Antananarivo")

# ===================== LOGIN =====================
if not st.session_state.auth:
    st.markdown("<div class='main-title'>aviator ANDR Ultra V2</div>", unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns([1, 1.2, 1])
    with col_b:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        pw = st.text_input("🔑 PASSWORD", type="password", placeholder="TENIMIAFINA ETO...")
        if st.button("ACTIVATE", use_container_width=True):
            # Ny tenimiafina dia: AVIATOR2026
            if hashlib.sha256(pw.encode()).hexdigest() == "396181f0bd24e8a156e50e932ec1a1e4839f972b94e772b1dcbdb24d3ab79e67":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("❌ Diso ny tenimiafina")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ===================== ML TRAINING =====================
def train_ml_model():
    labeled = [h for h in st.session_state.history if h.get('result') in ['WIN', 'LOSS']]
    if len(labeled) < 10: return None, None
    X, y = [], []
    for h in labeled:
        try:
            hex_val = int(h['hex'], 16) if all(c in '0123456789abcdef' for c in h['hex']) else 0
            features = [hex_val % 1000, (hex_val >> 8) % 1000, (hex_val >> 16) % 1000, h['last_cote'], h['prob'], h['conf']]
            X.append(features)
            y.append(1 if h['result'] == 'WIN' else 0)
        except: continue
    try:
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(np.array(X))
        model = GradientBoostingRegressor(n_estimators=200, max_depth=5, learning_rate=0.05, random_state=42)
        model.fit(X_scaled, np.array(y))
        save_ml_model(model, scaler)
        return model, scaler
    except: return None, None

# ===================== ULTRA ENGINE V4000 =====================
def run_andr_ultra_v2(hex_input, last_heure, last_cote):
    hex5 = hex_input.strip().lower()[:5]
    combined = f"{hex5}:{last_heure}:{last_cote}"
    full_hash = hashlib.sha512(combined.encode()).hexdigest()
    hash_num = int(full_hash[:16], 16)
    seed_val = int((hash_num & 0xFFFFFFFFFFFFFFFF) + int(last_cote * 10000))
    np.random.seed(seed_val % (2**32))
    
    if last_cote < 1.5: base, sigma = 2.12, 0.24
    elif last_cote < 2.5: base, sigma = 2.06, 0.21
    else: base, sigma = 2.00, 0.19
    
    sims = np.random.lognormal(np.log(base), sigma, 300_000)
    prob_x3 = round(float(np.mean(sims >= 3.0)) * 100, 2)
    conf = round(max(40, min(99, prob_x3 * 1.18 + (hash_num % 200) / 3.2 + last_cote * 13.0)), 2)
    strength = max(30.0, min(99.0, prob_x3 * 0.50 + conf * 0.30))
    
    now_mg = datetime.now(TZ_MG)
    total_shift = max(20, min(110, 48 + int(strength * 0.35)))
    entry_time = (now_mg + timedelta(seconds=total_shift)).strftime("%H:%M:%S")
    
    signal = "💎 ULTRA X3+" if strength >= 80 else "🟢 GOOD" if strength >= 60 else "⚠️ SKIP"
    
    res = {
        "id": full_hash[:8], "hex": hex5, "last_heure": last_heure, "last_cote": last_cote,
        "entry": entry_time, "signal": signal, "prob": prob_x3, "conf": conf, "strength": strength,
        "min": round(float(np.percentile(sims, 30)), 2), "moy": round(float(np.percentile(sims, 50)), 2), 
        "max": round(float(np.percentile(sims, 85)), 2), "result": "PENDING"
    }
    st.session_state.history.append(res)
    save_data(st.session_state.history)
    return res

# ===================== MAIN UI =====================
st.markdown("<div class='main-title'>aviator ANDR Ultra V2</div>", unsafe_allow_html=True)

col_in, col_out = st.columns([1, 2], gap="medium")
with col_in:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    hex_in = st.text_input("🔐 HEX", placeholder="HEX 5 chars...")
    heure_in = st.text_input("⏰ ORA", placeholder="HH:MM...")
    cote_in = st.number_input("📊 LAST COTE", value=1.88, step=0.01)
    if st.button("🚀 ANALYSER"):
        if hex_in and heure_in:
            st.session_state.last_res = run_andr_ultra_v2(hex_in, heure_in, cote_in)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with col_out:
    r = st.session_state.last_res
    if r:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align:center; color:#ff0066;'>{r['signal']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<div class='entry-time-mega'>{r['entry']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='prob-mega'>{r['prob']}%</div>", unsafe_allow_html=True)
        
        cw, cl = st.columns(2)
        if cw.button("✅ WIN"):
            for h in st.session_state.history:
                if h['id'] == r['id']: h['result'] = 'WIN'
            save_data(st.session_state.history)
            st.rerun()
        if cl.button("❌ LOSS"):
            for h in st.session_state.history:
                if h['id'] == r['id']: h['result'] = 'LOSS'
            save_data(st.session_state.history)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.history:
    st.markdown("---")
    df = pd.DataFrame(st.session_state.history[-5:][::-1])
    st.dataframe(df[['entry', 'prob', 'result']], use_container_width=True, hide_index=True)
