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
.main-title{font-family:'Orbitron'!important;font-size:clamp(1.4rem,6vw,2.8rem)!important;font-weight:900!important;text-align:center!important;color:#ffffff!important;margin:10px 0 5px 0!important;display:block!important;width:100%!important;word-break:break-word!important}
.main-title span{color:#b57bff!important}
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
    hv=(hn%60)-30; pb=int((bp-40)*0.40); sb=int((str_-50)*0.22); cb=int(lc*3.0)
    sh1=max(40,min(120,58+hv+pb+sb+cb))
    rd=max(10,min(40,15+(hn%22)-int(lc*1.5)))+max(6,int(hn%14))
    sh2=sh1+rd
    t1=(bt+timedelta(seconds=sh1)).strftime("%H:%M:%S")
    t2=(bt+timedelta(seconds=sh2)).strftime("%H:%M:%S")
    c2={"COLD":round(min(95,bp*1.18),1),"NORMAL":round(min(95,bp*1.08),1),"WARM":round(min(95,bp*0.95),1),"HOT":round(min(95,bp*0.88),1)}.get(s2st(lc),bp)
    return t1,sh1,bp,t2,sh2,c2

def calc_acc(base_acc,str_,h):
    wins=[x for x in h[-15:] if x.get("res")=="W"]
    hb=min(14,len(wins)*1.5)
    a=round(min(99,max(10,base_acc+hb+(str_-50)*0.12)),1)
    b=round(min(99,max(10,base_acc*0.72+hb*0.8+(str_-50)*0.08)),1)
    return a,b

def engine(h5,lt,lc):
    fh=hashlib.sha512(f"{h5}:{lt}:{lc}".encode()).hexdigest()
    hn=int(fh[:16],16)
    np.random.seed(int((hn&0xFFFFFFFF)+(lc*1000))%(2**32))
    if lc<1.5:    bs,sg=2.12,0.24
    elif lc<2.5: bs,sg=2.06,0.21
    elif lc<3.5: bs,sg=2.00,0.19
    else:         bs,sg=1.96,0.18
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
    base_a=max(10,min(80,38+(hn%30)+p3*0.35))
    acc_min,acc_moy=calc_acc(base_a,str_,st.session_state.H)
    acc_max=round(min(99,max(10,p3*0.82+(len([x for x in st.session_state.H[-15:] if x.get("res")=="W"])*0.8))),1)
    t1,sh1,c1,t2,sh2,c2=calc_tours(hn,bp,str_,lc,lt)
    if    str_>=90 and bp>=46: sig,sc="💎 ULTRA X3+ — FIRE MAX","sig-ultra"
    elif str_>=80 and bp>=40: sig,sc="💎 STRONG X3+ — BUY","sig-ultra"
    elif str_>=70 and bp>=34: sig,sc="🔥 GOOD X3+ — GO","sig-strong"
    elif str_>=58 and bp>=27: sig,sc="⚡ MODERATE — SMALL BET","sig-mod"
    else:                       sig,sc="◎ SKIP — PAS DE SIGNAL","sig-skip"
    return {"lc":lc,"t1":t1,"sh1":sh1,"c1":c1,"t2":t2,"sh2":sh2,"c2":c2,
            "sig":sig,"sc":sc,"bp":bp,"p3":p3,"p35":p35,"p4":p4,"str":str_,
            "cur":cur,"hp":hp,"tmin":tmin,"tmoy":tmoy,"tmax":tmax,
            "acc_min":acc_min,"acc_moy":acc_moy,"acc_max":acc_max,
            "res":None,"hi":len(st.session_state.H)}

def tgt_html(val,lbl,acc,vc,ac):
    return f"""<div class='tgt' style='background:rgba({vc},.08);border:1px solid rgba({vc},.22);'>
    <div class='tgt-v' style='color:rgb({vc});'>{val}×</div>
    <div class='tgt-l'>{lbl}</div>
    <div class='tgt-a' style='color:rgb({ac});'>{acc}%</div></div>"""

if not st.session_state.auth:
    st.markdown("<div class='main-title'>AVIATOR <span>X3 V9</span></div>",unsafe_allow_html=True)
    st.markdown("<div class='main-sub'>Ultra Sniper · Multi-Tour · Markov + Bayesian</div>",unsafe_allow_html=True)
    _,cb,_=st.columns([1,1.1,1])
    with cb:
        st.markdown("<div class='card'>",unsafe_allow_html=True)
        pw=st.text_input("Mot de passe",type="password",placeholder="AVIATOR2026")
        if st.button("Activer l'accès",use_container_width=True):
            if pw=="AVIATOR2026": st.session_state.auth=True; st.rerun()
            else: st.error("❌ Code incorrect")
        st.markdown("</div>",unsafe_allow_html=True)
    st.stop()

with st.sidebar:
    S=st.session_state.S; t,w,l=S.get("t",0),S.get("w",0),S.get("l",0)
    wr=round(w/t*100,1) if t>0 else 0
    st.markdown(f"""<div class='stat-grid'>
    <div class='stat-c'><div class='stat-v'>{wr}%</div><div class='stat-l'>Win Rate</div></div>
    <div class='stat-c'><div class='stat-v'>{w}</div><div class='stat-l'>Wins</div></div>
    <div class='stat-c'><div class='stat-v'>{l}</div><div class='stat-l'>Loss</div></div>
    </div><br>""",unsafe_allow_html=True)
    if st.button("Reset data",use_container_width=True):
        st.session_state.H=[];st.session_state.S={"t":0,"w":0,"l":0};st.session_state.R=None
        for f in [HF,SF]:
            try:
                if f.exists(): f.unlink()
            except: pass
        st.success("✅"); st.rerun()

st.markdown("<div class='main-title'>AVIATOR <span>X3 V9</span></div>",unsafe_allow_html=True)
st.markdown("<div class='main-sub'>Ultra Sniper · 450K Sims · Multi-Tour</div>",unsafe_allow_html=True)

ci,co=st.columns([1,2],gap="large")
with ci:
    st.markdown("<div class='card'>",unsafe_allow_html=True)
    st.markdown("<div class='section-lbl'>Paramètres</div>",unsafe_allow_html=True)
    h5 = st.text_input("HEX SHA512 — 5 chars",placeholder="ac50e")
    ti = st.text_input("Last Time — HH:MM:SS",placeholder="20:22:24")
    lc = st.number_input("Last Cote — résultat précédent",value=1.88,step=0.01,format="%.2f",min_value=1.01)
    cs=s2st(lc); cbg={"COLD":"rgba(68,136,255,.15)","NORMAL":"rgba(150,150,150,.12)","WARM":"rgba(255,200,0,.15)","HOT":"rgba(255,50,50,.15)"}[cs]; cc={"COLD":"#4488ff","NORMAL":"#888","WARM":"#ffcc00","HOT":"#ff3366"}[cs]
    st.markdown(f"<div style='text-align:center;margin:6px 0'><span style='background:{cbg};border:1px solid {cc}44;border-radius:20px;padding:5px 16px;color:{cc};font-size:.8rem;font-weight:700;'>⬤ {cs}</span></div>",unsafe_allow_html=True)
    st.markdown("</div>",unsafe_allow_html=True)
    if st.button("Analyser X3+",use_container_width=True):
        if h5 and ti:
            with st.spinner("Calcul 450k sims..."):
                r=engine(h5.strip(),ti.strip(),lc)
            st.session_state.R=r; st.session_state.H.append(dict(r))
            if len(st.session_state.H)>200: st.session_state.H.pop(0)
            sj(HF,st.session_state.H); st.session_state.ck+=1; st.rerun()
        else: st.error("HEX et Last Time requis")

with co:
    r=st.session_state.R
    if r:
        st.markdown("<div class='card-accent'>",unsafe_allow_html=True)
        st.markdown(f"<div class='sig-box {r['sc']}'>{r['sig']}</div>",unsafe_allow_html=True)
        t1h=tgt_html(r['tmin'],'Min',r['acc_min'],'0,255,204','0,255,136')
        t2h=tgt_html(r['tmoy'],'Moy',r['acc_moy'],'255,215,0','255,221,68')
        t3h=tgt_html(r['tmax'],'Max',r['acc_max'],'255,80,120','255,136,170')
        st.markdown(f"""<div class='tour-grid'>
        <div class='tour-card tour-1'>
          <div class='tour-lbl'>Tour 1 · +{r['sh1']}s</div>
          <div class='tour-t' style='color:#b57bff;'>{r['t1']}</div>
          <div class='tour-c' style='color:#c4a8ff;'>Confiance {r['c1']}%</div>
          <div class='tour-targets'>{t1h}{t2h}{t3h}</div>
        </div>
        <div class='tour-card tour-2'>
          <div class='tour-lbl'>Tour 2 · +{r['sh2']}s</div>
          <div class='tour-t' style='color:#00ddcc;'>{r['t2']}</div>
          <div class='tour-c' style='color:#66ffee;'>Confiance {r['c2']}%</div>
          <div class='tour-targets'>{t1h}{t2h}{t3h}</div>
        </div></div>""",unsafe_allow_html=True)
        st.markdown(f"""<div class='prob-center'>
        <div class='prob-val'>{r['bp']}%</div>
        <div class='prob-lbl'>Probabilité X3+ · Bayesian</div></div>""",unsafe_allow_html=True)
        st.markdown(f"""<div class='tags-row'>
        <span class='tag'>⬤ {r['cur']}</span><span class='tag'>🔥 Hot {r['hp']}%</span>
        <span class='tag'>💪 Str {r['str']}</span>
        <span class='tag-teal'>X3.5+ {r['p35']}%</span><span class='tag-teal'>X4+ {r['p4']}%</span>
        </div>""",unsafe_allow_html=True)
        cw,cl3=st.columns(2)
        with cw:
            if st.button("✅  WIN X3+",use_container_width=True,key="bw"):
                idx=r.get("hi",-1)
                if 0<=idx<len(st.session_state.H): st.session_state.H[idx]["res"]="W"; sj(HF,st.session_state.H)
                st.session_state.S["t"]+=1; st.session_state.S["w"]+=1; sj(SF,st.session_state.S); st.success("Win!"); st.rerun()
        with cl3:
            if st.button("❌  LOSS",use_container_width=True,key="bl"):
                idx=r.get("hi",-1)
                if 0<=idx<len(st.session_state.H): st.session_state.H[idx]["res"]="L"; sj(HF,st.session_state.H)
                st.session_state.S["t"]+=1; st.session_state.S["l"]+=1; sj(SF,st.session_state.S); st.rerun()
        st.markdown("</div>",unsafe_allow_html=True)
    else:
        st.markdown("""<div class='card empty-state'>
        <div style='font-size:3.5rem;'>✈️</div>
        <div style='font-family:Orbitron;font-size:.85rem;text-align:center;line-height:1.7;'>Entrez les paramètres<br>et lancez l'analyse</div>
        </div>""",unsafe_allow_html=True)

if st.session_state.H:
    st.markdown("---")
    df=pd.DataFrame([{"T1":x.get("t1",""),"C1%":f"{x.get('c1',0)}%","T2":x.get("t2",""),"C2%":f"{x.get('c2',0)}%","X3%":x.get("bp",""),"Min":x.get("tmin",""),"Max":x.get("tmax",""),"State":x.get("cur",""),"Res":"✅" if x.get("res")=="W" else "❌" if x.get("res")=="L" else "—"} for x in reversed(st.session_state.H[-10:])])
    st.dataframe(df,use_container_width=True,hide_index=True)
