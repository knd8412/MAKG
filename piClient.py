import requests

# When the physical button is pressed on the Pi 5:
def on_button_press():
    response = requests.post("http://45.76.137.251/api/button/toggle")
    print(response.json())

# When the AI Camera detects bad posture:
def on_bad_posture():
    requests.post("http://45.76.137.251/api/alert/bad-posture", params={"session_id": "active_id_here"})