import streamlit as st
import hashlib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import pytz, json
from pathlib import Path

st.set_page_config(page_title="AVIATOR X3 V7", layout="wide", initial_sidebar_state="collapsed")
try:    D = Path(__file__).parent / "av7_data"
except: D = Path.cwd() / "av7_data"
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
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@600;700&display=swap');
.stApp{background:radial-gradient(ellipse at 40% 0%,#1a002288 0%,#050008 65%);color:#f0eaff;font-family:'Rajdhani',sans-serif}

/* Hanitsiana ny soratra rehefa adika (Selection/Copy) */
::selection { background: #00ffcc; color: #000 !important; }

.ttl{font-family:'Orbitron';font-size:clamp(2rem,8vw,3rem);font-weight:900;text-align:center;background:linear-gradient(90deg,#ff0066,#ff66aa,#00ffcc);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:4px}
.sub{text-align:center;color:#ff006677;font-size:.8rem;letter-spacing:.3em;margin-bottom:1.5rem}
.card{background:rgba(12,0,28,.92);border:2px solid rgba(255,0,102,.35);border-radius:18px;padding:clamp(14px,4vw,22px);backdrop-filter:blur(14px);margin-bottom:16px}
.etime{font-family:'Orbitron';font-size:clamp(3rem,12vw,5rem);font-weight:900;text-align:center;color:#ff0066;text-shadow:0 0 40px #ff0066;margin:18px 0;animation:ep 2s ease-in-out infinite}

@keyframes ep{0%,100%{text-shadow:0 0 30px #ff0066}50%{text-shadow:0 0 60px #ff0066,0 0 90px #ff006688}}
.pct{font-size:clamp(2.8rem,10vw,4.2rem);font-weight:900;font-family:'Orbitron';text-align:center;color:#00ffcc;margin:8px 0}
.sig-u{text-align:center;font-family:'Orbitron';font-size:clamp(.95rem,3.5vw,1.5rem);font-weight:900;color:#ff0066;text-shadow:0 0 20px #ff006688;padding:12px}
.sig-s{text-align:center;font-family:'Orbitron';font-size:clamp(.9rem,3vw,1.3rem);font-weight:700;color:#00ffcc;padding:10px}
.sig-w{text-align:center;font-family:'Orbitron';font-size:clamp(.85rem,2.8vw,1.15rem);color:#ffaa00;padding:10px}
.sig-x{text-align:center;font-family:'Orbitron';font-size:clamp(.85rem,2.8vw,1.1rem);color:#666;padding:8px}

.tbox{background:rgba(255,255,255,.06);border-radius:14px;padding:14px;text-align:center;margin:4px}
.tv{font-size:clamp(1.4rem,5vw,2.2rem);font-weight:900;font-family:'Orbitron'}
.tl{font-size:.6rem;color:rgba(255,255,255,.38);letter-spacing:.12em;text-transform:uppercase;margin-top:3px}
.ta{font-size:.7rem;color:#00ff88;margin-top:4px;font-weight:700}

.stTextInput input::placeholder{color:rgba(255,255,255,0.7) !important; opacity: 1 !important; font-style:italic !important}
.stTextInput input{background:rgba(255,255,255,.1)!important;border:2px solid rgba(255,0,102,.5)!important;color:#fff!important;border-radius:11px!important;font-size:.93rem!important;padding:11px 14px!important}

.stButton>button{background:linear-gradient(135deg,#ff0066,#cc0055)!important;color:#fff!important;font-weight:900!important;border-radius:12px!important;height:52px!important;border:none!important;width:100%!important}
</style>
""", unsafe_allow_html=True)

for k,v in [("auth",False),("H",lj(HF,[])),("S",lj(SF,{"t":0,"w":0,"l":0})),("R",None),("ck",0)]:
    if k not in st.session_state: st.session_state[k]=v

ST=["COLD","NORMAL","WARM","HOT"]
def s2st(c):
    if c<1.5: return "COLD"
    if c<2.5: return "NORMAL"
    if c<3.5: return "WARM"
    return "HOT"

def markov(h,lc):
    tr={s:{s2:1 for s2 in ST} for s in ST}
    cs=[x.get("lc",2.0) for x in h if x.get("lc")]
    for i in range(len(cs)-1):
        tr[s2st(cs[i])][s2st(cs[i+1])]+=1
    mx={s:{s2:tr[s][s2]/sum(tr[s].values()) for s2 in ST} for s in ST}
    cur=s2st(lc); hp=mx[cur].get("HOT",0)+mx[cur].get("WARM",0)
    return round(hp*100,1),cur

def bayes(h,base):
    lb=[x for x in h if x.get("res") in ["W","L"]]
    if len(lb)<3: return base
    rc=lb[-20:]; w=sum(1 for x in rc if x.get("res")=="W"); n=len(rc)
    lik=(w+1)/(n+2); pr=base/100
    po=(lik*pr)/((lik*pr)+((1-lik)*(1-pr))+1e-9)
    return round(min(95,max(30,po*100)),1)

def entry_time(hn, bp, str_, lc):
    now = datetime.now(TZ)
    hash_var   = (hn % 50) - 25
    prob_boost = int((bp - 40) * 0.35)
    str_boost  = int((str_ - 50) * 0.22)
    cote_boost = int(lc * 2.5)
    base_shift = 42
    shift = max(15, min(85, base_shift + hash_var + prob_boost + str_boost + cote_boost))
    return (now + timedelta(seconds=shift)).strftime("%H:%M:%S"), shift

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
    hp,cur=markov(st.session_state.H,lc)
    bp=bayes(st.session_state.H,p3+(hp/100-0.5)*20)
    str_=round(bp*0.50+p35*0.20+p4*0.10+(hn%200)/12+(hp/100)*15,1)
    str_=max(30.0,min(99.0,str_))
    ent,shift=entry_time(hn,bp,str_,lc)
    if str_>=88 and bp>=44:   sig,sc="💎💎💎 ULTRA X3+ — BUY","sig-u"
    elif str_>=76 and bp>=36: sig,sc="🔥🔥 STRONG X3+ — GO","sig-s"
    elif str_>=62 and bp>=28: sig,sc="🟢 GOOD X3+ — WATCH","sig-w"
    else:                     sig,sc="⚠️ SKIP CE ROUND","sig-x"
    return {"lc":lc,"ent":ent,"shift":shift,"sig":sig,"sc":sc,"bp":bp,"p35":p35,"p4":p4,"str":str_,"cur":cur,"hp":hp,"tmin":tmin,"tmoy":tmoy,"tmax":tmax,"res":None,"hi":len(st.session_state.H)}

if not st.session_state.auth:
    st.markdown("<div class='ttl'>✈️ AVIATOR X3 V7</div>",unsafe_allow_html=True)
    st.markdown("<div class='sub'>MARKOV + BAYESIAN • ENTRY TIME ULTRA PRÉCIS</div>",unsafe_allow_html=True)
    _,cb,_=st.columns([1,1.2,1])
    with cb:
        st.markdown("<div class='card'>",unsafe_allow_html=True)
        pw=st.text_input("🔑 MOT DE PASSE",type="password",placeholder="Entrez: AVIATOR2026")
        if st.button("🔓 ACTIVER",use_container_width=True):
            if pw=="AVIATOR2026": st.session_state.auth=True; st.rerun()
            else: st.error("❌ Code incorrect")
        st.markdown("</div>",unsafe_allow_html=True)
    st.stop()

with st.sidebar:
    st.markdown("### ✈️ AVIATOR V7")
    S=st.session_state.S; t,w,l=S.get("t",0),S.get("w",0),S.get("l",0)
    wr=round(w/t*100,1) if t>0 else 0
    st.markdown(f"<div class='sb'><div class='sv'>{wr}%</div><div class='sl'>WIN RATE</div></div>",unsafe_allow_html=True)
    if st.button("🗑️ RESET",use_container_width=True):
        st.session_state.H=[];st.session_state.S={"t":0,"w":0,"l":0};st.session_state.R=None
        st.rerun()

st.markdown("<div class='ttl'>✈️ AVIATOR X3 V7</div>",unsafe_allow_html=True)
ci,co=st.columns([1,2],gap="medium")
with ci:
    st.markdown("<div class='card'>",unsafe_allow_html=True)
    h5=st.text_input("🔐 HEX SHA512 (5 chars)",placeholder="Ex: ac50e")
    ti=st.text_input("⏰ TIME ROUND PRÉCÉDENT",placeholder="Ex: 20:22:24")
    lc=st.number_input("📊 LAST COTE",value=1.88,step=0.01,format="%.2f")
    st.markdown("</div>",unsafe_allow_html=True)
    if st.button("🚀 ANALYSER",use_container_width=True):
        if h5 and ti:
            r=engine(h5.strip(),ti.strip(),lc)
            st.session_state.R=r
            st.session_state.H.append(dict(r))
            sj(HF,st.session_state.H); st.rerun()

with co:
    r=st.session_state.R
    if r:
        st.markdown("<div class='card'>",unsafe_allow_html=True)
        st.markdown(f"<div class='{r['sc']}'>{r['sig']}</div>",unsafe_allow_html=True)
        st.markdown(f"<div class='etime' id='copy-target'>{r['ent']}</div>",unsafe_allow_html=True)
        st.markdown(f"<div class='pct'>{r['bp']}%</div>",unsafe_allow_html=True)
        
        # Section ho an'ny fanaovana "Copy" ho mainty stylé
        st.code(f"HASH: {h5} | COTE: {r['tmax']} | TIME: {r['ent']}", language="markdown")
        
        cw,cl2=st.columns(2)
        with cw:
            if st.button("✅ WIN",use_container_width=True):
                idx=r.get("hi",-1)
                if 0<=idx<len(st.session_state.H): st.session_state.H[idx]["res"]="W"; sj(HF,st.session_state.H)
                st.session_state.S["t"]+=1; st.session_state.S["w"]+=1; sj(SF,st.session_state.S); st.rerun()
        with cl2:
            if st.button("❌ LOSS",use_container_width=True):
                idx=r.get("hi",-1)
                if 0<=idx<len(st.session_state.H): st.session_state.H[idx]["res"]="L"; sj(HF,st.session_state.H)
                st.session_state.S["t"]+=1; st.session_state.S["l"]+=1; sj(SF,st.session_state.S); st.rerun()
        st.markdown("</div>",unsafe_allow_html=True)

if st.session_state.H:
    df=pd.DataFrame([{"Entry":x.get("ent",""),"X3%":x.get("bp",""),"Min":x.get("tmin",""),"Max":x.get("tmax",""),"Res":x.get("res","—")} for x in reversed(st.session_state.H[-10:])])
    st.dataframe(df,use_container_width=True,hide_index=True)
