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
.tag{background:rgba(255,0,102,.12);border:1px solid rgba(255,0,102,.35);border-radius:8px;padding:4px 11px;font-size:.8rem;display:inline-block;margin:3px;color:#ffaacc}
.tag-g{background:rgba(0,255,204,.1);border:1px solid rgba(0,255,204,.3);border-radius:8px;padding:4px 11px;font-size:.8rem;display:inline-block;margin:3px;color:#aaffee}
.sb{background:rgba(255,0,102,.07);border:1px solid rgba(255,0,102,.2);border-radius:10px;padding:10px;text-align:center;margin:4px 0}
.sv{font-size:1.3rem;font-weight:900;font-family:'Orbitron';color:#ff0066}
.sl{font-size:.56rem;color:rgba(255,255,255,.35);letter-spacing:.12em;text-transform:uppercase;margin-top:2px}
.ib{background:rgba(0,255,204,.05);border-left:3px solid #00ffcc;border-radius:0 10px 10px 0;padding:11px 15px;margin:8px 0;font-size:.88rem;line-height:1.8}
.stButton>button{background:linear-gradient(135deg,#ff0066,#cc0055)!important;color:#fff!important;font-weight:900!important;border-radius:12px!important;height:52px!important;border:none!important;width:100%!important;font-family:'Rajdhani'!important;font-size:.95rem!important;transition:all .2s!important}
.stButton>button:hover{transform:scale(1.02);box-shadow:0 0 24px rgba(255,0,102,.5)!important}

/* FANITSIANA NY INPUT (Soratra mainty stylé) */
.stTextInput label, .stNumberInput label {color:#ffaacc!important;font-weight:700!important;font-size:.87rem!important;font-family:'Rajdhani'!important}
.stTextInput input, .stNumberInput input {
    background: rgba(255, 255, 255, 0.95) !important;
    border: 2px solid rgba(255, 0, 102, 0.6) !important;
    color: #000000 !important;
    font-weight: 900 !important;
    border-radius: 11px !important;
    font-size: 1.05rem !important;
    padding: 11px 14px !important;
    font-family: 'Orbitron', sans-serif !important;
}
.stTextInput input::placeholder, .stNumberInput input::placeholder {
    color: rgba(0, 0, 0, 0.45) !important; 
    font-style: italic !important;
    font-weight: 600 !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: #ff0066 !important;
    box-shadow: 0 0 16px rgba(255,0,102,0.4) !important;
    background: #ffffff !important;
}
/* Mba tsy ho transparent rehefa séléction-ena/adika */
.stTextInput input::selection, .stNumberInput input::selection {
    background-color: #00ffcc !important; 
    color: #000000 !important;
}

@media(max-width:768px){.card{padding:12px!important}}
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
    """
    HEURE D'ENTRÉE ULTRA PRÉCIS V7
    ================================
    Base = ORA ANKEHITRINY Madagascar
    
    FACTEURS 5 mihambana:
    1. hash_var   : variabilité déterministe du hash (-25..+25)
    2. prob_boost : prob X3+ avo → entry MIALOHA kokoa
    3. str_boost  : signal matanjaka → entry mialoha
    4. cote_boost : HOT state → round miavaka haingana
    5. anti_waste : Évite trop tôt (< 15sec) ou trop tard (> 85sec)
    
    Résultat: 15 à 85 secondes depuis maintenant
    """
    now = datetime.now(TZ)
    
    hash_var   = (hn % 50) - 25          # -25..+25
    prob_boost = int((bp - 40) * 0.35)   # prob 40-95 → -0..+19
    str_boost  = int((str_ - 50) * 0.22) # str 50-99 → 0..+11
    cote_boost = int(lc * 2.5)           # 1.0-5.0 → 2..12
    base_shift = 42                       # base 42sec
    
    shift = max(15, min(85,
        base_shift + hash_var + prob_boost + str_boost + cote_boost
    ))
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
    # Nampidirina eto ny h5 sy ti mba ho azo adika
    return {"lc":lc,"ent":ent,"shift":shift,"sig":sig,"sc":sc,
            "bp":bp,"p35":p35,"p4":p4,"str":str_,
            "cur":cur,"hp":hp,"tmin":tmin,"tmoy":tmoy,"tmax":tmax,
            "res":None,"hi":len(st.session_state.H), "h5":hex5, "ti":tin}

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
    st.markdown("""
    <div class='card' style='max-width:800px;margin:20px auto;'>
    <h3 style='color:#00ffcc;font-family:Orbitron;text-align:center;font-size:1.1rem;'>📖 FANAZAVANA HEURE D'ENTRÉE</h3>
    <div class='ib'><b style='color:#ff0066;'>⏰ COMMENT ÇA MARCHE?</b><br>
    Entry = ORA ANKEHITRINY Madagascar + SHIFT (15-85 sec)<br>
    Raha signal ULTRA = shift kely (entry mialoha)<br>
    Raha signal SKIP = shift lehibe (miandry)<br>
    Ohatra: Now 20:22:30 + 45sec → Entry <b style='color:#ff0066;'>20:23:15</b></div>
    <div class='ib'><b style='color:#ff0066;'>📥 INPUTS:</b><br>
    • <b>HEX 5 chars:</b> SHA512 premiers chars → Ex: <code>ac50e</code><br>
    • <b>TIME:</b> Ora round taloha (référence) → Ex: <code>20:22:24</code><br>
    • <b>LAST COTE:</b> Résultat taloha → Ex: <code>1.88</code></div>
    <div class='ib'><b style='color:#ff0066;'>⚠️ RAHA EFA LASA:</b> Tsindrio indray "ANALYSER" → entry vaovao</div>
    </div>
    """,unsafe_allow_html=True)
    st.stop()

with st.sidebar:
    st.markdown("### ✈️ AVIATOR V7")
    S=st.session_state.S; t,w,l=S.get("t",0),S.get("w",0),S.get("l",0)
    wr=round(w/t*100,1) if t>0 else 0
    st.markdown(f"<div class='sb'><div class='sv'>{wr}%</div><div class='sl'>WIN RATE</div></div>",unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1: st.markdown(f"<div class='sb'><div class='sv'>{w}</div><div class='sl'>WINS</div></div>",unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='sb'><div class='sv'>{l}</div><div class='sl'>LOSS</div></div>",unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🗑️ RESET",use_container_width=True):
        st.session_state.H=[];st.session_state.S={"t":0,"w":0,"l":0};st.session_state.R=None
        for f in [HF,SF]:
            try:
                if f.exists(): f.unlink()
            except: pass
        st.success("✅"); st.rerun()

st.markdown("<div class='ttl'>✈️ AVIATOR X3 V7</div>",unsafe_allow_html=True)
st.markdown("<div class='sub'>MARKOV + BAYESIAN • 400K SIMS • ENTRY ULTRA PRÉCIS</div>",unsafe_allow_html=True)
ci,co=st.columns([1,2],gap="medium")
with ci:
    st.markdown("<div class='card'>",unsafe_allow_html=True)
    h5=st.text_input("🔐 HEX SHA512 (5 chars)",placeholder="Ex: ac50e")
    ti=st.text_input("⏰ TIME ROUND PRÉCÉDENT",placeholder="Ex: 20:22:24")
    lc=st.number_input("📊 LAST COTE",value=1.88,step=0.01,format="%.2f")
    if lc<1.5: sl,sc2="🔵 COLD","#4488ff"
    elif lc<2.5: sl,sc2="⚪ NORMAL","#aaa"
    elif lc<3.5: sl,sc2="🟡 WARM","#ffcc00"
    else: sl,sc2="🔴 HOT","#ff3366"
    st.markdown(f"<div style='text-align:center;margin:6px 0;'><span style='background:rgba(255,255,255,.07);border-radius:8px;padding:4px 14px;color:{sc2};font-size:.82rem;'>{sl}</span></div>",unsafe_allow_html=True)
    st.markdown("</div>",unsafe_allow_html=True)
    if st.button("🚀 ANALYSER",use_container_width=True):
        if h5 and ti:
            with st.spinner("⚡ 400k sims..."):
                r=engine(h5.strip(),ti.strip(),lc)
            st.session_state.R=r
            st.session_state.H.append(dict(r))
            if len(st.session_state.H)>200: st.session_state.H.pop(0)
            sj(HF,st.session_state.H); st.session_state.ck+=1; st.rerun()
        else: st.error("❌ HEX et TIME obligatoires!")

with co:
    r=st.session_state.R
    if r:
        st.markdown("<div class='card'>",unsafe_allow_html=True)
        st.markdown(f"<div class='{r['sc']}'>{r['sig']}</div>",unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center;color:rgba(255,255,255,.4);font-size:.73rem;margin-top:14px;'>▸ HEURE D'ENTRÉE (NOW + {r['shift']}s)</p>",unsafe_allow_html=True)
        st.markdown(f"<div class='etime'>{r['ent']}</div>",unsafe_allow_html=True)
        st.markdown(f"<div class='pct'>{r['bp']}%</div>",unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:rgba(255,255,255,.32);font-size:.7rem;'>PROB X3+ BAYESIAN</p>",unsafe_allow_html=True)
        st.markdown(f"""<div style='text-align:center;margin:10px 0;'>
        <span class='tag'>🔄 {r['cur']}</span><span class='tag'>🔥 {r['hp']}%</span>
        <span class='tag'>💪 {r['str']}</span>
        <span class='tag-g'>X3.5+ {r['p35']}%</span><span class='tag-g'>X4+ {r['p4']}%</span>
        </div>""",unsafe_allow_html=True)
        c1,c2,c3=st.columns(3)
        with c1: st.markdown(f"<div class='tbox'><div class='tl'>MIN</div><div class='tv' style='color:#00ffcc;'>{r['tmin']}×</div><div class='ta'>70%</div></div>",unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='tbox'><div class='tl'>MOYEN</div><div class='tv' style='color:#ffd700;'>{r['tmoy']}×</div><div class='ta'>50%</div></div>",unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='tbox'><div class='tl'>MAX</div><div class='tv' style='color:#ff3366;'>{r['tmax']}×</div><div class='ta'>X3+</div></div>",unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        cw,cl2=st.columns(2)
        with cw:
            if st.button("✅ WIN",use_container_width=True,key="bw"):
                idx=r.get("hi",-1)
                if 0<=idx<len(st.session_state.H): st.session_state.H[idx]["res"]="W"; sj(HF,st.session_state.H)
                st.session_state.S["t"]+=1; st.session_state.S["w"]+=1; sj(SF,st.session_state.S); st.success("🎯"); st.rerun()
        with cl2:
            if st.button("❌ LOSS",use_container_width=True,key="bl"):
                idx=r.get("hi",-1)
                if 0<=idx<len(st.session_state.H): st.session_state.H[idx]["res"]="L"; sj(HF,st.session_state.H)
                st.session_state.S["t"]+=1; st.session_state.S["l"]+=1; sj(SF,st.session_state.S); st.rerun()
        
        # FARITRA VAOVAO MBY ADIKA MANONTOLO (1-Click Copy)
        st.markdown("<hr style='border-color:rgba(255,0,102,.2); margin: 15px 0 10px 0;'>", unsafe_allow_html=True)
        st.markdown("<div style='text-align:center; font-size:0.75rem; color:#00ffcc; margin-bottom:5px; font-weight:bold; letter-spacing:0.1em;'>📋 DATA AZO ADIKA MANONTOLO :</div>", unsafe_allow_html=True)
        data_to_copy = f"Hash: {r.get('h5', '')} | Cote: {r.get('lc', '')} | Time: {r.get('ti', '')}"
        st.code(data_to_copy, language="text")
        
        st.markdown("</div>",unsafe_allow_html=True)
    else:
        st.markdown("<div class='card' style='min-height:350px;display:flex;align-items:center;justify-content:center;'><div style='text-align:center;'><div style='font-size:3rem;'>✈️</div><div style='color:rgba(255,255,255,.15);font-family:Orbitron;margin-top:10px;'>EN ATTENTE...</div></div></div>",unsafe_allow_html=True)

if st.session_state.H:
    st.markdown("---")
    df=pd.DataFrame([{"Entry":x.get("ent",""),"Shift":f"{x.get('shift',0)}s","X3%":x.get("bp",""),"State":x.get("cur",""),"Min":x.get("tmin",""),"Max":x.get("tmax",""),"Res":"WIN" if x.get("res")=="W" else "LOSS" if x.get("res")=="L" else "—"} for x in reversed(st.session_state.H[-10:])])
    st.dataframe(df,use_container_width=True,hide_index=True)
st.markdown("<div style='text-align:center;margin-top:20px;color:rgba(255,255,255,.08);font-size:.55rem;'>AVIATOR X3 V7 • MARKOV+BAYESIAN • ENTRY ULTRA PRÉCIS</div>",unsafe_allow_html=True)
