import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="APEX · Pinnacle Peak Recovery",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Strip every pixel of Streamlit chrome
st.markdown("""
<style>
  #MainMenu, footer, header { visibility: hidden; }
  [data-testid="stHeader"] { display: none; }
  [data-testid="stSidebar"] { display: none; }
  [data-testid="collapsedControl"] { display: none; }
  .block-container { padding: 0 !important; margin: 0 !important; max-width: 100% !important; }
  .stApp { margin: 0 !important; padding: 0 !important; }
  div[data-testid="stVerticalBlock"] { gap: 0 !important; padding: 0 !important; }
  iframe { display: block !important; width: 100vw !important; border: none !important; margin: 0 !important; padding: 0 !important; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ⚙️ APEX Config")
    dg_key   = st.text_input("Deepgram API Key",    value=os.getenv("DEEPGRAM_API_KEY",""),    type="password")
    claude_key = st.text_input("Anthropic API Key", value=os.getenv("ANTHROPIC_API_KEY",""),   type="password")
    twilio_sid   = st.text_input("Twilio Account SID",  value=os.getenv("TWILIO_ACCOUNT_SID",""),  type="password")
    twilio_token = st.text_input("Twilio Auth Token",    value=os.getenv("TWILIO_AUTH_TOKEN",""),   type="password")
    twilio_number = st.text_input("Twilio Phone Number", value=os.getenv("TWILIO_PHONE_NUMBER",""), placeholder="+18005550100")
    st.markdown("---")
    language = st.selectbox("Language", ["en-US","en-GB","es","fr","de","pt"])
    coach_interval = st.slider("Coach every N words", 10, 60, 20, 5)
    st.markdown("---")
    st.markdown("🟢 Deepgram"  if dg_key    else "🔴 Deepgram missing")
    st.markdown("🟢 Anthropic" if claude_key else "🔴 Anthropic missing")
    st.markdown("🟢 Twilio"    if twilio_sid else "🔴 Twilio missing")

dg = (dg_key or "").replace("`","").replace("$","").strip()
cl = (claude_key or "").replace("`","").replace("$","").strip()
t_sid = (twilio_sid or "").strip()
t_token = (twilio_token or "").strip()
t_from = (twilio_number or "").strip()

html = open("ui.html", encoding="utf-8").read()
html = html.replace("__DG__", dg).replace("__CL__", cl)
html = html.replace("__LANG__", language)
html = html.replace("__CI__", str(int(coach_interval)))
html = html.replace("__TWILIO_SID__", t_sid)
html = html.replace("__TWILIO_TOKEN__", t_token)
html = html.replace("__TWILIO_FROM__", t_from)

st.components.v1.html(html, height=5500, scrolling=True)
