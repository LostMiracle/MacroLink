from flask import Flask, render_template, redirect, url_for
import requests

app = Flask(__name__)

# Replace this with your actual Pico W IP
PICO_IP = "http://192.168.50.35"

# Define your macros
MACROS = {
    "Reinforce": "redeploy",
    "Resupply": "resupply",
    "SOS Beacon": "sos"
}

@app.route("/")
def index():
    return render_template("index.html", macros=MACROS)

@app.route("/trigger/<macro>")
def trigger_macro(macro):
    try:
        response = requests.get(f"{PICO_IP}/{macro}", timeout=1)
        print(f"Triggered: {macro} → {response.status_code}")
    except requests.RequestException as e:
        print(f"Error triggering {macro}: {e}")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888)