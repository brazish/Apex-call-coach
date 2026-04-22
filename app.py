import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="Apex Call Coach", layout="wide")

st.markdown("""
<style>
    .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
        padding-left: 0rem;
        padding-right: 0rem;
    }
    header[data-testid="stHeader"] {
        display: none;
    }
    #root > div:first-child { margin-top: 0; }
    .stApp { margin-top: 0; }
    iframe { display: block; width: 100% !important; border: none; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Configuration")
    dg_key = st.text_input("Deepgram API Key", value=os.getenv("DEEPGRAM_API_KEY",""), type="password")
    claude_key = st.text_input("Anthropic API Key", value=os.getenv("ANTHROPIC_API_KEY",""), type="password")
    st.markdown("---")
    language = st.selectbox("Language", ["en-US","en-GB","es","fr","de","pt"])
    coach_interval = st.slider("Coach every N words", 10, 60, 20, 5)
    st.markdown("---")
    st.markdown("**Key Status**")
    st.markdown("🟢 Deepgram ready" if dg_key else "🔴 Deepgram key missing")
    st.markdown("🟢 Anthropic ready" if claude_key else "🔴 Anthropic key missing")

dg = dg_key.replace("`","").replace("$","").strip()
cl = claude_key.replace("`","").replace("$","").strip()

html = open("ui.html", encoding="utf-8").read()
html = html.replace("__DG__", dg).replace("__CL__", cl)
html = html.replace("__LANG__", language)
# Inject CI as a plain number string — avoids ReferenceError if placeholder not replaced
html = html.replace("__CI__", str(int(coach_interval)))
st.components.v1.html(html, height=4200, scrolling=True)
