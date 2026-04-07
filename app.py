import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="Apex Call Coach", layout="wide")

with st.sidebar:
    st.markdown("### Configuration")
    dg_key = st.text_input("Deepgram API Key", value=os.getenv("DEEPGRAM_API_KEY",""), type="password")
    claude_key = st.text_input("Anthropic API Key", value=os.getenv("ANTHROPIC_API_KEY",""), type="password")
    st.markdown("---")
    language = st.selectbox("Language", ["en-US","en-GB","es","fr","de","pt"])
    coach_interval = st.slider("Coach every N words", 10, 60, 20, 5)

dg = dg_key.replace("`","").replace("$","")
cl = claude_key.replace("`","").replace("$","")

html = open("ui.html", encoding="utf-8").read()
html = html.replace("__DG__", dg).replace("__CL__", cl)
html = html.replace("__LANG__", language).replace("__CI__", str(coach_interval))
st.components.v1.html(html, height=1020, scrolling=False)
