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
    
    .stTextInput input, .stNumberInput input {
        background: rgba(255, 0, 102, 0.05) !important;
        border: 2px solid rgba(255, 0, 102, 0.3) !important;
        color: #e0fbfc !important;
        border-radius: 12px !important;
        font-size: 1rem !important;
        padding: 12px !important;
    }
    
    @media (max-width: 768px) {
        .stApp {
            padding: 10px !important;
        }
        .glass-card {
            padding: 15px !important;
        }
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

# ===================== TIMEZONE MADAGASCAR =====================
TZ_MG = pytz.timezone("Indian/Antananarivo")

# ===================== LOGIN =====================
if not st.session_state.auth:
    st.markdown("<div class='main-title'>aviator ANDR Ultra V2</div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#ff006699; letter-spacing:0.3em;'>ULTRA X3+ PRECISION</p>", unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns([1, 1.2, 1])
    with col_b:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        pw = st.text_input("🔑 PASSWORD", type="password", placeholder="Ampidiro eto ny tenimiafina...")
        if st.button("ACTIVATE", use_container_width=True):
            # Cacher ny tenimiafina ety ivelany mampiasa SHA-256 (Mbola "AVIATOR2026" ihany no ampidirina)
            if hashlib.sha256(pw.encode()).hexdigest() == "396181f0bd24e8a156e50e932ec1a1e4839f972b94e772b1dcbdb24d3ab79e67":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("❌ Diso ny tenimiafina")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='glass-card' style='max-width:800px; margin:40px auto;'>
        <h2 style='color:#ff0066; text-align:center;'>📖 FANAZAVANA MALAGASY</h2>
        <h3 style='color:#00ffcc; margin-top:20px;'>🎯 ZAVATRA ILAINA (3):</h3>
        <p><b>1. HEX (SHA512 5 premiers):</b> 5 caractères voalohany @ SHA512 hash hitanao @ Provably Fair.</p>
        <p><b>2. LAST HEURE (HH:MM):</b> Ora tamin'ny round TALOHA vita tsara.</p>
        <p><b>3. LAST COTE:</b> Résultat tamin'ny round TALOHA (ex: 1.88).</p>
        <h3 style='color:#ff0066; margin-top:25px;'>⚠️ TSY MAINTSY TADIDIO:</h3>
        <ul style='line-height:2;'>
            <li><b>Entry time</b> = ORA MARINA hidirana (no décalage!)</li>
            <li><b>ML</b> = mianatra avy @ results marina ho azy</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
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
    elif last_cote < 3.5: base, sigma = 2.00, 0.19
    else: base, sigma = 1.96, 0.18
    
    base += (hash_num % 180) / 1200
    sigma = max(0.1, sigma - (last_cote * 0.0022))
    sims = np.random.lognormal(np.log(base), sigma, 300_000)
    
    prob_x3 = round(float(np.mean(sims >= 3.0)) * 100, 2)
    prob_x3_5 = round(float(np.mean(sims >= 3.5)) * 100, 2)
    prob_x4 = round(float(np.mean(sims >= 4.0)) * 100, 2)
    
    target_min = max(2.00, round(float(np.percentile(sims, 30)), 2))
    target_moy = max(2.60, round(float(np.percentile(sims, 50)), 2))
    sims_x3 = sims[sims >= 3.0]
    target_max = max(3.00, round(float(np.percentile(sims_x3, 85)), 2)) if len(sims_x3) > 0 else 3.80
    
    conf = round(max(40, min(99, prob_x3 * 1.18 + prob_x3_5 * 0.42 + (hash_num % 200) / 3.2 + last_cote * 13.0)), 2)
    strength = max(30.0, min(99.0, prob_x3 * 0.50 + conf * 0.30))
    
    ml_boost = 0
    if st.session_state.ml_model is not None:
        try:
            hex_val = int(hex5, 16) if all(c in '0123456789abcdef' for c in hex5) else 0
            feat = st.session_state.ml_scaler.transform([[hex_val%1000, (hex_val>>8)%1000, (hex_val>>16)%1000, last_cote, prob_x3, conf]])
            ml_boost = float(st.session_state.ml_model.predict(feat)[0]) * 8
        except: pass
    
    conf, strength = min(99, conf + ml_boost), min(99, strength + ml_boost * 0.5)
    
    now_mg = datetime.now(TZ_MG)
    total_shift = max(20, min(110, 48 + (hash_num % 90 - 45) + int(strength * 0.35)))
    entry_time = (now_mg + timedelta(seconds=total_shift)).strftime("%H:%M:%S")
    
    if strength >= 88 and prob_x3 >= 44: signal = "💎💎💎 ULTRA X3+ — BUY MAX"
    elif strength >= 76 and prob_x3 >= 36: signal = "🔥🔥 STRONG X3+ — ENGAGE"
    elif strength >= 62 and prob_x3 >= 28: signal = "🟢 GOOD X3+ — SCALP"
    else: signal = "⚠️ LOW — SKIP"
    
    res = {
        "id": full_hash[:8], "hex": hex5, "last_heure": last_heure, "last_cote": last_cote,
        "entry": entry_time, "signal": signal, "prob": prob_x3, "prob_x3_5": prob_x3_5,
        "prob_x4": prob_x4, "conf": conf, "strength": strength, "ml_boost": round(ml_boost, 1),
        "min": target_min, "moy": target_moy, "max": target_max, "result": "PENDING"
    }
    st.session_state.history.append(res)
    save_data(st.session_state.history)
    return res

# ===================== MAIN UI =====================
st.markdown("<div class='main-title'>aviator ANDR Ultra V2</div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 📊 STATS")
    if st.session_state.history:
        total = len(st.session_state.history)
        wins = sum(1 for h in st.session_state.history if h.get('result') == 'WIN')
        losses = sum(1 for h in st.session_state.history if h.get('result') == 'LOSS')
        wr = round(wins / (wins + losses) * 100, 1) if (wins + losses) > 0 else 0
        st.metric("WIN RATE", f"{wr}%")
    if st.button("🧠 TRAIN ML"):
        m, s = train_ml_model()
        if m: st.session_state.ml_model, st.session_state.ml_scaler = m, s
        st.rerun()
    if st.button("🗑️ RESET"):
        st.session_state.history, st.session_state.ml_model = [], None
        if HISTORY_FILE.exists(): HISTORY_FILE.unlink()
        st.rerun()

col_in, col_out = st.columns([1, 2], gap="medium")
with col_in:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    hex_in = st.text_input("🔐 HEX (5 chars)", placeholder="Ampidiro eto ny HEX (oh: ac50e)")
    heure_in = st.text_input("⏰ LAST HEURE", placeholder="Ampidiro ny ora farany (oh: 20:22)")
    cote_in = st.number_input("📊 LAST COTE", value=1.88, step=0.01)
    if st.button("🚀 ANALYSER ULTRA"):
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
        
        c1, c2, c3 = st.columns(3)
        c1.metric("MIN", f"{r['min']}×")
        c2.metric("MOY", f"{r['moy']}×")
        c3.metric("MAX", f"{r['max']}×")
        
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
    df = pd.DataFrame(st.session_state.history[-10:][::-1])
    st.dataframe(df[['entry', 'prob', 'min', 'max', 'result']], use_container_width=True, hide_index=True)
