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

    /* --- PLACEHOLDER SY INPUT STYLE --- */
    /* Mampiseho ny soratra placeholder ho mainty sy mazava */
    ::placeholder {
        color: #000000 !important;
        opacity: 1 !important;
        font-weight: 900 !important;
    }

    .stTextInput input, .stNumberInput input {
        background: rgba(255, 255, 255, 0.9) !important; /* Ambodika fotsy mba ho hita ny mainty */
        border: 2px solid #ff0066 !important;
        color: #000000 !important; /* Ny soratra soratanao koa ho mainty */
        border-radius: 12px !important;
        font-size: 1.1rem !important;
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
    
    .prob-mega {
        font-size: clamp(3rem, 10vw, 4.5rem);
        font-weight: 900;
        font-family: 'Orbitron';
        text-align: center;
        color: #00ffcc;
        margin: 15px 0;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #ff0066, #ff3399) !important;
        color: white !important;
        font-weight: 900 !important;
        border-radius: 12px !important;
        height: 55px !important;
        font-size: 1.1rem !important;
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
    st.markdown("<p style='text-align:center; color:#ff006699; letter-spacing:0.3em;'>ULTRA X3+ PRECISION</p>", unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns([1, 1.2, 1])
    with col_b:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        # Nesorina ny type="password" mba ho hita tsara ny AVIATOR2026 soratanao
        pw = st.text_input("🔑 PASSWORD", placeholder="SORATY ETO: AVIATOR2026")
        if st.button("ACTIVATE", use_container_width=True):
            if pw.strip() == "AVIATOR2026":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("❌ Diso ny tenimiafina")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ===================== ENGINE V4000 =====================
def run_andr_ultra_v2(hex_input, last_heure, last_cote):
    hex5 = hex_input.strip().lower()[:5]
    combined = f"{hex5}:{last_heure}:{last_cote}"
    full_hash = hashlib.sha512(combined.encode()).hexdigest()
    hash_num = int(full_hash[:16], 16)
    
    seed_val = int((hash_num & 0xFFFFFFFFFFFFFFFF) + int(last_cote * 10000))
    np.random.seed(seed_val % (2**32))
    
    base = 2.15 if last_cote < 1.8 else 1.95
    sims = np.random.lognormal(np.log(base), 0.20, 100_000)
    
    prob_x3 = round(float(np.mean(sims >= 3.0)) * 100, 2)
    target_min = round(float(np.percentile(sims, 30)), 2)
    target_moy = round(float(np.percentile(sims, 50)), 2)
    target_max = round(float(np.percentile(sims, 80)), 2)
    
    now_mg = datetime.now(TZ_MG)
    entry_time = (now_mg + timedelta(seconds=45)).strftime("%H:%M:%S")
    
    res = {
        "id": full_hash[:8], "entry": entry_time, "prob": prob_x3,
        "min": target_min, "moy": target_moy, "max": target_max, "result": "PENDING"
    }
    st.session_state.history.append(res)
    save_data(st.session_state.history)
    return res

# ===================== MAIN UI =====================
st.markdown("<div class='main-title'>aviator ANDR Ultra V2</div>", unsafe_allow_html=True)

col_in, col_out = st.columns([1, 2], gap="medium")
with col_in:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    hex_in = st.text_input("🔐 HEX", placeholder="OH: AC50E")
    heure_in = st.text_input("⏰ ORA FARANY", placeholder="OH: 16:40")
    cote_in = st.number_input("📊 COTE FARANY", value=1.88, step=0.01)
    if st.button("🚀 ANALYSER ULTRA"):
        if hex_in and heure_in:
            st.session_state.last_res = run_andr_ultra_v2(hex_in, heure_in, cote_in)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with col_out:
    r = st.session_state.last_res
    if r:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='entry-time-mega'>{r['entry']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='prob-mega'>{r['prob']}%</div>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("MIN", f"{r['min']}x")
        c2.metric("MOY", f"{r['moy']}x")
        c3.metric("MAX", f"{r['max']}x")
        st.markdown("</div>", unsafe_allow_html=True)
