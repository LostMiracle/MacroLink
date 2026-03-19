import json, os
from flask import Flask, jsonify, send_from_directory, request  # type: ignore
from flask_cors import CORS # type: ignore
from pathlib import Path
from threading import Lock
profile_lock = Lock()
# Lock for thread-safe profile access
import requests # type: ignore
import urllib.parse

app = Flask(__name__, static_folder='dist', static_url_path='')
CORS(app)
app.url_map.strict_slashes = False


PROFILE_PATH = os.path.join(os.path.dirname(__file__), 'profiles.json')

# macroData.js = source of truth for macros (used by Vue frontend)

def load_profiles():
    if not os.path.exists(PROFILE_PATH):
        return {}
    with open(PROFILE_PATH, 'r') as f:
        return json.load(f)


def load_user_profiles(user):
    try:
        with open("profiles.json", "r") as f:
            data = json.load(f)
            return data.get(user, {})  # returns a dict of profiles
    except Exception as e:
        print("Failed to load profiles.json:", e)
        return {}


def save_profiles(data):
    with open(PROFILE_PATH, 'w') as f:
        json.dump(data, f, indent=2)

def normalize_name(name):
    return name.strip().lower()

@app.route('/static/manifest.json')
def manifest():
    return send_from_directory(app.static_folder, 'manifest.json', mimetype='application/manifest+json')

@app.route('/')
def index():
    return send_from_directory('dist', 'index.html')

@app.route('/dashboard')
def dashboard_view():
    return send_from_directory('dist', 'index.html')

@app.route('/settings')
def settings_view():
    return send_from_directory('dist', 'index.html')

# Old server-side dashboard route (deprecated)
# @app.route("/dashboard")
# def dashboard():
#     image_dir = Path(app.static_folder) / "images"
#     existing_images = [f.name for f in image_dir.glob("*.png")]
#     return render_template(
#         "dashboard.html",
#         static_macros=STATIC_MACROS,
#         dynamic_macros=DYNAMIC_MACROS,
#         normalized_macros=NORMALIZED_MACROS,
#         macro_images=MACRO_IMAGES,
#         macro_styles=MACRO_STYLES,
#         image_files=existing_images
#     )

PICO_IPS = {
    "green": "http://192.168.50.34:8888",
    "blue": "http://192.168.50.35:8888"
}

@app.route("/dashboard/status.json")
def combined_status():
    results = {}
    for pico_id, pico_url in PICO_IPS.items():
        try:
            r = requests.get(f"{pico_url}/system/status.json", timeout=2)
            results[pico_id] = r.json()
        except Exception as e:
            results[pico_id] = {"error": str(e)}
    return jsonify(results)

@app.route("/trigger/<macro>")
def trigger_macro(macro):
    selected_user = request.args.get("user", "user1")
    server_map = {
        "user1": "http://192.168.50.34:8888",
        "user2": "http://192.168.50.35:8888"
    }
    target_server = server_map.get(selected_user)

    if not target_server:
        return jsonify({"error": "Invalid user"}), 400
    
    print(f"Triggering macro '{macro}' for user '{selected_user}' → {target_server}")

    try:
        # Target server expects lowercase macro keys (e.g. cqc-20_breaching_hammer)
        macro_lower = macro.lower()
        # Macros can take 1–2s to execute (key hold + delay per input); short timeout caused
        # client to close the connection while Pico was still running, leading to crashes
        response = requests.get(f"{target_server}/{macro_lower}", timeout=5)
        response.raise_for_status()
        return jsonify({"status": "success", "macro": macro})
    except requests.exceptions.RequestException as e:
        print(f"Error triggering macro '{macro}': {e}")
        return jsonify({"status": "error", "macro": macro, "message": 
        str(e)}), 500
    
@app.route('/save_profile', methods=['POST'])
def save_profile():
    data = request.get_json()
    user = data.get('user')
    macros = data.get('macros')
    profile = normalize_name(data.get('profile', 'default'))  # allow profile name override

    if not user or not isinstance(macros, list):
        return jsonify({'error': 'Missing user or macros'}), 400

    with profile_lock:
        profiles = load_profiles()
        profiles.setdefault(user, {})[profile] = macros
        save_profiles(profiles)

    return jsonify({'status': 'saved', 'user': user, 'profile': profile})


@app.route('/all_profiles')
def all_profiles():
    try:
        with profile_lock:
            profiles = load_profiles()
            return jsonify(profiles)
    except Exception as e:
        print(f"[ERROR] all_profiles failed: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/list_profiles')
def list_profiles():
    user = request.args.get('user')
    if not user:
        return jsonify({'error': 'Missing user'}), 400
    try:
        with profile_lock:
            profiles = load_profiles()
            return jsonify({'profiles': list(profiles.get(user, {}).keys())})
    except Exception as e:
        print(f"[ERROR] list_profiles failed: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route("/get_profile")
def get_profile():
    try:
        user = request.args.get("user", "").strip()
        profile = request.args.get("profile", "").strip()

        # Decode + normalize
        profile = urllib.parse.unquote_plus(profile).lower()

        # Simulated: load your profiles (dict or db)
        all_profiles = load_user_profiles(user)  # returns dict like { "major defense": {...} }

        # Normalize keys
        normalized_profiles = {k.lower(): v for k, v in all_profiles.items()}
        data = normalized_profiles.get(profile)

        if not data:
            return jsonify({"error": "Profile not found"}), 404

        return jsonify({"macros": data})

    except Exception as e:
        print("get_profile error:", e)
        return jsonify({"error": str(e)}), 500


@app.route('/delete_profile', methods=['POST'])
def delete_profile():
    data = request.get_json()
    user = data.get('user')
    profile = normalize_name(data.get('profile'))

    if not user or not profile:
        return jsonify({'error': 'Missing user or profile'}), 400

    with profile_lock:
        profiles = load_profiles()
        if user in profiles and profile in profiles[user]:
            del profiles[user][profile]
            save_profiles(profiles)
            return jsonify({'status': 'deleted'})
        return jsonify({'error': 'Profile not found'}), 404
    
@app.route('/rename_profile', methods=['POST'])
def rename_profile():
    data = request.get_json()
    user = data.get('user')
    old_name = normalize_name(data.get('old_profile'))
    new_name = normalize_name(data.get('new_profile'))

    if not user or not old_name or not new_name:
        return jsonify({'error': 'Missing parameters'}), 400

    with profile_lock:
        profiles = load_profiles()
        user_profiles = profiles.get(user, {})
        if old_name not in user_profiles:
            return jsonify({'error': 'Old profile not found'}), 404
        if new_name in user_profiles:
            return jsonify({'error': 'New profile already exists'}), 400

        user_profiles[new_name] = user_profiles.pop(old_name)
        save_profiles(profiles)
        return jsonify({'status': 'renamed', 'from': old_name, 'to': new_name})
    
# @app.route('/macros.json')
# def serve_macros():
#     return send_from_directory("static/json", "macros.json")

# Catch-all for Vue Router (must be LAST route)
@app.route('/<path:path>')
def catch_all(path):
    print(f"[CATCH-ALL] Requested path: {path}")
    file_path = os.path.join('dist', path)
    print(f"[CATCH-ALL] Checking if exists: {file_path}")
    if os.path.exists(file_path):
        print(f"[CATCH-ALL] File exists, serving: {path}")
        return send_from_directory('dist', path)
    print(f"[CATCH-ALL] File not found, serving index.html")
    return send_from_directory('dist', 'index.html')
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888)