import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import json
import streamlit.components.v1 as components
from datetime import datetime

st.set_page_config(page_title="MarketRace · Day 27", page_icon="🏁", layout="wide", initial_sidebar_state="collapsed")

STOCKS = {
    "TCS":          {"ticker":"TCS.NS",       "sector":"IT",       "color":"#4a9eff","emoji":"💻"},
    "Infosys":      {"ticker":"INFY.NS",       "sector":"IT",       "color":"#74b9ff","emoji":"🖥️"},
    "Wipro":        {"ticker":"WIPRO.NS",      "sector":"IT",       "color":"#0984e3","emoji":"⚡"},
    "HCL Tech":     {"ticker":"HCLTECH.NS",    "sector":"IT",       "color":"#6c5ce7","emoji":"🔮"},
    "HDFC Bank":    {"ticker":"HDFCBANK.NS",   "sector":"Banking",  "color":"#c9a96e","emoji":"🏦"},
    "ICICI Bank":   {"ticker":"ICICIBANK.NS",  "sector":"Banking",  "color":"#e0a04a","emoji":"💰"},
    "SBI":          {"ticker":"SBIN.NS",       "sector":"Banking",  "color":"#fdcb6e","emoji":"🏛️"},
    "Kotak Bank":   {"ticker":"KOTAKBANK.NS",  "sector":"Banking",  "color":"#e17055","emoji":"🔑"},
    "Reliance":     {"ticker":"RELIANCE.NS",   "sector":"Energy",   "color":"#00b894","emoji":"⛽"},
    "ITC":          {"ticker":"ITC.NS",        "sector":"FMCG",     "color":"#55efc4","emoji":"🌿"},
    "HUL":          {"ticker":"HINDUNILVR.NS", "sector":"FMCG",     "color":"#00cec9","emoji":"🧴"},
    "Asian Paints": {"ticker":"ASIANPAINT.NS", "sector":"Consumer", "color":"#fd79a8","emoji":"🎨"},
    "Maruti":       {"ticker":"MARUTI.NS",     "sector":"Auto",     "color":"#e05c6c","emoji":"🚗"},
    "Tata Motors":  {"ticker":"TATAMOTORS.NS", "sector":"Auto",     "color":"#d63031","emoji":"🚙"},
    "Sun Pharma":   {"ticker":"SUNPHARMA.NS",  "sector":"Pharma",   "color":"#a29bfe","emoji":"💊"},
    "Nifty 50":     {"ticker":"^NSEI",         "sector":"Index",    "color":"#e8e4dc","emoji":"📈"},
    "Bank Nifty":   {"ticker":"^NSEBANK",      "sector":"Index",    "color":"#dfe6e9","emoji":"🏪"},
}
PERIODS = {"1 Month":"1mo","3 Months":"3mo","6 Months":"6mo","1 Year":"1y"}

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');
html,body,[class*="css"]{font-family:'Syne',sans-serif!important;background:#09090e!important;color:#e8e4dc!important;}
[data-testid="stApp"],.stApp,[data-testid="stAppViewContainer"],[data-testid="stVerticalBlock"]{background:#09090e!important;}
#MainMenu,footer,header,[data-testid="stDecoration"],[data-testid="stToolbar"]{display:none!important;}
.block-container{padding:1rem 2rem!important;max-width:100%!important;}
.stButton>button{font-family:'DM Mono',monospace!important;border-radius:2px!important;}
.stButton>button[kind="primary"]{background:#c9a96e!important;color:#09090e!important;border:none!important;font-size:.8rem!important;font-weight:600!important;}
.stButton>button[kind="secondary"]{background:transparent!important;color:#e8e4dc!important;border:1px solid rgba(255,255,255,.12)!important;font-size:.8rem!important;}
.stSelectbox>div>div,.stMultiSelect>div>div{background:#111118!important;border:1px solid rgba(255,255,255,.08)!important;border-radius:3px!important;color:#e8e4dc!important;}
.stCheckbox label{color:#888!important;font-family:'DM Mono',monospace!important;font-size:.75rem!important;}
::-webkit-scrollbar{width:3px;}::-webkit-scrollbar-thumb{background:rgba(201,169,110,.15);}
</style>"""

def make_serialisable(obj):
    if isinstance(obj,(np.int64,np.int32,np.int16,np.int8)): return int(obj)
    if isinstance(obj,(np.float64,np.float32,np.float16)): return float(obj)
    if isinstance(obj,np.ndarray): return obj.tolist()
    if isinstance(obj,dict): return {k:make_serialisable(v) for k,v in obj.items()}
    if isinstance(obj,list): return [make_serialisable(i) for i in obj]
    return obj

@st.cache_data(ttl=3600)
def fetch_stock_data(ticker, period):
    try:
        df = yf.download(ticker, period=period, interval="1d", progress=False, auto_adjust=True)
        if df.empty or len(df) < 10: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = [c[0] for c in df.columns]
        df = df.dropna()
        closes  = [float(x) for x in df["Close"].round(2).tolist()]
        highs   = [float(x) for x in df["High"].round(2).tolist()]
        lows    = [float(x) for x in df["Low"].round(2).tolist()]
        volumes = [int(x) for x in df["Volume"].fillna(0).astype(int).tolist()]
        dates   = df.index.strftime("%d %b %y").tolist()
        rets = [0.0]
        for i in range(1, len(closes)):
            r = (closes[i]-closes[i-1])/closes[i-1] if closes[i-1]>0 else 0.0
            rets.append(round(float(r), 5))
        total_return = float((closes[-1]/closes[0]-1) if closes[0]>0 else 0)
        sorted_moves = sorted(enumerate(rets), key=lambda x: abs(x[1]), reverse=True)[:5]
        big_moves = [{"idx":int(idx),"ret":round(float(ret),4),"date":dates[idx],
                      "price":float(closes[idx]),"direction":"up" if ret>0 else "down"}
                     for idx,ret in sorted_moves]
        vol_arr = np.array(volumes, dtype=float)
        v_min, v_max = vol_arr.min(), vol_arr.max()
        vol_norm = ((vol_arr - v_min) / (v_max - v_min + 1)).tolist()
        roughness = [round(float((highs[i]-lows[i])/closes[i]*100),3) if closes[i]>0 else 0.0 for i in range(len(closes))]
        ann_vol = float(np.array(rets[1:]).std() * np.sqrt(252)) if len(rets)>1 else 0.0
        try:
            divs = yf.Ticker(ticker).dividends
            div_events = []
            if not divs.empty:
                for dt2, amount in divs.items():
                    ds = dt2.strftime("%d %b %y")
                    if ds in dates:
                        div_events.append({"idx":dates.index(ds),"amount":float(round(amount,2)),"date":ds})
        except:
            div_events = []
        vol_mean = float(np.mean(volumes))
        buyback_events = sorted([
            {"idx":i,"date":dates[i],"ret":rets[i]}
            for i in range(len(closes)) if volumes[i]>vol_mean*2.2 and rets[i]>0.005
        ], key=lambda x: x["ret"], reverse=True)[:3]
        return {
            "closes":closes,"highs":highs,"lows":lows,"volumes":volumes,"dates":dates,
            "returns":rets,"vol_norm":[float(x) for x in vol_norm],"roughness":roughness,
            "total_return":round(total_return,4),"big_moves":big_moves,
            "n_days":int(len(closes)),"start_price":float(closes[0]),"end_price":float(closes[-1]),
            "ann_vol":round(ann_vol*100,2),"div_events":div_events,"buyback_events":buyback_events,
        }
    except: return None

def prepare_race_data(selected, period):
    racers, failed = [], []
    for name in selected:
        cfg = STOCKS[name]
        data = fetch_stock_data(cfg["ticker"], period)
        if data is None: failed.append(name); continue
        racers.append({"name":name,"ticker":cfg["ticker"],"sector":cfg["sector"],
                       "color":cfg["color"],"emoji":cfg["emoji"],"data":data})
    racers.sort(key=lambda r: r["data"]["total_return"], reverse=True)
    return {"racers":racers,"failed":failed,"period":period,
            "n_racers":len(racers),"generated":datetime.now().strftime("%H:%M:%S IST")}

# ─────────────────────────────────────────────────────────────────
# COMPUTER RACE HTML
# ─────────────────────────────────────────────────────────────────
COMPUTER_RACE_CSS = """
*{margin:0;padding:0;box-sizing:border-box;}
body{background:#09090e;font-family:'DM Mono',monospace;overflow:hidden;}
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@1,700&family=DM+Mono:wght@400;500&display=swap');
#gw{width:100%;height:680px;position:relative;background:#09090e;}
canvas{display:block;width:100%;height:100%;}
#hud{position:absolute;top:12px;left:16px;right:16px;display:flex;justify-content:space-between;pointer-events:none;gap:8px;}
.hc{background:rgba(17,17,24,.88);border:1px solid rgba(255,255,255,.07);border-radius:4px;padding:8px 12px;backdrop-filter:blur(8px);}
.ht{font-size:8px;color:#444;text-transform:uppercase;letter-spacing:.12em;margin-bottom:5px;}
.lr{display:flex;align-items:center;gap:7px;font-size:10px;margin:3px 0;}
.pb{width:15px;height:15px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:8px;font-weight:bold;background:rgba(255,255,255,.08);color:#666;flex-shrink:0;}
.pb.gold{background:#c9a96e;color:#09090e;}.pb.silver{background:#aaa;color:#09090e;}.pb.bronze{background:#cd7f32;color:#09090e;}
#pgbar{position:absolute;bottom:0;left:0;right:0;height:3px;background:rgba(255,255,255,.04);}
#pgfill{height:100%;background:linear-gradient(90deg,#c9a96e,#4ab87a);width:0%;}
#startOv{position:absolute;inset:0;background:rgba(9,9,14,.94);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;}
#cdTxt{font-family:'Playfair Display',serif;font-size:88px;color:#c9a96e;line-height:1;}
#resOv{position:absolute;inset:0;background:rgba(9,9,14,.95);display:none;flex-direction:column;align-items:center;justify-content:center;gap:10px;}
.rbtn{background:#c9a96e;color:#09090e;border:none;padding:9px 26px;font-family:'DM Mono';font-size:12px;font-weight:600;border-radius:2px;cursor:pointer;}
"""

COMPUTER_RACE_JS = """
const canvas=document.getElementById('gc'),ctx=canvas.getContext('2d');
let W=0,H=0;
function resize(){W=canvas.offsetWidth;H=canvas.offsetHeight;canvas.width=W;canvas.height=H;}
resize();
window.addEventListener('resize',()=>{resize();if(terrains.length)terrains=GD.racers.map(r=>genTerrain(r.data));});

function drawBG(){
  const g=ctx.createLinearGradient(0,0,0,H);
  g.addColorStop(0,'#09090e');g.addColorStop(.6,'#0d1117');g.addColorStop(1,'#111118');
  ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
  ctx.fillStyle='rgba(255,255,255,.2)';
  [[.08,.04],[.22,.07],[.38,.03],[.55,.06],[.72,.04],[.88,.09],[.15,.12],[.48,.10],[.65,.08],[.82,.05]].forEach(([rx,ry])=>{
    ctx.beginPath();ctx.arc(rx*W,ry*H,.8,0,Math.PI*2);ctx.fill();
  });
}

function genTerrain(d){
  const MT=H*.18,MB=H*.20,UH=H-MT-MB,n=d.n_days||d.closes.length;
  const mn=Math.min(...d.closes),mx=Math.max(...d.closes),rng=(mx-mn)||1;
  return d.closes.map((p,i)=>{
    const norm=(p-mn)/rng,baseY=H-MB-norm*UH;
    const ba=(d.roughness[i]||0)*(d.vol_norm[i]||0)*7;
    const bump=(Math.sin(i*2.31)*.6+Math.cos(i*1.73)*.4)*ba;
    return{x:(i/Math.max(n-1,1))*W,y:Math.max(MT,Math.min(H-MB,baseY+bump)),ret:d.returns[i],date:d.dates[i]};
  });
}

function getTY(t,x){
  if(!t||!t.length)return H*.5;
  if(x<=t[0].x)return t[0].y;
  if(x>=t[t.length-1].x)return t[t.length-1].y;
  let lo=0,hi=t.length-1;
  while(lo<hi-1){const m=(lo+hi)>>1;if(t[m].x<=x)lo=m;else hi=m;}
  const d=t[hi].x-t[lo].x,t2=d<.001?0:(x-t[lo].x)/d;
  return t[lo].y+t2*(t[hi].y-t[lo].y);
}
function getTA(t,x){const dx=W/Math.max(t.length,1);return Math.atan2(getTY(t,x+dx)-getTY(t,x),dx);}

function drawTerrain(t,col){
  if(!t||t.length<2)return;
  ctx.beginPath();ctx.moveTo(t[0].x,H);t.forEach(p=>ctx.lineTo(p.x,p.y));
  ctx.lineTo(t[t.length-1].x,H);ctx.closePath();ctx.fillStyle=col+'18';ctx.fill();
  ctx.beginPath();ctx.moveTo(t[0].x,t[0].y);
  for(let i=1;i<t.length-2;i++){
    const cpx=(t[i].x+t[i+1].x)/2,cpy=(t[i].y+t[i+1].y)/2;
    ctx.quadraticCurveTo(t[i].x,t[i].y,cpx,cpy);
  }
  ctx.lineTo(t[t.length-1].x,t[t.length-1].y);
  ctx.strokeStyle=col+'55';ctx.lineWidth=2;ctx.stroke();
}

function drawAnnot(t,m,col){
  if(!SHOW_ANN||!m)return;
  const pt=t[Math.min(m.idx,t.length-1)];if(!pt)return;
  const up=m.ret>0,lbl=(up?'▲ +':'▼ ')+(m.ret*100).toFixed(1)+'%';
  ctx.beginPath();ctx.moveTo(pt.x,pt.y-8);ctx.lineTo(pt.x,pt.y-42);
  ctx.strokeStyle=(up?'#4ab87a':'#e05c6c')+'70';ctx.lineWidth=1;ctx.setLineDash([2,4]);ctx.stroke();ctx.setLineDash([]);
  ctx.font='8px DM Mono,monospace';ctx.fillStyle=up?'#4ab87a':'#e05c6c';
  ctx.textAlign='center';ctx.fillText(lbl,pt.x,pt.y-46);
  ctx.fillStyle='#3a3a4a';ctx.fillText(m.date,pt.x,pt.y-36);
}

function drawFinish(){
  const x=W-18;
  for(let i=0;i<14;i++){ctx.fillStyle=i%2===0?'rgba(255,255,255,.85)':'rgba(0,0,0,.7)';ctx.fillRect(x,i*12,8,12);}
  ctx.font='bold 8px DM Mono';ctx.fillStyle='rgba(201,169,110,.7)';ctx.textAlign='center';ctx.fillText('FINISH',x+4,H-6);
}

function drawCar(v,terrain){
  const y=getTY(terrain,v.x),ang=getTA(terrain,v.x);
  if(v.trail.length>2){
    ctx.beginPath();ctx.moveTo(v.trail[0].x,v.trail[0].y-6);
    v.trail.forEach(p=>ctx.lineTo(p.x,p.y-6));
    ctx.strokeStyle=v.color+'30';ctx.lineWidth=2;ctx.stroke();
  }
  ctx.save();ctx.translate(v.x,y-14);ctx.rotate(ang);
  ctx.beginPath();ctx.ellipse(0,10,18,5,0,0,Math.PI*2);ctx.fillStyle='rgba(0,0,0,.2)';ctx.fill();
  ctx.fillStyle=v.color;
  ctx.beginPath();ctx.moveTo(-18,0);ctx.lineTo(-18,10);ctx.lineTo(18,10);ctx.lineTo(18,0);ctx.lineTo(12,-2);ctx.closePath();ctx.fill();
  ctx.fillStyle=v.color+'dd';
  ctx.beginPath();ctx.moveTo(-10,0);ctx.lineTo(-14,-10);ctx.lineTo(8,-10);ctx.lineTo(12,0);ctx.closePath();ctx.fill();
  ctx.fillStyle='rgba(180,225,255,.65)';
  ctx.beginPath();ctx.moveTo(-8,0);ctx.lineTo(-11,-9);ctx.lineTo(7,-9);ctx.lineTo(10,0);ctx.closePath();ctx.fill();
  ctx.fillStyle='rgba(255,240,140,.9)';ctx.beginPath();ctx.arc(17,4,3,0,Math.PI*2);ctx.fill();
  [[-11,10],[11,10]].forEach(([wx,wy])=>{
    ctx.beginPath();ctx.arc(wx,wy,6,0,Math.PI*2);ctx.fillStyle='#1a1a22';ctx.fill();
    ctx.beginPath();ctx.arc(wx,wy,2.5,0,Math.PI*2);ctx.fillStyle='#555';ctx.fill();
  });
  ctx.restore();
  ctx.font='bold 9px DM Mono,monospace';ctx.fillStyle=v.color;ctx.textAlign='center';
  ctx.fillText(v.emoji+' '+v.name,v.x,y-30);
}

function updateLB(vs){
  const act=vs.filter(v=>v.active);if(!act.length)return;
  const s=[...act].sort((a,b)=>b.x-a.x);
  let h='<div class="ht">Live Standings</div>';
  s.forEach((v,i)=>{
    const p=Math.min(100,(v.x/W*100)).toFixed(0),b=i===0?'gold':i===1?'silver':i===2?'bronze':'';
    h+=`<div class="lr"><div class="pb ${b}">${i+1}</div><span style="color:${v.color}">${v.emoji} ${v.name}</span><span style="color:#333;margin-left:auto">${p}%</span></div>`;
  });
  document.getElementById('lb').innerHTML=h;
}

function showResults(fo){
  document.getElementById('resOv').style.display='flex';
  const pc=[{oi:1,h:90,c:'#aaa',m:'🥈'},{oi:0,h:120,c:'#c9a96e',m:'🏆'},{oi:2,h:70,c:'#cd7f32',m:'🥉'}];
  let ph='';
  pc.forEach(sl=>{
    const v=fo[sl.oi];if(!v)return;
    const d=GD.racers[v.ri]&&GD.racers[v.ri].data;
    const ret=d?(d.total_return*100).toFixed(1):'?';
    ph+=`<div style="text-align:center">
      <div style="font-size:8px;color:#555;margin-bottom:3px">${v.name.toUpperCase()}</div>
      <div style="font-size:18px;margin-bottom:3px">${v.emoji}</div>
      <div style="width:76px;height:${sl.h}px;background:rgba(255,255,255,.04);border-top:2px solid ${sl.c};display:flex;align-items:center;justify-content:center;font-size:18px">${sl.m}</div>
      <div style="font-size:10px;color:${parseFloat(ret)>0?'#4ab87a':'#e05c6c'};margin-top:5px;font-weight:600">${parseFloat(ret)>0?'+':''}${ret}%</div>
    </div>`;
  });
  document.getElementById('pod').innerHTML=ph;
  let t='<table style="border-collapse:collapse;margin:4px auto">';
  t+='<tr><th style="padding:3px 8px;color:#333;font-size:8px">Rank</th><th style="padding:3px 8px;color:#333;font-size:8px">Stock</th><th style="padding:3px 8px;color:#333;font-size:8px">1Y Return</th></tr>';
  fo.forEach((v,i)=>{
    if(!v)return;
    const d=GD.racers[v.ri]&&GD.racers[v.ri].data;
    const ret=d?(d.total_return*100).toFixed(1):'?';
    t+=`<tr><td style="padding:3px 8px;color:#444;font-size:9px">#${i+1}</td><td style="padding:3px 8px;color:${v.color};font-size:9px">${v.emoji} ${v.name}</td><td style="padding:3px 8px;color:${parseFloat(ret)>0?'#4ab87a':'#e05c6c'};font-size:9px">${parseFloat(ret)>0?'+':''}${ret}%</td></tr>`;
  });
  t+='</table>';document.getElementById('rtab').innerHTML=t;
}

let vehicles=[],terrains=[],state='cd',frame=0,fo=[],aid;

function init(){
  vehicles=[];terrains=[];fo=[];frame=0;
  GD.racers.forEach((r,i)=>{
    terrains.push(genTerrain(r.data));
    vehicles.push({name:r.name,color:r.color,emoji:r.emoji,ri:i,x:0,
      spd:1.8*SPD,active:false,finished:false,trail:[],startDelay:80+i*35});
  });
}

function loop(){
  ctx.clearRect(0,0,W,H);drawBG();
  if(state==='cd'){
    terrains.forEach((t,i)=>drawTerrain(t,vehicles[i]?vehicles[i].color:'#fff'));
    drawFinish();
    const el=frame/60,rem=3-Math.floor(el);
    const e=document.getElementById('cdTxt');
    if(rem>0){e.textContent=rem;e.style.color='#c9a96e';}else{e.textContent='GO!';e.style.color='#4ab87a';}
    if(el>=4.5){state='race';document.getElementById('startOv').style.display='none';}
    frame++;aid=requestAnimationFrame(loop);return;
  }
  if(state==='race'){
    terrains.forEach((t,i)=>{
      if(!t)return;
      drawTerrain(t,vehicles[i]?vehicles[i].color:'#fff');
      if(SHOW_ANN&&GD.racers[i]&&GD.racers[i].data&&GD.racers[i].data.big_moves){
        GD.racers[i].data.big_moves.slice(0,3).forEach(m=>drawAnnot(t,m,vehicles[i]?vehicles[i].color:'#fff'));
      }
    });
    drawFinish();
    vehicles.forEach((v,i)=>{
      const t=terrains[i];if(!t||!t.length)return;
      if(frame<v.startDelay){drawCar(v,t);return;}
      v.active=true;
      const r=GD.racers[i];if(!r)return;
      const ang=getTA(t,v.x);
      const di=Math.min(Math.floor((v.x/W)*(r.data.n_days-1)),r.data.returns.length-1);
      const dr=r.data.returns[di]||0,sl=-Math.sin(ang)*2.8,rb=dr*18;
      v.spd=Math.max(0.6,Math.min(7.5,v.spd+(sl+rb)*.045));
      v.x+=v.spd*SPD;
      const y=getTY(t,v.x);
      v.trail.push({x:v.x,y});if(v.trail.length>55)v.trail.shift();
      drawCar(v,t);
      if(v.x>=W-22&&!v.finished){v.finished=true;fo.push(v);}
    });
    updateLB(vehicles);
    const lead=vehicles.reduce((a,b)=>b.x>a.x?b:a,vehicles[0]);
    const p=Math.min(100,(lead.x/W*100)).toFixed(0);
    document.getElementById('pct').textContent=p+'%';
    document.getElementById('pgfill').style.width=p+'%';
    if(vehicles.length===1&&vehicles[0].finished){state='done';showResults(fo);return;}
    if(vehicles.length>1&&vehicles.every(v=>v.finished)){state='done';showResults(fo);return;}
    frame++;aid=requestAnimationFrame(loop);
  }
}

function restart(){
  cancelAnimationFrame(aid);
  document.getElementById('resOv').style.display='none';
  document.getElementById('startOv').style.display='flex';
  document.getElementById('cdTxt').textContent='3';
  document.getElementById('cdTxt').style.color='#c9a96e';
  state='cd';init();frame=0;loop();
}

init();loop();
"""

def build_computer_race_html(race_data, race_speed, show_ann, period_label):
    speed_map = {"Slow":0.6,"Normal":1.0,"Fast":1.5,"Turbo":2.2}
    spd = str(speed_map.get(race_speed, 1.0))
    gj = json.dumps(make_serialisable(race_data))
    racers_str = " vs ".join(r["name"] for r in race_data["racers"])
    sa = "true" if show_ann else "false"
    html = (
        '<!DOCTYPE html><html><head><meta charset="utf-8">'
        '<style>' + COMPUTER_RACE_CSS + '</style></head><body>'
        '<div id="gw"><canvas id="gc"></canvas>'
        '<div id="hud">'
        '<div class="hc"><div class="ht">🏁 MARKETRACE · ' + period_label + '</div>'
        '<div style="font-size:10px;color:#c9a96e;font-style:italic;">Day 27 · 30 Days of AI Finance</div></div>'
        '<div class="hc" id="lb"><div class="ht">Live Standings</div></div>'
        '<div class="hc"><div class="ht">Progress</div>'
        '<div id="pct" style="font-size:20px;color:#e8e4dc;font-family:\'Playfair Display\',serif;">0%</div></div>'
        '</div>'
        '<div id="pgbar"><div id="pgfill"></div></div>'
        '<div id="startOv">'
        '<div style="font-family:\'Playfair Display\',serif;font-size:22px;color:#c9a96e;font-style:italic;">🏁 MarketRace</div>'
        '<div style="font-size:11px;color:#555;text-align:center;max-width:340px;line-height:1.6;">'
        + racers_str + '<br><span style="color:#444">Best 1Y performer wins.</span></div>'
        '<div id="cdTxt">3</div>'
        '<div style="font-size:9px;color:#333;letter-spacing:.08em;">TERRAIN FROM REAL NSE PRICE DATA</div>'
        '</div>'
        '<div id="resOv">'
        '<div style="font-family:\'Playfair Display\',serif;font-size:30px;color:#c9a96e;">🏆 Race Complete</div>'
        '<div id="pod" style="display:flex;gap:16px;align-items:flex-end;margin:6px 0;"></div>'
        '<div id="rtab" style="margin-top:6px;font-size:10px;color:#666;text-align:center;"></div>'
        '<button class="rbtn" onclick="restart()">↺ Race Again</button>'
        '<div style="font-size:8px;color:#333;margin-top:8px;">RESULTS REFLECT ACTUAL ' + period_label + ' PERFORMANCE · NOT INVESTMENT ADVICE</div>'
        '</div></div>'
        '<script>const GD=' + gj + ';const SHOW_ANN=' + sa + ';const SPD=' + spd + ';'
        + COMPUTER_RACE_JS +
        '</script></body></html>'
    )
    return html

# ─────────────────────────────────────────────────────────────────
# PLAY MODE HTML TEMPLATE
# FIX 1 — car: buildT called BEFORE initCar in boot, so tPts always populated
# FIX 2 — terrain lines: stroke only the surface line, no fill overlap artefacts
# FIX 3 — brake/gas SVG: corrected gradient IDs (bG / gG are unique per page)
# ─────────────────────────────────────────────────────────────────
PLAY_HTML_TEMPLATE = r"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@1,700&family=DM+Mono:wght@400;500;600&family=Syne:wght@700&display=swap');
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent;touch-action:none;user-select:none;}
html,body{width:100%;height:100%;overflow:hidden;background:#020206;}
#lsGate{display:none;position:fixed;inset:0;background:#020206;z-index:9999;flex-direction:column;align-items:center;justify-content:center;gap:20px;text-align:center;padding:32px;}
.phoneIcon{font-size:56px;animation:rotH 2s ease-in-out infinite;}
@keyframes rotH{0%,100%{transform:rotate(0deg)}45%,55%{transform:rotate(90deg)}}
@media(orientation:portrait)and(max-width:900px){#lsGate{display:flex;}}
#wrap{width:100%;height:100vh;position:relative;overflow:hidden;}
canvas{display:block;width:100%;height:100%;}
#topHud{position:absolute;top:0;left:0;right:0;height:44px;display:flex;align-items:stretch;pointer-events:none;z-index:20;background:rgba(2,2,6,.78);border-bottom:1px solid rgba(255,255,255,.05);}
.hCell{display:flex;flex-direction:column;justify-content:center;padding:0 12px;border-right:1px solid rgba(255,255,255,.05);}
.hCell:last-child{border-right:none;}
.hLbl{font-family:'DM Mono',monospace;font-size:7px;color:#3a3a4a;text-transform:uppercase;letter-spacing:.1em;margin-bottom:1px;}
.hVal{font-family:'Playfair Display',serif;font-size:18px;color:#c9a96e;line-height:1;font-style:italic;}
.hMono{font-family:'DM Mono',monospace;font-size:12px;color:#e8e4dc;font-style:normal;}
#fuelCell{flex:1.4;}
#fuelBar{width:100%;height:6px;background:rgba(255,255,255,.06);border-radius:3px;overflow:hidden;margin-top:3px;}
#fuelFill{height:100%;width:100%;border-radius:3px;transition:width .12s;}
#stkName{font-family:'DM Mono',monospace;font-size:9px;color:#c9a96e;font-weight:600;}
#stkRet{font-family:'DM Mono',monospace;font-size:8px;color:#444;}
#flipBanner{position:absolute;top:58px;left:50%;transform:translateX(-50%);font-family:'Playfair Display',serif;font-size:24px;color:#c9a96e;font-style:italic;text-shadow:0 0 20px rgba(201,169,110,.5);opacity:0;transition:opacity .12s;pointer-events:none;z-index:30;white-space:nowrap;}
#ticker{position:absolute;bottom:108px;left:0;right:0;height:20px;background:rgba(2,2,6,.7);border-top:1px solid rgba(255,255,255,.04);overflow:hidden;display:flex;align-items:center;pointer-events:none;z-index:10;}
#tickerInner{font-family:'DM Mono',monospace;font-size:8px;color:#444;letter-spacing:.05em;white-space:nowrap;animation:tickA 35s linear infinite;}
@keyframes tickA{0%{transform:translateX(100vw)}100%{transform:translateX(-100%)}}
#ctrlBar{position:absolute;bottom:0;left:0;right:0;height:108px;display:flex;align-items:center;justify-content:space-between;padding:8px 16px 12px;pointer-events:all;z-index:20;background:linear-gradient(0deg,rgba(2,2,6,.92) 60%,transparent);}
.pedal{cursor:pointer;pointer-events:all;}
.pedal svg{display:block;transition:filter .1s;}
.pedal:active svg,.pedal.pressed svg{filter:brightness(1.5) drop-shadow(0 0 8px currentColor);}
.pLbl{font-family:'DM Mono',monospace;font-size:8px;letter-spacing:.08em;text-transform:uppercase;text-align:center;margin-top:5px;}
#brkBtn .pLbl{color:#e05c6c;}
#gasBtn .pLbl{color:#4ab87a;}
#ctrlMid{display:flex;flex-direction:column;align-items:center;gap:3px;pointer-events:none;}
#pauseBtn{position:absolute;top:50px;left:10px;z-index:25;background:rgba(9,9,14,.75);border:1px solid rgba(255,255,255,.07);border-radius:3px;padding:4px 10px;font-family:'DM Mono',monospace;font-size:8px;color:#444;cursor:pointer;pointer-events:all;}
#stkSelBtn{position:absolute;top:50px;right:10px;z-index:25;background:rgba(9,9,14,.75);border:1px solid rgba(255,255,255,.07);border-radius:3px;padding:4px 10px;font-family:'DM Mono',monospace;font-size:8px;color:#666;cursor:pointer;pointer-events:all;white-space:nowrap;}
#stkPanel{display:none;position:absolute;right:10px;top:76px;z-index:26;background:rgba(8,8,14,.97);border:1px solid rgba(255,255,255,.08);border-radius:4px;padding:6px;width:170px;max-height:220px;overflow-y:auto;}
.sItem{font-family:'DM Mono',monospace;font-size:9px;color:#555;padding:4px 8px;cursor:pointer;border-radius:2px;display:flex;justify-content:space-between;}
.sItem:hover,.sItem.active{background:rgba(201,169,110,.1);color:#c9a96e;}
.ov{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;z-index:50;}
#loadScr{background:rgba(2,2,6,1);}
#startScr{background:rgba(2,2,6,.97);display:none;}
#goScr{background:rgba(2,2,6,.97);display:none;}
#pauseScr{background:rgba(2,2,6,.88);display:none;backdrop-filter:blur(6px);}
.ovT{font-family:'Playfair Display',serif;font-size:clamp(24px,5vw,38px);color:#c9a96e;font-style:italic;text-align:center;}
.ovS{font-family:'DM Mono',monospace;font-size:clamp(9px,2vw,11px);color:#444;text-align:center;max-width:300px;line-height:1.75;}
.ovBtn{background:#c9a96e;color:#09090e;border:none;padding:10px 28px;font-family:'DM Mono',monospace;font-size:12px;font-weight:600;border-radius:2px;cursor:pointer;}
.ovBtn:hover{background:#d4b87a;}
.ovBtn.sec{background:transparent;color:#555;border:1px solid rgba(255,255,255,.1);}
.goGrid{display:grid;grid-template-columns:1fr 1fr;gap:8px;width:240px;}
.goCell{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:3px;padding:8px 12px;text-align:center;}
.goCL{font-size:7px;color:#333;text-transform:uppercase;letter-spacing:.1em;margin-bottom:2px;font-family:'DM Mono',monospace;}
.goCV{font-size:18px;color:#e8e4dc;font-family:'Playfair Display',serif;font-style:italic;}
.ldBar{width:220px;height:3px;background:rgba(255,255,255,.06);border-radius:3px;overflow:hidden;}
.ldFill{height:100%;background:linear-gradient(90deg,#c9a96e,#4ab87a);border-radius:3px;animation:ldA 1.8s ease-in-out infinite;}
@keyframes ldA{0%{width:0;margin-left:0}55%{width:70%;margin-left:0}100%{width:0;margin-left:100%}}
.dots{display:flex;gap:8px;}
.dot{width:6px;height:6px;border-radius:50%;background:#c9a96e;opacity:.3;animation:dp 1.2s ease-in-out infinite;}
.dot:nth-child(2){animation-delay:.2s;}.dot:nth-child(3){animation-delay:.4s;}
@keyframes dp{0%,100%{opacity:.3;transform:scale(1)}50%{opacity:1;transform:scale(1.3)}}
::-webkit-scrollbar{width:3px;}::-webkit-scrollbar-thumb{background:rgba(201,169,110,.2);}
</style></head>
<body>
<div id="lsGate">
  <div class="phoneIcon">📱</div>
  <div style="font-family:'Syne',sans-serif;font-size:20px;color:#c9a96e;font-weight:700;">Rotate Your Phone</div>
  <div style="font-family:'DM Mono',monospace;font-size:11px;color:#444;line-height:1.8;text-align:center;">MarketRace plays best in landscape.<br>Turn sideways to start.</div>
</div>
<div id="wrap">
  <canvas id="gc"></canvas>
  <div id="topHud">
    <div class="hCell" style="min-width:75px;"><div class="hLbl">Score</div><div class="hVal" id="scoreV">0</div></div>
    <div class="hCell" style="min-width:85px;"><div class="hLbl">Distance</div><div class="hVal hMono" id="distV">0m</div></div>
    <div class="hCell" id="fuelCell"><div class="hLbl">Fuel</div><div id="fuelBar"><div id="fuelFill"></div></div></div>
    <div class="hCell" style="min-width:100px;"><div id="stkName">—</div><div id="stkRet">1Y: —</div></div>
    <div class="hCell" style="min-width:70px;"><div class="hLbl">Time</div><div class="hVal hMono" id="timeV">00:00</div></div>
  </div>
  <div id="flipBanner"></div>
  <div id="ticker"><div id="tickerInner">TICKER_PLACEHOLDER</div></div>
  <div id="pauseBtn" onclick="togglePause()">⏸ Pause</div>
  <div id="stkSelBtn" onclick="toggleSel()">📈 Stock ▾</div>
  <div id="stkPanel"></div>
  <div id="ctrlBar">
    <!-- BRAKE PEDAL: wide horizontal brake pad with vertical rubber ribs -->
    <div class="pedal" id="brkBtn">
      <svg width="92" height="80" viewBox="0 0 92 80" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="brakeGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#2a1218"/>
            <stop offset="100%" stop-color="#180a0e"/>
          </linearGradient>
        </defs>
        <!-- shaft -->
        <rect x="36" y="57" width="20" height="20" rx="2" fill="#111118" stroke="#252530" stroke-width="1"/>
        <!-- pad face -->
        <path d="M6 16 L86 16 L80 60 L12 60 Z" fill="url(#brakeGrad)" stroke="#e05c6c" stroke-width="1.5"/>
        <!-- top glint -->
        <path d="M10 18 L82 18 L78 26 L14 26 Z" fill="rgba(255,255,255,.06)"/>
        <!-- vertical rubber ribs -->
        <line x1="22" y1="23" x2="19" y2="55" stroke="rgba(0,0,0,.45)" stroke-width="5" stroke-linecap="round"/>
        <line x1="38" y1="21" x2="35" y2="57" stroke="rgba(0,0,0,.45)" stroke-width="5" stroke-linecap="round"/>
        <line x1="54" y1="21" x2="51" y2="57" stroke="rgba(0,0,0,.45)" stroke-width="5" stroke-linecap="round"/>
        <line x1="70" y1="23" x2="67" y2="55" stroke="rgba(0,0,0,.45)" stroke-width="5" stroke-linecap="round"/>
        <text x="46" y="43" text-anchor="middle" font-family="DM Mono,monospace" font-size="10" fill="rgba(224,92,108,.9)" font-weight="600">BRAKE</text>
        <text x="46" y="54" text-anchor="middle" font-family="DM Mono,monospace" font-size="9" fill="rgba(224,92,108,.5)">◀◀</text>
      </svg>
      <div class="pLbl">Brake / Tilt Fwd</div>
    </div>
    <div id="ctrlMid">
      <div style="font-family:'DM Mono',monospace;font-size:7px;color:#22222a;letter-spacing:.1em;">MARKETRACE · DAY 27</div>
      <div id="airInd" style="font-size:10px;margin-top:3px;color:#c9a96e;"></div>
    </div>
    <!-- GAS PEDAL: angled narrow-top wide-bottom accelerator with horizontal rubber ribs -->
    <div class="pedal" id="gasBtn">
      <svg width="92" height="80" viewBox="0 0 92 80" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="gasGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#0c1e10"/>
            <stop offset="100%" stop-color="#07100a"/>
          </linearGradient>
        </defs>
        <!-- angled shaft -->
        <rect x="55" y="55" width="16" height="22" rx="2" fill="#111118" stroke="#252530" stroke-width="1" transform="rotate(-6 63 66)"/>
        <!-- pad face: narrow top, wide bottom -->
        <path d="M26 10 L72 10 L82 62 L16 62 Z" fill="url(#gasGrad)" stroke="#4ab87a" stroke-width="1.5"/>
        <!-- top glint -->
        <path d="M28 12 L70 12 L72 20 L26 20 Z" fill="rgba(255,255,255,.06)"/>
        <!-- horizontal rubber ribs -->
        <line x1="21" y1="23" x2="69" y2="23" stroke="rgba(0,0,0,.45)" stroke-width="4.5" stroke-linecap="round"/>
        <line x1="20" y1="35" x2="71" y2="35" stroke="rgba(0,0,0,.45)" stroke-width="4.5" stroke-linecap="round"/>
        <line x1="18" y1="47" x2="74" y2="47" stroke="rgba(0,0,0,.45)" stroke-width="4.5" stroke-linecap="round"/>
        <line x1="17" y1="59" x2="77" y2="59" stroke="rgba(0,0,0,.45)" stroke-width="4.5" stroke-linecap="round"/>
        <text x="47" y="40" text-anchor="middle" font-family="DM Mono,monospace" font-size="10" fill="rgba(74,184,122,.9)" font-weight="600">GAS</text>
        <text x="47" y="52" text-anchor="middle" font-family="DM Mono,monospace" font-size="9" fill="rgba(74,184,122,.5)">▶▶</text>
      </svg>
      <div class="pLbl">Gas / Tilt Back</div>
    </div>
  </div>
  <!-- LOAD SCREEN -->
  <div class="ov" id="loadScr">
    <div class="ovT">Building Terrain</div>
    <canvas id="ldCanvas" width="280" height="70" style="border:1px solid rgba(255,255,255,.06);border-radius:4px;"></canvas>
    <div id="ldStock" style="font-family:'DM Mono',monospace;font-size:11px;color:#c9a96e;">Initialising...</div>
    <div class="ldBar"><div class="ldFill"></div></div>
    <div class="dots"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>
    <div style="font-family:'DM Mono',monospace;font-size:8px;color:#2a2a36;letter-spacing:.08em;text-transform:uppercase;">Converting NSE price history to road</div>
  </div>
  <!-- START SCREEN -->
  <div class="ov" id="startScr">
    <div style="font-size:38px;">🏁</div>
    <div class="ovT">MarketRace</div>
    <div style="font-family:'DM Mono',monospace;font-size:9px;color:#c9a96e;letter-spacing:.12em;text-transform:uppercase;">Play Mode · Real Hill Climb Physics</div>
    <div class="ovS">Drive through <span id="startStkName" style="color:#c9a96e;font-weight:600;"></span>'s 1Y terrain.<br>
      <span style="color:#4ab87a;">💰 Dividends = coins</span> &nbsp;·&nbsp; <span style="color:#c9a96e;">⛽ Buybacks = fuel</span><br>
      Backflip off hills. Land on wheels or crash!
    </div>
    <div style="background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:3px;padding:8px 14px;font-family:'DM Mono',monospace;font-size:8px;color:#3a3a4a;line-height:1.8;text-align:center;">
      ▶▶ GAS = accelerate + tilt back (backflip)<br>◀◀ BRAKE = slow + tilt forward (frontflip)<br>Arrow keys / Space work too
    </div>
    <button class="ovBtn" onclick="startGame()">Start Driving →</button>
  </div>
  <!-- GAME OVER -->
  <div class="ov" id="goScr">
    <div id="goTitle" class="ovT"></div>
    <div id="goReason" class="ovS"></div>
    <div class="goGrid" id="goStats"></div>
    <div style="display:flex;gap:10px;flex-wrap:wrap;justify-content:center;">
      <button class="ovBtn" onclick="restartGame()">↺ Try Again</button>
      <button class="ovBtn sec" onclick="nextStock()">Next Stock →</button>
    </div>
  </div>
  <!-- PAUSE -->
  <div class="ov" id="pauseScr">
    <div class="ovT">Paused</div>
    <button class="ovBtn" onclick="togglePause()">▶ Resume</button>
    <button class="ovBtn sec" onclick="restartGame()">↺ Restart</button>
  </div>
</div>
<script>
var ALL_STOCKS = ALLSTOCKS_PLACEHOLDER;
var si = 0;

var canvas = document.getElementById('gc');
var ctx = canvas.getContext('2d');
var W = 0, H = 0;
function resize() {
  W = canvas.clientWidth || window.innerWidth;
  H = canvas.clientHeight || window.innerHeight;
  canvas.width = W; canvas.height = H;
}
resize();
window.addEventListener('resize', function() { resize(); if (tPts.length) buildT(ALL_STOCKS[si].data); });

var keys = { gas: false, brake: false };
function pg() { keys.gas=true;  document.getElementById('gasBtn').classList.add('pressed'); }
function rg() { keys.gas=false; document.getElementById('gasBtn').classList.remove('pressed'); }
function pb() { keys.brake=true;  document.getElementById('brkBtn').classList.add('pressed'); }
function rb() { keys.brake=false; document.getElementById('brkBtn').classList.remove('pressed'); }
var gasEl=document.getElementById('gasBtn'), brkEl=document.getElementById('brkBtn');
gasEl.addEventListener('touchstart',function(e){e.preventDefault();pg();},{passive:false});
gasEl.addEventListener('touchend',function(e){e.preventDefault();rg();},{passive:false});
gasEl.addEventListener('touchcancel',function(){rg();});
gasEl.addEventListener('mousedown',pg);gasEl.addEventListener('mouseup',rg);gasEl.addEventListener('mouseleave',rg);
brkEl.addEventListener('touchstart',function(e){e.preventDefault();pb();},{passive:false});
brkEl.addEventListener('touchend',function(e){e.preventDefault();rb();},{passive:false});
brkEl.addEventListener('touchcancel',function(){rb();});
brkEl.addEventListener('mousedown',pb);brkEl.addEventListener('mouseup',rb);brkEl.addEventListener('mouseleave',rb);
document.addEventListener('keydown',function(e){
  if(e.key==='ArrowRight'||e.key===' '||e.key==='ArrowUp'){e.preventDefault();pg();}
  if(e.key==='ArrowLeft'||e.key==='ArrowDown'){e.preventDefault();pb();}
  if(e.key==='p'||e.key==='P'||e.key==='Escape')togglePause();
});
document.addEventListener('keyup',function(e){
  if(e.key==='ArrowRight'||e.key===' '||e.key==='ArrowUp')rg();
  if(e.key==='ArrowLeft'||e.key==='ArrowDown')rb();
});

var SEG=55, tPts=[], curData=null;
function buildT(data){
  curData=data;
  var n=data.n_days,mn=Infinity,mx=-Infinity;
  for(var i=0;i<data.closes.length;i++){if(data.closes[i]<mn)mn=data.closes[i];if(data.closes[i]>mx)mx=data.closes[i];}
  var rng=(mx-mn)||1,AMP=H*0.36,BASE=H*0.60;
  tPts=[];
  for(var j=0;j<6;j++)tPts.push({x:j*SEG,y:BASE});
  for(var i=0;i<n;i++){
    var norm=(data.closes[i]-mn)/rng,bY=BASE-norm*AMP;
    var ba=(data.roughness[i]||0)*(data.vol_norm[i]||0)*9;
    var bump=Math.sin(i*2.3+0.7)*ba*0.6+Math.cos(i*1.7)*ba*0.4;
    tPts.push({x:(i+6)*SEG,y:Math.max(H*.12,Math.min(H*.85,bY+bump)),dayIdx:i,ret:data.returns[i],date:data.dates[i]});
  }
  var lastY=tPts[tPts.length-1].y;
  for(var k=0;k<8;k++)tPts.push({x:(n+6+k)*SEG,y:lastY});
}
function tyAt(wx){
  if(!tPts.length)return H*0.6;
  if(wx<=tPts[0].x)return tPts[0].y;
  if(wx>=tPts[tPts.length-1].x)return tPts[tPts.length-1].y;
  var lo=0,hi=tPts.length-1;
  while(lo<hi-1){var m=(lo+hi)>>1;if(tPts[m].x<=wx)lo=m;else hi=m;}
  var d=tPts[hi].x-tPts[lo].x,t=d<.001?0:(wx-tPts[lo].x)/d;
  return tPts[lo].y+t*(tPts[hi].y-tPts[lo].y);
}
function tangAt(wx){var dx=SEG*.5;return Math.atan2(tyAt(wx+dx)-tyAt(wx),dx);}

var colls=[];
function buildColls(data){
  colls=[];
  (data.div_events||[]).forEach(function(d){var wx=(d.idx+6)*SEG;colls.push({type:'coin',wx:wx,wy:tyAt(wx)-34,col:false,val:Math.max(25,Math.round(d.amount*8))});});
  (data.buyback_events||[]).forEach(function(b){var wx=(b.idx+6)*SEG;colls.push({type:'fuel',wx:wx,wy:tyAt(wx)-42,col:false,val:28});});
  (data.big_moves||[]).forEach(function(m){if(m.ret>0.012){var wx=(m.idx+6)*SEG+15;colls.push({type:'coin',wx:wx,wy:tyAt(wx)-28,col:false,val:Math.round(m.ret*600)});}});
  for(var i=7;i<(data.n_days||0);i+=7){var wx=(i+6)*SEG;colls.push({type:'coin',wx:wx,wy:tyAt(wx)-25,col:false,val:20});}
}

var G=900,CW=48,CH=16,WR=14,SL=20,SK=750,SD=55,DRIV=700,BRAK=480;
var car={x:0,y:0,vx:0,vy:0,angle:0,angVel:0,onGround:false};
var fw={c:false,comp:0,nf:0},bw={c:false,comp:0,nf:0};
var fuel=100,score=0,coins=0,flips=0,elapsed=0,dist=0,wspin=0,camX=0;
var pAng=0,totRot=0,airT=0,flipDone=false;
var parts=[],pops=[];
var gState='loading',paused=false,cinited=false;

function hexA(hex,a){
  var r=parseInt(hex.slice(1,3),16),g=parseInt(hex.slice(3,5),16),b=parseInt(hex.slice(5,7),16);
  return 'rgba('+r+','+g+','+b+','+a+')';
}

// ── FIX: initCar only called after buildT has populated tPts ──
function initCar(){
  if(!tPts.length)return;
  var sx=4*SEG,sy=tyAt(sx)-CH-WR-SL-4;
  car={x:sx,y:sy,vx:0,vy:0,angle:0,angVel:0,onGround:false};
  fw={c:false,comp:0,nf:0};bw={c:false,comp:0,nf:0};
  pAng=0;totRot=0;airT=0;flipDone=false;wspin=0;camX=0;
  cinited=true;
}

function stepPhys(dt){
  if(!cinited||isNaN(car.x))return;
  if(dt>0.05)dt=0.05;
  var cos=Math.cos(car.angle),sin=Math.sin(car.angle);
  var fwx=car.x+cos*CW-sin*CH,fwy=car.y+sin*CW+cos*CH;
  var bwx=car.x-cos*CW-sin*CH,bwy=car.y-sin*CW+cos*CH;
  var fX=0,fY=0,tq=0;
  function wF(wx,wy,ws,isDrv){
    var gY=tyAt(wx),pen=gY-(wy+WR);
    if(pen>-1){
      ws.c=true;var rv=(pen-ws.comp)/dt;ws.comp=Math.max(0,pen);
      ws.nf=Math.max(0,SK*Math.max(0,pen)+SD*Math.max(0,rv));
      fY-=ws.nf;tq+=(wx-car.x)*(-ws.nf);
      var ta=tangAt(wx);
      if(isDrv&&keys.gas){fX+=DRIV*Math.cos(ta)*dt;wspin+=DRIV*dt*.04;}
      if(keys.brake){fX-=car.vx*BRAK*.7*dt;tq-=car.angVel*1.3*6;}
      fX-=car.vx*.2;
    }else{ws.c=false;ws.comp*=.7;ws.nf=0;}
  }
  wF(fwx,fwy,fw,false);wF(bwx,bwy,bw,true);
  car.onGround=fw.c||bw.c;fY+=G;
  if(!car.onGround){
    if(keys.gas)car.angVel-=4.0*dt;if(keys.brake)car.angVel+=4.0*dt;
    car.angVel*=.97;airT+=dt;wspin+=Math.abs(car.vx)*.02;
  }else{tq-=car.angVel*1.3*14;car.angVel*=.82;airT=0;wspin+=keys.gas?18:Math.abs(car.vx)*.04;}
  car.vx+=fX*dt;car.vy+=fY*dt;car.vx*=car.onGround?.992:.998;car.vy*=.998;
  car.angVel+=(tq/1.3)*dt;car.angle+=car.angVel*dt;car.x+=car.vx*dt;car.y+=car.vy*dt;
  var fl=tyAt(car.x);
  if(car.y+CH+WR+SL>fl+2){car.y=fl-CH-WR-SL;if(car.vy>20)car.vy*=-.15;else car.vy=0;}
  if(car.x<SEG*2){car.x=SEG*2;if(car.vx<0)car.vx=0;}
  fuel-=(keys.gas?3.0:.6)*dt;fuel=Math.max(0,fuel);
  elapsed+=dt;dist=Math.max(dist,car.x);
  var dA=car.angle-pAng;
  totRot+=dA-Math.round(dA/(Math.PI*2))*Math.PI*2;pAng=car.angle;
  if(!car.onGround&&Math.abs(totRot)>=Math.PI*2&&!flipDone){
    var isB=totRot<0;flips++;var lbl=isB?'🔄 BACKFLIP! +500':'⤴ FRONTFLIP! +500';
    score+=500;showBanner(lbl);addPop(car.x,car.y-55,lbl,'#c9a96e');flipDone=true;totRot=0;
  }
  if(car.onGround){flipDone=false;totRot=0;}
  if(keys.gas&&Math.floor(elapsed*60)%3===0)
    parts.push({x:car.x-cos*CW,y:car.y-sin*CW,vx:-car.vx*.2-20-Math.random()*15,vy:-12+Math.random()*24,life:.3+Math.random()*.2,ml:.5,r:3,fire:true});
  if(car.onGround&&Math.abs(car.vx)>80&&Math.floor(elapsed*60)%5===0)
    parts.push({x:car.x-cos*CW,y:fl,vx:-Math.abs(car.vx)*.2,vy:-25-Math.random()*20,life:.25,ml:.25,r:4,dust:true});
  var tgt=car.x-W*.33;camX+=(tgt-camX)*.1;camX=Math.max(0,camX);
  colls.forEach(function(c){
    if(c.col)return;var dx=car.x-c.wx,dy=car.y-c.wy;
    if(dx*dx+dy*dy<900){c.col=true;if(c.type==='fuel'){fuel=Math.min(100,fuel+28);addPop(c.wx,c.wy-20,'⛽ BUYBACK! +Fuel','#c9a96e');}else{coins+=c.val;addPop(c.wx,c.wy-18,'+'+c.val+' 💰','#4ab87a');}}
  });
  score=Math.max(0,Math.round(dist*0.08+coins*2));
}

function crashed(){
  if(!cinited||isNaN(car.x))return false;
  var cos=Math.cos(car.angle),sin=Math.sin(car.angle);
  var tops=[{x:car.x+cos*CW-sin*(-CH),y:car.y+sin*CW+cos*(-CH)},{x:car.x-cos*CW-sin*(-CH),y:car.y-sin*CW+cos*(-CH)}];
  for(var i=0;i<tops.length;i++){if(tops[i].y>=tyAt(tops[i].x)-2)return true;}
  return false;
}

function skyAt(t){
  var phase=(t%90)/90;
  function lp(a,b,f){return[Math.round(a[0]+(b[0]-a[0])*f),Math.round(a[1]+(b[1]-a[1])*f),Math.round(a[2]+(b[2]-a[2])*f)];}
  var kf=[{p:0.00,sky:[8,6,18],hor:[60,30,50]},{p:0.20,sky:[20,50,100],hor:[100,120,140]},
    {p:0.50,sky:[8,18,40],hor:[50,40,30]},{p:0.65,sky:[25,10,8],hor:[80,40,15]},
    {p:0.78,sky:[2,2,10],hor:[5,5,18]},{p:1.00,sky:[8,6,18],hor:[60,30,50]}];
  var lo=kf[kf.length-1],hi=kf[0];
  for(var i=0;i<kf.length-1;i++){if(phase>=kf[i].p&&phase<kf[i+1].p){lo=kf[i];hi=kf[i+1];break;}}
  var span=hi.p-lo.p,f=span<.001?0:(phase-lo.p)/span;
  return{sky:lp(lo.sky,hi.sky,f),hor:lp(lo.hor,hi.hor,f),phase:phase};
}

function drawBG(){
  var sc=skyAt(elapsed),sky=sc.sky,hor=sc.hor,ph=sc.phase;
  var grad=ctx.createLinearGradient(0,0,0,H*.72);
  grad.addColorStop(0,'rgb('+sky[0]+','+sky[1]+','+sky[2]+')');
  grad.addColorStop(1,'rgb('+hor[0]+','+hor[1]+','+hor[2]+')');
  ctx.fillStyle=grad;ctx.fillRect(0,0,W,H);
  var sa=ph<0.3?(1-ph/0.3)*.8:ph>0.65?((ph-.65)/.35)*.9:0;
  if(sa>.02){
    for(var i=0;i<30;i++){var sx=((i*137.5)%W+W*3)%W,sy=((i*73)%(H*.5));
    var tw=.5+Math.sin(elapsed*1.5+i)*.5;ctx.globalAlpha=sa*tw;ctx.fillStyle='#fff';
    ctx.beginPath();ctx.arc(sx,sy,.9,0,Math.PI*2);ctx.fill();}ctx.globalAlpha=1;
  }
  var bp=ph*Math.PI*2,sunX=W*.5+Math.cos(bp-Math.PI*.5)*W*.42,sunY=H*.4+Math.sin(bp-Math.PI*.5)*H*.55;
  if(sunY>-30&&sunY<H*.65){
    if(ph<0.5){var sg=ctx.createRadialGradient(sunX,sunY,2,sunX,sunY,22);sg.addColorStop(0,'rgba(255,245,200,.9)');sg.addColorStop(1,'rgba(255,180,40,0)');ctx.fillStyle=sg;ctx.beginPath();ctx.arc(sunX,sunY,22,0,Math.PI*2);ctx.fill();ctx.fillStyle='rgba(255,255,220,.95)';ctx.beginPath();ctx.arc(sunX,sunY,9,0,Math.PI*2);ctx.fill();}
    else{var ma=Math.sin((ph-.5)*Math.PI*2)*.85;if(ma>0){ctx.fillStyle='rgba(220,225,255,'+ma*.9+')';ctx.beginPath();ctx.arc(sunX,sunY,9,0,Math.PI*2);ctx.fill();ctx.fillStyle='rgba(8,8,20,'+ma*.7+')';ctx.beginPath();ctx.arc(sunX+3,sunY-1,7,0,Math.PI*2);ctx.fill();ctx.fillStyle='rgba(220,225,255,'+ma*.9+')';ctx.beginPath();ctx.arc(sunX,sunY,9,0,Math.PI*2);ctx.fill();}}
  }
  ctx.fillStyle='rgba(18,28,46,.3)';
  for(var i=0;i<10;i++){var mx=((i*210-camX*.1)%(W+240))-80,mh=50+(i*37)%55;ctx.beginPath();ctx.moveTo(mx,H*.58);ctx.lineTo(mx+85,H*.58-mh);ctx.lineTo(mx+170,H*.58);ctx.fill();}
  var vis=[];for(var i=0;i<tPts.length;i++){if(tPts[i].x>=camX-SEG&&tPts[i].x<=camX+W+SEG)vis.push(tPts[i]);}
  if(vis.length>1){
    ctx.beginPath();ctx.moveTo(vis[0].x-camX,H);for(var i=0;i<vis.length;i++)ctx.lineTo(vis[i].x-camX,vis[i].y);
    ctx.lineTo(vis[vis.length-1].x-camX,H);ctx.closePath();
    var gg=ctx.createLinearGradient(0,H*.5,0,H);gg.addColorStop(0,'#1a2a1a');gg.addColorStop(1,'#0a0f0a');ctx.fillStyle=gg;ctx.fill();
  }
}

function drawTerrain(){
  var vis=[];for(var i=0;i<tPts.length;i++){if(tPts[i].x>=camX-SEG&&tPts[i].x<=camX+W+SEG)vis.push(tPts[i]);}
  if(vis.length<2)return;
  // ── FIX: single clean grass line, no fill artefacts ──
  ctx.beginPath();ctx.moveTo(vis[0].x-camX,vis[0].y);
  for(var i=1;i<vis.length-1;i++){var cpx=(vis[i].x+vis[i+1].x)/2-camX,cpy=(vis[i].y+vis[i+1].y)/2;ctx.quadraticCurveTo(vis[i].x-camX,vis[i].y,cpx,cpy);}
  ctx.lineTo(vis[vis.length-1].x-camX,vis[vis.length-1].y);
  ctx.strokeStyle='#3a5a3a';ctx.lineWidth=4;ctx.stroke();
  // softer secondary line for depth
  ctx.strokeStyle='#2a4a2a';ctx.lineWidth=2;ctx.stroke();
  // grass tufts
  ctx.fillStyle='#2a4a22';
  for(var i=0;i<vis.length;i++){if(i%5===0){ctx.beginPath();ctx.arc(vis[i].x-camX,vis[i].y-2,2,0,Math.PI*2);ctx.fill();}}
  // event annotations
  if(curData){
    for(var i=0;i<vis.length;i++){
      var p=vis[i];if(!p.dayIdx)continue;
      var m=null;for(var j=0;j<(curData.big_moves||[]).length;j++){if(curData.big_moves[j].idx===p.dayIdx){m=curData.big_moves[j];break;}}
      if(!m)continue;
      var sx=p.x-camX,up=m.ret>0;
      ctx.beginPath();ctx.moveTo(sx,p.y-6);ctx.lineTo(sx,p.y-36);
      ctx.strokeStyle=(up?'#4ab87a':'#e05c6c')+'75';ctx.lineWidth=1;ctx.setLineDash([2,4]);ctx.stroke();ctx.setLineDash([]);
      ctx.font='7px DM Mono,monospace';ctx.fillStyle=up?'#4ab87a':'#e05c6c';ctx.textAlign='center';
      ctx.fillText((up?'▲ +':'▼')+(m.ret*100).toFixed(1)+'%',sx,p.y-39);
      ctx.fillStyle='#2a2a3a';ctx.fillText(p.date,sx,p.y-29);
    }
  }
}

function drawColls(){
  for(var i=0;i<colls.length;i++){
    var c=colls[i];if(c.col)continue;
    var sx=c.wx-camX,sy=c.wy+Math.sin(elapsed*3+c.wx*.08)*4;
    if(sx<-50||sx>W+50)continue;
    if(c.type==='coin'){
      ctx.beginPath();ctx.arc(sx,sy,11,0,Math.PI*2);
      var cg=ctx.createRadialGradient(sx-3,sy-3,2,sx,sy,11);cg.addColorStop(0,'#ffe080');cg.addColorStop(1,'#c9a96e');
      ctx.fillStyle=cg;ctx.fill();ctx.strokeStyle='#a07838';ctx.lineWidth=1.5;ctx.stroke();
      ctx.font='bold 8px monospace';ctx.fillStyle='#6a4a18';ctx.textAlign='center';ctx.fillText('₹',sx,sy+3);
    }else{
      var fg=ctx.createLinearGradient(sx-10,sy,sx+10,sy);fg.addColorStop(0,'#286040');fg.addColorStop(1,'#4ab87a');
      ctx.fillStyle=fg;ctx.fillRect(sx-10,sy-14,20,18);ctx.strokeStyle='#1a5030';ctx.lineWidth=1.5;ctx.strokeRect(sx-10,sy-14,20,18);
      ctx.fillStyle='#1a5030';ctx.fillRect(sx+4,sy-18,6,5);
      ctx.font='bold 8px monospace';ctx.fillStyle='#d0ffe0';ctx.textAlign='center';ctx.fillText('⛽',sx,sy+5);
    }
  }
}

// ── FIX: drawCar now works because cinited is only true after buildT+initCar ──
function drawCar(){
  if(!cinited||typeof car.x!=='number'||isNaN(car.x)||isNaN(car.y))return;
  var s=ALL_STOCKS[si],col=s.color;
  var cos=Math.cos(car.angle),sin=Math.sin(car.angle);
  var gd=tyAt(car.x)-car.y;
  if(gd>0&&gd<140){ctx.save();ctx.translate(car.x-camX,tyAt(car.x));ctx.scale(1,.2);ctx.beginPath();ctx.ellipse(0,0,CW*.8,10,0,0,Math.PI*2);ctx.fillStyle='rgba(0,0,0,'+(0.35*(1-gd/140))+')';ctx.fill();ctx.restore();}
  ctx.save();ctx.translate(car.x-camX,car.y);ctx.rotate(car.angle);
  // suspension arms
  ctx.strokeStyle='rgba(200,200,200,.13)';ctx.lineWidth=2;
  ctx.beginPath();ctx.moveTo(-CW+10,CH);ctx.lineTo(-CW+10,CH+SL);ctx.stroke();
  ctx.beginPath();ctx.moveTo(CW-10,CH);ctx.lineTo(CW-10,CH+SL);ctx.stroke();
  // wheels
  var wpos=[[-CW+10,CH+SL],[CW-10,CH+SL]];
  for(var wi=0;wi<2;wi++){
    var wx=wpos[wi][0],wy=wpos[wi][1];
    ctx.beginPath();ctx.arc(wx,wy,WR,0,Math.PI*2);ctx.fillStyle='#1a1a22';ctx.fill();ctx.strokeStyle='#3a3a48';ctx.lineWidth=2;ctx.stroke();
    ctx.beginPath();ctx.arc(wx,wy,WR*.42,0,Math.PI*2);ctx.fillStyle='#555560';ctx.fill();
    var sa=wspin*.008+(wi===0?0:Math.PI*.25);ctx.strokeStyle='#707078';ctx.lineWidth=1.8;
    for(var sp=0;sp<4;sp++){var ang=sa+sp*Math.PI/2;ctx.beginPath();ctx.moveTo(wx,wy);ctx.lineTo(wx+Math.cos(ang)*WR*.38,wy+Math.sin(ang)*WR*.38);ctx.stroke();}
  }
  // body
  ctx.beginPath();ctx.moveTo(-CW,CH);ctx.lineTo(-CW,-CH+4);ctx.lineTo(-CW+8,-CH);ctx.lineTo(CW-6,-CH);ctx.lineTo(CW,-CH+4);ctx.lineTo(CW,CH);ctx.closePath();
  ctx.fillStyle=col;ctx.fill();ctx.strokeStyle=hexA(col,.5);ctx.lineWidth=1.5;ctx.stroke();
  // roof
  ctx.beginPath();ctx.moveTo(-CW*.5+2,-CH);ctx.lineTo(-CW*.48,-CH-14);ctx.lineTo(CW*.42,-CH-14);ctx.lineTo(CW*.5,-CH);ctx.closePath();
  ctx.fillStyle=hexA(col,.82);ctx.fill();ctx.strokeStyle=hexA(col,.35);ctx.lineWidth=1;ctx.stroke();
  // windshield
  ctx.beginPath();ctx.moveTo(-CW*.44+1,-CH-1);ctx.lineTo(-CW*.42,-CH-12);ctx.lineTo(CW*.38,-CH-12);ctx.lineTo(CW*.44-1,-CH-1);ctx.closePath();
  var wg=ctx.createLinearGradient(0,-CH-12,0,-CH-1);wg.addColorStop(0,'rgba(180,225,255,.78)');wg.addColorStop(1,'rgba(140,190,240,.35)');ctx.fillStyle=wg;ctx.fill();
  // headlight
  ctx.beginPath();ctx.arc(CW-5,CH*.2,3.5,0,Math.PI*2);ctx.fillStyle='rgba(255,248,180,.9)';ctx.fill();
  // rear light
  ctx.beginPath();ctx.arc(-CW+4,-CH*.1,2.5,0,Math.PI*2);ctx.fillStyle=keys.brake?'rgba(255,80,80,.95)':'rgba(180,40,40,.6)';ctx.fill();
  // exhaust
  ctx.fillStyle='#22222a';ctx.fillRect(-CW-5,CH*.5,6,4);
  // emoji on roof
  ctx.font='bold 11px monospace';ctx.fillStyle='rgba(255,255,255,.88)';ctx.textAlign='center';ctx.fillText(s.emoji,-CW*.03,-CH-17);
  ctx.restore();
  // headlight beam
  if(car.vx>20){var bx=car.x-camX+cos*CW-sin*CH*.2,by=car.y+sin*CW+cos*CH*.2;var bg=ctx.createRadialGradient(bx,by,0,bx+cos*60,by+sin*60,70);bg.addColorStop(0,'rgba(255,245,180,.1)');bg.addColorStop(1,'rgba(255,245,180,0)');ctx.fillStyle=bg;ctx.beginPath();ctx.arc(bx+cos*35,by+sin*35,65,0,Math.PI*2);ctx.fill();}
}

function drawParts(dt){
  parts=parts.filter(function(p){return p.life>0;});
  parts.forEach(function(p){p.x+=p.vx*dt;p.y+=p.vy*dt;p.life-=dt;});
  parts.forEach(function(p){var a=p.life/p.ml,sx=p.x-camX;ctx.beginPath();ctx.arc(sx,p.y,p.r*Math.max(.1,a),0,Math.PI*2);ctx.fillStyle=p.fire?'rgba(255,'+(Math.round(80+a*120))+',20,'+a*.6+')':p.dust?'rgba(90,70,40,'+a*.5+')':'rgba(150,150,130,'+a*.4+')';ctx.fill();});
}

function drawPops(dt){
  pops=pops.filter(function(p){return p.life>0;});pops.forEach(function(p){p.wy-=28*dt;p.life-=dt;});
  ctx.save();pops.forEach(function(p){ctx.globalAlpha=Math.min(1,p.life);ctx.font='bold 11px DM Mono,monospace';ctx.fillStyle=p.color||'#4ab87a';ctx.textAlign='center';ctx.fillText(p.text,p.wx-camX,p.wy);});ctx.globalAlpha=1;ctx.restore();
}

function drawFlag(){
  if(!curData)return;var ex=(curData.n_days+6)*SEG,sx=ex-camX;
  if(sx<-60||sx>W+60)return;var gy=tyAt(ex);
  ctx.strokeStyle='#aaa';ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(sx,gy);ctx.lineTo(sx,gy-88);ctx.stroke();
  for(var r=0;r<4;r++)for(var c=0;c<4;c++){ctx.fillStyle=(r+c)%2===0?'#fff':'#222';ctx.fillRect(sx+c*11,gy-88+r*8,11,8);}
  ctx.font='bold 8px DM Mono';ctx.fillStyle='#c9a96e';ctx.textAlign='center';ctx.fillText('FINISH',sx+22,gy-96);
}

function updateHUD(){
  document.getElementById('scoreV').textContent=Math.floor(score).toLocaleString();
  document.getElementById('distV').textContent=Math.round(dist/SEG*2)+'m';
  var fp=Math.max(0,Math.min(100,fuel));
  document.getElementById('fuelFill').style.width=fp+'%';
  document.getElementById('fuelFill').style.background=fp<20?'#e05c6c':fp<40?'linear-gradient(90deg,#e17055,#fdcb6e)':'linear-gradient(90deg,#e05c6c,#fdcb6e,#4ab87a)';
  var mm=Math.floor(elapsed/60),ss=Math.floor(elapsed%60);
  document.getElementById('timeV').textContent=(mm<10?'0':'')+mm+':'+(ss<10?'0':'')+ss;
  document.getElementById('airInd').textContent=(!car.onGround&&airT>.1)?('🌀 '+Math.round(Math.abs(totRot)/(Math.PI*2)*360)+'°'):'';
}

function addPop(wx,wy,text,color){pops.push({wx:wx,wy:wy,text:text,color:color,life:1.4,ml:1.4});}
function showBanner(t){var el=document.getElementById('flipBanner');el.textContent=t;el.style.opacity='1';setTimeout(function(){el.style.opacity='0';},1300);}

function doGameOver(title,reason){
  if(gState==='gameover')return;gState='gameover';
  var m=Math.round(dist/SEG*2);
  document.getElementById('goTitle').textContent=title;
  document.getElementById('goReason').textContent=reason;
  document.getElementById('goStats').innerHTML='<div class="goCell"><div class="goCL">Score</div><div class="goCV">'+Math.floor(score).toLocaleString()+'</div></div><div class="goCell"><div class="goCL">Distance</div><div class="goCV">'+m+'m</div></div><div class="goCell"><div class="goCL">Coins</div><div class="goCV">'+coins+'</div></div><div class="goCell"><div class="goCL">Flips</div><div class="goCV">'+flips+'</div></div>';
  document.getElementById('goScr').style.display='flex';
}

var lastT=0,animId=null;
function gameLoop(ts){
  var dt=Math.min((ts-lastT)/1000,.05);lastT=ts;
  ctx.clearRect(0,0,W,H);
  drawBG();
  if(tPts.length>1){drawTerrain();drawColls();drawFlag();}
  drawParts(dt);
  drawCar();
  drawPops(dt);
  if(cinited)updateHUD();
  if(gState==='playing'&&!paused){
    stepPhys(dt);
    if(crashed()&&gState==='playing'){gState='dead';for(var i=0;i<15;i++)parts.push({x:car.x,y:car.y,vx:(Math.random()-.5)*300,vy:-80-Math.random()*200,life:.7,ml:.7,r:5,dust:true});setTimeout(function(){doGameOver('💥 Crashed!','Car flipped — land on your wheels!');},500);}
    if(fuel<=0&&gState==='playing'){gState='dead';setTimeout(function(){doGameOver('⛽ Out of Fuel!','Collect fuel cans (buybacks) to refuel.');},300);}
    if(curData&&car.x>=(curData.n_days+5)*SEG&&gState==='playing'){var ret=(curData.total_return*100).toFixed(1);score+=2000;addPop(car.x,car.y-70,'🏆 FINISHED! +2000','#c9a96e');gState='dead';var sn=ALL_STOCKS[si].name;setTimeout(function(){doGameOver('🏆 Race Complete!',sn+' returned '+(parseFloat(ret)>=0?'+':'')+ret+'% in 1Y!');},1200);}
  }
  animId=requestAnimationFrame(gameLoop);
}

function buildSel(){
  var h='';ALL_STOCKS.forEach(function(s,i){var ret=(s.data.total_return*100).toFixed(1),col=parseFloat(ret)>=0?'#4ab87a':'#e05c6c';h+='<div class="sItem'+(i===si?' active':'')+'" onclick="loadSt('+i+')">'+(s.emoji||'')+' '+s.name+'<span style="color:'+col+'">'+(parseFloat(ret)>=0?'+':'')+ret+'%</span></div>';});
  document.getElementById('stkPanel').innerHTML=h;
}
function toggleSel(){var p=document.getElementById('stkPanel');p.style.display=p.style.display==='block'?'none':'block';if(p.style.display==='block')buildSel();}

function loadSt(i){
  si=i;document.getElementById('stkPanel').style.display='none';
  var s=ALL_STOCKS[i];buildT(s.data);buildColls(s.data);
  document.getElementById('stkName').textContent=(s.emoji||'')+' '+s.name;
  var ret=(s.data.total_return*100).toFixed(1);document.getElementById('stkRet').textContent='1Y: '+(parseFloat(ret)>=0?'+':'')+ret+'%';
  var el=document.getElementById('startStkName');if(el)el.textContent=s.name;buildSel();
}

function startGame(){document.getElementById('startScr').style.display='none';resetRun();gState='playing';lastT=performance.now();}
function resetRun(){score=0;fuel=100;dist=0;coins=0;flips=0;elapsed=0;parts=[];pops=[];camX=0;cinited=false;initCar();buildColls(ALL_STOCKS[si].data);document.getElementById('goScr').style.display='none';}
function restartGame(){document.getElementById('goScr').style.display='none';resetRun();gState='playing';lastT=performance.now();}
function nextStock(){document.getElementById('goScr').style.display='none';si=(si+1)%ALL_STOCKS.length;loadSt(si);resetRun();gState='playing';lastT=performance.now();}
function togglePause(){if(gState!=='playing'&&gState!=='paused')return;paused=!paused;document.getElementById('pauseScr').style.display=paused?'flex':'none';document.getElementById('pauseBtn').textContent=paused?'▶ Resume':'⏸ Pause';if(!paused)lastT=performance.now();}

function startLoadAnim(){
  var lc=document.getElementById('ldCanvas');if(!lc)return null;
  var lx=lc.getContext('2d');var LW=280,LH=70,lt=0;
  return setInterval(function(){
    lx.fillStyle='#0a0a0f';lx.fillRect(0,0,LW,LH);
    lx.beginPath();for(var x=0;x<=LW;x+=2){var y=LH*.55+Math.sin((x*.035)+lt*.8)*14+Math.cos((x*.022)+lt*.5)*8;if(x===0)lx.moveTo(x,y);else lx.lineTo(x,y);}
    lx.strokeStyle='#c9a96e55';lx.lineWidth=2;lx.stroke();
    var cx=(lt*22)%LW,cy=LH*.55+Math.sin((cx*.035)+lt*.8)*14+Math.cos((cx*.022)+lt*.5)*8-10;
    lx.fillStyle='#c9a96e';lx.fillRect(cx-8,cy-5,16,8);lx.fillStyle='#c9a96eaa';lx.fillRect(cx-5,cy-9,10,5);
    lx.fillStyle='#1a1a22';lx.beginPath();lx.arc(cx-5,cy+3,4,0,Math.PI*2);lx.fill();lx.beginPath();lx.arc(cx+5,cy+3,4,0,Math.PI*2);lx.fill();
    lt+=.05;
  },33);
}

// ── BOOT: buildT first, then initCar, THEN show start screen ──
(function(){
  resize();lastT=performance.now();animId=requestAnimationFrame(gameLoop);
  var la=startLoadAnim(),ll=document.getElementById('ldStock'),idx=0;
  function loadNext(){
    if(idx>=ALL_STOCKS.length){
      clearInterval(la);
      // ── KEY FIX: buildT stock 0 first, THEN initCar so tPts is populated ──
      buildT(ALL_STOCKS[0].data);
      buildColls(ALL_STOCKS[0].data);
      si=0;
      initCar();   // tPts now has data, so sy = tyAt(sx) is valid, cinited=true
      // update HUD labels
      var s=ALL_STOCKS[0];
      document.getElementById('stkName').textContent=(s.emoji||'')+' '+s.name;
      var ret=(s.data.total_return*100).toFixed(1);
      document.getElementById('stkRet').textContent='1Y: '+(parseFloat(ret)>=0?'+':'')+ret+'%';
      var el=document.getElementById('startStkName');if(el)el.textContent=s.name;
      setTimeout(function(){document.getElementById('loadScr').style.display='none';document.getElementById('startScr').style.display='flex';gState='start';},350);
      return;
    }
    var s=ALL_STOCKS[idx];if(ll)ll.textContent='Loading '+(s.emoji||'')+' '+s.name+'...';
    setTimeout(function(){idx++;loadNext();},25);
  }
  setTimeout(loadNext,150);
})();
</script></body></html>"""

def build_play_mode_html(all_stocks_data):
    stock_json = json.dumps(make_serialisable(all_stocks_data))
    ticker_parts = []
    for s in all_stocks_data:
        ret = s["data"]["total_return"] * 100
        ticker_parts.append(s["emoji"] + " " + s["name"] + " " + ("+"+f"{ret:.1f}" if ret>=0 else f"{ret:.1f}") + "%  ·  ")
    ticker_text = ("  ".join(ticker_parts)) * 3
    html = PLAY_HTML_TEMPLATE
    html = html.replace("ALLSTOCKS_PLACEHOLDER", stock_json)
    html = html.replace("TICKER_PLACEHOLDER", ticker_text)
    return html

# ─────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────
for k,v in [('page','home'),('race_data',None),('last_cfg',None),
            ('race_speed','Normal'),('show_ann',True),('period_label','1 Year'),('play_data',None)]:
    if k not in st.session_state: st.session_state[k]=v

st.markdown(CSS, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# HOME PAGE
# ─────────────────────────────────────────────────────────────────
def render_home():
    st.markdown("""
    <div style="padding:3rem 0 1.5rem;">
      <div style="font-family:'DM Mono',monospace;font-size:.62rem;color:#444;letter-spacing:.18em;text-transform:uppercase;margin-bottom:1.2rem;">
        ● STOCK RACING GAME &nbsp;·&nbsp; REAL NSE DATA &nbsp;·&nbsp; TWO GAME MODES
      </div>
      <h1 style="font-family:'Playfair Display',serif;font-size:clamp(3.5rem,9vw,7rem);color:#e8e4dc;line-height:.9;margin:0 0 .6rem 0;font-weight:700;letter-spacing:-.02em;">
        Market<span style="color:#c9a96e;font-style:italic;">Race</span>
      </h1>
      <p style="font-family:'Playfair Display',serif;font-style:italic;font-size:1.15rem;color:#c9a96e;margin:0 0 1.2rem 0;">
        The market as you've never seen it.
      </p>
      <p style="color:#555;font-size:.88rem;max-width:520px;line-height:1.75;margin-bottom:.8rem;">
        Every stock's price chart is a road. 1 year of real NSE data becomes the terrain — uphill on good days, crash valleys on bad ones.
      </p>
      <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:2.5rem;">
        <span style="background:#111118;border:1px solid rgba(255,255,255,.07);border-radius:2px;padding:3px 10px;font-family:'DM Mono',monospace;font-size:.66rem;color:#666;">Real yfinance data</span>
        <span style="background:#111118;border:1px solid rgba(255,255,255,.07);border-radius:2px;padding:3px 10px;font-family:'DM Mono',monospace;font-size:.66rem;color:#666;">Hill climb physics</span>
        <span style="background:#111118;border:1px solid rgba(255,255,255,.07);border-radius:2px;padding:3px 10px;font-family:'DM Mono',monospace;font-size:.66rem;color:#666;">17 NSE stocks</span>
        <span style="background:#111118;border:1px solid rgba(255,255,255,.07);border-radius:2px;padding:3px 10px;font-family:'DM Mono',monospace;font-size:.66rem;color:#666;">Backflips</span>
        <span style="background:#111118;border:1px solid rgba(255,255,255,.07);border-radius:2px;padding:3px 10px;font-family:'DM Mono',monospace;font-size:.66rem;color:#666;">Day / Night sky</span>
        <span style="background:#111118;border:1px solid rgba(255,255,255,.07);border-radius:2px;padding:3px 10px;font-family:'DM Mono',monospace;font-size:.66rem;color:#666;">💰 Dividend coins</span>
      </div>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown("""
        <div style="background:#0e0e14;border:1px solid rgba(255,255,255,.07);border-radius:6px;padding:22px 24px 18px;">
          <div style="font-size:32px;margin-bottom:10px;">🤖</div>
          <div style="font-family:'Syne',sans-serif;font-size:1.05rem;font-weight:700;color:#e8e4dc;margin-bottom:8px;">Computer Race</div>
          <div style="font-family:'DM Mono',monospace;font-size:.72rem;color:#555;line-height:1.75;margin-bottom:14px;">
            Pick 2–5 NSE stocks and watch AI cars race automatically on each stock's 1-year price terrain. Staggered grid start, live leaderboard, podium finish.
          </div>
          <div style="display:flex;flex-wrap:wrap;gap:5px;">
            <span style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.07);border-radius:2px;padding:2px 8px;font-family:'DM Mono',monospace;font-size:.64rem;color:#555;">AI drivers</span>
            <span style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.07);border-radius:2px;padding:2px 8px;font-family:'DM Mono',monospace;font-size:.64rem;color:#555;">Staggered start</span>
            <span style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.07);border-radius:2px;padding:2px 8px;font-family:'DM Mono',monospace;font-size:.64rem;color:#555;">Podium results</span>
            <span style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.07);border-radius:2px;padding:2px 8px;font-family:'DM Mono',monospace;font-size:.64rem;color:#555;">Event annotations</span>
          </div>
        </div>""", unsafe_allow_html=True)
        if st.button("→ Watch Race", type="primary", use_container_width=True, key="btn_computer"):
            st.session_state.page = 'computer'; st.rerun()

    with col2:
        st.markdown("""
        <div style="background:#0e0e14;border:1px solid rgba(201,169,110,.2);border-radius:6px;padding:22px 24px 18px;">
          <div style="font-size:32px;margin-bottom:10px;">🎮</div>
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
            <span style="font-family:'Syne',sans-serif;font-size:1.05rem;font-weight:700;color:#c9a96e;">Play Mode</span>
            <span style="background:rgba(201,169,110,.15);border:1px solid rgba(201,169,110,.3);border-radius:2px;padding:1px 7px;font-family:'DM Mono',monospace;font-size:.6rem;color:#c9a96e;letter-spacing:.08em;">NEW</span>
          </div>
          <div style="font-family:'DM Mono',monospace;font-size:.72rem;color:#555;line-height:1.75;margin-bottom:14px;">
            You drive. Real suspension physics — spring + damper. Collect dividend coins, grab buyback fuel cans, pull backflips off big hills. Day/night sky cycles as you drive. Don't crash.
          </div>
          <div style="display:flex;flex-wrap:wrap;gap:5px;">
            <span style="background:rgba(201,169,110,.08);border:1px solid rgba(201,169,110,.2);border-radius:2px;padding:2px 8px;font-family:'DM Mono',monospace;font-size:.64rem;color:#c9a96e;">Spring physics</span>
            <span style="background:rgba(201,169,110,.08);border:1px solid rgba(201,169,110,.2);border-radius:2px;padding:2px 8px;font-family:'DM Mono',monospace;font-size:.64rem;color:#c9a96e;">Day / Night</span>
            <span style="background:rgba(201,169,110,.08);border:1px solid rgba(201,169,110,.2);border-radius:2px;padding:2px 8px;font-family:'DM Mono',monospace;font-size:.64rem;color:#c9a96e;">Backflip +500</span>
            <span style="background:rgba(201,169,110,.08);border:1px solid rgba(201,169,110,.2);border-radius:2px;padding:2px 8px;font-family:'DM Mono',monospace;font-size:.64rem;color:#c9a96e;">Mobile ready</span>
          </div>
        </div>""", unsafe_allow_html=True)
        if st.button("→ Play Now", type="primary", use_container_width=True, key="btn_play"):
            st.session_state.page = 'play'; st.rerun()

    preview = """<div style="background:#0e0e14;border:1px solid rgba(255,255,255,.06);border-radius:6px;overflow:hidden;margin-top:2.5rem;height:112px;">
<canvas id="pvC" style="width:100%;height:112px;display:block;"></canvas></div>
<script>(function(){
  var c=document.getElementById('pvC');if(!c)return;
  var cx=c.getContext('2d');var W=c.offsetWidth,H=112;c.width=W;c.height=H;
  var stocks=[{col:'#4a9eff',f:.022,a:20,ph:0},{col:'#c9a96e',f:.016,a:16,ph:1.2},{col:'#00b894',f:.029,a:14,ph:2.4},{col:'#e05c6c',f:.019,a:18,ph:.7}];
  var cars=[{x:W*.12,spd:1.1},{x:W*.33,spd:1.3},{x:W*.56,spd:.9},{x:W*.77,spd:1.2}];
  var t=0;
  function draw(){
    cx.fillStyle='#0e0e14';cx.fillRect(0,0,W,H);
    stocks.forEach(function(st,i){
      var pts=[];for(var x=0;x<=W;x+=3){var y=H*.55+Math.sin((x*st.f)+t*.6+st.ph*35)*st.a+Math.cos((x*st.f*1.6)+t*.4)*st.a*.4;pts.push({x:x,y:y});}
      cx.beginPath();pts.forEach(function(p,j){if(j===0)cx.moveTo(p.x,p.y);else cx.lineTo(p.x,p.y);});cx.strokeStyle=st.col+'55';cx.lineWidth=1.5;cx.stroke();
      var car=cars[i];car.x=(car.x+car.spd)%(W+40);
      var li=Math.max(0,Math.min(pts.length-2,Math.floor(car.x/3)));var cy=pts[li]?pts[li].y:H*.55;
      cx.save();cx.translate(car.x,cy-8);
      cx.fillStyle=st.col;cx.fillRect(-12,-5,24,9);cx.fillStyle=st.col+'bb';cx.fillRect(-7,-11,14,7);
      cx.fillStyle='#1a1a22';cx.beginPath();cx.arc(-7,4,4,0,Math.PI*2);cx.fill();cx.beginPath();cx.arc(7,4,4,0,Math.PI*2);cx.fill();
      cx.restore();
    });
    t+=.4;requestAnimationFrame(draw);
  }draw();
})();</script>"""
    components.html(preview, height=122, scrolling=False)
    st.markdown("""<div style="margin-top:.6rem;font-family:'DM Mono',monospace;font-size:.62rem;color:#2a2a3a;text-align:center;letter-spacing:.05em;">
      MarketRace · Day 27 · 30 Days of AI Finance · Preetham · Price data via yfinance · Not investment advice
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# COMPUTER RACE PAGE
# ─────────────────────────────────────────────────────────────────
def render_computer():
    if st.button("← Home", type="secondary", key="back_c"): st.session_state.page='home'; st.rerun()
    st.markdown("<div style='font-family:\"DM Mono\",monospace;font-size:.62rem;color:#444;letter-spacing:.15em;text-transform:uppercase;margin:.5rem 0 1.5rem;'>● COMPUTER RACE MODE · 1Y NSE TERRAIN</div>", unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### Select Racers")
        selected = st.multiselect("Pick 2–5 stocks to race", list(STOCKS.keys()),
            default=["TCS","HDFC Bank","Reliance","ITC"], max_selections=5, label_visibility="collapsed")
    with col2:
        st.markdown("### Settings")
        period_label = st.selectbox("Period", list(PERIODS.keys()), index=3, label_visibility="collapsed")
        race_speed = st.select_slider("Speed", ["Slow","Normal","Fast","Turbo"], value="Normal")
        show_ann = st.checkbox("Show market event markers", value=True)
    st.session_state.race_speed=race_speed; st.session_state.show_ann=show_ann; st.session_state.period_label=period_label
    if len(selected) < 1: st.warning("Select at least 1 stock to race."); return
    load_btn = st.button("🚀 Load & Race", type="primary", use_container_width=True)
    cfg = (tuple(sorted(selected)), period_label)
    if load_btn or (st.session_state.race_data is not None and st.session_state.last_cfg == cfg):
        if load_btn or st.session_state.race_data is None:
            with st.spinner("Fetching 1Y data from NSE..."):
                rd = prepare_race_data(selected, PERIODS[period_label])
                st.session_state.race_data = rd; st.session_state.last_cfg = cfg
        rd = st.session_state.race_data
        if not rd["racers"]: st.error("Could not fetch data for any selected stock."); return
        if rd["failed"]: st.warning("Could not fetch: " + ", ".join(rd["failed"]))
        st.markdown("---")
        st.markdown("<div style='font-family:\"DM Mono\",monospace;font-size:.62rem;color:#444;letter-spacing:.12em;text-transform:uppercase;margin-bottom:.8rem;'>● PRE-RACE STATS</div>", unsafe_allow_html=True)
        cols = st.columns(len(rd["racers"]))
        for i, r in enumerate(rd["racers"]):
            d = r["data"]; ret = d["total_return"]*100
            best = max(d["big_moves"], key=lambda m: m["ret"])
            worst = min(d["big_moves"], key=lambda m: m["ret"])
            with cols[i]:
                st.markdown(f"""<div style="background:#0e0e14;border:1px solid rgba(255,255,255,.06);border-radius:4px;padding:12px;">
                  <div style="font-size:20px;margin-bottom:6px;">{r['emoji']}</div>
                  <div style="font-family:'DM Mono',monospace;font-size:.7rem;color:#777;">{r['name']}</div>
                  <div style="font-family:'Playfair Display',serif;font-size:1.4rem;color:{'#4ab87a' if ret>=0 else '#e05c6c'};font-style:italic;">{'+' if ret>=0 else ''}{ret:.1f}%</div>
                  <div style="font-family:'DM Mono',monospace;font-size:.62rem;color:#3a3a4a;margin-top:7px;line-height:1.7;">
                    Vol: {d['ann_vol']:.1f}% ann.<br>
                    <span style="color:#4ab87a80">▲ +{best['ret']*100:.1f}%</span> {best['date']}<br>
                    <span style="color:#e05c6c80">▼ {worst['ret']*100:.1f}%</span> {worst['date']}
                  </div></div>""", unsafe_allow_html=True)
        st.markdown("---")
        components.html(build_computer_race_html(rd, race_speed, show_ann, period_label), height=680, scrolling=False)
        st.markdown("<div style='margin-top:1rem;font-family:\"DM Mono\",monospace;font-size:.62rem;color:#2a2a3a;text-align:center;border-top:1px solid rgba(255,255,255,.04);padding-top:1rem;'>MarketRace · Day 27 · 30 Days of AI Finance · Data via yfinance · Not investment advice</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# PLAY MODE PAGE
# ─────────────────────────────────────────────────────────────────
def render_play():
    if st.button("← Home", type="secondary", key="back_p"): st.session_state.page='home'; st.rerun()
    if st.session_state.play_data is None:
        with st.spinner("Fetching all stock data (cached after first load)..."):
            play_stocks = []
            for name, cfg in STOCKS.items():
                data = fetch_stock_data(cfg["ticker"], "1y")
                if data is not None:
                    play_stocks.append({"name":name,"ticker":cfg["ticker"],"sector":cfg["sector"],
                                        "color":cfg["color"],"emoji":cfg["emoji"],"data":data})
            play_stocks.sort(key=lambda s: s["data"]["total_return"], reverse=True)
            st.session_state.play_data = play_stocks
    if not st.session_state.play_data: st.error("Could not load any stock data. Check your network."); return
    components.html(build_play_mode_html(st.session_state.play_data), height=700, scrolling=False)
    st.markdown("<div style='margin-top:.4rem;font-family:\"DM Mono\",monospace;font-size:.62rem;color:#2a2a3a;text-align:center;'>▶▶ GAS &nbsp;·&nbsp; ◀◀ BRAKE &nbsp;·&nbsp; Air tilt for backflips &nbsp;·&nbsp; Not investment advice</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────────────────────────────
if   st.session_state.page == 'home':     render_home()
elif st.session_state.page == 'computer': render_computer()
elif st.session_state.page == 'play':     render_play()
