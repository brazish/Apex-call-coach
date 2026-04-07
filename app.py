"""
APEX CALL COACH
Run: streamlit run app.py
"""

import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Apex Call Coach", page_icon="🎯", layout="wide")

st.markdown("""
<style>
html,body,[data-testid="stAppViewContainer"]{background:#080C10!important;color:#C8D8E4!important;}
[data-testid="stSidebar"]{background:#0E1318!important;border-right:1px solid #1E2D3D!important;}
#MainMenu,footer,header,[data-testid="stToolbar"]{display:none!important;}
div[data-testid="stTextInput"] input,div[data-testid="stTextArea"] textarea{background:#090D11!important;border:1px solid #1E2D3D!important;color:#C8D8E4!important;}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    with st.expander("🔑 API Keys", expanded=True):
        dg_key     = st.text_input("Deepgram API Key",  value=os.getenv("DEEPGRAM_API_KEY",""),  type="password")
        claude_key = st.text_input("Anthropic API Key", value=os.getenv("ANTHROPIC_API_KEY",""), type="password")
    st.markdown("---")
    st.markdown("**📞 Call Context**")
    product_ctx = st.text_area("Product / Service", placeholder="e.g. SaaS CRM at $500/mo", height=70)
    persona_ctx = st.text_area("Prospect Persona",  placeholder="e.g. VP Sales, 200-person company", height=70)
    st.markdown("---")
    language       = st.selectbox("Language", ["en-US","en-GB","es","fr","de","pt"])
    coach_interval = st.slider("Coach every N words", 10, 60, 20, 5)

# ── Escape values for safe JS embedding ───────────────────────────────────────
def js_str(s):
    return s.replace('\\','\\\\').replace('`','\\`').replace('$','\\$').replace('\n','\\n')

dg_safe      = js_str(dg_key)
claude_safe  = js_str(claude_key)
product_safe = js_str(product_ctx)
persona_safe = js_str(persona_ctx)

# ── Full browser app ───────────────────────────────────────────────────────────
st.components.v1.html(f"""
<!DOCTYPE html>
<html>
<head>
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&display=swap');
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ background:#080C10; color:#C8D8E4; font-family:'DM Mono',monospace; padding:20px; }}
  .header {{ display:flex; align-items:center; gap:16px; padding-bottom:16px; border-bottom:1px solid #1E2D3D; margin-bottom:20px; }}
  .logo {{ width:48px; height:48px; background:linear-gradient(135deg,#00E5FF,#0080FF); border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:24px; flex-shrink:0; }}
  .title {{ font-family:'Syne',sans-serif; font-size:22px; font-weight:800; color:#EFF6FB; }}
  .subtitle {{ font-size:11px; color:#00E5FF; letter-spacing:2px; text-transform:uppercase; }}
  .metrics {{ display:grid; grid-template-columns:repeat(5,1fr); gap:12px; margin-bottom:20px; }}
  .metric {{ background:#131A22; border:1px solid #1E2D3D; border-radius:10px; padding:14px; text-align:center; }}
  .metric-val {{ font-family:'Syne',sans-serif; font-size:24px; font-weight:800; color:#EFF6FB; }}
  .metric-lbl {{ font-size:10px; color:#4A6070; letter-spacing:1.5px; text-transform:uppercase; margin-top:2px; }}
  .buttons {{ display:flex; gap:12px; margin-bottom:12px; }}
  .btn {{ flex:1; padding:10px; border:none; border-radius:8px; font-weight:700; font-size:14px; cursor:pointer; font-family:'DM Mono',monospace; transition:opacity 0.2s; }}
  .btn-start {{ background:linear-gradient(135deg,#00B8CC,#0080FF); color:#000; }}
  .btn-stop  {{ background:#131A22; color:#FF3B5C; border:1px solid rgba(255,59,92,0.4); }}
  .btn-clear {{ background:#131A22; color:#4A6070; border:1px solid #1E2D3D; }}
  .btn:disabled {{ opacity:0.35; cursor:not-allowed; }}
  .status-bar {{ font-size:13px; color:#00E5FF; padding:6px 0; min-height:24px; }}
  .interim-bar {{ font-size:13px; color:#4A6070; font-style:italic; min-height:20px; padding:4px 0; }}
  .error-box {{ background:rgba(255,59,92,0.1); border:1px solid rgba(255,59,92,0.3); border-radius:8px; padding:10px 14px; color:#FF3B5C; font-size:13px; margin:8px 0; display:none; }}
  .columns {{ display:grid; grid-template-columns:5fr 4fr; gap:24px; margin-top:20px; }}
  .section-title {{ font-family:'Syne',sans-serif; font-size:16px; font-weight:700; color:#EFF6FB; margin-bottom:12px; }}
  .tx-box {{ background:#090D11; border:1px solid #1E2D3D; border-radius:8px; padding:16px; min-height:280px; max-height:400px; overflow-y:auto; font-size:13px; line-height:1.8; }}
  .tx-line {{ margin:4px 0; }}
  .tx-speaker {{ color:#00E5FF; font-weight:500; }}
  .tx-empty {{ color:#4A6070; font-style:italic; }}
  .coach-card {{ border-radius:10px; padding:14px; margin-bottom:10px; border-left:3px solid #00E5FF; background:#131A22; font-size:14px; line-height:1.6; }}
  .coach-card.objection {{ border-left-color:#FF3B5C; }}
  .coach-card.tip        {{ border-left-color:#FFD60A; }}
  .coach-card.positive   {{ border-left-color:#00FF9D; }}
  .coach-tag {{ font-size:10px; font-weight:600; letter-spacing:1.5px; text-transform:uppercase; padding:2px 8px; border-radius:4px; margin-bottom:6px; display:inline-block; }}
  .tag-objection {{ background:rgba(255,59,92,0.15);  color:#FF3B5C; }}
  .tag-tip       {{ background:rgba(255,214,10,0.15); color:#FFD60A; }}
  .tag-positive  {{ background:rgba(0,255,157,0.15);  color:#00FF9D; }}
  .tag-coach     {{ background:rgba(0,229,255,0.10);  color:#00E5FF; }}
  .coach-ts  {{ font-size:10px; color:#4A6070; float:right; }}
  .coach-empty {{ text-align:center; padding:30px 0; color:#4A6070; font-size:13px; }}
  .pill-live {{ display:inline-flex;align-items:center;gap:6px;padding:5px 12px;border-radius:100px;background:rgba(0,255,157,0.12);color:#00FF9D;border:1px solid rgba(0,255,157,0.3);font-size:12px; }}
  .pill-idle {{ display:inline-flex;align-items:center;gap:6px;padding:5px 12px;border-radius:100px;background:rgba(74,96,112,0.2);color:#4A6070;border:1px solid #1E2D3D;font-size:12px; }}
  .dot {{ width:8px;height:8px;border-radius:50%;display:inline-block; }}
  .dot-green {{ background:#00FF9D;animation:blink 1.2s infinite; }}
  .dot-grey  {{ background:#4A6070; }}
  @keyframes blink {{0%,100%{{opacity:1}}50%{{opacity:0.2}}}}
</style>
</head>
<body>

<div class="header">
  <div class="logo">🎯</div>
  <div>
    <div class="title">APEX Call Coach</div>
    <div class="subtitle">Live AI Sales Intelligence</div>
  </div>
</div>

<div class="metrics">
  <div class="metric"><div class="metric-val" id="m-dur">00:00</div><div class="metric-lbl">Duration</div></div>
  <div class="metric"><div class="metric-val" id="m-wrd">0</div><div class="metric-lbl">Words</div></div>
  <div class="metric"><div class="metric-val" id="m-obj" style="color:#FF3B5C">0</div><div class="metric-lbl">Objections</div></div>
  <div class="metric"><div class="metric-val" id="m-ins" style="color:#00E5FF">0</div><div class="metric-lbl">Insights</div></div>
  <div class="metric">
    <div id="m-stat"><span class="pill-idle"><span class="dot dot-grey"></span>IDLE</span></div>
    <div class="metric-lbl" style="margin-top:6px">Status</div>
  </div>
</div>

<div class="buttons">
  <button class="btn btn-start" id="btn-start" onclick="startListening()">▶ Start Listening</button>
  <button class="btn btn-stop"  id="btn-stop"  onclick="stopListening()" disabled>◼ Stop</button>
  <button class="btn btn-clear" id="btn-clear" onclick="clearSession()">🗑 Clear Session</button>
</div>

<div class="status-bar" id="status">👆 Add API keys in the sidebar, then click Start Listening.</div>
<div class="interim-bar" id="interim"></div>
<div class="error-box" id="err-box"></div>

<div class="columns">
  <div>
    <div class="section-title">🎙️ Live Transcript</div>
    <div class="tx-box" id="tx-box"><div class="tx-empty">Transcript will appear here when you start listening…</div></div>
  </div>
  <div>
    <div class="section-title">💡 Live Coaching Feed</div>
    <div class="tx-box" id="coach-box">
      <div class="coach-empty">🎤<br><br>Coaching insights will appear here.<br><br><span style="color:#00E5FF">Start listening to begin.</span></div>
    </div>
  </div>
</div>

<script>
  const DG_KEY      = `{dg_safe}`;
  const CLAUDE_KEY  = `{claude_safe}`;
  const LANGUAGE    = `{language}`;
  const COACH_EVERY = {coach_interval};
  const PRODUCT     = `{product_safe}`;
  const PERSONA     = `{persona_safe}`;

  let socket, audioCtx, processor, source, mediaStream;
  let recording=false, startTime=null, timer=null;
  let words=0, objCount=0, insCount=0, wordsSinceCoach=0;
  let lines=[], pending='', lastCoach=0;

  const $ = id => document.getElementById(id);

  function ts() {{ return new Date().toLocaleTimeString('en-US',{{hour12:false}}); }}
  function setStatus(msg,col='#00E5FF'){{ $('status').style.color=col; $('status').textContent=msg; }}
  function showErr(msg){{ $('err-box').textContent='❌ '+msg; $('err-box').style.display='block'; }}
  function clearErr(){{ $('err-box').style.display='none'; }}
  function setLive(live){{
    $('m-stat').innerHTML = live
      ? '<span class="pill-live"><span class="dot dot-green"></span>LIVE</span>'
      : '<span class="pill-idle"><span class="dot dot-grey"></span>IDLE</span>';
    $('btn-start').disabled = live;
    $('btn-stop').disabled  = !live;
  }}
  function updateMetrics(){{
    $('m-wrd').textContent = words;
    $('m-obj').textContent = objCount;
    $('m-ins').textContent = insCount;
  }}
  function startTimer(){{
    startTime = Date.now();
    timer = setInterval(()=>{{
      const s=Math.floor((Date.now()-startTime)/1000);
      $('m-dur').textContent = String(Math.floor(s/60)).padStart(2,'0')+':'+String(s%60).padStart(2,'0');
    }},500);
  }}
  function stopTimer(){{ clearInterval(timer); }}

  function addLine(t,text){{
    const box=$('tx-box');
    const empty=box.querySelector('.tx-empty');
    if(empty) empty.remove();
    const d=document.createElement('div');
    d.className='tx-line';
    d.innerHTML=`<span class="tx-speaker">[${{t}}] You</span>: ${{text}}`;
    box.appendChild(d);
    box.scrollTop=box.scrollHeight;
  }}

  function addCoach(type,content,t){{
    const box=$('coach-box');
    const empty=box.querySelector('.coach-empty');
    if(empty) empty.remove();
    const map={{
      objection:['🚨','tag-objection','OBJECTION'],
      tip:['💡','tag-tip','TIP'],
      positive:['✅','tag-positive','GREAT MOVE'],
      coach:['🎯','tag-coach','COACHING'],
    }};
    const [icon,cls,label]=map[type]||map.coach;
    const d=document.createElement('div');
    d.className=`coach-card ${{type}}`;
    d.innerHTML=`<span class="coach-tag ${{cls}}">${{icon}} ${{label}}</span><span class="coach-ts">${{t}}</span><div style="clear:both;margin-top:4px">${{content}}</div>`;
    box.insertBefore(d,box.firstChild);
  }}

  async function getCoaching(chunk,fullTx){{
    if(!CLAUDE_KEY) return;
    try{{
      const system=`You are APEX, a real-time sales call coach.
Product: ${{PRODUCT||'the product'}}
Persona: ${{PERSONA||'a business decision-maker'}}
Full transcript so far: ${{fullTx.slice(-2000)}}
Latest chunk: ${{chunk}}
Reply ONLY in raw JSON (no markdown fences):
{{"type":"objection"|"tip"|"positive"|"coach"|"none","content":"1-3 sentence coaching tip","urgency":"high"|"medium"|"low"}}`;
      const r=await fetch('https://api.anthropic.com/v1/messages',{{
        method:'POST',
        headers:{{
          'x-api-key':CLAUDE_KEY,
          'anthropic-version':'2023-06-01',
          'content-type':'application/json',
          'anthropic-dangerous-direct-browser-access':'true',
        }},
        body:JSON.stringify({{
          model:'claude-haiku-4-5-20251001',
          max_tokens:200,
          system:system,
          messages:[{{role:'user',content:'Coach me now.'}}],
        }}),
      }});
      const data=await r.json();
      const raw=(data.content?.[0]?.text||'').trim().replace(/^```[a-z]*\n?|\n?```$/g,'');
      const result=JSON.parse(raw);
      if(result.type && result.type!=='none'){{
        insCount++;
        addCoach(result.type,result.content,ts());
        if(result.type==='objection') objCount++;
        updateMetrics();
      }}
    }}catch(e){{ console.error('Coaching error:',e); }}
  }}

  function processFinal(text){{
    const t=ts();
    addLine(t,text);
    lines.push(text);
    const w=text.trim().split(/\s+/).length;
    words+=w; wordsSinceCoach+=w;
    pending+=' '+text;
    updateMetrics();
    const now=Date.now();
    if(wordsSinceCoach>=COACH_EVERY && (now-lastCoach)>8000){{
      getCoaching(pending.trim(), lines.join(' '));
      lastCoach=now; wordsSinceCoach=0; pending='';
    }}
  }}

  async function startListening(){{
    clearErr();
    if(!DG_KEY){{ showErr('Add your Deepgram API key in the sidebar.'); return; }}
    if(!CLAUDE_KEY){{ showErr('Add your Anthropic API key in the sidebar.'); return; }}
    try{{
      mediaStream=await navigator.mediaDevices.getUserMedia({{audio:true,video:false}});
      setStatus('🎙️ Mic open — connecting to Deepgram...');
      const params=new URLSearchParams({{language:LANGUAGE,model:'nova-2',smart_format:'true',interim_results:'true',punctuate:'true',endpointing:'300',encoding:'linear16',sample_rate:'16000'}});
      socket=new WebSocket(`wss://api.deepgram.com/v1/listen?${{params}}`,['token',DG_KEY]);
      socket.binaryType='arraybuffer';
      socket.onopen=()=>{{
        setStatus('✅ LIVE — Listening...'); setLive(true); recording=true; startTimer();
        audioCtx=new AudioContext({{sampleRate:16000}});
        source=audioCtx.createMediaStreamSource(mediaStream);
        processor=audioCtx.createScriptProcessor(4096,1,1);
        source.connect(processor); processor.connect(audioCtx.destination);
        processor.onaudioprocess=e=>{{
          if(socket.readyState!==WebSocket.OPEN) return;
          const f32=e.inputBuffer.getChannelData(0);
          const i16=new Int16Array(f32.length);
          for(let i=0;i<f32.length;i++) i16[i]=Math.max(-32768,Math.min(32767,f32[i]*32768));
          socket.send(i16.buffer);
        }};
      }};
      socket.onmessage=e=>{{
        const d=JSON.parse(e.data);
        if(d.type!=='Results') return;
        const alt=(d.channel?.alternatives||[{{}}])[0];
        const txt=(alt.transcript||'').trim();
        if(!txt) return;
        if(d.is_final){{ $('interim').textContent=''; processFinal(txt); }}
        else {{ $('interim').textContent='… '+txt; }}
      }};
      socket.onerror=()=>{{ showErr('Deepgram connection error — check your API key.'); stopListening(); }};
      socket.onclose=()=>{{ if(recording) setStatus('⏹ Disconnected.'); setLive(false); recording=false; stopTimer(); }};
    }}catch(e){{ showErr('Microphone error: '+e.message); }}
  }}

  function stopListening(){{
    recording=false; stopTimer(); setLive(false);
    setStatus('⏹ Stopped.'); $('interim').textContent='';
    if(socket) socket.close();
    if(processor){{ processor.disconnect(); processor=null; }}
    if(source){{ source.disconnect(); source=null; }}
    if(audioCtx){{ audioCtx.close(); audioCtx=null; }}
    if(mediaStream){{ mediaStream.getTracks().forEach(t=>t.stop()); mediaStream=null; }}
  }}

  function clearSession(){{
    stopListening();
    words=0; objCount=0; insCount=0; wordsSinceCoach=0;
    lines=[]; pending=''; lastCoach=0;
    $('m-dur').textContent='00:00';
    $('interim').textContent='';
    $('tx-box').innerHTML='<div class="tx-empty">Transcript will appear here when you start listening…</div>';
    $('coach-box').innerHTML='<div class="coach-empty">🎤<br><br>Coaching insights will appear here.<br><br><span style="color:#00E5FF">Start listening to begin.</span></div>';
    clearErr(); updateMetrics();
    setStatus('👆 Add API keys in the sidebar, then click Start Listening.');
  }}
</script>
</body>
</html>
""", height=900, scrolling=False)
# updated
