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
import os

# ===================== CONFIGURATION =====================
st.set_page_config(
    page_title="AVIATOR ULTRA V4000 X3+", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===================== PERSISTENCE =====================
# Amboarina ny lalana halehan'ny data mba tsy hisy error
BASE_DIR = Path.cwd()
DATA_DIR = BASE_DIR / "aviator_v4000_data"
DATA_DIR.mkdir(exist_ok=True, parents=True)

HISTORY_FILE = DATA_DIR / "history.json"
ML_MODEL_FILE = DATA_DIR / "ml_model.pkl"

def save_data(data):
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        st.error(f"Error saving data: {e}")

def load_data():
    try:
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return []

def save_ml_model(model, scaler):
    try:
        with open(ML_MODEL_FILE, 'wb') as f:
            pickle.dump({'model': model, 'scaler': scaler}, f)
    except Exception:
        pass

def load_ml_model():
    try:
        if ML_MODEL_FILE.exists():
            with open(ML_MODEL_FILE, 'rb') as f:
                data = pickle.load(f)
                return data.get('model'), data.get('scaler')
    except Exception:
        pass
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
    
    .entry-time-mega {
        font-family: 'Orbitron', sans-serif;
        font-size: clamp(3rem, 12vw, 5rem);
        font-weight: 900;
        text-align: center;
        color: #ff0066;
        text-shadow: 0 0 30px #ff0066;
        margin: 20px 0;
    }
    
    .prob-mega {
        font-size: clamp(3rem, 10vw, 4.5rem);
        font-weight: 900;
        font-family: 'Orbitron';
        text-align: center;
        color: #00ffcc;
        margin: 15px 0;
    }
    
    .target-box {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        margin: 5px;
    }
    
    .target-val {
        font-size: clamp(1.5rem, 6vw, 2.5rem);
        font-weight: 900;
        font-family: 'Orbitron';
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
    m, s = load_ml_model()
    st.session_state.ml_model = m
    st.session_state.ml_scaler = s

# ===================== TIMEZONE MADAGASCAR =====================
TZ_MG = pytz.timezone("Indian/Antananarivo")

# ===================== LOGIN =====================
if not st.session_state.auth:
    st.markdown("<div class='main-title'>AVIATOR V4000</div>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 1.2, 1])
    with col_b:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        pw = st.text_input("🔑 PASSWORD", type="password")
        if st.button("ACTIVATE"):
            if pw == "AVIATOR2026":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("❌ Password diso")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ===================== ML TRAINING =====================
def train_ml_model():
    labeled = [h for h in st.session_state.history if h.get('result') in ['WIN', 'LOSS']]
    if len(labeled) < 10:
        return None, None
    
    X, y = [], []
    for h in labeled:
        try:
            hex_val = int(h['hex'], 16) if all(c in '0123456789abcdef' for c in h['hex']) else 0
            features = [hex_val % 1000, h.get('last_cote', 1.0), h.get('prob', 0), h.get('conf', 0)]
            X.append(features)
            y.append(1 if h['result'] == 'WIN' else 0)
        except: continue
        
    try:
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        model.fit(X_scaled, y)
        save_ml_model(model, scaler)
        return model, scaler
    except:
        return None, None

# ===================== ENGINE =====================
def run_ultra_v4000(hex_input, last_heure, last_cote):
    hex5 = hex_input.strip().lower()[:5]
    combined = f"{hex5}:{last_heure}:{last_cote}"
    full_hash = hashlib.sha512(combined.encode()).hexdigest()
    hash_num = int(full_hash[:16], 16)
    
    np.random.seed(hash_num % (2**32))
    sims = np.random.lognormal(np.log(2.0), 0.2, 100_000)
    
    prob_x3 = round(float(np.mean(sims >= 3.0)) * 100, 2)
    conf = round(min(99, prob_x3 * 2.1), 2)
    
    now_mg = datetime.now(TZ_MG)
    entry_time = (now_mg + timedelta(seconds=45)).strftime("%H:%M:%S")
    
    result = {
        "id": full_hash[:8],
        "hex": hex5,
        "entry": entry_time,
        "prob": prob_x3,
        "conf": conf,
        "min": round(float(np.percentile(sims, 20)), 2),
        "moy": round(float(np.percentile(sims, 50)), 2),
        "max": round(float(np.percentile(sims, 80)), 2),
        "result": "PENDING",
        "last_cote": last_cote,
        "signal": "🟢 GOOD" if prob_x3 > 30 else "⚠️ WAIT"
    }
    
    st.session_state.history.append(result)
    save_data(st.session_state.history)
    return result

# ===================== MAIN UI =====================
st.markdown("<div class='main-title'>AVIATOR ULTRA V4000</div>", unsafe_allow_html=True)

col_in, col_out = st.columns([1, 2])

with col_in:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    hex_in = st.text_input("🔐 HEX SHA512 (5 chars)", placeholder="ac50e")
    heure_in = st.text_input("⏰ LAST HEURE (HH:MM)", placeholder="20:22")
    cote_in = st.number_input("📊 LAST COTE", value=1.88, step=0.01)
    
    if st.button("🚀 ANALYSER"):
        if hex_in and heure_in:
            res = run_ultra_v4000(hex_in, heure_in, cote_in)
            st.session_state.last_res = res
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with col_out:
    r = st.session_state.last_res
    if r:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align:center;'>{r['signal']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<div class='entry-time-mega'>{r['entry']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='prob-mega'>{r['prob']}%</div>", unsafe_allow_html=True)
        
        cw, cl = st.columns(2)
        if cw.button("✅ WIN"):
            st.session_state.history[-1]['result'] = 'WIN'
            save_data(st.session_state.history)
            st.rerun()
        if cl.button("❌ LOSS"):
            st.session_state.history[-1]['result'] = 'LOSS'
            save_data(st.session_state.history)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# History table
if st.session_state.history:
    st.markdown("### 📜 LOGS")
    st.dataframe(pd.DataFrame(st.session_state.history[::-1]).head(10), use_container_width=True)
