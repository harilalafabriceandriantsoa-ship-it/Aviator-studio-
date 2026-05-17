import streamlit as st
import hashlib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import pytz, json
from pathlib import Path

st.set_page_config(page_title="✈️ AVIATOR X3 V9", layout="wide", initial_sidebar_state="collapsed")
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
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@600;700&display=swap');
*{box-sizing:border-box}
.stApp{background:#04000e;color:#f0f0ff;font-family:'Rajdhani',sans-serif;min-height:100vh}
.stApp::before{content:'';position:fixed;inset:0;background:radial-gradient(ellipse at 20% 20%,#ff006622 0%,transparent 60%),radial-gradient(ellipse at 80% 80%,#00ffcc11 0%,transparent 60%);pointer-events:none;z-index:0}

.hero{text-align:center;padding:24px 0 8px}
.hero-icon{font-size:3.5rem;margin-bottom:8px;filter:drop-shadow(0 0 20px #ff0066)}
.hero-title{font-family:'Orbitron';font-size:clamp(2rem,8vw,3.2rem);font-weight:900;background:linear-gradient(135deg,#ff0066 0%,#ff6688 40%,#00ffcc 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1.1;margin-bottom:6px}
.hero-sub{color:rgba(255,255,255,.4);font-size:.82rem;letter-spacing:.35em;text-transform:uppercase}

.glass{background:linear-gradient(135deg,rgba(255,0,102,.06) 0%,rgba(0,0,20,.92) 100%);border:1.5px solid rgba(255,0,102,.25);border-radius:20px;padding:clamp(14px,4vw,24px);backdrop-filter:blur(20px);margin-bottom:16px;box-shadow:0 8px 32px rgba(255,0,102,.08),inset 0 1px 0 rgba(255,255,255,.05)}
.glass-g{background:linear-gradient(135deg,rgba(0,255,204,.06) 0%,rgba(0,10,20,.92) 100%);border:1.5px solid rgba(0,255,204,.25);border-radius:20px;padding:clamp(14px,4vw,24px);backdrop-filter:blur(20px);margin-bottom:16px;box-shadow:0 8px 32px rgba(0,255,204,.08),inset 0 1px 0 rgba(255,255,255,.05)}

.section-label{font-family:'Orbitron';font-size:.62rem;font-weight:700;letter-spacing:.4em;color:rgba(255,0,102,.7);text-transform:uppercase;margin-bottom:10px}

/* ENTRY TIME CARD */
.entry-card{background:linear-gradient(135deg,#ff006622,#00000088);border:2px solid #ff0066;border-radius:18px;padding:20px;text-align:center;margin:10px 0;box-shadow:0 0 40px rgba(255,0,102,.2),inset 0 0 30px rgba(255,0,102,.05)}
.entry-label{font-size:.7rem;letter-spacing:.25em;color:rgba(255,0,102,.7);text-transform:uppercase;margin-bottom:8px}
.entry-time{font-family:'Orbitron';font-size:clamp(3.5rem,14vw,5.5rem);font-weight:900;color:#ff0066;line-height:1;text-shadow:0 0 50px #ff006699;animation:pulse-r 2s ease-in-out infinite}
@keyframes pulse-r{0%,100%{text-shadow:0 0 40px #ff006688}50%{text-shadow:0 0 70px #ff0066cc,0 0 100px #ff006644}}
.entry-shift{font-size:.75rem;color:rgba(255,255,255,.35);margin-top:6px}

/* TOUR CARDS */
.tour-card{border-radius:14px;padding:16px;text-align:center;margin:6px 0}
.tour-1{background:linear-gradient(135deg,rgba(255,0,102,.15),rgba(255,0,102,.05));border:1.5px solid rgba(255,0,102,.5)}
.tour-2{background:linear-gradient(135deg,rgba(0,255,204,.12),rgba(0,255,204,.04));border:1.5px solid rgba(0,255,204,.5)}
.tour-lbl{font-size:.65rem;letter-spacing:.2em;color:rgba(255,255,255,.45);text-transform:uppercase;margin-bottom:4px}
.tour-t{font-family:'Orbitron';font-size:clamp(1.6rem,6vw,2.4rem);font-weight:900}
.tour-c{font-size:.72rem;font-weight:700;margin-top:4px}

/* PROB */
.prob-ring{text-align:center;padding:16px 0}
.prob-val{font-family:'Orbitron';font-size:clamp(3rem,12vw,5rem);font-weight:900;background:linear-gradient(135deg,#ff0066,#ff3399,#00ffcc);-webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1}
.prob-lbl{font-size:.7rem;letter-spacing:.2em;color:rgba(255,255,255,.35);text-transform:uppercase;margin-top:4px}

/* SIGNAL */
.signal{border-radius:14px;padding:14px;text-align:center;margin:10px 0;font-family:'Orbitron';font-weight:900;letter-spacing:.06em}
.sig-ultra{background:linear-gradient(135deg,rgba(255,0,102,.2),rgba(255,50,50,.1));border:2px solid #ff0066;color:#ff0066;font-size:clamp(.9rem,3vw,1.3rem);text-shadow:0 0 20px #ff006688;box-shadow:0 0 30px rgba(255,0,102,.15)}
.sig-strong{background:linear-gradient(135deg,rgba(0,255,204,.15),rgba(0,200,200,.08));border:2px solid #00ffcc;color:#00ffcc;font-size:clamp(.88rem,2.8vw,1.2rem);box-shadow:0 0 25px rgba(0,255,204,.12)}
.sig-mod{background:rgba(255,170,0,.1);border:1.5px solid rgba(255,170,0,.4);color:#ffaa00;font-size:clamp(.82rem,2.6vw,1.05rem)}
.sig-skip{background:rgba(80,80,80,.15);border:1.5px solid rgba(100,100,100,.3);color:#666;font-size:clamp(.8rem,2.4vw,1rem)}

/* TARGETS */
.targets{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:12px 0}
.t-card{background:rgba(255,255,255,.04);border-radius:14px;padding:14px;text-align:center;border:1px solid rgba(255,255,255,.08)}
.t-val{font-family:'Orbitron';font-size:clamp(1.3rem,4.5vw,2rem);font-weight:900;margin:4px 0}
.t-lbl{font-size:.58rem;color:rgba(255,255,255,.35);letter-spacing:.12em;text-transform:uppercase}
.t-acc{font-size:.68rem;font-weight:700;margin-top:3px}

/* TAGS */
.tags{display:flex;flex-wrap:wrap;gap:6px;justify-content:center;margin:10px 0}
.tag{background:rgba(255,0,102,.1);border:1px solid rgba(255,0,102,.3);border-radius:20px;padding:4px 12px;font-size:.78rem;color:#ffaacc;white-space:nowrap}
.tag-g{background:rgba(0,255,204,.1);border:1px solid rgba(0,255,204,.3);border-radius:20px;padding:4px 12px;font-size:.78rem;color:#aaffee;white-space:nowrap}

/* STATS */
.stat-row{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.stat-c{background:rgba(255,0,102,.07);border:1px solid rgba(255,0,102,.2);border-radius:12px;padding:10px;text-align:center}
.stat-v{font-family:'Orbitron';font-size:1.3rem;font-weight:900;color:#ff0066}
.stat-l{font-size:.55rem;color:rgba(255,255,255,.35);letter-spacing:.1em;text-transform:uppercase;margin-top:2px}

/* INPUTS */
.stTextInput label,.stNumberInput label{color:rgba(255,150,180,.8)!important;font-weight:700!important;font-size:.85rem!important;font-family:'Rajdhani'!important}
.stTextInput input{background:rgba(255,0,102,.06)!important;border:1.5px solid rgba(255,0,102,.4)!important;color:#fff!important;border-radius:12px!important;font-size:.92rem!important;padding:11px 14px!important;transition:all .2s!important}
.stTextInput input::placeholder{color:rgba(255,255,255,.4)!important;font-style:italic!important}
.stTextInput input:focus{border-color:#ff0066!important;box-shadow:0 0 16px rgba(255,0,102,.25)!important;background:rgba(255,0,102,.1)!important}
.stNumberInput input{background:rgba(255,0,102,.06)!important;border:1.5px solid rgba(255,0,102,.4)!important;color:#fff!important;border-radius:12px!important;font-size:.92rem!important;padding:11px 14px!important}
.stNumberInput input:focus{border-color:#ff0066!important;box-shadow:0 0 16px rgba(255,0,102,.25)!important}

/* BUTTONS */
.stButton>button{background:linear-gradient(135deg,#ff0066,#cc0044)!important;color:#fff!important;font-weight:900!important;border-radius:14px!important;height:52px!important;border:none!important;width:100%!important;font-family:'Rajdhani'!important;font-size:.95rem!important;letter-spacing:.04em!important;transition:all .2s!important;box-shadow:0 4px 20px rgba(255,0,102,.3)!important}
.stButton>button:hover{transform:translateY(-2px);box-shadow:0 8px 30px rgba(255,0,102,.5)!important}
.stButton>button:active{transform:translateY(0)}

@media(max-width:768px){.glass,.glass-g{padding:14px!important}.targets{grid-template-columns:repeat(3,1fr)}}
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

def parse_time(ts):
    now=datetime.now(TZ)
    try:
        pts=ts.strip().split(":")
        h2,m2=int(pts[0]),int(pts[1]); s2=int(pts[2]) if len(pts)>2 else 0
        dt=now.replace(hour=h2,minute=m2,second=s2,microsecond=0)
        if dt<now-timedelta(hours=1): dt+=timedelta(days=1)
        return dt
    except: return now

def calc_tours(hn,bp,str_,lc,lt):
    bt=parse_time(lt)
    hv=(hn%50)-25; pb=int((bp-40)*0.32); sb=int((str_-50)*0.20); cb=int(lc*2.5)
    sh1=max(20,min(85,42+hv+pb+sb+cb))
    rd=max(8,min(35,12+(hn%20)-int(lc*2)))
    sh2=sh1+rd+max(5,int(hn%12))
    t1=(bt+timedelta(seconds=sh1)).strftime("%H:%M:%S")
    t2=(bt+timedelta(seconds=sh2)).strftime("%H:%M:%S")
    c2={"COLD":round(min(95,bp*1.18),1),"NORMAL":round(min(95,bp*1.08),1),"WARM":round(min(95,bp*0.95),1),"HOT":round(min(95,bp*0.88),1)}.get(s2st(lc),bp)
    return t1,sh1,bp,t2,sh2,c2

def engine(h5,lt,lc):
    fh=hashlib.sha512(f"{h5}:{lt}:{lc}".encode()).hexdigest()
    hn=int(fh[:16],16)
    np.random.seed(int((hn&0xFFFFFFFF)+(lc*1000))%(2**32))
    if lc<1.5:   bs,sg=2.12,0.24
    elif lc<2.5: bs,sg=2.06,0.21
    elif lc<3.5: bs,sg=2.00,0.19
    else:        bs,sg=1.96,0.18
    bs+=(hn%180)/1200; sg=max(0.14,sg-lc*0.0022)
    sm=np.random.lognormal(np.log(bs),sg,450_000)
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
    t1,sh1,c1,t2,sh2,c2=calc_tours(hn,bp,str_,lc,lt)
    if   str_>=90 and bp>=46: sig,sc="💎💎💎 ULTRA X3+ — FIRE MAX","sig-ultra"
    elif str_>=80 and bp>=40: sig,sc="💎💎 STRONG X3+ — BUY","sig-ultra"
    elif str_>=70 and bp>=34: sig,sc="🔥 GOOD X3+ — GO","sig-strong"
    elif str_>=58 and bp>=27: sig,sc="🟡 MODERATE — SMALL BET","sig-mod"
    else:                     sig,sc="⚠️ SKIP — NO SIGNAL","sig-skip"
    return {"lc":lc,"t1":t1,"sh1":sh1,"c1":c1,"t2":t2,"sh2":sh2,"c2":c2,
            "sig":sig,"sc":sc,"bp":bp,"p3":p3,"p35":p35,"p4":p4,"str":str_,
            "cur":cur,"hp":hp,"tmin":tmin,"tmoy":tmoy,"tmax":tmax,
            "acc_min":70.0,"acc_moy":50.0,"acc_max":round(p3*0.85,1),
            "res":None,"hi":len(st.session_state.H)}

# LOGIN
if not st.session_state.auth:
    st.markdown("""
    <div class='hero'>
        <div class='hero-icon'>✈️</div>
        <div class='hero-title'>AVIATOR X3 V9</div>
        <div class='hero-sub'>Ultra Sniper • Multi-Tour • Markov + Bayesian</div>
    </div>
    """, unsafe_allow_html=True)
    _,cb,_=st.columns([1,1.1,1])
    with cb:
        st.markdown("<div class='glass'>",unsafe_allow_html=True)
        pw=st.text_input("🔑 MOT DE PASSE",type="password",placeholder="Entrez AVIATOR2026")
        if st.button("🔓 ACTIVER",use_container_width=True):
            if pw=="AVIATOR2026": st.session_state.auth=True; st.rerun()
            else: st.error("❌ Code incorrect")
        st.markdown("</div>",unsafe_allow_html=True)
    st.markdown("""
    <div class='glass' style='max-width:720px;margin:20px auto;'>
    <div class='section-label'>📖 Fanazavana Malagasy</div>
    <div style='line-height:1.9;font-size:.9rem;color:rgba(255,255,255,.75);'>
    <b style='color:#ff0066;'>🎯 FOMBA FAMPIASANA:</b><br>
    1. Jereo Provably Fair @ casino → Copy <b>HEX 5 chars</b> (ex: ac50e)<br>
    2. Tadidio <b>LAST TIME</b> = ora nilanihan'ny round taloha (ex: 20:22:24)<br>
    3. Tadidio <b>LAST COTE</b> = résultat taloha (ex: 1.88×)<br>
    4. Tsindrio <b>ANALYSER</b> → miseho TOUR 1 sy TOUR 2<br>
    5. <b>TOUR 1</b> = round akaiky (confidence = prob X3+ marina)<br>
    6. <b>TOUR 2</b> = round faharoa (confidence miova @ state)<br>
    7. Miditra @ <b>TOUR 1 raha confidence avo</b><br>
    8. Raha LOSS @ Tour 1 → miandry <b>TOUR 2</b> (souvent correction!)<br>
    9. Cash out @ target MIN (safe) na MOYEN na MAX (X3+ only)
    </div>
    </div>
    """,unsafe_allow_html=True)
    st.stop()

with st.sidebar:
    st.markdown("<div class='section-label'>📊 Performance</div>",unsafe_allow_html=True)
    S=st.session_state.S; t,w,l=S.get("t",0),S.get("w",0),S.get("l",0)
    wr=round(w/t*100,1) if t>0 else 0
    st.markdown(f"""<div class='stat-row'>
    <div class='stat-c'><div class='stat-v'>{wr}%</div><div class='stat-l'>WIN</div></div>
    <div class='stat-c'><div class='stat-v'>{w}</div><div class='stat-l'>WINS</div></div>
    <div class='stat-c'><div class='stat-v'>{l}</div><div class='stat-l'>LOSS</div></div>
    </div>""",unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🗑️ RESET DATA",use_container_width=True):
        st.session_state.H=[];st.session_state.S={"t":0,"w":0,"l":0};st.session_state.R=None
        for f in [HF,SF]:
            try:
                if f.exists(): f.unlink()
            except: pass
        st.success("✅"); st.rerun()

st.markdown("""
<div class='hero'>
    <div class='hero-icon'>✈️</div>
    <div class='hero-title'>AVIATOR X3 V9</div>
    <div class='hero-sub'>Ultra Sniper • Multi-Tour • 450K Sims</div>
</div>
""",unsafe_allow_html=True)

ci,co=st.columns([1,2],gap="large")

with ci:
    st.markdown("<div class='glass'>",unsafe_allow_html=True)
    st.markdown("<div class='section-label'>📥 Paramètres</div>",unsafe_allow_html=True)
    h5  = st.text_input("🔐 HEX SHA512 (5 chars)",placeholder="ac50e  —  5 premiers chars")
    ti  = st.text_input("⏰ LAST TIME (HH:MM:SS)",placeholder="20:22:24  —  ora round taloha")
    lc  = st.number_input("📊 LAST COTE",value=1.88,step=0.01,format="%.2f")
    cols={"COLD":"#4488ff","NORMAL":"#888","WARM":"#ffcc00","HOT":"#ff3366"}
    cur_s=s2st(lc)
    st.markdown(f"<div style='text-align:center;margin:8px 0;'><span style='background:rgba(255,255,255,.06);border:1px solid {cols[cur_s]}44;border-radius:20px;padding:5px 16px;color:{cols[cur_s]};font-size:.82rem;font-weight:700;'>{'🔵 COLD' if cur_s=='COLD' else '⚪ NORMAL' if cur_s=='NORMAL' else '🟡 WARM' if cur_s=='WARM' else '🔴 HOT'}</span></div>",unsafe_allow_html=True)
    st.markdown("</div>",unsafe_allow_html=True)
    if st.button("🚀 ANALYSER X3+",use_container_width=True):
        if h5 and ti:
            with st.spinner("⚡ 450k sims ciblés X3+..."):
                r=engine(h5.strip(),ti.strip(),lc)
            st.session_state.R=r
            st.session_state.H.append(dict(r))
            if len(st.session_state.H)>200: st.session_state.H.pop(0)
            sj(HF,st.session_state.H); st.session_state.ck+=1; st.rerun()
        else: st.error("❌ HEX et LAST TIME requis!")

with co:
    r=st.session_state.R
    if r:
        st.markdown(f"<div class='signal {r['sc']}'>{r['sig']}</div>",unsafe_allow_html=True)
        ct1,ct2=st.columns(2)
        with ct1:
            st.markdown(f"""<div class='tour-card tour-1'>
            <div class='tour-lbl'>🎯 TOUR 1 · +{r['sh1']}s</div>
            <div class='tour-t' style='color:#ff0066;'>{r['t1']}</div>
            <div class='tour-c' style='color:#ff9999;'>Confiance {r['c1']}%</div>
            </div>""",unsafe_allow_html=True)
        with ct2:
            st.markdown(f"""<div class='tour-card tour-2'>
            <div class='tour-lbl'>🎯 TOUR 2 · +{r['sh2']}s</div>
            <div class='tour-t' style='color:#00ffcc;'>{r['t2']}</div>
            <div class='tour-c' style='color:#88ffcc;'>Confiance {r['c2']}%</div>
            </div>""",unsafe_allow_html=True)
        st.markdown(f"""<div class='prob-ring'>
        <div class='prob-val'>{r['bp']}%</div>
        <div class='prob-lbl'>Probabilité X3+ · Bayesian</div>
        </div>""",unsafe_allow_html=True)
        st.markdown(f"""<div class='tags'>
        <span class='tag'>🔄 {r['cur']}</span>
        <span class='tag'>🔥 HOT {r['hp']}%</span>
        <span class='tag'>💪 STR {r['str']}</span>
        <span class='tag-g'>X3.5+ {r['p35']}%</span>
        <span class='tag-g'>X4+ {r['p4']}%</span>
        </div>""",unsafe_allow_html=True)
        st.markdown(f"""<div class='targets'>
        <div class='t-card'><div class='t-lbl'>MIN SAFE</div><div class='t-val' style='color:#00ffcc;'>{r['tmin']}×</div><div class='t-acc' style='color:#00ff88;'>{r['acc_min']}% acc</div></div>
        <div class='t-card'><div class='t-lbl'>MOYEN</div><div class='t-val' style='color:#ffd700;'>{r['tmoy']}×</div><div class='t-acc' style='color:#ffdd44;'>{r['acc_moy']}% acc</div></div>
        <div class='t-card'><div class='t-lbl'>MAX X3+</div><div class='t-val' style='color:#ff3366;'>{r['tmax']}×</div><div class='t-acc' style='color:#ff99aa;'>{r['acc_max']}% acc</div></div>
        </div>""",unsafe_allow_html=True)
        cw,cl2=st.columns(2)
        with cw:
            if st.button("✅ WIN X3+",use_container_width=True,key="bw"):
                idx=r.get("hi",-1)
                if 0<=idx<len(st.session_state.H): st.session_state.H[idx]["res"]="W"; sj(HF,st.session_state.H)
                st.session_state.S["t"]+=1; st.session_state.S["w"]+=1; sj(SF,st.session_state.S); st.success("🎯 WIN!"); st.rerun()
        with cl2:
            if st.button("❌ LOSS",use_container_width=True,key="bl"):
                idx=r.get("hi",-1)
                if 0<=idx<len(st.session_state.H): st.session_state.H[idx]["res"]="L"; sj(HF,st.session_state.H)
                st.session_state.S["t"]+=1; st.session_state.S["l"]+=1; sj(SF,st.session_state.S); st.rerun()
    else:
        st.markdown("""<div class='glass-g' style='min-height:360px;display:flex;align-items:center;justify-content:center;'>
        <div style='text-align:center;opacity:.3;'>
        <div style='font-size:4rem;'>✈️</div>
        <div style='font-family:Orbitron;font-size:.9rem;margin-top:12px;'>AMPIDITRA PARAMS<br>TSINDRIO ANALYSER</div>
        </div></div>""",unsafe_allow_html=True)

if st.session_state.H:
    st.markdown("---")
    df=pd.DataFrame([{"T1":x.get("t1",""),"C1":f"{x.get('c1',0)}%","T2":x.get("t2",""),"C2":f"{x.get('c2',0)}%","X3%":x.get("bp",""),"State":x.get("cur",""),"Res":"✅" if x.get("res")=="W" else "❌" if x.get("res")=="L" else "—"} for x in reversed(st.session_state.H[-10:])])
    st.dataframe(df,use_container_width=True,hide_index=True)
