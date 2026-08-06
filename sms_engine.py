import os
import json
import anthropic
from datetime import datetime
from twilio.rest import Client as TwilioClient
import alumni as db

# ── CHECKPOINT MESSAGES ─────────────────────────────────────────
CHECKPOINT_PROMPTS = {
    "24h": "It has been 24 hours since the client's discharge.",
    "72h": "It has been 72 hours since the client's discharge.",
    "7d":  "It has been 7 days since the client's discharge.",
}

SYSTEM_PROMPT = """You are a warm, empathetic support outreach specialist for Pinnacle Peak Recovery (PPR) in Scottsdale, Arizona. You are texting with a former client who recently completed or left our program.

Your role:
- Check in genuinely and warmly — like a caring human, not a bot
- Listen and respond to whatever they share
- If they mention a slip, relapse, or struggle — respond with compassion and gently explore if they'd want support
- If they express interest in returning or need help — encourage them and let them know PPR is here
- If they seem to be in crisis — express concern clearly and mention that PPR or 988 (crisis line) are available
- Keep messages SHORT — 1-3 sentences max, conversational SMS style
- Never be pushy or salesy — this is genuine human connection
- Sign messages naturally, don't always sign off with a name
- Do NOT mention you are an AI

CRITICAL FLAGS — include these exact strings in your response JSON when detected:
- "FLAG:RELAPSE" — if they mention using substances, relapse, or slipping
- "FLAG:CRISIS" — if they mention self-harm, suicidal thoughts, or acute danger
- "FLAG:INTERESTED" — if they express interest in returning to treatment
- "FLAG:CONCERNING" — if something feels off or worth a human following up on

Facility info if needed:
- Pinnacle Peak Recovery, McCormick Ranch, Scottsdale AZ
- Full continuum: Detox → Residential → PHP → IOP
- PPR Guarantee: complete program + slip in year 1 = 30 days residential free
- Phone: have them call the main line or say staff will reach out

Always respond in this JSON format:
{
  "message": "your SMS message here",
  "flag": null or "FLAG:RELAPSE" or "FLAG:CRISIS" or "FLAG:INTERESTED" or "FLAG:CONCERNING",
  "flag_note": "brief note for the coordinator about why this was flagged"
}"""


def get_twilio_client():
    sid = os.getenv("TWILIO_ACCOUNT_SID", "")
    token = os.getenv("TWILIO_AUTH_TOKEN", "")
    if not sid or not token:
        raise ValueError("Twilio credentials not configured")
    return TwilioClient(sid, token)


def get_twilio_number():
    return os.getenv("TWILIO_PHONE_NUMBER", "")


def send_sms(to_number, body, client_id):
    """Send SMS via Twilio and log it"""
    twilio = get_twilio_client()
    from_number = get_twilio_number()
    msg = twilio.messages.create(body=body, from_=from_number, to=to_number)
    db.add_message(client_id, "outbound", body, sid=msg.sid)
    return msg.sid


def claude_respond(client, incoming_message):
    """Generate Claude response to an incoming SMS"""
    anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))
    
    # Build conversation history
    history = []
    for msg in client["conversations"]:
        role = "assistant" if msg["role"] == "outbound" else "user"
        history.append({"role": role, "content": msg["body"]})
    
    # Add the new incoming message
    history.append({"role": "user", "content": incoming_message})
    
    # Build context
    discharge = client.get("discharge_date", "unknown")
    name = client.get("name", "the client")
    notes = client.get("notes", "")
    
    system = SYSTEM_PROMPT + f"\n\nCLIENT CONTEXT:\nName: {name}\nDischarge date: {discharge}\nNotes: {notes}"
    
    response = anthropic_client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=400,
        system=system,
        messages=history
    )
    
    raw = response.content[0].text.strip()
    
    # Parse JSON response
    try:
        # Strip markdown if present
        raw = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)
    except:
        # Fallback if JSON parse fails
        result = {
            "message": raw[:300],
            "flag": None,
            "flag_note": ""
        }
    
    return result


