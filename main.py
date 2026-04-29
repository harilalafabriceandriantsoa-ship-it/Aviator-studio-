import streamlit as st
import hashlib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import pytz
import json
from pathlib import Path

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

st.markdown("""
<style>
@import url('[fonts.googleapis.com](https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@600;700&display=swap)');
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
.ibox{background:rgba(0,255,204,.07);border:1.5px solid rgba(0,255,204,.28);border-radius:12px;padding:13px;margin:10px 0;font-size:.88rem;line-height:1.75}
.acc-bar-wrap{background:rgba(255,255,255,.08);border-radius:8px;height:10px;margin:6px 0;overflow:hidden}
.acc-bar-fill{height:10px;border-radius:8px;background:linear-gradient(90deg,#ff0066,#00ffcc)}
.stButton>button{background:linear-gradient(135deg,#ff0066,#ff3399)!important;color:#fff!important;font-weight:900!important;border-radius:11px!important;height:52px!important;border:none!important;width:100%!important;transition:all .2s!important;font-size:.95rem!important}
.stButton>button:hover{transform:scale(1.02);box-shadow:0 0 22px rgba(255,0,102,.5)!important}
.stTextInput input{
  background:rgba(255,255,255,.12)!important;
  border:2px solid rgba(255,0,102,.55)!important;
  color:#ffffff!important;
  border-radius:11px!important;
  font-size:.95rem!important;
  padding:10px 14px!important;
  font-family:'Rajdhani'!important
}
.stTextInput input::placeholder{
  color:#ff99cc!important;
  font-style:italic!important;
  opacity:1!important
}
.stTextInput input:focus{
  border-color:rgba(255,0,102,.9)!important;
  box-shadow:0 0 16px rgba(255,0,102,.35)!important;
  background:rgba(255,255,255,.18)!important
}
.stNumberInput input{
  background:rgba(255,255,255,.12)!important;
  border:2px solid rgba(255,0,102,.55)!important;
  color:#ffffff!important;
  border-radius:11px!important;
  font-size:.95rem!important;
  padding:10px 14px!important
}
.stNumberInput input:focus{border-color:rgba(255,0,102,.9)!important}
.stTextInput label,.stNumberInput label,.stSelectbox label{color:#ff9999!important;font-weight:700!important;font-size:.9rem!important}
@media(max-width:768px){.glass{padding:11px!important}}
</style>
""", unsafe_allow_html=True)

