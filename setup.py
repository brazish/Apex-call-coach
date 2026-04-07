"""
APEX Call Coach - Setup & Launcher
===================================
Double-click this file or right-click -> Open With -> Python

It will:
1. Install all required packages automatically
2. Launch the APEX Call Coach app in your browser
"""

import subprocess
import sys
import os
import time
import webbrowser

# ── Packages to install ───────────────────────────────────────────────────────
PACKAGES = [
    "streamlit",
    "anthropic",
    "pyaudio",
    "websocket-client",
    "python-dotenv",
    "deepgram-sdk",
    "websockets",
]

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def banner():
    print("=" * 50)
    print("   APEX Call Coach — Setup & Launcher")
    print("=" * 50)
    print()

clear()
banner()

# ── Install packages ──────────────────────────────────────────────────────────
print("Checking and installing dependencies...")
print()

for pkg in PACKAGES:
    print(f"  Installing {pkg}...", end=" ", flush=True)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", pkg, "-q"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print("✓")
        else:
            print(f"⚠ (may already be installed)")
    except Exception as e:
        print(f"✗ Error: {e}")

print()
print("All dependencies ready!")
print()
print("=" * 50)
print("  Launching APEX Call Coach...")
print("  Your browser will open automatically.")
print()
print("  To STOP the app, close this window.")
print("=" * 50)
print()

# ── Open browser after short delay ───────────────────────────────────────────
def open_browser():
    time.sleep(4)
    webbrowser.open("http://localhost:8501")

import threading
threading.Thread(target=open_browser, daemon=True).start()

# ── Launch Streamlit ──────────────────────────────────────────────────────────
script_dir = os.path.dirname(os.path.abspath(__file__))
app_path   = os.path.join(script_dir, "app.py")

if not os.path.exists(app_path):
    print("ERROR: app.py not found!")
    print(f"Make sure app.py is in the same folder as this file.")
    print(f"Expected location: {app_path}")
    input("\nPress Enter to exit...")
    sys.exit(1)

subprocess.run([
    sys.executable, "-m", "streamlit", "run", app_path
])

input("\nApp closed. Press Enter to exit...")
