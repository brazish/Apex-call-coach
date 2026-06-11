import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="APEX Call Coach",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* Hide everything Streamlit */
    #MainMenu {visibility: hidden}
    footer {visibility: hidden}
    header {visibility: hidden}
    [data-testid="stHeader"] {display: none}
    [data-testid="stSidebar"] {display: none}
    [data-testid="collapsedControl"] {display: none}
    section[data-testid="stSidebarContent"] {display: none}

    /* Zero out all padding/margin */
    .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
    }
    .stApp {
        margin: 0 !important;
        padding: 0 !important;
    }
    .main .block-container {
        padding: 0 !important;
    }
    /* Full width iframe */
    iframe {
        display: block !important;
        width: 100vw !important;
        min-width: 100% !important;
        border: none !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    /* Kill any remaining gaps */
    div[data-testid="stVerticalBlock"] {
        gap: 0 !important;
        padding: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ⚙️ APEX Config")
    dg_key = st.text_input("Deepgram API Key", value=os.getenv("DEEPGRAM_API_KEY",""), type="password")
    claude_key = st.text_input("Anthropic API Key", value=os.getenv("ANTHROPIC_API_KEY",""), type="password")
    st.markdown("---")
    language = st.selectbox("Language", ["en-US","en-GB","es","fr","de","pt"])
    coach_interval = st.slider("Coach every N words", 10, 60, 20, 5)
    st.markdown("---")
    st.markdown("🟢 Deepgram ready" if dg_key else "🔴 Deepgram key missing")
    st.markdown("🟢 Anthropic ready" if claude_key else "🔴 Anthropic key missing")

dg = dg_key.replace("`","").replace("$","").strip()
cl = claude_key.replace("`","").replace("$","").strip()

html = open("ui.html", encoding="utf-8").read()
html = html.replace("__DG__", dg).replace("__CL__", cl)
html = html.replace("__LANG__", language)
html = html.replace("__CI__", str(int(coach_interval)))

st.components.v1.html(html, height=5500, scrolling=True)
