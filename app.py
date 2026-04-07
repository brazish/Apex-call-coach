"""
APEX CALL COACH
Run: streamlit run app.py
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import time
import os
import re
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Apex Call Coach", page_icon="🎯", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&family=Inter:wght@400;500&display=swap');
:root {
    --black:#080C10;--card:#131A22;--border:#1E2D3D;
    --accent:#00E5FF;--green:#00FF9D;--red:#FF3B5C;--yellow:#FFD60A;
    --muted:#4A6070;--text:#C8D8E4;--white:#EFF6FB;
}
html,body,[data-testid="stAppViewContainer"]{background:var(--black)!important;color:var(--text)!important;}
[data-testid="stSidebar"]{background:#0E1318!important;border-right:1px solid var(--border)!important;}
#MainMenu,footer,header,[data-testid="stToolbar"]{display:none!important;visibility:hidden!important;}
.metric-box{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:14px;text-align:center;}
.metric-val{font-family:'Syne',sans-serif;font-size:24px;font-weight:800;color:var(--white);}
.metric-lbl{font-family:'DM Mono',monospace;font-size:10px;color:var(--muted);letter-spacing:1.5px;text-transform:uppercase;margin-top:2px;}
.tx-box{background:#090D11;border:1px solid var(--border);border-radius:8px;padding:16px;min-height:220px;max-height:360px;overflow-y:auto;font-family:'DM Mono',monospace;font-size:13px;line-height:1.8;}
.tx-box::-webkit-scrollbar{width:4px;}
.tx-box::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px;}
.tx-speaker{color:var(--accent);font-weight:500;}
.tx-interim{color:var(--muted);font-style:italic;}
.tx-empty{color:var(--muted);font-style:italic;}
.coach-card{border-radius:10px;padding:14px;margin-bottom:10px;border-left:3px solid var(--accent);background:var(--card);font-size:14px;line-height:1.6;color:var(--text);}
.coach-card.objection{border-left-color:var(--red);}
.coach-card.tip{border-left-color:var(--yellow);}
.coach-card.positive{border-left-color:var(--green);}
.coach-tag{font-family:'DM Mono',monospace;font-size:10px;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;padding:2px 8px;border-radius:4px;margin-bottom:6px;display:inline-block;}
.tag-objection{background:rgba(255,59,92,0.15);color:var(--red);}
.tag-tip{background:rgba(255,214,10,0.15);color:var(--yellow);}
.tag-positive{background:rgba(0,255,157,0.15);color:var(--green);}
.tag-coach{background:rgba(0,229,255,0.10);color:var(--accent);}
.pill-live{display:inline-flex;align-items:center;gap:6px;padding:5px 12px;border-radius:100px;background:rgba(0,255,157,0.12);color:var(--green);border:1px solid rgba(0,255,157,0.3);font-family:'DM Mono',monospace;font-size:12px;}
.pill-idle{display:inline-flex;align-items:center;gap:6px;padding:5px 12px;border-radius:100px;background:rgba(74,96,112,0.2);color:var(--muted);border:1px solid var(--border);font-family:'DM Mono',monospace;font-size:12px;}
.dot-green{width:8px;height:8px;border-radius:50%;background:var(--green);animation:blink 1.2s infinite;display:inline-block;}
.dot-grey{width:8px;height:8px;border-radius:50%;background:var(--muted);display:inline-block;}
@keyframes blink{0%,100%{opacity:1}50%{opacity:0.2}}
div[data-testid="stButton"]>button{background:linear-gradient(135deg,#00B8CC,#0080FF)!important;color:#000!important;font-weight:700!important;border:none!important;border-radius:8px!important;width:100%!important;}
div[data-testid="stButton"]>button[kind="secondary"]{background:var(--card)!important;color:var(--red)!important;border:1px solid rgba(255,59,92,0.4)!important;}
div[data-testid="stTextInput"] input,div[data-testid="stTextArea"] textarea{background:#090D11!important;border:1px solid var(--border)!important;color:var(--text)!important;}
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
for k, v in {
    "recording": False, "lines": [], "interim": "", "coaching": [],
    "objections": [], "words": 0, "obj_count": 0, "coach_count": 0,
    "pending": "", "last_coach": 0, "start_time": None, "error": "",
    "transcript_json": None,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

ss = st.session_state

# ── Claude coaching ────────────────────────────────────────────────────────────
def get_coaching(chunk, full_tx, persona, product, api_key):
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        system = f"""You are APEX, a real-time sales call coach.
Product: {product or "the product"}
Persona: {persona or "a business decision-maker"}
Full transcript so far: {full_tx[-2000:]}
Latest chunk: {chunk}
Reply ONLY in raw JSON (no markdown fences):
{{"type":"objection"|"tip"|"positive"|"coach"|"none","content":"1-3 sentence coaching tip","urgency":"high"|"medium"|"low"}}"""
        msg = client.messages.create(
            model="claude-opus-4-5", max_tokens=200, system=system,
            messages=[{"role": "user", "content": "Coach me now."}],
        )
        raw = re.sub(r"^```[a-z]*\n?|\n?```$", "", msg.content[0].text.strip())
        return json.loads(raw)
    except Exception as e:
        return {"type": "none", "content": str(e), "urgency": "low"}

def elapsed():
    if not ss.start_time: return "00:00"
    s = int(time.time() - ss.start_time)
    return f"{s//60:02d}:{s%60:02d}"

# ── Process incoming transcript from browser ───────────────────────────────────
def process_transcript(data, claude_key, persona_ctx, product_ctx, coach_interval):
    txt = data.get("text", "").strip()
    is_final = data.get("final", False)
    if not txt:
        return
    if is_final:
        ss.interim = ""
        ss.lines.append({"ts": datetime.now().strftime("%H:%M:%S"), "text": txt})
        ss.words += len(txt.split())
        ss.pending += " " + txt
        now = time.time()
        pending = ss.pending.strip()
        if len(pending.split()) >= coach_interval and (now - ss.last_coach) > 8 and claude_key:
            full_tx = " ".join(l["text"] for l in ss.lines)
            result = get_coaching(pending, full_tx, persona_ctx, product_ctx, claude_key)
            ss.last_coach = now
            if result.get("type") != "none":
                ss.coach_count += 1
                ss.coaching.append({"type": result.get("type", "coach"), "content": result.get("content", ""), "ts": datetime.now().strftime("%H:%M:%S")})
            if result.get("type") == "objection":
                ss.obj_count += 1
                ss.objections.append({"text": result["content"], "ts": datetime.now().strftime("%H:%M:%S")})
            ss.pending = ""
    else:
        ss.interim = txt

# ── Check for transcript data coming from browser component ───────────────────
if ss.get("transcript_json"):
    data = ss.transcript_json
    ss.transcript_json = None
    dg_key = os.getenv("DEEPGRAM_API_KEY", "")
    claude_key = os.getenv("ANTHROPIC_API_KEY", "")
    # Get sidebar values - we'll use session state to pass them
    process_transcript(data, ss.get("claude_key_val",""), ss.get("persona_val",""), ss.get("product_val",""), ss.get("coach_interval_val", 20))

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    with st.expander("🔑 API Keys", expanded=True):
        dg_key    = st.text_input("Deepgram API Key",   value=os.getenv("DEEPGRAM_API_KEY",""),   type="password")
        claude_key = st.text_input("Anthropic API Key", value=os.getenv("ANTHROPIC_API_KEY",""), type="password")
        ss.claude_key_val = claude_key
    st.markdown("---")
    st.markdown("**🎤 Microphone**")
    st.info("Microphone access is handled via your browser below.")
    st.markdown("---")
    st.markdown("**📞 Call Context**")
    product_ctx = st.text_area("Product / Service", placeholder="e.g. SaaS CRM at $500/mo", height=70)
    persona_ctx = st.text_area("Prospect Persona",  placeholder="e.g. VP Sales, 200-person company", height=70)
    ss.product_val = product_ctx
    ss.persona_val = persona_ctx
    st.markdown("---")
    language       = st.selectbox("Language", ["en-US","en-GB","es","fr","de","pt"])
    coach_interval = st.slider("Coach every N words", 10, 60, 20, 5)
    ss.coach_interval_val = coach_interval

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:16px;padding:20px 0 16px;border-bottom:1px solid #1E2D3D;margin-bottom:20px">
  <div style="width:48px;height:48px;background:linear-gradient(135deg,#00E5FF,#0080FF);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:24px">🎯</div>
  <div>
    <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;color:#EFF6FB;letter-spacing:-0.5px">APEX Call Coach</div>
    <div style="font-family:'DM Mono',monospace;font-size:11px;color:#00E5FF;letter-spacing:2px;text-transform:uppercase">Live AI Sales Intelligence</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Metrics ────────────────────────────────────────────────────────────────────
m1,m2,m3,m4,m5 = st.columns(5)
with m1: st.markdown(f'<div class="metric-box"><div class="metric-val">{elapsed()}</div><div class="metric-lbl">Duration</div></div>', unsafe_allow_html=True)
with m2: st.markdown(f'<div class="metric-box"><div class="metric-val">{ss.words}</div><div class="metric-lbl">Words</div></div>', unsafe_allow_html=True)
with m3: st.markdown(f'<div class="metric-box"><div class="metric-val" style="color:#FF3B5C">{ss.obj_count}</div><div class="metric-lbl">Objections</div></div>', unsafe_allow_html=True)
with m4: st.markdown(f'<div class="metric-box"><div class="metric-val" style="color:#00E5FF">{ss.coach_count}</div><div class="metric-lbl">Insights</div></div>', unsafe_allow_html=True)
with m5:
    pill = '<span class="pill-live"><span class="dot-green"></span>LIVE</span>' if ss.recording else '<span class="pill-idle"><span class="dot-grey"></span>IDLE</span>'
    st.markdown(f'<div class="metric-box"><div style="display:flex;align-items:center;justify-content:center;height:24px">{pill}</div><div class="metric-lbl" style="margin-top:6px">Status</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Buttons ────────────────────────────────────────────────────────────────────
b1,b2,b3 = st.columns([2,2,3])
with b1: btn_start = st.button("▶  Start Listening", disabled=ss.recording,      key="start")
with b2: btn_stop  = st.button("◼  Stop",            disabled=not ss.recording,  key="stop", type="secondary")
with b3: btn_clear = st.button("🗑  Clear Session",   disabled=ss.recording,      key="clear")

if btn_start:
    if not dg_key:
        ss.error = "⚠️ Add your Deepgram API key in the sidebar."
    elif not claude_key:
        ss.error = "⚠️ Add your Anthropic API key in the sidebar."
    else:
        ss.error = ""
        ss.recording = True
        ss.start_time = time.time()
        st.rerun()

if btn_stop:
    ss.recording = False
    ss.interim   = ""
    st.rerun()

if btn_clear:
    for k in ["lines","coaching","objections"]: ss[k] = []
    for k in ["interim","error","pending"]:      ss[k] = ""
    for k in ["words","obj_count","coach_count","last_coach"]: ss[k] = 0
    ss.start_time = None
    ss.recording  = False
    st.rerun()

if ss.error:
    st.error(ss.error)

# ── Browser microphone component ───────────────────────────────────────────────
if ss.recording and dg_key:
    recorder_html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
  body {{ margin:0; padding:12px; font-family: 'DM Mono', monospace; background: #090D11; color: #C8D8E4; }}
  #status {{ font-size:12px; color:#00E5FF; margin-bottom:8px; letter-spacing:1px; }}
  #interim {{ font-size:13px; color:#4A6070; font-style:italic; min-height:20px; }}
  .err {{ color: #FF3B5C; }}
</style>
</head>
<body>
<div id="status">🔴 Connecting to microphone...</div>
<div id="interim"></div>
<script>
const DG_KEY = "{dg_key}";
const LANG   = "{language}";
let mediaRecorder, socket, stream;

async function start() {{
  try {{
    stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
    document.getElementById('status').textContent = '🎙️ Mic open — connecting to Deepgram...';

    const url = `wss://api.deepgram.com/v1/listen?encoding=linear16&sample_rate=16000&channels=1&model=nova-2&smart_format=true&interim_results=true&punctuate=true&endpointing=300&language=${{LANG}}`;
    socket = new WebSocket(url, ['token', DG_KEY]);

    socket.onopen = () => {{
      document.getElementById('status').textContent = '✅ LIVE — listening...';
      mediaRecorder = new MediaRecorder(stream, {{ mimeType: 'audio/webm' }});
      mediaRecorder.ondataavailable = e => {{
        if (socket.readyState === WebSocket.OPEN && e.data.size > 0) {{
          socket.send(e.data);
        }}
      }};
      mediaRecorder.start(250);
    }};

    socket.onmessage = (msg) => {{
      const d = JSON.parse(msg.data);
      if (d.type !== 'Results') return;
      const alt = (d.channel?.alternatives || [{{}}])[0];
      const txt = (alt.transcript || '').trim();
      if (!txt) return;
      const isFinal = d.is_final;
      document.getElementById('interim').textContent = isFinal ? '' : txt;

      // Send transcript back to Streamlit
      window.parent.postMessage({{
        type: 'streamlit:setComponentValue',
        value: JSON.stringify({{ text: txt, final: isFinal }})
      }}, '*');
    }};

    socket.onerror = (e) => {{
      document.getElementById('status').innerHTML = '<span class="err">❌ Deepgram connection error. Check your API key.</span>';
    }};

    socket.onclose = () => {{
      document.getElementById('status').textContent = '⏹ Stopped.';
    }};

  }} catch(e) {{
    document.getElementById('status').innerHTML = `<span class="err">❌ Mic error: ${{e.message}}</span>`;
  }}
}}

start();
</script>
</body>
</html>
"""
    result = components.html(recorder_html, height=80)
    if result:
        try:
            ss.transcript_json = json.loads(result)
            process_transcript(ss.transcript_json, claude_key, persona_ctx, product_ctx, coach_interval)
            ss.transcript_json = None
            st.rerun()
        except Exception:
            pass

