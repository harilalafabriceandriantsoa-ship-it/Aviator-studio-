import streamlit as st
import hashlib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import pytz, json
from pathlib import Path

st.set_page_config(page_title="AVIATOR X3 V9", layout="wide", initial_sidebar_state="collapsed")
try:    D = Path(__file__).parent / "av9_data"
except: D = Path.cwd() / "av9_data"
D.mkdir(exist_ok=True, parents=True)
HF = D/"h.json"; SF = D/"s.json"

def sj(p,d):
    try:
        with open(p,"w") as f: json.dump(d,f,indent=2)
    except: pass
def lj(p,d):
    try:
        if p.exists():
            with open(p) as f: return json.load(f)
    except: pass
    return d

TZ = pytz.timezone("Indian/Antananarivo")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Inter:wght@400;500;600;700&display=swap');
html,body,.stApp{background:#05010f!important;color:#f0ecff;font-family:'Inter',sans-serif}
[data-testid="stSidebar"]{background:#08030f!important;border-right:1px solid rgba(155,77,255,.15)!important}
.block-container{padding-top:1.2rem!important;max-width:1100px}

/* Ireto ny fanitsiana ho an'ny Titre */
.main-title {
    font-family: 'Orbitron', sans-serif !important;
    font-size: clamp(1.4rem, 6vw, 2.8rem) !important;
    font-weight: 900 !important;
    text-align: center !important;
    color: #ffffff !important;
    margin: 10px 0 5px 0 !important;
    display: block !important;
    width: 100% !important;
    word-break: break-word !important;
}
.main-title span { color: #b57bff !important; }

.main-sub{text-align:center;font-size:.76rem;letter-spacing:.35em;color:#5a4a7a;text-transform:uppercase;margin-bottom:1.4rem}
.card{background:linear-gradient(160deg,#120828 0%,#0a0520 100%);border:1px solid rgba(155,77,255,.22);border-radius:20px;padding:clamp(14px,4vw,24px);margin-bottom:16px;box-shadow:0 4px 24px rgba(0,0,0,.4)}
.card-accent{background:linear-gradient(160deg,#1a0a2e 0%,#0a0520 100%);border:1px solid rgba(155,77,255,.35);border-radius:20px;padding:clamp(14px,4vw,24px);margin-bottom:16px;box-shadow:0 4px 28px rgba(100,40,200,.15)}
.section-lbl{font-size:.65rem;font-weight:700;letter-spacing:.35em;color:rgba(155,77,255,.65);text-transform:uppercase;margin-bottom:10px}
.sig-box{border-radius:16px;padding:14px 18px;text-align:center;font-family:'Orbitron';font-weight:900;letter-spacing:.06em;font-size:clamp(.88rem,3vw,1.25rem);margin-bottom:14px}
.sig-ultra{background:linear-gradient(135deg,#3d0066,#1a003d);border:2px solid #b57bff;color:#d4aaff;box-shadow:0 0 30px rgba(181,123,255,.2)}
.sig-strong{background:linear-gradient(135deg,#003344,#001a22);border:2px solid #00ddcc;color:#66ffee;box-shadow:0 0 25px rgba(0,221,204,.12)}
.sig-mod{background:rgba(255,170,0,.08);border:1.5px solid rgba(255,170,0,.35);color:#ffcc44}
.sig-skip{background:rgba(60,60,60,.3);border:1.5px solid rgba(100,100,100,.25);color:#666}
.tour-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:12px 0}
.tour-card{border-radius:16px;padding:16px;text-align:center}
.tour-1{background:linear-gradient(135deg,rgba(181,123,255,.15),rgba(100,40,200,.06));border:1.5px solid rgba(181,123,255,.45)}
.tour-2{background:linear-gradient(135deg,rgba(0,221,204,.12),rgba(0,150,140,.05));border:1.5px solid rgba(0,221,204,.4)}
.tour-lbl{font-size:.62rem;letter-spacing:.22em;color:rgba(255,255,255,.4);text-transform:uppercase;margin-bottom:5px}
.tour-t{font-family:'Orbitron';font-size:clamp(1.6rem,6vw,2.4rem);font-weight:900;line-height:1.1}
.tour-c{font-size:.75rem;font-weight:700;margin-top:5px}
.tour-targets{margin-top:10px;display:flex;gap:6px;justify-content:center;flex-wrap:wrap}
.tgt{border-radius:10px;padding:5px 10px;text-align:center;min-width:56px}
.tgt-v{font-family:'Orbitron';font-size:.86rem;font-weight:900}
.tgt-l{font-size:.52rem;color:rgba(255,255,255,.4);letter-spacing:.08em;text-transform:uppercase}
.tgt-a{font-size:.63rem;font-weight:700;margin-top:1px}
.prob-center{text-align:center;padding:12px 0}
.prob-val{font-family:'Orbitron';font-size:clamp(3rem,12vw,4.8rem);font-weight:900;color:#b57bff;line-height:1}
.prob-lbl{font-size:.68rem;letter-spacing:.2em;color:rgba(155,77,255,.5);text-transform:uppercase;margin-top:4px}
.tags-row{display:flex;flex-wrap:wrap;gap:6px;justify-content:center;margin:10px 0}
.tag{background:rgba(181,123,255,.1);border:1px solid rgba(181,123,255,.25);border-radius:20px;padding:4px 12px;font-size:.76rem;color:#c4a8ff}
.tag-teal{background:rgba(0,221,204,.08);border:1px solid rgba(0,221,204,.25);border-radius:20px;padding:4px 12px;font-size:.76rem;color:#66ffee}
.stat-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.stat-c{background:rgba(181,123,255,.07);border:1px solid rgba(181,123,255,.15);border-radius:14px;padding:10px;text-align:center}
.stat-v{font-family:'Orbitron';font-size:1.25rem;font-weight:900;color:#b57bff}
.stat-l{font-size:.52rem;color:rgba(255,255,255,.3);letter-spacing:.12em;text-transform:uppercase;margin-top:2px}
.empty-state{min-height:340px;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:12px;opacity:.25}
.stTextInput input, .stNumberInput input{background:#1a1033 !important;border:2px solid #b57bff !important;color:#ffffff !important;border-radius:13px !important;font-size:1rem !important;padding:12px 16px !important}
.stTextInput input::placeholder, .stNumberInput input::placeholder{color:#a0a0a0 !important;opacity:1 !important;font-style:italic!important}
.stTextInput input:focus, .stNumberInput input:focus{border-color:rgba(181,123,255,.7)!important;box-shadow:0 0 0 3px rgba(181,123,255,.12)!important}
.stButton>button{background:linear-gradient(135deg,#7722cc,#5511aa)!important;color:#fff!important;font-weight:700!important;border-radius:14px!important;height:52px!important;border:none!important;width:100%!important;font-family:'Inter'!important;font-size:.93rem!important;transition:all .2s!important;box-shadow:0 4px 20px rgba(119,34,204,.35)!important}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 28px rgba(119,34,204,.5)!important}
@media(max-width:768px){.card,.card-accent{padding:14px!important}.tour-grid{grid-template-columns:1fr 1fr}}
</style>
""", unsafe_allow_html=True)

# ... (Ny ambin'ny code-nao dia tsy niova) ...