def generate_checkpoint_message(client, checkpoint):
    """Generate the initial outreach message for a checkpoint"""
    anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))
    
    name = client.get("name", "").split()[0]  # First name only
    notes = client.get("notes", "")
    ctx = CHECKPOINT_PROMPTS.get(checkpoint, "")
    
    system = SYSTEM_PROMPT + f"\n\nCLIENT CONTEXT:\nName: {name}\nNotes: {notes}\n\nSITUATION: {ctx} This is your first outreach. Send a warm, brief check-in text. Do not mention time intervals or that this is a scheduled message."
    
    response = anthropic_client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=300,
        system=system,
        messages=[{"role": "user", "content": f"Generate the {checkpoint} check-in message for {name}."}]
    )
    
    raw = response.content[0].text.strip().replace("```json", "").replace("```", "").strip()
    
    try:
        result = json.loads(raw)
    except:
        result = {"message": raw[:300], "flag": None, "flag_note": ""}
    
    return result


def process_checkpoints():
    """Check all clients for due checkpoints and send messages. Returns list of actions taken."""
    actions = []
    clients = db.get_all_clients()
    
    for client in clients:
        if client.get("status") != "active":
            continue
        
        due = db.get_due_checkpoints(client)
        for checkpoint in due:
            try:
                result = generate_checkpoint_message(client, checkpoint)
                message = result.get("message", "")
                flag = result.get("flag")
                flag_note = result.get("flag_note", "")
                
                if message:
                    send_sms(client["phone"], message, client["id"])
                    db.mark_scheduled(client["id"], checkpoint)
                    
                    if flag:
                        db.set_flag(client["id"], flag.replace("FLAG:", "").lower(), flag_note)
                    
                    actions.append({
                        "client": client["name"],
                        "checkpoint": checkpoint,
                        "message": message,
                        "flag": flag
                    })
            except Exception as e:
                actions.append({
                    "client": client["name"],
                    "checkpoint": checkpoint,
                    "error": str(e)
                })
    
    return actions


def fetch_inbound_replies():
    """Poll Twilio for new inbound messages and process them with Claude. Returns new replies."""
    try:
        twilio = get_twilio_client()
        from_number = get_twilio_number()
    except Exception as e:
        return []
    
    new_replies = []
    clients = db.get_all_clients()
    
    # Build phone → client map
    phone_map = {c["phone"]: c for c in clients if c.get("status") == "active"}
    
    # Fetch recent inbound messages to our number
    try:
        messages = twilio.messages.list(to=from_number, limit=50)
    except:
        return []
    
    for msg in messages:
        from_phone = msg.from_
        client = phone_map.get(from_phone)
        if not client:
            continue
        
        # Check if we already have this message logged
        existing_sids = {m.get("sid") for m in client["conversations"]}
        if msg.sid in existing_sids:
            continue
        
        # New inbound message — log it
        db.add_message(client["id"], "inbound", msg.body, sid=msg.sid)
        
        # Generate Claude response
        try:
            result = claude_respond(client, msg.body)
            response_text = result.get("message", "")
            flag = result.get("flag")
            flag_note = result.get("flag_note", "")
            
            if response_text:
                send_sms(client["phone"], response_text, client["id"])
            
            if flag:
                db.set_flag(client["id"], flag.replace("FLAG:", "").lower(), flag_note)
            
            # Reload client to get updated conversations
            updated_client = db.get_client(client["id"])
            
            new_replies.append({
                "client_id": client["id"],
                "client_name": client["name"],
                "inbound": msg.body,
                "response": response_text,
                "flag": flag,
                "flag_note": flag_note
            })
        except Exception as e:
            new_replies.append({
                "client_id": client["id"],
                "client_name": client["name"],
                "inbound": msg.body,
                "error": str(e)
            })
    
    return new_replies
