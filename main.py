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
    initial_sidebar_state="expanded"
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
        font-size: clamp(1.8rem, 7vw, 3rem);
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
        padding: 20px;
        backdrop-filter: blur(12px);
        margin-bottom: 20px;
    }

    /* PLACEHOLDER MAINTY TANTERAKA */
    ::placeholder {
        color: #000000 !important;
        opacity: 1 !important;
        font-weight: 900 !important;
    }

    .stTextInput input, .stNumberInput input {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid #ff0066 !important;
        color: #000000 !important;
        border-radius: 12px !important;
        font-size: 1rem !important;
        padding: 12px !important;
        font-weight: bold !important;
    }
    
    .entry-time-mega {
        font-family: 'Orbitron', sans-serif;
        font-size: clamp(2.5rem, 10vw, 4.5rem);
        font-weight: 900;
        text-align: center;
        color: #ff0066;
        text-shadow: 0 0 25px #ff0066;
    }

    .prob-val {
        font-size: 2.5rem;
        font-family: 'Orbitron';
        text-align: center;
        color: #00ffcc;
        margin-bottom: 10px;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #ff0066, #ff3399) !important;
        color: white !important;
        font-weight: 900 !important;
        border-radius: 12px !important;
        height: 50px !important;
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
    col_a, col_b, col_c = st.columns([1, 1.5, 1])
    with col_b:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        pw = st.text_input("🔑 PASSWORD", placeholder="AVIATOR2026")
        if st.button("ACTIVATE"):
            if pw.strip() == "AVIATOR2026":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("❌ Diso ny tenimiafina")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ===================== ML TRAINING =====================
def train_ml_model():
    labeled = [h for h in st.session_state.history if h.get('result') in ['WIN', 'LOSS']]
    if len(labeled) < 5: return None, None
    X, y = [], []
    for h in labeled:
        try:
            hex_val = int(h['hex'], 16) if h.get('hex') else 0
            X.append([hex_val % 1000, h['last_cote'], h['prob']])
            y.append(1 if h['result'] == 'WIN' else 0)
        except: continue
    try:
        scaler = StandardScaler()
        X_s = scaler.fit_transform(np.array(X))
        model = GradientBoostingRegressor(n_estimators=100).fit(X_s, np.array(y))
        save_ml_model(model, scaler)
        return model, scaler
    except: return None, None

# ===================== SIDEBAR =====================
with st.sidebar:
    st.markdown("## 📊 DASHBOARD")
    if st.session_state.history:
        wins = sum(1 for h in st.session_state.history if h.get('result') == 'WIN')
        losses = sum(1 for h in st.session_state.history if h.get('result') == 'LOSS')
        wr = round(wins/(wins+losses)*100, 1) if (wins+losses)>0 else 0
        st.metric("WIN RATE", f"{wr}%")
    
    st.markdown("---")
    if st.button("🧠 TRAIN ML MODEL"):
        m, s = train_ml_model()
        if m: 
            st.session_state.ml_model, st.session_state.ml_scaler = m, s
            st.success("Model Updated!")
    
    if st.button("🗑️ RESET ALL DATA"):
        st.session_state.history = []
        if HISTORY_FILE.exists(): HISTORY_FILE.unlink()
        st.rerun()

# ===================== ENGINE V4000 =====================
def run_ultra_engine(hex_in, heure_in, cote_in):
    hex5 = hex_in.strip().lower()[:5]
    combined = f"{hex5}{heure_in}{cote_in}"
    h_hash = hashlib.sha256(combined.encode()).hexdigest()
    np.random.seed(int(h_hash[:8], 16) % (2**32))
    
    # Algorithm simulation
    base = 2.10 if cote_in < 2.0 else 1.90
    sims = np.random.lognormal(np.log(base), 0.22, 100_000)
    
    prob = round(float(np.mean(sims >= 3.0)) * 100, 2)
    t_min = round(float(np.percentile(sims, 25)), 2)
    t_moy = round(float(np.percentile(sims, 50)), 2)
    t_max = round(float(np.percentile(sims, 85)), 2)
    
    now_mg = datetime.now(TZ_MG)
    entry = (now_mg + timedelta(seconds=42)).strftime("%H:%M:%S")
    
    res = {
        "id": h_hash[:6], "hex": hex5, "entry": entry, "prob": prob, 
        "min": t_min, "moy": t_moy, "max": t_max, "result": "PENDING", "last_cote": cote_in
    }
    st.session_state.history.append(res)
    save_data(st.session_state.history)
    return res

# ===================== MAIN UI =====================
st.markdown("<div class='main-title'>aviator ANDR Ultra V2</div>", unsafe_allow_html=True)

c_in, c_out = st.columns([1, 2])
with c_in:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    h_in = st.text_input("🔐 HEX (Provably)", placeholder="OH: ac50e")
    t_in = st.text_input("⏰ ORA TEONY", placeholder="OH: 15:30")
    l_in = st.number_input("📊 COTE TEONY", value=1.88, step=0.01)
    if st.button("🚀 ANALYSER ULTRA"):
        if h_in and t_in:
            st.session_state.last_res = run_ultra_engine(h_in, t_in, l_in)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with c_out:
    r = st.session_state.last_res
    if r:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='entry-time-mega'>{r['entry']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='prob-val'>{r['prob']}% Probabilité</div>", unsafe_allow_html=True)
        
        # Naveriko ny COTE MIN, MOY, MAX eto
        m1, m2, m3 = st.columns(3)
        m1.metric("TARGET MIN", f"{r['min']}x")
        m2.metric("TARGET MOY", f"{r['moy']}x")
        m3.metric("TARGET MAX", f"{r['max']}x")
        
        st.markdown("---")
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
    st.markdown("### 📜 RECENT HISTORY")
    df = pd.DataFrame(st.session_state.history[-5:][::-1])
    st.dataframe(df[['entry', 'prob', 'min', 'max', 'result']], use_container_width=True, hide_index=True)