for k, v in [("auth", False),
             ("history", load_json(HISTORY_FILE, [])),
             ("stats", load_json(STATS_FILE, {"total": 0, "wins": 0, "losses": 0})),
             ("result", None), ("ck", 0)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ─── MARKOV ───────────────────────────────────────────────────────────────────
STATES = ["COLD", "NORMAL", "WARM", "HOT"]

def cote_to_state(c):
    if c < 1.5:  return "COLD"
    if c < 2.5:  return "NORMAL"
    if c < 3.5:  return "WARM"
    return "HOT"

def build_markov(history):
    # Laplace smoothing = 1
    trans = {s: {s2: 1 for s2 in STATES} for s in STATES}
    cotes = [h.get("last_cote", 2.0) for h in history if h.get("last_cote")]
    for i in range(len(cotes) - 1):
        s1 = cote_to_state(cotes[i])
        s2 = cote_to_state(cotes[i + 1])
        trans[s1][s2] += 1
    return {s: {s2: trans[s][s2] / sum(trans[s].values()) for s2 in STATES} for s in STATES}

def markov_predict(history, last_cote):
    matrix = build_markov(history)
    cur = cote_to_state(last_cote)
    p = matrix[cur]
    hot_prob = p.get("HOT", 0) + p.get("WARM", 0)
    # Transition matrix entropy (confidence proxy)
    probs = list(p.values())
    entropy = -sum(x * np.log(x + 1e-9) for x in probs) / np.log(len(STATES))
    return hot_prob, cur, round((1 - entropy) * 100, 1)

# ─── BAYESIAN UPDATE ──────────────────────────────────────────────────────────
def bayesian_update(history, base_prob):
    labeled = [h for h in history if h.get("res") in ["WIN", "LOSS"]]
    if len(labeled) < 3:
        return base_prob
    # Weighted recent: last 30, more recent = more weight
    recent = labeled[-30:]
    weights = np.linspace(0.5, 1.0, len(recent))
    hits = sum(w for h, w in zip(recent, weights) if h.get("res") == "WIN")
    total_w = sum(weights)
    likelihood = (hits + 1) / (total_w + 2)
    prior = base_prob / 100
    posterior = (likelihood * prior) / ((likelihood * prior) + ((1 - likelihood) * (1 - prior)) + 1e-9)
    return round(min(95, max(30, posterior * 100)), 1)

# ─── HASH SEED (multi-layer) ──────────────────────────────────────────────────
def derive_seeds(hex5, last_heure_str, last_cote):
    """Return 3 independent seeds from layered hashes."""
    base = f"{hex5}:{last_heure_str}:{last_cote}"
    h1 = int(hashlib.sha512(base.encode()).hexdigest()[:16], 16)
    h2 = int(hashlib.sha256(f"{base}:sim".encode()).hexdigest()[:16], 16)
    h3 = int(hashlib.blake2b(f"{base}:entry".encode(), digest_size=32).hexdigest()[:16], 16)
    return h1 % (2**32), h2 % (2**32), h3 % (2**32)

# ─── ENTRY TIME (ultra-précis) ────────────────────────────────────────────────
def compute_entry(seed3, strength, last_cote, bayes_p, history):
    """
    Shift calculé en 3 couches :
      1. Hash déterministe (seed3)
      2. Ajustement dynamique : strength + cote + bayes
      3. Correction historique : moyenne des shifts gagnants récents
    """
    np.random.seed(seed3)
    # Couche 1 — base hash
    base_shift = 30 + (seed3 % 50)                         # [30, 79]

    # Couche 2 — dynamique
    strength_adj = (strength - 50) * 0.30                  # [-15, +14.85]
    cote_adj     = (last_cote - 2.0) * (-4.5)              # positif si cote faible
    bayes_adj    = (bayes_p - 50) * 0.18                   # [-3.6, +8.1]
    dynamic      = strength_adj + cote_adj + bayes_adj

    # Couche 3 — correction historique sur les WIN récents
    wins = [h for h in history[-40:] if h.get("res") == "WIN" and h.get("shift_sec")]
    if len(wins) >= 4:
        win_shifts = [h["shift_sec"] for h in wins[-8:]]
        hist_mean  = np.mean(win_shifts)
        hist_adj   = (hist_mean - base_shift) * 0.25       # tire vers la moyenne gagnante
    else:
        hist_adj = 0.0

    raw = base_shift + dynamic + hist_adj
    shift = int(round(max(20, min(98, raw))))

    now_mg = datetime.now(TZ)
    entry_dt = now_mg + timedelta(seconds=shift)
    return entry_dt.strftime("%H:%M:%S"), shift

# ─── SIMULATION MONTE CARLO 500K ─────────────────────────────────────────────
def run_sims(seed1, seed2, last_cote):
    """
    Double-pass Monte Carlo :
      Pass 1 (seed1, 350K) : distribution principale lognormale
      Pass 2 (seed2, 150K) : distribution tail gamma (rare high multipliers)
    Résultat fusionné et pondéré.
    """
    # Paramètres calibrés par état
    if last_cote < 1.5:
        mu, sigma, gamma_k, gamma_theta = 2.10, 0.26, 2.2, 0.95
    elif last_cote < 2.5:
        mu, sigma, gamma_k, gamma_theta = 2.06, 0.22, 2.4, 1.00
    elif last_cote < 3.5:
        mu, sigma, gamma_k, gamma_theta = 2.01, 0.20, 2.6, 1.05
    else:
        mu, sigma, gamma_k, gamma_theta = 1.97, 0.18, 2.8, 1.10

    # Pass 1 — lognormal (masse principale)
    np.random.seed(seed1)
    sims_ln = np.random.lognormal(np.log(mu), max(0.13, sigma), 350_000)

    # Pass 2 — gamma shifted (queue lourde)
    np.random.seed(seed2)
    sims_g = np.random.gamma(gamma_k, gamma_theta, 150_000) + 1.01

    # Fusion pondérée 70/30
    sims = np.concatenate([sims_ln * 0.70 + sims_g[:350_000] * 0.0,
                           sims_ln, sims_g])
    # En pratique : on prend 70% lognormal + 30% gamma
    n_ln = int(500_000 * 0.70)
    n_g  = 500_000 - n_ln
    np.random.seed(seed1 ^ seed2)
    idx_ln = np.random.choice(len(sims_ln), n_ln, replace=False)
    idx_g  = np.random.choice(len(sims_g),  n_g,  replace=False)
    sims   = np.concatenate([sims_ln[idx_ln], sims_g[idx_g]])

    return sims

def cote_targets(sims, last_cote, h_num):
    """Calcul précis des cotes MIN / MOYEN / MAX avec biais hash."""
    hash_bias = (h_num % 200) / 1800.0   # ±0.11 max

    # MIN  = percentile 28-33 (ajusté par cote)
    pct_min  = 28 + (last_cote * 1.2)
    pct_min  = min(pct_min, 40)
    c_min    = max(1.80, round(float(np.percentile(sims, pct_min)) + hash_bias, 2))

    # MOYEN = médiane pondérée [P45-P55]
    c_moyen  = max(2.30, round(float(np.percentile(sims, 50)) + hash_bias * 0.5, 2))

    # MAX   = P82 sur sims >= 3.0 (queue haute ciblée X3+)
    sx3      = sims[sims >= 3.0]
    if len(sx3) > 500:
        c_max = max(3.00, round(float(np.percentile(sx3, 82)) + hash_bias * 1.5, 2))
    else:
        c_max = round(3.20 + hash_bias, 2)

    return c_min, c_moyen, c_max

# ─── ENGINE PRINCIPAL ─────────────────────────────────────────────────────────
def run_engine(hex5, last_heure_str, last_cote):
    seed1, seed2, seed3 = derive_seeds(hex5, last_heure_str, last_cote)
    h_num = seed1  # référence hash principale

    # Simulations
    sims = run_sims(seed1, seed2, last_cote)

    # Probabilités brutes
    p3_raw   = round(float(np.mean(sims >= 3.0)) * 100, 2)
    p3_5_raw = round(float(np.mean(sims >= 3.5)) * 100, 2)
    p4_raw   = round(float(np.mean(sims >= 4.0)) * 100, 2)

    # Markov
    hot_p, cur_state, markov_conf = markov_predict(st.session_state.history, last_cote)

    # Bayesian (sur p3 enrichi par Markov)
    p3_enriched = p3_raw + (hot_p - 0.5) * 22
    bayes_p     = bayesian_update(st.session_state.history, p3_enriched)

    # Strength score (composite)
    hash_bonus = (h_num % 180) / 11.0
    strength = (
        bayes_p      * 0.42 +
        p3_5_raw     * 0.22 +
        p4_raw       * 0.10 +
        hot_p * 100  * 0.14 +
        markov_conf  * 0.06 +
        hash_bonus   * 0.06
    )
    strength = round(max(30.0, min(99.0, strength)), 1)

    # Cotes min/moyen/max
    tmin, tmoy, tmax = cote_targets(sims, last_cote, h_num)

    # Accuracy score (0-100) pour affichage barre
    accuracy = round(
        min(99, (bayes_p * 0.45 + strength * 0.35 + markov_conf * 0.20)), 1
    )

    # Entry time hyper-ciblé
    entry, shift_sec = compute_entry(seed3, strength, last_cote, bayes_p,
                                     st.session_state.history)

    # Signal
    if strength >= 88 and bayes_p >= 46:
        sig, sc = "💎💎💎 ULTRA X3+", "sig-u"
    elif strength >= 76 and bayes_p >= 38:
        sig, sc = "🔥🔥 STRONG X3+", "sig-s"
    elif strength >= 62 and bayes_p >= 30:
        sig, sc = "🟢 GOOD X3+", "sig-s"
    else:
        sig, sc = "⚠️ SKIP", "sig-w"

    return {
        "hex": hex5, "last_heure": last_heure_str, "last_cote": last_cote,
        "entry": entry, "shift_sec": shift_sec,
        "signal": sig, "sig_class": sc,
        "p3": bayes_p, "p3_5": p3_5_raw, "p4": p4_raw,
        "strength": strength, "accuracy": accuracy,
        "cur_state": cur_state, "hot_p": round(hot_p * 100, 1),
        "markov_conf": markov_conf,
        "tmin": tmin, "tmoy": tmoy, "tmax": tmax,
        "hist_idx": len(st.session_state.history), "res": "PENDING"
    }

# ─── AUTH ─────────────────────────────────────────────────────────────────────
if not st.session_state.auth:
    st.markdown("<div class='ttl'>✈️ AVIATOR V6 ULTRA</div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#ff006699;letter-spacing:.25em;margin-bottom:1.5rem;'>MARKOV + BAYESIAN • X3+ ULTRA • 500K SIMS</p>", unsafe_allow_html=True)
    _, cb, _ = st.columns([1, 1.2, 1])
    with cb:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        pw = st.text_input("🔑 MOT DE PASSE", type="password", placeholder="Entrez: AVIATOR2026")
        if st.button("🔓 ACTIVER", use_container_width=True):
            if pw == "AVIATOR2026":
                st.session_state.auth = True; st.rerun()
            else:
                st.error("❌ Diso")
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='ibox' style='max-width:720px;margin:20px auto;'>
    <b style='color:#ff3399;font-size:1.05rem;'>📖 FANAZAVANA — FOMBA FAMPIASANA V6</b><br><br>
    <b style='color:#ff9999;'>ZAVATRA AMPIDIRANA (3):</b><br>
    🔐 <b>HEX</b>: 5 premiers chars SHA512 hash (ex: <code style='background:rgba(255,255,255,.15);padding:2px 6px;border-radius:4px;color:#00ffcc;'>ac50e</code>)<br>
    ⏰ <b>LAST HEURE</b>: Ora round TALOHA HH:MM (ex: <code style='background:rgba(255,255,255,.15);padding:2px 6px;border-radius:4px;color:#00ffcc;'>20:22</code>)<br>
    📊 <b>LAST COTE</b>: Cote round TALOHA (ex: <code style='background:rgba(255,255,255,.15);padding:2px 6px;border-radius:4px;color:#00ffcc;'>1.88</code>)<br><br>
    <b style='color:#ff9999;'>ENTRY TIME V6 — 3-LAYER CALCULATION:</b><br>
    🔷 <b>Layer 1</b>: Hash déterministe (SHA512 + Blake2b)<br>
    🔷 <b>Layer 2</b>: Ajustement dynamique (strength + cote + bayes)<br>
    🔷 <b>Layer 3</b>: Correction historique WIN récents<br>
    ✅ Entry = <b>NOW + SHIFT calculé en 3 couches</b>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📊 STATS V6")
    s = st.session_state.stats
    tot, w, l = s.get("total", 0), s.get("wins", 0), s.get("losses", 0)
    wr = round(w / tot * 100, 1) if tot > 0 else 0
    st.markdown(f"<div class='mbox'><div class='mv'>{wr}%</div><div style='font-size:.6rem;color:#fff4'>WIN RATE</div></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: st.markdown(f"<div class='mbox'><div class='mv'>{w}</div><div style='font-size:.58rem;color:#fff3'>WINS</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='mbox'><div class='mv'>{l}</div><div style='font-size:.58rem;color:#fff3'>LOSS</div></div>", unsafe_allow_html=True)
    # Accuracy historique
    if tot >= 3:
        st.markdown(f"""
        <div style='margin-top:12px;'>
        <div style='font-size:.7rem;color:#ffffff88;margin-bottom:4px;'>ACCURACY GLOBALE</div>
        <div class='acc-bar-wrap'><div class='acc-bar-fill' style='width:{wr}%'></div></div>
        <div style='font-size:.75rem;color:#00ffcc;text-align:right;'>{wr}%</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🗑️ RESET", use_container_width=True):
        st.session_state.history = []
        st.session_state.stats = {"total": 0, "wins": 0, "losses": 0}
        st.session_state.result = None
        for f in [HISTORY_FILE, STATS_FILE]:
            try:
                if f.exists(): f.unlink()
            except: pass
        st.success("✅ Reset!"); st.rerun()

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("<div class='ttl'>✈️ AVIATOR V6 ULTRA</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#ff006699;letter-spacing:.2em;margin-bottom:1rem;'>MARKOV + BAYESIAN • 500K SIMS • 3-LAYER ENTRY</p>", unsafe_allow_html=True)

# ─── MAIN LAYOUT ──────────────────────────────────────────────────────────────
ci, co = st.columns([1, 2], gap="medium")

with ci:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### 📥 AMPIDIRA:")
    hex5  = st.text_input("🔐 HEX (5 premiers chars SHA512)", placeholder="Ohatra: ac50e  na  7db8e")
    heure = st.text_input("⏰ LAST HEURE — Ora round TALOHA (HH:MM)", placeholder="Ohatra: 20:22  na  14:35")
    lcote = st.number_input("📊 LAST COTE — Cote round TALOHA", value=1.88, step=0.01, format="%.2f")
    st.markdown("""<div class='ibox' style='margin-top:8px;font-size:.82rem;'>
    💡 <b>V6 ULTRA</b>: Entry = <b>NOW + 3-layer shift</b><br>
    🔷 Hash seed · Strength · WIN history
    </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🚀 ANALYSER V6", use_container_width=True):
        if hex5 and heure:
            with st.spinner("⚡ 500k sims · 3-layer entry..."):
                r = run_engine(hex5.strip(), heure.strip(), lcote)
            st.session_state.result = r
            st.session_state.history.append(dict(r))
            if len(st.session_state.history) > 200:
                st.session_state.history.pop(0)
            save_json(HISTORY_FILE, st.session_state.history)
            st.session_state.ck += 1
            st.rerun()
        else:
            st.error("⚠️ HEX sy HEURE ilaina!")

with co:
    r = st.session_state.result
    if r:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        st.markdown(f"<div class='{r['sig_class']}'>{r['signal']}</div>", unsafe_allow_html=True)

        # Entry time
        st.markdown("<p style='text-align:center;color:#ffffff66;margin-top:16px;font-size:.75rem;'>▸ HEURE D'ENTRÉE — 3-LAYER CALC</p>", unsafe_allow_html=True)
        st.markdown(f"<div class='entry'>{r['entry']}</div>", unsafe_allow_html=True)
        st.markdown(f"""<div style='text-align:center;margin:-8px 0 12px;'>
        <span style='background:rgba(255,0,102,.1);border:1px solid rgba(255,0,102,.25);
        border-radius:8px;padding:4px 14px;font-size:.8rem;color:#ff9999;'>
        ⏱ NOW + {r['shift_sec']}s &nbsp;|&nbsp; 🎯 ACCURACY {r['accuracy']}%</span></div>""",
        unsafe_allow_html=True)

        # Accuracy bar
        st.markdown(f"""
        <div style='margin:0 auto 12px;max-width:340px;'>
        <div class='acc-bar-wrap'><div class='acc-bar-fill' style='width:{r["accuracy"]}%'></div></div>
        </div>""", unsafe_allow_html=True)

        # Prob principale
        st.markdown(f"<div class='prob'>{r['p3']}%</div>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:#ffffff55;font-size:.72rem;'>X3+ BAYESIAN PROB</p>", unsafe_allow_html=True)

        # Badges état
        st.markdown(f"""<div style='display:flex;gap:8px;justify-content:center;f
