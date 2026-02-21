import requests

API_URL = "http://your-vultr-ip-address"
current_session = None

def on_off_button_pressed():
    global current_session
    # This hits your FastAPI toggle endpoint
    response = requests.post(f"{API_URL}/api/button/toggle").json()
    
    if response["status"] == "started":
        current_session = response["session_id"]
        print(f"Session Started: {current_session}")
    else:
        print(f"Session Stopped. Studied for {response['study_time_minutes']} mins.")
        current_session = None

# If camera detects slouching:
def report_slouch():
    if current_session:
        requests.post(f"{API_URL}/api/alert/bad-posture", 
                      json={"session_id": current_session})