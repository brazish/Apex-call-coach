import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()

with st.sidebar:
    st.markdown("### Configuration")
    dg_key = st.text_input("Deepgram API Key", value=os.getenv("DEEPGRAM_API_KEY",""), type="password")
    claude_key = st.text_input("Anthropic API Key", value=os.getenv("ANTHROPIC_API_KEY",""), type="password")
    product_ctx = st.text_area("Product / Service", placeholder="e.g. SaaS CRM at $500/mo", height=70)
    persona_ctx = st.text_area("Prospect Persona", placeholder="e.g. VP Sales", height=70)
    language = st.selectbox("Language", ["en-US","en-GB","es","fr","de","pt"])
    coach_interval = st.slider("Coach every N words", 10, 60, 20, 5)

st.write("App loaded!")
