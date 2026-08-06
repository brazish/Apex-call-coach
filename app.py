import streamlit as st
import os
import json
import time
from datetime import datetime, date, timedelta
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="APEX · Pinnacle Peak Recovery",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── GLOBAL STYLES ────────────────────────────────────────────────
st.markdown("""
<style>
  #MainMenu, footer, header { visibility: hidden; }
  [data-testid="stHeader"] { display: none; }
  [data-testid="stSidebar"] { display: none; }
  [data-testid="collapsedControl"] { display: none; }
  .block-container { padding: 0 !important; margin: 0 !important; max-width: 100% !important; }
  .stApp { margin: 0 !important; padding: 0 !important; }
  div[data-testid="stVerticalBlock"] { gap: 0 !important; padding: 0 !important; }
  iframe { display: block !important; width: 100vw !important; border: none !important; margin: 0 !important; }

  /* Hide Streamlit's own button styles, replace with our nav */
  div[data-testid="stHorizontalBlock"] { gap: 0 !important; background: #FFFFFF; border-bottom: 1px solid #E2DDD8; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }

  /* Nav tab buttons */
  .nav-wrap { background: white; border-bottom: 1px solid #E2DDD8; box-shadow: 0 1px 3px rgba(0,0,0,0.06); display: flex; align-items: stretch; height: 52px; width: 100%; }
  .nav-brand { display: flex; align-items: center; gap: 10px; padding: 0 24px; border-right: 1px solid #E2DDD8; flex-shrink: 0; }
  .nav-logo { width: 30px; height: 30px; background: #883E27; border-radius: 7px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 800; font-size: 14px; }
  .nav-name { font-weight: 700; font-size: 13px; color: #17120E; font-family: 'Plus Jakarta Sans', sans-serif; }
  .nav-sub { font-size: 10px; color: #BC9642; font-weight: 600; letter-spacing: 0.3px; font-family: 'Plus Jakarta Sans', sans-serif; }
  .nav-tabs { display: flex; align-items: stretch; flex: 1; }

  /* Style Streamlit buttons inside nav to look like tabs */
  .nav-tabs .stButton > button {
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    color: #9E9189 !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
    padding: 0 24px !important;
    height: 52px !important;
    cursor: pointer !important;
    transition: all .15s !important;
    box-shadow: none !important;
    width: auto !important;
    white-space: nowrap !important;
  }
  .nav-tabs .stButton > button:hover {
    color: #883E27 !important;
    background: rgba(136,62,39,0.03) !important;
    border-bottom-color: rgba(136,62,39,0.3) !important;
  }
  .nav-tabs .stButton.active-tab > button {
    color: #883E27 !important;
    border-bottom-color: #883E27 !important;
    background: transparent !important;
  }

  /* Alumni dashboard styles */
  .card { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 16px; border: 1px solid #E2DDD8; }
  .flag-crisis { border-left: 4px solid #B83030 !important; background: #FDF5F5 !important; }
  .flag-relapse { border-left: 4px solid #B83030 !important; }
  .flag-interested { border-left: 4px solid #1E7C50 !important; background: #F0FAF4 !important; }
  .flag-concerning { border-left: 4px solid #A07020 !important; }
  .msg-out { background: #883E27; color: white; border-radius: 16px 16px 4px 16px; padding: 10px 14px; margin: 4px 0 4px 40px; font-size: 13px; line-height: 1.5; }
  .msg-in  { background: #F0EDE8; color: #17120E; border-radius: 16px 16px 16px 4px; padding: 10px 14px; margin: 4px 40px 4px 0; font-size: 13px; line-height: 1.5; }
  .msg-time { font-size: 10px; color: #9E9189; margin: 2px 4px; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 100px; font-size: 10px; font-weight: 700; }
  .badge-crisis    { background: #FDE8E8; color: #B83030; }
  .badge-relapse   { background: #FDE8E8; color: #B83030; }
  .badge-interested { background: #E8F5EE; color: #1E7C50; }
  .badge-concerning { background: #FBF5E6; color: #A07020; }
  .badge-active    { background: #EAF0FB; color: #3B5CA8; }
  .stat-box { background: white; border-radius: 10px; padding: 16px 20px; text-align: center; border: 1px solid #E2DDD8; }
  .stat-val { font-size: 28px; font-weight: 800; color: #17120E; line-height: 1; }
  .stat-lbl { font-size: 10px; font-weight: 600; color: #9E9189; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }
</style>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# ── NAV BAR ──────────────────────────────────────────────────────
st.markdown("""
<div class="nav-wrap">
  <div class="nav-brand">
    <div class="nav-logo">P</div>
    <div>
      <div class="nav-name">Pinnacle Peak Recovery</div>
      <div class="nav-sub">APEX Platform</div>
    </div>
  </div>
  <div class="nav-tabs" id="nav-tabs">
""", unsafe_allow_html=True)

# Render tab buttons inline inside the nav div
nav_col1, nav_col2, nav_spacer = st.columns([1, 1, 8])
with nav_col1:
    if st.button("🎯  Call Coach", key="tab_coach"):
        st.session_state.active_tab = "coach"
        st.rerun()
with nav_col2:
    if st.button("👥  Alumni Outreach", key="tab_alumni"):
        st.session_state.active_tab = "alumni"
        st.rerun()

st.markdown("</div></div>", unsafe_allow_html=True)

# Inject active tab highlight via JS
active = st.session_state.get("active_tab", "coach")
st.markdown(f"""
<script>
  // Highlight active tab button
  window.addEventListener('load', function() {{
    const btns = window.parent.document.querySelectorAll('[data-testid="stButton"] button');
    btns.forEach(btn => {{
      if (btn.textContent.includes('{"Call Coach" if active == "coach" else "Alumni Outreach"}')) {{
        btn.style.color = '#883E27';
        btn.style.borderBottom = '2px solid #883E27';
      }}
    }});
  }});
</script>
""", unsafe_allow_html=True)

# ── SESSION STATE ────────────────────────────────────────────────
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "coach"
if "selected_client" not in st.session_state:
    st.session_state.selected_client = None
if "last_poll" not in st.session_state:
    st.session_state.last_poll = datetime.now()
if "notifications" not in st.session_state:
    st.session_state.notifications = []

# ── SIDEBAR CONFIG ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ APEX Config")
    dg_key = st.text_input("Deepgram API Key", value=os.getenv("DEEPGRAM_API_KEY",""), type="password")
    claude_key = st.text_input("Anthropic API Key", value=os.getenv("ANTHROPIC_API_KEY",""), type="password")
    twilio_sid = st.text_input("Twilio Account SID", value=os.getenv("TWILIO_ACCOUNT_SID",""), type="password")
    twilio_token = st.text_input("Twilio Auth Token", value=os.getenv("TWILIO_AUTH_TOKEN",""), type="password")
    twilio_number = st.text_input("Twilio Phone Number", value=os.getenv("TWILIO_PHONE_NUMBER",""), placeholder="+18005550100")
    st.markdown("---")
    language = st.selectbox("Language", ["en-US","en-GB","es","fr","de","pt"])
    coach_interval = st.slider("Coach every N words", 10, 60, 20, 5)

# Set env vars from sidebar inputs
if twilio_sid: os.environ["TWILIO_ACCOUNT_SID"] = twilio_sid
if twilio_token: os.environ["TWILIO_AUTH_TOKEN"] = twilio_token
if twilio_number: os.environ["TWILIO_PHONE_NUMBER"] = twilio_number
if claude_key: os.environ["ANTHROPIC_API_KEY"] = claude_key

# ── CALL COACH TAB ───────────────────────────────────────────────
if st.session_state.active_tab == "coach":
    dg = (dg_key or "").replace("`","").replace("$","").strip()
    cl = (claude_key or "").replace("`","").replace("$","").strip()
    html = open("ui.html", encoding="utf-8").read()
    html = html.replace("__DG__", dg).replace("__CL__", cl)
    html = html.replace("__LANG__", language)
    html = html.replace("__CI__", str(int(coach_interval)))
    st.components.v1.html(html, height=5500, scrolling=True)

# ── ALUMNI TAB ───────────────────────────────────────────────────
else:
    import alumni as adb

    # Auto-poll every 30 seconds for new replies
    now = datetime.now()
    should_poll = (now - st.session_state.last_poll).seconds > 30

    # ── NOTIFICATIONS BAR ────────────────────────────────────────
    all_clients = adb.get_all_clients()
    flagged = [c for c in all_clients if c.get("flag") and c["flag"].get("type") in ("crisis","relapse","interested","concerning")]
    
    if flagged:
        for fc in flagged[:3]:
            flag_type = fc["flag"]["type"]
            flag_msg = fc["flag"].get("message","")
            icon = "🚨" if flag_type in ("crisis","relapse") else "🟡" if flag_type == "concerning" else "✅"
            color = "#B83030" if flag_type in ("crisis","relapse") else "#A07020" if flag_type == "concerning" else "#1E7C50"
            st.markdown(f"""
            <div style="background:{'#FDE8E8' if flag_type in ('crisis','relapse') else '#FBF5E6' if flag_type == 'concerning' else '#E8F5EE'};
                border-left:4px solid {color};padding:12px 20px;margin-bottom:4px;border-radius:0 8px 8px 0;
                font-family:'Plus Jakarta Sans',sans-serif;font-size:13px;display:flex;align-items:center;gap:12px">
              <span style="font-size:18px">{icon}</span>
              <div>
                <strong style="color:{color}">{fc['name']} — {flag_type.upper()} FLAGGED</strong>
                {f'<div style="color:#5C4E46;font-size:12px;margin-top:2px">{flag_msg}</div>' if flag_msg else ''}
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ── STATS ROW ────────────────────────────────────────────────
    active = len([c for c in all_clients if c.get("status") == "active"])
    flagged_count = len(flagged)
    interested = len([c for c in all_clients if c.get("flag") and c["flag"].get("type") == "interested"])
    total_msgs = sum(len(c.get("conversations", [])) for c in all_clients)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="stat-box"><div class="stat-val">{active}</div><div class="stat-lbl">Active Alumni</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-box"><div class="stat-val" style="color:#B83030">{flagged_count}</div><div class="stat-lbl">Flagged</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-box"><div class="stat-val" style="color:#1E7C50">{interested}</div><div class="stat-lbl">Re-Interested</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="stat-box"><div class="stat-val">{total_msgs}</div><div class="stat-lbl">Total Messages</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ── MAIN LAYOUT ──────────────────────────────────────────────
    left_col, right_col = st.columns([1, 1.6], gap="large")

    # ── LEFT: Add Client + Client List ───────────────────────────
    with left_col:

        # Add New Client
        with st.expander("➕ Add Discharged Client", expanded=False):
            with st.form("add_client_form"):
                name = st.text_input("Full Name *")
                phone = st.text_input("Phone Number *", placeholder="+1 (480) 555-0100")
                discharge_date = st.date_input("Discharge Date *", value=date.today())
                notes = st.text_area("Clinical Notes (optional)", placeholder="Opioid use disorder, completed 30-day residential, strong family support...", height=80)
                submitted = st.form_submit_button("Add Client & Start Sequence", type="primary")
                
                if submitted:
                    if not name or not phone:
                        st.error("Name and phone are required.")
                    else:
                        try:
                            client_id = adb.add_client(name, phone, discharge_date, notes)
                            st.success(f"✅ {name} added. Outreach sequence started — first text in 24 hours.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

        st.markdown("### Client List")

        # Filter
        filter_opt = st.selectbox("Filter", ["All", "Flagged", "Re-Interested", "Active Only"], label_visibility="collapsed")

        clients_to_show = all_clients
        if filter_opt == "Flagged":
            clients_to_show = [c for c in all_clients if c.get("flag")]
        elif filter_opt == "Re-Interested":
            clients_to_show = [c for c in all_clients if c.get("flag") and c["flag"].get("type") == "interested"]
        elif filter_opt == "Active Only":
            clients_to_show = [c for c in all_clients if c.get("status") == "active"]

        if not clients_to_show:
            st.markdown('<div style="color:#9E9189;font-size:13px;padding:20px 0;text-align:center">No clients yet. Add a discharged client above to start the re-engagement sequence.</div>', unsafe_allow_html=True)

        for client in reversed(clients_to_show):
            flag = client.get("flag")
            flag_type = flag["type"] if flag else None
            flag_class = f"flag-{flag_type}" if flag_type else ""
            badge_html = f'<span class="badge badge-{flag_type}">{flag_type.upper()}</span>' if flag_type else '<span class="badge badge-active">ACTIVE</span>'
            
            scheduled = client.get("scheduled", {})
            sent = sum(1 for v in scheduled.values() if v)
            total_sched = len(scheduled)
            
            msg_count = len(client.get("conversations", []))
            
            is_selected = st.session_state.selected_client == client["id"]
            border = "border:2px solid #883E27 !important;" if is_selected else ""

            st.markdown(f"""
            <div class="card {flag_class}" style="{border}cursor:pointer" id="client-{client['id']}">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px">
                <div>
                  <div style="font-weight:700;font-size:14px;color:#17120E">{client['name']}</div>
                  <div style="font-size:11px;color:#9E9189;margin-top:2px">{client['phone']} · Discharged {client['discharge_date']}</div>
                </div>
                {badge_html}
              </div>
              <div style="display:flex;gap:16px;font-size:11px;color:#6E665E;margin-top:8px">
                <span>📤 {sent}/{total_sched} checkpoints sent</span>
                <span>💬 {msg_count} messages</span>
              </div>
              {f'<div style="font-size:11px;color:#B83030;margin-top:6px;font-weight:500">⚠️ {flag["message"][:80]}</div>' if flag_type in ("crisis","relapse") else ""}
              {f'<div style="font-size:11px;color:#1E7C50;margin-top:6px;font-weight:500">✅ Expressed interest in returning</div>' if flag_type == "interested" else ""}
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"View Conversation", key=f"sel_{client['id']}", use_container_width=True):
                st.session_state.selected_client = client["id"]
                st.rerun()

    # ── RIGHT: Conversation View ──────────────────────────────────
    with right_col:
        if not st.session_state.selected_client:
            st.markdown("""
            <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:400px;color:#9E9189;text-align:center">
              <div style="font-size:40px;margin-bottom:12px">💬</div>
              <div style="font-size:15px;font-weight:600;color:#5C4E46;margin-bottom:6px">Select a client to view their conversation</div>
              <div style="font-size:13px">Claude handles outreach autonomously.<br>You'll be notified of anything that needs attention.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            client = adb.get_client(st.session_state.selected_client)
            if not client:
                st.error("Client not found.")
            else:
                flag = client.get("flag")
                flag_type = flag["type"] if flag else None

                # Client header
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"### {client['name']}")
                    st.markdown(f"<div style='font-size:12px;color:#9E9189'>{client['phone']} · Discharged {client['discharge_date']}</div>", unsafe_allow_html=True)
                with col_b:
                    if flag_type:
                        flag_colors = {"crisis":"#B83030","relapse":"#B83030","interested":"#1E7C50","concerning":"#A07020"}
                        st.markdown(f'<div class="badge badge-{flag_type}" style="margin-top:20px;font-size:12px;padding:4px 12px">{flag_type.upper()}</div>', unsafe_allow_html=True)

                # Flag detail
                if flag and flag.get("message"):
                    color = "#B83030" if flag_type in ("crisis","relapse") else "#A07020" if flag_type == "concerning" else "#1E7C50"
                    st.markdown(f"""
                    <div style="background:{'#FDE8E8' if flag_type in ('crisis','relapse') else '#FBF5E6' if flag_type == 'concerning' else '#E8F5EE'};
                        border-left:3px solid {color};padding:10px 14px;border-radius:0 8px 8px 0;
                        font-size:12px;color:{color};margin:8px 0">
                      <strong>Note:</strong> {flag['message']}
                    </div>
                    """, unsafe_allow_html=True)

                # Checkpoint timeline
                scheduled = client.get("scheduled", {})
                discharge = datetime.fromisoformat(str(client["discharge_date"]))
                checkpoints = {"24h": discharge + timedelta(hours=24), "72h": discharge + timedelta(hours=72), "7d": discharge + timedelta(days=7)}
                
                timeline_html = '<div style="display:flex;gap:0;margin:12px 0;background:#F9F8F6;border-radius:8px;overflow:hidden;border:1px solid #E2DDD8">'
                for key, send_time in checkpoints.items():
                    sent = scheduled.get(key, False)
                    due = datetime.now() >= send_time
                    color = "#883E27" if sent else "#9E9189" if not due else "#A07020"
                    bg = "#FDF0EB" if sent else "#F9F8F6"
                    label = {"24h":"24 Hours","72h":"72 Hours","7d":"7 Days"}[key]
                    status = "✓ Sent" if sent else ("Pending" if not due else "Overdue")
                    timeline_html += f'<div style="flex:1;text-align:center;padding:10px 8px;background:{bg};border-right:1px solid #E2DDD8"><div style="font-size:10px;font-weight:700;color:{color};text-transform:uppercase;letter-spacing:.5px">{label}</div><div style="font-size:10px;color:{color};margin-top:2px">{status}</div></div>'
                timeline_html += "</div>"
                st.markdown(timeline_html, unsafe_allow_html=True)

                # Conversation
                st.markdown("**Conversation**")
                conversations = client.get("conversations", [])
                
                if not conversations:
                    st.markdown('<div style="color:#9E9189;font-size:13px;padding:16px 0;text-align:center">No messages yet. First outreach fires 24 hours after discharge.</div>', unsafe_allow_html=True)
                else:
                    conv_html = '<div style="max-height:420px;overflow-y:auto;padding:8px 0">'
                    for msg in conversations:
                        ts = msg.get("timestamp","")[:16] if msg.get("timestamp") else ""
                        if msg["role"] == "outbound":
                            conv_html += f'<div class="msg-out">{msg["body"]}</div><div class="msg-time" style="text-align:right">{ts}</div>'
                        else:
                            conv_html += f'<div class="msg-in">{msg["body"]}</div><div class="msg-time">{ts}</div>'
                    conv_html += "</div>"
                    st.markdown(conv_html, unsafe_allow_html=True)

                # Manual message
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                with st.form(f"manual_msg_{client['id']}"):
                    manual_text = st.text_area("Send Manual Message", placeholder="Type a message to send directly from PPR...", height=70, label_visibility="collapsed")
                    send_col, clear_col = st.columns([3, 1])
                    with send_col:
                        send_btn = st.form_submit_button("Send Message", type="primary", use_container_width=True)
                    with clear_col:
                        clear_flag = st.form_submit_button("Clear Flag", use_container_width=True)

                    if send_btn and manual_text.strip():
                        try:
                            from sms_engine import send_sms
                            send_sms(client["phone"], manual_text.strip(), client["id"])
                            st.success("✅ Message sent.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to send: {e}")
                    
                    if clear_flag:
                        adb.set_flag(client["id"], None, "")
                        st.success("Flag cleared.")
                        st.rerun()

                # Archive
                if st.button("Archive Client", key=f"archive_{client['id']}"):
                    adb.update_client_status(client["id"], "archived")
                    st.session_state.selected_client = None
                    st.rerun()

    # ── AUTO-PROCESS CHECKPOINTS + POLL REPLIES ──────────────────
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    
    col_run, col_status = st.columns([1, 3])
    with col_run:
        if st.button("🔄 Check for Replies & Process Outreach", use_container_width=True):
            with st.spinner("Checking Twilio for new replies and processing due checkpoints..."):
                try:
                    from sms_engine import process_checkpoints, fetch_inbound_replies
                    
                    # Process due checkpoints
                    checkpoint_actions = process_checkpoints()
                    
                    # Fetch new replies
                    new_replies = fetch_inbound_replies()
                    
                    st.session_state.last_poll = datetime.now()
                    
                    if checkpoint_actions:
                        for action in checkpoint_actions:
                            if "error" in action:
                                st.warning(f"⚠️ {action['client']} ({action['checkpoint']}): {action['error']}")
                            else:
                                st.success(f"📤 Sent {action['checkpoint']} check-in to {action['client']}")
                                if action.get("flag"):
                                    st.warning(f"🚩 Flagged: {action['flag']}")
                    
                    if new_replies:
                        for reply in new_replies:
                            if "error" in reply:
                                st.warning(f"⚠️ Reply from {reply['client_name']}: processing error — {reply['error']}")
                            else:
                                st.info(f"💬 New reply from **{reply['client_name']}**: \"{reply['inbound'][:60]}...\"")
                                if reply.get("flag"):
                                    st.error(f"🚨 {reply['client_name']} FLAGGED: {reply['flag']}")
                    
                    if not checkpoint_actions and not new_replies:
                        st.info("✓ All up to date — no new checkpoints or replies.")
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error: {e}")
    
    with col_status:
        last_poll_str = st.session_state.last_poll.strftime("%I:%M:%S %p")
        st.markdown(f'<div style="font-size:11px;color:#9E9189;padding:10px 0">Last checked: {last_poll_str} · Auto-check every 30s when active</div>', unsafe_allow_html=True)

    # Auto-rerun for polling (30s)
    if should_poll and st.session_state.active_tab == "alumni":
        st.session_state.last_poll = datetime.now()
        time.sleep(0.1)
        st.rerun()
