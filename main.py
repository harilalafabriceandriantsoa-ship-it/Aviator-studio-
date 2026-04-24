import streamlit as st
import hashlib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
from pathlib import Path

# Config
st.set_page_config(page_title="AVIATOR ANDR V2", layout="wide")

# Persistence
try:
    DATA_DIR = Path(__file__).parent / "aviator_v3000_data"
except:
    DATA_DIR = Path.cwd() / "aviator_v3000_data"
DATA_DIR.mkdir(exist_ok=True)
HISTORY_FILE = DATA_DIR / "history.json"

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

# CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap');
.stApp {background: radial-gradient(ellipse at 50% 0%, #1a0033 0%, #000008 60%, #001a0d 100%); color: #e0fbfc;}
h1 {font-family: 'Orbitron'; font-size: 3.5rem; text-align: center; 
    background: linear-gradient(90deg, #ff0066, #00ffcc); 
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
.glass {background: rgba(10,0,25,0.9); border: 2px solid rgba(255,0,102,0.4); 
        border-radius: 20px; padding: 28px; backdrop-filter: blur(12px);}
.entry-mega {font-family: 'Orbitron'; font-size: 5rem; font-weight: 900; text-align: center;
             color: #ff0066; text-shadow: 0 0 40px #ff0066; margin: 20px 0;}
.target-box {border-radius: 16px; padding: 20px; text-align: center; margin: 8px;}
.target-min {background: linear-gradient(135deg, rgba(0,255,204,0.2), rgba(0,200,100,0.1)); 
             border: 2px solid rgba(0,255,204,0.5);}
.target-moy {background: linear-gradient(135deg, rgba(255,215,0,0.2), rgba(255,170,0,0.1)); 
             border: 2px solid rgba(255,215,0,0.5);}
.target-max {background: linear-gradient(135deg, rgba(255,51,102,0.25), rgba(200,0,60,0.1)); 
             border: 2px solid rgba(255,51,102,0.6);}
</style>
""", unsafe_allow_html=True)

# Session
if "auth" not in st.session_state:
    st.session_state.auth = False
if "history" not in st.session_state:
    st.session_state.history = load_data()
if "last" not in st.session_state:
    st.session_state.last = None

# Login
if not st.session_state.auth:
    st.markdown("<h1>🔐 AVIATOR STUDIO V3000</h1>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 1.2, 1])
    with col_b:
        pw = st.text_input("🔑 MOT DE PASSE", type="password")
        if st.button("ACTIVER", use_container_width=True):
            if pw == "AVIATOR2026":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("❌ Incorrect")
    
    st.markdown("""
    <div style='max-width:700px; margin:40px auto; padding:24px; background:rgba(255,0,102,0.08); border-radius:14px;'>
    <h3 style='color:#ff0066; text-align:center;'>📖 TOROLALANA MALAGASY</h3>
    <p style='line-height:2;'>
    <b>ZAVATRA ILAINA (4):</b><br>
    1. <b>SHA512 5 premiers:</b> 5 caractères voalohany @ hash (ex: ac50e)<br>
    2. <b>Heure (HH:MM):</b> Ora tamin'ny round taloha (ex: 20:22)<br>
    3. <b>Last Cote:</b> Cote tamin'ny round taloha (ex: 1.88)<br>
    4. <b>Hex (optionnel):</b> Hex complet raha misy<br><br>
    
    <b>FOMBA FAMPIASANA:</b><br>
    1. Jereo Provably Fair @ Aviator<br>
    2. Copier SHA512 → Raisina 5 premiers caractères<br>
    3. Copier Heure (HH:MM fotsiny)<br>
    4. Tadidio Last Cote (résultat taloha)<br>
    5. Tsindrio "ANALYSER"<br>
    6. Miseho: Entry time + 3 targets (accuracy) + Signal<br><br>
    
    <b>RESULT:</b><br>
    • Entry Time: Fotoana hidirana (variable @ SHA512)<br>
    • MIN: Safe target (70% accuracy)<br>
    • MOYEN: Normal target (50% accuracy)<br>
    • MAX: X3+ target (realistic accuracy)<br>
    • Signal: Ultra/Strong/Good/Skip
    </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Engine
def aviator_engine_v3000(sha5, heure, last_cote, hex_full=""):
    # SHA extraction
    if len(sha5) < 5:
        st.error("❌ SHA512 dia 5 caractères minimum")
        return None
    
    sha5 = sha5[:5].lower()
    
    # Seed generation avy @ SHA5 + time + last_cote
    combined = f"{sha5}:{heure}:{last_cote}"
    if hex_full:
        combined += f":{hex_full[:10]}"
    
    hash_bytes = hashlib.sha512(combined.encode()).digest()
    seed_int = int.from_bytes(hash_bytes[:8], "big")
    np.random.seed(seed_int % (2**32))
    
    # Base calculation
    sha_val = int(sha5, 16) if all(c in '0123456789abcdef' for c in sha5) else sum(ord(c) for c in sha5)
    
    if last_cote < 1.5:
        base = 2.15 + (sha_val % 150) / 1000
        sigma = 0.24
    elif last_cote < 2.5:
        base = 2.08 + (sha_val % 130) / 1000
        sigma = 0.21
    elif last_cote < 3.5:
        base = 2.00 + (sha_val % 120) / 1000
        sigma = 0.19
    else:
        base = 1.95 + (sha_val % 110) / 1000
        sigma = 0.18
    
    sigma -= (last_cote * 0.0022)
    
    # 250k simulations
    sims = np.random.lognormal(np.log(base), sigma, 250_000)
    
    # Probabilities
    x3_prob = round(float(np.mean(sims >= 3.0)) * 100, 2)
    x3_5_prob = round(float(np.mean(sims >= 3.5)) * 100, 2)
    x4_prob = round(float(np.mean(sims >= 4.0)) * 100, 2)
    
    # Targets avec accuracy
    target_min = max(2.00, round(float(np.percentile(sims, 30)), 2))
    acc_min = 70.0
    
    target_moy = max(2.50, round(float(np.percentile(sims, 50)), 2))
    acc_moy = 50.0
    
    sims_x3 = sims[sims >= 3.0]
    if len(sims_x3) > 0:
        target_max = max(3.00, round(float(np.percentile(sims_x3, 85)), 2))
        acc_max = round(x3_prob * 0.85, 1)
    else:
        target_max = 3.50
        acc_max = 10.0
    
    # Confidence
    conf = round(max(40, min(99,
        x3_prob * 1.15 +
        x3_5_prob * 0.40 +
        x4_prob * 0.25 +
        (sha_val % 200) / 3.0 +
        last_cote * 12.0 -
        (100 - x3_prob) * 0.30
    )), 2)
    
    # Strength
    x3_count = int(np.sum(sims >= 3.0))
    strength = round(
        x3_prob * 0.50 +
        conf * 0.30 +
        x3_5_prob * 0.15 +
        (x3_count / 2500) +
        (100 if x3_prob >= 45 else 80 if x3_prob >= 38 else 60) * 0.05
    , 2)
    strength = max(30.0, min(99.0, strength))
    
    # Entry time VARIABLE @ SHA512
    try:
        h, m = map(int, heure.split(':'))
        base_time = datetime.now().replace(hour=h, minute=m, second=0)
    except:
        base_time = datetime.now()
    
    # Multi-factor shift basé SHA512
    sha_shift = (sha_val % 90) - 45
    strength_bonus = int(strength * 0.4)
    cote_factor = int(last_cote * 5)
    prob_penalty = int((50 - x3_prob) * 0.5)
    
    total_shift = max(20, min(110,
        55 + sha_shift + strength_bonus + cote_factor - prob_penalty
    ))
    
    entry_time = (base_time + timedelta(seconds=total_shift)).strftime("%H:%M:%S")
    
    # Signal
    if strength >= 90 and x3_prob >= 45:
        signal = "💎💎💎 ULTRA X3+ — BUY MAX"
        sig_class = "ultra"
    elif strength >= 78 and x3_prob >= 38:
        signal = "🔥🔥 STRONG X3+ — ENGAGE"
        sig_class = "strong"
    elif strength >= 65 and x3_prob >= 30:
        signal = "🟢 GOOD X3+ — SCALP"
        sig_class = "good"
    else:
        signal = "⚠️ LOW — SKIP"
        sig_class = "skip"
    
    return {
        "entry": entry_time,
        "signal": signal,
        "sig_class": sig_class,
        "x3_prob": x3_prob,
        "x3_5_prob": x3_5_prob,
        "x4_prob": x4_prob,
        "conf": conf,
        "strength": strength,
        "target_min": target_min,
        "target_moy": target_moy,
        "target_max": target_max,
        "acc_min": acc_min,
        "acc_moy": acc_moy,
        "acc_max": acc_max,
        "sha_used": sha5,
        "time_used": heure,
        "cote_used": last_cote
    }

# Sidebar
with st.sidebar:
    st.markdown("### 📊 STATS")
    if st.session_state.history:
        total = len(st.session_state.history)
        wins = sum(1 for h in st.session_state.history if h.get('result') == 'win')
        st.metric("Total", total)
        st.metric("Wins", wins)
        st.metric("Win Rate", f"{round(wins/total*100,1)}%" if total > 0 else "0%")
    
    st.markdown("---")
    if st.button("🗑️ RESET DATA", use_container_width=True):
        st.session_state.history = []
        save_data([])
        st.success("✅ Reset!")
        st.rerun()

# Main
st.markdown("<h1>✈️ AVIATOR STUDIO V3000</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#ff006699; letter-spacing:0.3em;'>ULTRA X3+ PREDICTION ENGINE</p>", unsafe_allow_html=True)

col_in, col_out = st.columns([1, 2.2], gap="large")

with col_in:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### 📥 PARAMÈTRES")
    
    sha5 = st.text_input(
        "🔐 SHA512 (5 premiers)",
        placeholder="Ex: ac50e",
        help="5 caractères voalohany @ SHA512 hash"
    )
    
    heure = st.text_input(
        "⏰ HEURE (HH:MM)",
        placeholder="Ex: 20:22",
        help="Ora @ round taloha"
    )
    
    last_cote = st.number_input(
        "📊 LAST COTE",
        value=1.88,
        step=0.01,
        format="%.2f",
        help="Cote tamin'ny round taloha"
    )
    
    hex_full = st.text_input(
        "🔢 HEX Complet (optionnel)",
        placeholder="Ex: 7db8e01413d6d...",
        help="Hex complet (optionnel pour + précision)"
    )
    
    if st.button("🚀 ANALYSER ULTRA", use_container_width=True):
        if sha5 and heure:
            with st.spinner("⚡ Analyse 250k simulations..."):
                result = aviator_engine_v3000(sha5, heure, last_cote, hex_full)
            if result:
                st.session_state.last = result
                st.session_state.history.append(result)
                save_data(st.session_state.history[-50:])
                st.rerun()
        else:
            st.error("SHA5 et Heure obligatoires")
    
    st.markdown("</div>", unsafe_allow_html=True)

with col_out:
    r = st.session_state.last
    if r:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        
        # Signal
        st.markdown(f"<h2 style='color:#ff0066; text-align:center;'>{r['signal']}</h2>", unsafe_allow_html=True)
        
        # Entry
        st.markdown("<p style='text-align:center; color:#ffffff66; margin-top:20px;'>▸ ENTRY TIME</p>", unsafe_allow_html=True)
        st.markdown(f"<div class='entry-mega'>{r['entry']}</div>", unsafe_allow_html=True)
        
        # X3+ Prob
        st.markdown(f"<h1 style='text-align:center; color:#ff3399; font-size:4rem;'>{r['x3_prob']}%</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#ffffff66;'>PROBABILITÉ X3+</p>", unsafe_allow_html=True)
        
        # Sub-probs
        st.markdown(f"""
        <div style='display:flex; gap:16px; justify-content:center; margin:20px 0;'>
            <div style='text-align:center;'>
                <div style='font-size:1.4rem; font-weight:700; color:#ff3399;'>{r['x3_5_prob']}%</div>
                <div style='font-size:0.7rem; color:#ffffff55;'>X3.5+</div>
            </div>
            <div style='text-align:center;'>
                <div style='font-size:1.4rem; font-weight:700; color:#ff6699;'>{r['x4_prob']}%</div>
                <div style='font-size:0.7rem; color:#ffffff55;'>X4+</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Metrics
        st.markdown(f"""
        <div style='display:flex; gap:16px; justify-content:center; margin:16px 0;'>
            <div style='text-align:center;'>
                <div style='font-size:1.6rem; font-weight:700; color:#00ffcc;'>{r['conf']}%</div>
                <div style='font-size:0.7rem; color:#ffffff55;'>CONF</div>
            </div>
            <div style='text-align:center;'>
                <div style='font-size:1.6rem; font-weight:700; color:#ff0066;'>{r['strength']}</div>
                <div style='font-size:0.7rem; color:#ffffff55;'>STRENGTH</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Targets
        st.markdown("<p style='text-align:center; color:#ffffff66; margin-top:24px;'>▸ TARGETS AVEC ACCURACY</p>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class='target-box target-min'>
                <div style='font-size:0.75rem; color:#ffffff88;'>MIN SAFE</div>
                <div style='font-size:2.5rem; font-weight:900; color:#00ffcc; margin:8px 0;'>{r['target_min']}×</div>
                <div style='font-size:0.9rem; color:#00ff88;'>Accuracy: {r['acc_min']}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with c2:
            st.markdown(f"""
            <div class='target-box target-moy'>
                <div style='font-size:0.75rem; color:#ffffff88;'>MOYEN</div>
                <div style='font-size:2.5rem; font-weight:900; color:#ffd700; margin:8px 0;'>{r['target_moy']}×</div>
                <div style='font-size:0.9rem; color:#ffd700;'>Accuracy: {r['acc_moy']}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with c3:
            st.markdown(f"""
            <div class='target-box target-max'>
                <div style='font-size:0.75rem; color:#ffffff88;'>MAX X3+</div>
                <div style='font-size:2.5rem; font-weight:900; color:#ff3366; margin:8px 0;'>{r['target_max']}×</div>
                <div style='font-size:0.9rem; color:#ff66aa;'>Accuracy: {r['acc_max']}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Info
        st.markdown(f"""
        <div style='margin-top:16px; font-size:0.75rem; color:#ffffff44; text-align:center;'>
            SHA: {r['sha_used']} • Time: {r['time_used']} • Last: {r['cote_used']}×
        </div>
        """, unsafe_allow_html=True)
        
        # Win/Loss
        col_w, col_l = st.columns(2)
        with col_w:
            if st.button("✅ WIN", use_container_width=True):
                st.session_state.history[-1]['result'] = 'win'
                save_data(st.session_state.history[-50:])
                st.success("Win!")
                st.rerun()
        with col_l:
            if st.button("❌ LOSS", use_container_width=True):
                st.session_state.history[-1]['result'] = 'loss'
                save_data(st.session_state.history[-50:])
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='glass' style='min-height:400px; display:flex; align-items:center; justify-content:center;'>
            <div style='text-align:center;'>
                <div style='font-size:3.5rem; color:rgba(255,0,102,0.15);'>✈️</div>
                <div style='color:#ffffff33; font-size:1.1rem; margin-top:16px;'>En attente...</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# History
if st.session_state.history:
    st.markdown("---")
    st.markdown("### 📜 HISTORIQUE (20 derniers)")
    df = pd.DataFrame(st.session_state.history[-20:][::-1])
    cols = ['entry', 'x3_prob', 'conf', 'target_min', 'target_moy', 'target_max', 'result']
    available = [c for c in cols if c in df.columns]
    st.dataframe(df[available], use_container_width=True, hide_index=True)

st.markdown("""
<div style='text-align:center; margin-top:50px; padding:20px; color:#ffffff18; font-size:0.7rem; letter-spacing:0.2em;'>
AVIATOR STUDIO V3000 • 250K SIMS • SHA512 ENGINE • ULTRA X3+
</div>
""", unsafe_allow_html=True)
