import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="Apex Call Coach", page_icon="favicon.ico", layout="wide")

with st.sidebar:
    st.markdown("### Configuration")
    dg_key = st.text_input("Deepgram API Key", value=os.getenv("DEEPGRAM_API_KEY",""), type="password")
    claude_key = st.text_input("Anthropic API Key", value=os.getenv("ANTHROPIC_API_KEY",""), type="password")
    st.markdown("---")
    product_ctx = st.text_area("Product / Service", placeholder="e.g. SaaS CRM at $500/mo", height=70)
    persona_ctx = st.text_area("Prospect Persona", placeholder="e.g. VP Sales", height=70)
    language = st.selectbox("Language", ["en-US","en-GB","es","fr","de","pt"])
    coach_interval = st.slider("Coach every N words", 10, 60, 20, 5)

dg = dg_key.replace("`","").replace("$","")
cl = claude_key.replace("`","").replace("$","")
prod = product_ctx.replace("`","").replace("$","")
pers = persona_ctx.replace("`","").replace("$","")
lang = language
ci = coach_interval

html = open("ui.html", encoding="utf-8").read()
html = html.replace("__DG__", dg).replace("__CL__", cl)
html = html.replace("__PROD__", prod).replace("__PERS__", pers)
html = html.replace("__LANG__", lang).replace("__CI__", str(ci))
st.components.v1.html(html, height=920, scrolling=False)