# ── Two columns ────────────────────────────────────────────────────────────────
left, right = st.columns([5,4], gap="large")

with left:
    st.markdown("#### 🎙️ Live Transcript")
    lines_html = ""
    for line in ss.lines[-60:]:
        lines_html += f'<div style="margin:4px 0"><span class="tx-speaker">[{line["ts"]}] You</span>: {line["text"]}</div>'
    if ss.interim:
        lines_html += f'<div style="margin:4px 0" class="tx-interim">… {ss.interim}</div>'
    if not lines_html:
        lines_html = '<div class="tx-empty">Transcript will appear here when you start listening…</div>'
    st.markdown(f'<div class="tx-box">{lines_html}</div>', unsafe_allow_html=True)

    if ss.objections:
        st.markdown("#### 🚨 Objection Log")
        for obj in reversed(ss.objections[-5:]):
            st.markdown(f'<div style="margin:4px 0;padding:8px 12px;background:#1a0a0f;border-left:3px solid #FF3B5C;border-radius:6px;font-size:13px"><span style="color:#4A6070;font-size:11px">[{obj["ts"]}]</span> {obj["text"]}</div>', unsafe_allow_html=True)

with right:
    st.markdown("#### 💡 Live Coaching Feed")
    tag_map = {
        "objection": ("🚨","objection","tag-objection","OBJECTION"),
        "tip":       ("💡","tip",      "tag-tip",      "TIP"),
        "positive":  ("✅","positive", "tag-positive", "GREAT MOVE"),
        "coach":     ("🎯","",         "tag-coach",    "COACHING"),
    }
    if not ss.coaching:
        st.markdown('<div style="text-align:center;padding:30px 0;color:#4A6070;font-family:\'DM Mono\',monospace;font-size:13px">🎤<br><br>Coaching insights will appear here.<br><br><span style="color:#00E5FF">Start listening to begin.</span></div>', unsafe_allow_html=True)
    else:
        for item in reversed(ss.coaching[-12:]):
            icon,cls,tag_cls,label = tag_map.get(item["type"],("🎯","","tag-coach","COACHING"))
            st.markdown(f'<div class="coach-card {cls}"><span class="coach-tag {tag_cls}">{icon} {label}</span><span style="font-family:\'DM Mono\',monospace;font-size:10px;color:#4A6070;float:right">{item["ts"]}</span><div style="clear:both;margin-top:4px">{item["content"]}</div></div>', unsafe_allow_html=True)

    if not ss.recording and not ss.coaching:
        st.info("👆 Add API keys, then click **Start Listening**.")

# ── Auto refresh while recording ───────────────────────────────────────────────
if ss.recording:
    time.sleep(0.5)
    st.rerun()
