import streamlit as st
import hashlib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import pytz
import json
from pathlib import Path

# --- CONFIGURATION ---
st.set_page_config(page_title="AVIATOR V6 ULTRA", layout="wide", initial_sidebar_state="collapsed")

try:
    DATA_DIR = Path(__file__).parent / "aviator_v6_data"
except:
    DATA_DIR = Path.cwd() / "aviator_v6_data"

DATA_DIR.mkdir(exist_ok=True, parents=True)
HISTORY_FILE = DATA_DIR / "history.json"
STATS_FILE   = DATA_DIR / "stats.json"

def save_json(p, d):
    try:
        with open(p, "w", encoding="utf-8") as f: json.dump(d, f, indent=2)
    except: pass

def load_json(p, d):
    try:
        if p.exists():
            with open(p, "r", encoding="utf-8") as f: return json.load(f)
    except: pass
    return d

TZ = pytz.timezone("Indian/Antananarivo")

# --- STYLING ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@600;700&display=swap');
.stApp{background:radial-gradient(ellipse at 50% 0%,#1a0033 0%,#000008 60%,#001a1a 100%);color:#e0fbfc;font-family:'Rajdhani',sans-serif}
.ttl{font-family:'Orbitron';font-size:clamp(1.8rem,7vw,3rem);font-weight:900;text-align:center;background:linear-gradient(90deg,#ff0066,#ff3399,#00ffcc);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:2px}
.glass{background:rgba(10,0,25,.9);border:2px solid rgba(255,0,102,.4);border-radius:18px;padding:clamp(12px,4vw,22px);backdrop-filter:blur(12px);margin-bottom:16px}
.entry{font-family:'Orbitron';font-size:clamp(3rem,12vw,5rem);font-weight:900;text-align:center;color:#ff0066;text-shadow:0 0 30px #ff0066;margin:16px 0}
.prob{font-size:clamp(2.5rem,10vw,4rem);font-weight:900;font-family:'Orbitron';text-align:center;color:#00ffcc;margin:10px 0}
.sig-u{text-align:center;font-family:'Orbitron';font-size:clamp(1rem,3.5vw,1.6rem);font-weight:900;color:#ff0066;text-shadow:0 0 20px #ff0066;padding:10px}
.sig-s{text-align:center;font-family:'Orbitron';font-size:clamp(.9rem,3vw,1.4rem);font-weight:700;color:#00ffcc;padding:10px}
.sig-w{text-align:center;font-family:'Orbitron';font-size:clamp(.9rem,3vw,1.3rem);color:#ff6600;padding:10px}
.tbox{background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.12);border-radius:14px;padding:14px;text-align:center;margin:4px}
.tv{font-size:clamp(1.4rem,5vw,2.2rem);font-weight:900;font-family:'Orbitron'}
.tl{font-size:.65rem;color:rgba(255,255,255,.5);letter-spacing:.12em;text-transform:uppercase;margin-top:3px}
.mbox{background:rgba(255,0,102,.08);border:1px solid rgba(255,0,102,.25);border-radius:10px;padding:10px;text-align:center;margin:4px 0}
.mv{font-size:1.4rem;font-weight:900;font-family:'Orbitron';color:#ff0066}
.acc-bar-wrap{background:rgba(255,255,255,.08);border-radius:8px;height:10px;margin:6px 0;overflow:hidden}
.acc-bar-fill{height:10px;border-radius:8px;background:linear-gradient(90deg,#ff0066,#00ffcc)}
.stButton>button{background:linear-gradient(135deg,#ff0066,#ff3399)!important;color:#fff!important;font-weight:900!important;border-radius:11px!important;height:52px!important;width:100%!important}
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
for k, v in [("auth", False), ("history", load_json(HISTORY_FILE, [])),
             ("stats", load_json(STATS_FILE, {"total": 0, "wins": 0, "losses": 0})),
             ("result", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# --- CORE LOGIC (MARKOV & BAYESIAN) ---
STATES = ["COLD", "NORMAL", "WARM", "HOT"]

def cote_to_state(c):
    if c < 1.5: return "COLD"
    if c < 2.5: return "NORMAL"
    if c < 3.5: return "WARM"
    return "HOT"

def build_markov(history):
    trans = {s: {s2: 1 for s2 in STATES} for s in STATES}
    cotes = [h.get("last_cote", 2.0) for h in history if h.get("last_cote")]
    for i in range(len(cotes) - 1):
        s1, s2 = cote_to_state(cotes[i]), cote_to_state(cotes[i+1])
        trans[s1][s2] += 1
    return {s: {s2: trans[s][s2] / sum(trans[s].values()) for s2 in STATES} for s in STATES}

def markov_predict(history, last_cote):
    matrix = build_markov(history)
    cur = cote_to_state(last_cote)
    p = matrix[cur]
    hot_prob = p.get("HOT", 0) + p.get("WARM", 0)
    entropy = -sum(x * np.log(x + 1e-9) for x in p.values()) / np.log(len(STATES))
    return hot_prob, cur, round((1 - entropy) * 100, 1)

def bayesian_update(history, base_prob):
    labeled = [h for h in history if h.get("res") in ["WIN", "LOSS"]]
    if len(labeled) < 3: return base_prob
    recent = labeled[-30:]
    weights = np.linspace(0.5, 1.0, len(recent))
    hits = sum(w for h, w in zip(recent, weights) if h.get("res") == "WIN")
    likelihood = (hits + 1) / (sum(weights) + 2)
    prior = base_prob / 100
    posterior = (likelihood * prior) / ((likelihood * prior) + ((1 - likelihood) * (1 - prior)) + 1e-9)
    return round(min(95, max(30, posterior * 100)), 1)

def derive_seeds(hex5, h_str, lc):
    base = f"{hex5}:{h_str}:{lc}"
    h1 = int(hashlib.sha512(base.encode()).hexdigest()[:16], 16)
    h2 = int(hashlib.sha256(f"{base}:sim".encode()).hexdigest()[:16], 16)
    h3 = int(hashlib.blake2b(f"{base}:entry".encode(), digest_size=32).hexdigest()[:16], 16)
    return h1 % (2**32), h2 % (2**32), h3 % (2**32)

def compute_entry(seed3, strength, lc, bayes_p, history):
    np.random.seed(seed3)
    base_shift = 30 + (seed3 % 50)
    dynamic = (strength-50)*0.3 + (lc-2.0)*(-4.5) + (bayes_p-50)*0.18
    wins = [h for h in history[-40:] if h.get("res") == "WIN" and h.get("shift_sec")]
    hist_adj = (np.mean([h["shift_sec"] for h in wins[-8:]]) - base_shift) * 0.25 if len(wins) >= 4 else 0
    shift = int(round(max(20, min(98, base_shift + dynamic + hist_adj))))
    entry_dt = datetime.now(TZ) + timedelta(seconds=shift)
    return entry_dt.strftime("%H:%M:%S"), shift

def run_sims(s1, s2, lc):
    if lc < 1.5: mu, sigma, gk, gt = 2.10, 0.26, 2.2, 0.95
    elif lc < 2.5: mu, sigma, gk, gt = 2.06, 0.22, 2.4, 1.00
    elif lc < 3.5: mu, sigma, gk, gt = 2.01, 0.20, 2.6, 1.05
    else: mu, sigma, gk, gt = 1.97, 0.18, 2.8, 1.10
    np.random.seed(s1); s_ln = np.random.lognormal(np.log(mu), max(0.13, sigma), 350_000)
    np.random.seed(s2); s_g = np.random.gamma(gk, gt, 150_000) + 1.01
    return np.concatenate([s_ln[np.random.choice(350_000, 350_000, replace=False)], s_g])

def run_engine(hex5, h_str, lc):
    s1, s2, s3 = derive_seeds(hex5, h_str, lc)
    sims = run_sims(s1, s2, lc)
    p3_raw = float(np.mean(sims >= 3.0)) * 100
    hot_p, cur, mk_conf = markov_predict(st.session_state.history, lc)
    bayes_p = bayesian_update(st.session_state.history, p3_raw + (hot_p - 0.5) * 22)
    strength = round(max(30, min(99, bayes_p*0.42 + float(np.mean(sims>=3.5))*22 + hot_p*14 + mk_conf*6 + (s1%180)/11)), 1)
    acc = round(min(99, (bayes_p * 0.45 + strength * 0.35 + mk_conf * 0.20)), 1)
    entry, shift = compute_entry(s3, strength, lc, bayes_p, st.session_state.history)
    sig, sc = ("💎 ULTRA X3+", "sig-u") if strength >= 88 else ("🔥🔥 STRONG X3+", "sig-s") if strength >= 76 else ("🟢 GOOD X3+", "sig-s") if strength >= 62 else ("⚠️ SKIP", "sig-w")
    return {"entry": entry, "shift_sec": shift, "signal": sig, "sig_class": sc, "p3": bayes_p, "p3_5": round(float(np.mean(sims>=3.5))*100,1), "p4": round(float(np.mean(sims>=4.0))*100,1), "strength": strength, "accuracy": acc, "cur_state": cur, "hot_p": round(hot_p*100, 1), "markov_conf": mk_conf, "tmin": round(float(np.percentile(sims, 32)), 2), "tmoy": round(float(np.percentile(sims, 50)), 2), "tmax": round(float(np.percentile(sims, 85)), 2), "res": "PENDING", "hist_idx": len(st.session_state.history), "last_cote": lc}

# --- UI LOGIC ---
if not st.session_state.auth:
    st.markdown("<div class='ttl'>✈️ AVIATOR V6 ULTRA</div>", unsafe_allow_html=True)
    _, cb, _ = st.columns([1, 1.2, 1])
    with cb:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        pw = st.text_input("🔑 MOT DE PASSE", type="password")
        if st.button("🔓 ACTIVER"):
            if pw == "AVIATOR2026": st.session_state.auth = True; st.rerun()
            else: st.error("❌ Diso")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- MAIN APP ---
with st.sidebar:
    st.markdown("### 📊 STATS V6")
    s = st.session_state.stats
    wr = round(s['wins'] / max(1, s['total']) * 100, 1)
    st.markdown(f"<div class='mbox'><div class='mv'>{wr}%</div><div style='font-size:.6rem;'>WIN RATE</div></div>", unsafe_allow_html=True)
    if st.button("🗑️ RESET"):
        st.session_state.history = []; st.session_state.stats = {"total":0,"wins":0,"losses":0}; st.rerun()

st.markdown("<div class='ttl'>✈️ AVIATOR V6 ULTRA</div>", unsafe_allow_html=True)
ci, co = st.columns([1, 2], gap="medium")

with ci:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    h5 = st.text_input("🔐 HEX", placeholder="ac50e")
    hr = st.text_input("⏰ LAST HEURE", placeholder="20:22")
    lc = st.number_input("📊 LAST COTE", value=1.88, step=0.01)
    if st.button("🚀 ANALYSER V6"):
        if h5 and hr:
            res = run_engine(h5.strip(), hr.strip(), lc)
            st.session_state.result = res
            st.session_state.history.append(res)
            save_json(HISTORY_FILE, st.session_state.history); st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with co:
    r = st.session_state.result
    if r:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        st.markdown(f"<div class='{r['sig_class']}'>{r['signal']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='entry'>{r['entry']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='prob'>{r['p3']}%</div>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"<div class='tbox'><div class='tl'>MIN</div><div class='tv'>{r['tmin']}x</div></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='tbox'><div class='tl'>MOYEN</div><div class='tv'>{r['tmoy']}x</div></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='tbox'><div class='tl'>MAX</div><div class='tv'>{r['tmax']}x</div></div>", unsafe_allow_html=True)
        
        cw, cl = st.columns(2)
        if cw.button("✅ WIN"):
            st.session_state.history[r['hist_idx']]['res'] = "WIN"
            st.session_state.stats['total'] += 1; st.session_state.stats['wins'] += 1
            save_json(STATS_FILE, st.session_state.stats); st.rerun()
        if cl.button("❌ LOSS"):
            st.session_state.history[r['hist_idx']]['res'] = "LOSS"
            st.session_state.stats['total'] += 1; st.session_state.stats['losses'] += 1
            save_json(STATS_FILE, st.session_state.stats); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.history:
    st.markdown("---")
    st.markdown("### 📜 LOGS V6")
    df = pd.DataFrame([{
        "Entry": h.get("entry"), "X3%": h.get("p3"), 
        "Acc%": h.get("accuracy"), "State": h.get("cur_state"), "Res": h.get("res")
    } for h in reversed(st.session_state.history[-10:])])
    st.dataframe(df, use_container_width=True, hide_index=True)
