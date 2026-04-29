import streamlit as st
import hashlib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import pytz, json
from pathlib import Path

st.set_page_config(page_title="AVIATOR X3 V6", layout="wide", initial_sidebar_state="collapsed")

try:    D = Path(__file__).parent / "av6_data"
except: D = Path.cwd() / "av6_data"
D.mkdir(exist_ok=True, parents=True)
HF = D / "h.json"; SF = D / "s.json"

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

# ─── CSS AMBOARINA NY SORATRA (MAINTY STYLÉ) ───
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@600;700&display=swap');
.stApp{background:radial-gradient(ellipse at 40% 0%,#1a002288 0%,#050008 65%);color:#f0eaff;font-family:'Rajdhani',sans-serif}
.ttl{font-family:'Orbitron';font-size:clamp(2rem,8vw,3.2rem);font-weight:900;text-align:center;background:linear-gradient(90deg,#ff0066,#ff66aa,#00ffcc);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:4px}
.sub{text-align:center;color:#ff006677;font-size:.8rem;letter-spacing:.3em;margin-bottom:1.5rem}
.card{background:rgba(12,0,28,.92);border:2px solid rgba(255,0,102,.35);border-radius:18px;padding:clamp(14px,4vw,24px);backdrop-filter:blur(14px);margin-bottom:16px}
.etime{font-family:'Orbitron';font-size:clamp(3.5rem,13vw,5.5rem);font-weight:900;text-align:center;color:#ff0066;text-shadow:0 0 40px #ff0066;margin:20px 0;animation:ep 2s ease-in-out infinite}
@keyframes ep{0%,100%{text-shadow:0 0 30px #ff0066}50%{text-shadow:0 0 60px #ff0066,0 0 90px #ff006688}}
.pct{font-size:clamp(3rem,11vw,4.5rem);font-weight:900;font-family:'Orbitron';text-align:center;color:#00ffcc;margin:8px 0}
.sig-u{text-align:center;font-family:'Orbitron';font-size:clamp(1rem,3.5vw,1.6rem);font-weight:900;color:#ff0066;text-shadow:0 0 20px #ff006688;padding:12px}
.sig-s{text-align:center;font-family:'Orbitron';font-size:clamp(.95rem,3vw,1.4rem);font-weight:700;color:#00ffcc;padding:10px}
.sig-w{text-align:center;font-family:'Orbitron';font-size:clamp(.9rem,3vw,1.2rem);color:#ffaa00;padding:10px}
.sig-x{text-align:center;font-family:'Orbitron';font-size:clamp(.9rem,3vw,1.1rem);color:#888;padding:8px}
.tbox{background:rgba(255,255,255,.06);border-radius:14px;padding:14px;text-align:center;margin:4px}
.tv{font-size:clamp(1.5rem,5.5vw,2.4rem);font-weight:900;font-family:'Orbitron'}
.tl{font-size:.62rem;color:rgba(255,255,255,.38);letter-spacing:.12em;text-transform:uppercase;margin-top:3px}
.ta{font-size:.72rem;color:#00ff88;margin-top:4px;font-weight:700}
.tag{background:rgba(255,0,102,.12);border:1px solid rgba(255,0,102,.35);border-radius:8px;padding:4px 12px;font-size:.82rem;display:inline-block;margin:3px;color:#ffaacc}
.tag-g{background:rgba(0,255,204,.1);border:1px solid rgba(0,255,204,.3);border-radius:8px;padding:4px 12px;font-size:.82rem;display:inline-block;margin:3px;color:#aaffee}
.sb{background:rgba(255,0,102,.07);border:1px solid rgba(255,0,102,.2);border-radius:10px;padding:10px;text-align:center;margin:4px 0}
.sv{font-size:1.4rem;font-weight:900;font-family:'Orbitron';color:#ff0066}
.sl{font-size:.58rem;color:rgba(255,255,255,.35);letter-spacing:.12em;text-transform:uppercase;margin-top:2px}
.ib{background:rgba(0,255,204,.06);border-left:3px solid #00ffcc;border-radius:0 10px 10px 0;padding:12px 16px;margin:8px 0;font-size:.9rem;line-height:1.8}
.stButton>button{background:linear-gradient(135deg,#ff0066,#cc0055)!important;color:#fff!important;font-weight:900!important;border-radius:12px!important;height:52px!important;border:none!important;width:100!important;font-family:'Rajdhani'!important;font-size:.95rem!important;letter-spacing:.04em!important;transition:all .2s!important}
.stButton>button:hover{transform:scale(1.02);box-shadow:0 0 24px rgba(255,0,102,.5)!important}

/* --- KAJY HO AN'NY INPUT (SORATRA MAINTY SY STYLÉ) --- */
.stTextInput label, .stNumberInput label {
    color:#ffaacc!important; 
    font-weight:700!important; 
    font-size:.88rem!important;
}
.stTextInput input, .stNumberInput input {
    background: #ffffff !important; /* Fotsy tanteraka ny background */
    color: #000000 !important; /* Mainty tanteraka ny soratra */
    border: 2px solid #ff0066 !important;
    border-radius: 11px !important;
    font-size: 1rem !important;
    font-weight: 800 !important; /* Matevina kely */
    font-family: 'Rajdhani', sans-serif !important;
    opacity: 1 !important;
}
.stTextInput input::placeholder {
    color: #333333 !important; /* Placeholder somary mainty */
    opacity: 0.7 !important;
}
.stTextInput input:focus {
    box-shadow: 0 0 15px rgba(255,0,102,0.5) !important;
    border-color: #00ffcc !important;
}
@media(max-width:768px){.card{padding:12px!important}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

for k,v in [("auth",False),("H",lj(HF,[])),("S",lj(SF,{"t":0,"w":0,"l":0})),("R",None),("ck",0)]:
    if k not in st.session_state: st.session_state[k]=v

# ─── MARKOV ───
ST=["COLD","NORMAL","WARM","HOT"]
def s2st(c):
    if c<1.5: return "COLD"
    if c<2.5: return "NORMAL"
    if c<3.5: return "WARM"
    return "HOT"

def markov(h, lc):
    tr={s:{s2:1 for s2 in ST} for s in ST}
    cs=[x.get("lc",2.0) for x in h if x.get("lc")]
    for i in range(len(cs)-1):
        tr[s2st(cs[i])][s2st(cs[i+1])]+=1
    mx={s:{s2:tr[s][s2]/sum(tr[s].values()) for s2 in ST} for s in ST}
    cur=s2st(lc)
    hp=mx[cur].get("HOT",0)+mx[cur].get("WARM",0)
    return round(hp*100,1), cur

# ─── BAYESIAN ───
def bayes(h, base):
    lb=[x for x in h if x.get("res") in ["W","L"]]
    if len(lb)<3: return base
    rc=lb[-20:]
    w=sum(1 for x in rc if x.get("res")=="W")
    n=len(rc)
    lik=(w+1)/(n+2)
    pr=base/100
    po=(lik*pr)/((lik*pr)+((1-lik)*(1-pr))+1e-9)
    return round(min(95,max(30,po*100)),1)

# ─── ENGINE ───
def engine(hex5, tin, lc):
    fh=hashlib.sha512(f"{hex5}:{tin}:{lc}".encode()).hexdigest()
    hn=int(fh[:16],16)
    np.random.seed(int((hn&0xFFFFFFFF)+(lc*1000))%(2**32))

    if lc<1.5:   bs,sg=2.12,0.24
    elif lc<2.5: bs,sg=2.06,0.21
    elif lc<3.5: bs,sg=2.00,0.19
    else:        bs,sg=1.96,0.18
    bs+=(hn%180)/1200; sg=max(0.14,sg-lc*0.0022)

    sm=np.random.lognormal(np.log(bs),sg,400_000)
    p3=round(float(np.mean(sm>=3.0))*100,2)
    p35=round(float(np.mean(sm>=3.5))*100,2)
    p4=round(float(np.mean(sm>=4.0))*100,2)
    sx=sm[sm>=3.0]
    tmin=max(2.0,round(float(np.percentile(sm,30)),2))
    tmoy=max(2.5,round(float(np.percentile(sm,50)),2))
    tmax=max(3.0,round(float(np.percentile(sx,85)),2)) if len(sx)>0 else 3.8

    hp,cur=markov(st.session_state.H, lc)
    bp=bayes(st.session_state.H, p3+(hp/100-0.5)*20)
    str_=round(bp*0.50+p35*0.20+p4*0.10+(hn%200)/12+(hp/100)*15,1)
    str_=max(30.0,min(99.0,str_))

    now=datetime.now(TZ)
    hs=(hn%60)-30          
    sb=int(str_*0.28)      
    cf=int(lc*3)           
    pp=int((48-bp)*0.38)   
    shift=max(15,min(90,38+hs+sb+cf-pp))
    ent=(now+timedelta(seconds=shift)).strftime("%H:%M:%S")

    if str_>=88 and bp>=44:   sig,sc="💎💎💎 ULTRA X3+ — BUY","sig-u"
    elif str_>=76 and bp>=36: sig,sc="🔥🔥 STRONG X3+ — GO","sig-s"
    elif str_>=62 and bp>=28: sig,sc="🟢 GOOD X3+ — WATCH","sig-w"
    else:                     sig,sc="⚠️ SKIP CE ROUND","sig-x"

    return {"lc":lc,"ent":ent,"sig":sig,"sc":sc,
            "bp":bp,"p35":p35,"p4":p4,"str":str_,
            "cur":cur,"hp":hp,"tmin":tmin,"tmoy":tmoy,"tmax":tmax,
            "res":None,"hi":len(st.session_state.H)}

# ─── LOGIN ───
if not st.session_state.auth:
    st.markdown("<div class='ttl'>✈️ AVIATOR X3 V6</div>",unsafe_allow_html=True)
    st.markdown("<div class='sub'>MARKOV + BAYESIAN • ULTRA X3+</div>",unsafe_allow_html=True)
    _,cb,_=st.columns([1,1.2,1])
    with cb:
        st.markdown("<div class='card'>",unsafe_allow_html=True)
        pw=st.text_input("🔑 MOT DE PASSE",type="password",placeholder="Entrez: AVIATOR2026")
        if st.button("🔓 ACTIVER",use_container_width=True):
            if pw=="AVIATOR2026": st.session_state.auth=True; st.rerun()
            else: st.error("❌ Code incorrect")
        st.markdown("</div>",unsafe_allow_html=True)
    st.stop()

# ─── SIDEBAR ───
with st.sidebar:
    st.markdown("### ✈️ AVIATOR V6")
    S=st.session_state.S
    t,w,l=S.get("t",0),S.get("w",0),S.get("l",0)
    wr=round(w/t*100,1) if t>0 else 0
    st.markdown(f"<div class='sb'><div class='sv'>{wr}%</div><div class='sl'>WIN RATE</div></div>",unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1: st.markdown(f"<div class='sb'><div class='sv'>{w}</div><div class='sl'>WINS</div></div>",unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='sb'><div class='sv'>{l}</div><div class='sl'>LOSS</div></div>",unsafe_allow_html=True)
    if st.button("🗑️ RESET",use_container_width=True):
        st.session_state.H=[];st.session_state.S={"t":0,"w":0,"l":0};st.session_state.R=None
        try:
            if HF.exists(): HF.unlink()
            if SF.exists(): SF.unlink()
        except: pass
        st.success("✅ Reset!"); st.rerun()

# ─── MAIN ───
st.markdown("<div class='ttl'>✈️ AVIATOR X3 V6</div>",unsafe_allow_html=True)
st.markdown("<div class='sub'>MARKOV + BAYESIAN • 400K SIMS • ULTRA X3+</div>",unsafe_allow_html=True)

ci,co=st.columns([1,2],gap="medium")

with ci:
    st.markdown("<div class='card'>",unsafe_allow_html=True)
    st.markdown("<p style='font-family:Orbitron;font-size:.85rem;color:#ff0066;margin-bottom:12px;'>📥 PARAMÈTRES</p>",unsafe_allow_html=True)
    h5=st.text_input("🔐 HEX SHA512",placeholder="Ex: ac50e")
    ti=st.text_input("⏰ TIME ROUND",placeholder="Ex: 20:22:24")
    lc=st.number_input("📊 LAST COTE",value=1.88,step=0.01,format="%.2f")
    st.markdown("</div>",unsafe_allow_html=True)
    if st.button("🚀 ANALYSER X3+",use_container_width=True):
        if h5 and ti:
            with st.spinner("⚡ 400k sims..."):
                r=engine(h5.strip(),ti.strip(),lc)
            st.session_state.R=r
            st.session_state.H.append(dict(r))
            sj(HF,st.session_state.H); st.rerun()

with co:
    r=st.session_state.R
    if r:
        st.markdown("<div class='card'>",unsafe_allow_html=True)
        st.markdown(f"<div class='{r['sc']}'>{r['sig']}</div>",unsafe_allow_html=True)
        st.markdown(f"<div class='etime'>{r['ent']}</div>",unsafe_allow_html=True)
        st.markdown(f"<div class='pct'>{r['bp']}%</div>",unsafe_allow_html=True)
        c1,c2,c3=st.columns(3)
        with c1: st.markdown(f"<div class='tbox'><div class='tl'>MIN SAFE</div><div class='tv' style='color:#00ffcc;'>{r['tmin']}×</div></div>",unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='tbox'><div class='tl'>MOYEN</div><div class='tv' style='color:#ffd700;'>{r['tmoy']}×</div></div>",unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='tbox'><div class='tl'>MAX X3+</div><div class='tv' style='color:#ff3366;'>{r['tmax']}×</div></div>",unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        cw,cl2=st.columns(2)
        with cw:
            if st.button("✅ WIN",use_container_width=True,key="bw"):
                idx=r.get("hi",-1)
                if 0<=idx<len(st.session_state.H):
                    st.session_state.H[idx]["res"]="W"; sj(HF,st.session_state.H)
                st.session_state.S["t"]+=1; st.session_state.S["w"]+=1
                sj(SF,st.session_state.S); st.rerun()
        with cl2:
            if st.button("❌ LOSS",use_container_width=True,key="bl"):
                idx=r.get("hi",-1)
                if 0<=idx<len(st.session_state.H):
                    st.session_state.H[idx]["res"]="L"; sj(HF,st.session_state.H)
                st.session_state.S["t"]+=1; st.session_state.S["l"]+=1
                sj(SF,st.session_state.S); st.rerun()
        st.markdown("</div>",unsafe_allow_html=True)

if st.session_state.H:
    st.markdown("---"); st.markdown("### 📜 HISTORIQUE")
    df=pd.DataFrame([{"Entry":x.get("ent",""),"X3%":x.get("bp",""),"Res":"WIN" if x.get("res")=="W" else "LOSS" if x.get("res")=="L" else "—"} for x in reversed(st.session_state.H[-10:])])
    st.dataframe(df,use_container_width=True,hide_index=True)

st.markdown("<div style='text-align:center;margin-top:24px;color:rgba(255,255,255,.1);font-size:.56rem;'>AVIATOR X3 V6 • MARKOV+BAYESIAN • 400K SIMS</div>",unsafe_allow_html=True)
