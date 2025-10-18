import json, os
from flask import Flask, render_template, jsonify, send_from_directory, request  # type: ignore
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

# macroData.js = source of truth for macros
# Update app.py from macroData.js whenever new macros are added

STATIC_MACROS = {
    "Reinforce": "Reinforce",
    "Resupply": "Resupply"
}

DYNAMIC_MACROS = {
    # Orbital Strikes
    "Orbital_Precision_Strike": "Orbital Precision Strike",
    "Orbital_Gatling_Barrage": "Orbital Gatling Barrage",
    "Orbital_Airburst_Strike": "Orbital Airburst Strike",
    "Orbital_Napalm_Barrage": "Orbital Napalm Barrage",
    "Orbital_120MM_HE_Barrage": "Orbital 120MM HE Barrage",
    "Orbital_Walking_Barrage": "Orbital Walking Barrage",
    "Orbital_380MM_HE_Barrage": "Orbital 380MM HE Barrage",
    "Orbital_Railcannon_Strike": "Orbital Railcannon Strike",
    "Orbital_Laser": "Orbital Laser",
    "Orbital_EMS_Strike": "Orbital EMS Strike",
    "Orbital_Gas_Strike": "Orbital Gas Strike",
    "Orbital_Smoke_Strike": "Orbital Smoke Strike",
    # Eagle Strikes
    "Eagle_500KG_Bomb": "Eagle 500KG Bomb",
    "Eagle_Strafing_Run": "Eagle Strafing Run",
    "Eagle_110MM_Rocket_Pods": "Eagle 110MM Rocket Pods",
    "Eagle_Airstrike": "Eagle Airstrike",
    "Eagle_Cluster_Bomb": "Eagle Cluster Bomb",
    "Eagle_Napalm_Airstrike": "Eagle Napalm Airstrike",
    "Eagle_Smoke_Strike": "Eagle Smoke Strike",
    # Support Weapons
    "CQC-1_One_True_Flag": "CQC-1 One True Flag",
    "MG-43_Machine_Gun": "MG-43 Machine Gun",
    "M-105_Stalwart": "M-105 Stalwart",
    "MG-206_Heavy_Machine_Gun": "MG-206 Heavy Machine Gun",
    "RS-422_Railgun": "RS-422 Railgun",
    "APW-1_Anti-Materiel_Rifle": "APW-1 Anti-Materiel Rifle",
    "GL-21_Grenade_Launcher": "GL-21 Grenade Launcher",
    "GL-52_De-Escalator": "GL-52 De-Escalator",
    "TX-14_Sterilizer": "TX-14 Sterilizer",
    "FLAM-40_Flamethrower": "FLAM-40 Flamethrower",
    "LAS-98_Laser_Cannon": "LAS-98 Laser Cannon",
    "LAS-99_Quasar_Cannon": "LAS-99 Quasar Cannon",
    "PLAS-45_Epoch": "PLAS-45 Epoch",
    "ARC-3_Arc_Thrower": "ARC-3 Arc Thrower",
    "MLS-4X_Commando": "MLS-4X Commando",
    "S-11_Speargun": "S-11 Speargun",
    "EAT-17_Expendable_Anti-Tank": "EAT-17 Expendable Anti-Tank",
    "EAT-700_Expendable_Napalm": "EAT-700 Expendable Napalm",
    "AC-8_Autocannon": "AC-8 Autocannon",
    "RL-77_Airburst_Rocket_Launcher": "RL-77 Airburst Rocket Launcher",
    "FAF-14_Spear_Launcher": "FAF-14 Spear Launcher",
    "StA-X3_W.A.S.P._Launcher": "StA-X3 W.A.S.P. Launcher",
    "GR-8_Recoilless_Rifle": "GR-8 Recoilless Rifle",
    "MS-11_Solo_Silo": "MS-11 Solo Silo",
    # Support Equipment
    "LIFT-860_Hover_Pack": "LIFT-860 Hover Pack",
    "LIFT-850_Jump_Pack": "LIFT-850 Jump Pack",
    "LIFT-182_Warp_Pack": "LIFT-182 Warp Pack",
    "SH-32_Shield_Generator_Pack": "SH-32 Shield Generator Pack",
    "SH-51_Directional_Shield_Backpack": "SH-51 Directional Shield Backpack",
    "SH-20_Ballistic_Shield_Backpack": "SH-20 Ballistic Shield Backpack",
    "B-1_Supply_Pack": "B-1 Supply Pack",
    "B-100_Portable_Hellbomb": "B-100 Portable Hellbomb",
    "AX-AR-23_Guard_Dog": "AX/AR-23 'Guard Dog'",
    "AX-LAS-5_Guard_Dog_Rover": "AX/LAS-5 'Guard Dog' Rover",
    "AX-TX-13_Guard_Dog_Dog_Breath": "AX/TX-13 'Guard Dog' Dog Breath",
    "AX_ARC-3_Guard_Dog_K9": "AX/ARC-3 'Guard Dog' K9",
    "M-102_Fast_Recon_Vehicle": "M-102 Fast Recon Vehicle",
    "EXO-49_Emancipator_Exosuit": "EXO-49 Emancipator Exosuit",
    "EXO-45_Patriot_Exosuit": "EXO-45 Patriot Exosuit",
    # Sentries and Emplacements
    "A-G-16_Gatling_Sentry": "A/G-16 Gatling Sentry",
    "A-MG-43_Machine_Gun_Sentry": "A/MG-43 Machine Gun Sentry",
    "E-FLAM-40_Flame_Sentry": "E/FLAM-40 Flame Sentry",
    "A-MLS-4X_Rocket_Sentry": "A/MLS-4X Rocket Sentry",
    "A-LAS-98_Laser_Sentry": "A/LAS-98 Laser Sentry",
    "A-AC-8_Autocannon_Sentry": "A/AC-8 Autocannon Sentry",
    "A-M-23_EMS_Mortar_Sentry": "A/M-23 EMS Mortar Sentry",
    "A-M-12_Mortar_Sentry": "A/M-12 Mortar Sentry",
    "FX-12_Shield_Generator_Relay": "FX-12 Shield Generator Relay",
    "E-GL-21_Grenadier_Battlement": "E/GL-21 Grenadier Battlement",
    "E-AT-12_Anti-Tank_Emplacement": "E/AT-12 Anti-Tank Emplacement",
    "E-MG-101_HMG_Emplacement": "E/MG-101 HMG Emplacement",
    "A-ARC-3_Tesla_Tower": "A/ARC-3 Tesla Tower",
    "MD-17_Anti-Tank_Mines": "MD-17 Anti-Tank Mines",
    "MD-8_Gas_Mines": "MD-8 Gas Mines",
    "MD-6_Anti-Personnel_Minefield": "MD-6 Anti-Personnel Minefield",
    "MD-14_Incendiary_Mines": "MD-14 Incendiary Mines",
    # General Actions
    "SOS_Beacon": "SOS Beacon",
    "NUX-223_Hellbomb": "NUX-223 Hellbomb",
    "SSSD_Delivery": "SSSD Delivery",
    "Seismic_Probe": "Seismic Probe",
    "Upload_Data": "Upload Data",
    "Eagle_Rearm": "Eagle Rearm",
    "Hive_Breaker_Drill": "Hive Breaker Drill",
    "Prospecting_Drill": "Prospecting Drill",
    "Super_Earth_Flag": "Super Earth Flag",
    "SEAF_Artillery": "SEAF Artillery"
}

MACRO_IMAGES = {
    # Orbital Strikes
    "Orbital_Precision_Strike": "Orbital_Precision_Strike.png",
    "Orbital_Gatling_Barrage": "Orbital_Gatling_Barrage.png",
    "Orbital_Airburst_Strike": "Orbital_Airburst_Strike.png",
    "Orbital_Napalm_Barrage": "Orbital_Napalm_Barrage.png",
    "Orbital_120MM_HE_Barrage": "Orbital_120MM_HE_Barrage.png",
    "Orbital_Walking_Barrage": "Orbital_Walking_Barrage.png",
    "Orbital_380MM_HE_Barrage": "Orbital_380MM_HE_Barrage.png",
    "Orbital_Railcannon_Strike": "Orbital_Railcannon_Strike.png",
    "Orbital_Laser": "Orbital_Laser.png",
    "Orbital_EMS_Strike": "Orbital_EMS_Strike.png",
    "Orbital_Gas_Strike": "Orbital_Gas_Strike.png",
    "Orbital_Smoke_Strike": "Orbital_Smoke_Strike.png",
    # Eagle Strikes
    "Eagle_500KG_Bomb": "Eagle_500KG_Bomb.png",
    "Eagle_Strafing_Run": "Eagle_Strafing_Run.png",
    "Eagle_110MM_Rocket_Pods": "Eagle_110MM_Rocket_Pods.png",
    "Eagle_Airstrike": "Eagle_Airstrike.png",
    "Eagle_Cluster_Bomb": "Eagle_Cluster_Bomb.png",
    "Eagle_Napalm_Airstrike": "Eagle_Napalm_Airstrike.png",
    "Eagle_Smoke_Strike": "Eagle_Smoke_Strike.png",
    # Support Weapons
    "CQC-1_One_True_Flag": "CQC-1_One_True_Flag.png",
    "MG-43_Machine_Gun": "MG-43_Machine_Gun.png",
    "M-105_Stalwart": "M-105_Stalwart.png",
    "MG-206_Heavy_Machine_Gun": "MG-206_Heavy_Machine_Gun.png",
    "RS-422_Railgun": "RS-422_Railgun.png",
    "APW-1_Anti-Materiel_Rifle": "APW-1_Anti-Materiel_Rifle.png",
    "GL-21_Grenade_Launcher": "GL-21_Grenade_Launcher.png",
    "TX-14_Sterilizer": "TX-14_Sterilizer.png",
    "FLAM-40_Flamethrower": "FLAM-40_Flamethrower.png",
    "LAS-98_Laser_Cannon": "LAS-98_Laser_Cannon.png",
    "LAS-99_Quasar_Cannon": "LAS-99_Quasar_Cannon.png",
    "ARC-3_Arc_Thrower": "ARC-3_Arc_Thrower.png",
    "MLS-4X_Commando": "MLS-4X_Commando.png",
    "EAT-17_Expendable_Anti-Tank": "EAT-17_Expendable_Anti-Tank.png",
    "AC-8_Autocannon": "AC-8_Autocannon.png",
    "RL-77_Airburst_Rocket_Launcher": "RL-77_Airburst_Rocket_Launcher.png",
    "FAF-14_Spear_Launcher": "FAF-14_Spear_Launcher.png",
    "StA-X3_W.A.S.P._Launcher": "StA-X3_W.A.S.P._Launcher.png",
    "GR-8_Recoilless_Rifle": "GR-8_Recoilless_Rifle.png",
    "GL-52_De-Escalator": "GL-52_De-Escalator.png",
    # Support Equipment
    "SH-32_Shield_Generator_Pack": "SH-32_Shield_Generator_Pack.png",
    "SH-51_Directional_Shield_Backpack": "SH-51_Directional_Shield_Backpack.png",
    "SH-20_Ballistic_Shield_Backpack": "SH-20_Ballistic_Shield_Backpack.png",
    "LIFT-860_Hover_Pack": "LIFT-860_Hover_Pack.png",
    "B-1_Supply_Pack": "B-1_Supply_Pack.png",
    "B-100_Portable_Hellbomb": "B-100_Portable_Hellbomb.png",
    "LIFT-850_Jump_Pack": "LIFT-850_Jump_Pack.png",
    "AX-AR-23_Guard_Dog": "AX_AR-23_Guard_Dog.png",
    "AX-LAS-5_Guard_Dog_Rover": "AX_LAS-5_Guard_Dog_Rover.png",
    "AX-TX-13_Guard_Dog_Dog_Breath": "AX_TX-13_Guard_Dog_Dog_Breath.png",
    "M-102_Fast_Recon_Vehicle": "M-102_Fast_Recon_Vehicle.png",
    "EXO-49_Emancipator_Exosuit": "EXO-49_Emancipator_Exosuit.png",
    "EXO-45_Patriot_Exosuit": "EXO-45_Patriot_Exosuit.png",
    "AX_ARC-3_Guard_Dog_K9": "AX_ARC-3_Guard_Dog_K9.png",
    # Sentries and Emplacements
    "A-G-16_Gatling_Sentry": "A_G-16_Gatling_Sentry.png",
    "A-MG-43_Machine_Gun_Sentry": "A_MG-43_Machine_Gun_Sentry.png",
    "E-FLAM-40_Flame_Sentry": "E_FLAM-40_Flame_Sentry.png",
    "A-MLS-4X_Rocket_Sentry": "A_MLS-4X_Rocket_Sentry.png",
    "A-AC-8_Autocannon_Sentry": "A_AC-8_Autocannon_Sentry.png",
    "A-M-23_EMS_Mortar_Sentry": "A_M-23_EMS_Mortar_Sentry.png",
    "A-M-12_Mortar_Sentry": "A_M-12_Mortar_Sentry.png",
    "FX-12_Shield_Generator_Relay": "FX-12_Shield_Generator_Relay.png",
    "E-GL-21_Grenadier_Battlement": "E_GL-21_Grenadier_Battlement.png",
    "E-AT-12_Anti-Tank_Emplacement": "E_AT-12_Anti-Tank_Emplacement.png",
    "E-MG-101_HMG_Emplacement": "E_MG-101_HMG_Emplacement.png",
    "A-ARC-3_Tesla_Tower": "A_ARC-3_Tesla_Tower.png",
    "MD-17_Anti-Tank_Mines": "MD-17_Anti-Tank_Mines.png",
    "MD-8_Gas_Mines": "MD-8_Gas_Mines.png",
    "MD-6_Anti-Personnel_Minefield": "MD-6_Anti-Personnel_Minefield.png",
    "MD-14_Incendiary_Mines": "MD-14_Incendiary_Mines.png",
    "NUX-223_Hellbomb": "NUX-223_Hellbomb.png",
    # General Actions
    "SSSD_Delivery": "SSSD_Delivery.png",
    "Seismic_Probe": "Seismic_Probe.png",
    "Upload_Data": "Upload_Data.png",
    "Eagle_Rearm": "Eagle_Rearm.png",
    "Reinforce": "redeploy.png",
    "Resupply": "resupply.png",
    "SOS_Beacon": "sos.png",
    "Hive_Breaker_Drill": "Hive_Breaker_Drill.png",
    "Prospecting_Drill": "Prospecting_Drill.png",
    "Super_Earth_Flag": "Super_Earth_Flag.png",
    "SEAF_Artillery": "SEAF_Artillery.png",
    # Control Group
    "PLAS-45_Epoch": "Epoch.png",
    "LIFT-182_Warp_Pack": "Warp_Pack.png",
    "A-LAS-98_Laser_Sentry": "Laser_Sentry.png",
    # Dust Devils
    "S-11_Speargun": "Speargun.png",
    "EAT-700_Expendable_Napalm": "Expendable_Napalm.png",
    "MS-11_Solo_Silo": "Solo_Silo.png"
}

MACRO_STYLES = {
    "Orbital_Precision_Strike": {"border": "red"},
    "Orbital_Gatling_Barrage": {"border": "red"},
    "Orbital_Airburst_Strike": {"border": "red"},
    "Orbital_Napalm_Barrage": {"border": "red"},
    "Orbital_120MM_HE_Barrage": {"border": "red"},
    "Orbital_Walking_Barrage": {"border": "red"},
    "Orbital_380MM_HE_Barrage": {"border": "red"},
    "Orbital_Railcannon_Strike": {"border": "red"},
    "Orbital_Laser": {"border": "red"},
    "Orbital_EMS_Strike": {"border": "red"},
    "Orbital_Gas_Strike": {"border": "red"},
    "Orbital_Smoke_Strike": {"border": "red"},
    "Eagle_500KG_Bomb": {"border": "red"},
    "Eagle_Strafing_Run": {"border": "red"},
    "Eagle_110MM_Rocket_Pods": {"border": "red"},
    "Eagle_Airstrike": {"border": "red"},
    "Eagle_Cluster_Bomb": {"border": "red"},
    "Eagle_Napalm_Airstrike": {"border": "red"},
    "Eagle_Smoke_Strike": {"border": "red"},
    "CQC-1_One_True_Flag": {"border": "blue"},
    "MG-43_Machine_Gun": {"border": "blue"},
    "M-105_Stalwart": {"border": "blue"},
    "MG-206_Heavy_Machine_Gun": {"border": "blue"},
    "RS-422_Railgun": {"border": "blue"},
    "APW-1_Anti-Materiel_Rifle": {"border": "blue"},
    "GL-21_Grenade_Launcher": {"border": "blue"},
    "TX-14_Sterilizer": {"border": "blue"},
    "FLAM-40_Flamethrower": {"border": "blue"},
    "LAS-98_Laser_Cannon": {"border": "blue"},
    "LAS-99_Quasar_Cannon": {"border": "blue"},
    "ARC-3_Arc_Thrower": {"border": "blue"},
    "MLS-4X_Commando": {"border": "blue"},
    "EAT-17_Expendable_Anti-Tank": {"border": "blue"},
    "AC-8_Autocannon": {"border": "blue"},
    "RL-77_Airburst_Rocket_Launcher": {"border": "blue"},
    "FAF-14_Spear_Launcher": {"border": "blue"},
    "StA-X3_W.A.S.P._Launcher": {"border": "blue"},
    "GR-8_Recoilless_Rifle": {"border": "blue"},
    "SH-32_Shield_Generator_Pack": {"border": "blue"},
    "SH-51_Directional_Shield_Backpack": {"border": "blue"},
    "SH-20_Ballistic_Shield_Backpack": {"border": "blue"},
    "LIFT-860_Hover_Pack": {"border": "blue"},
    "B-1_Supply_Pack": {"border": "blue"},
    "B-100_Portable_Hellbomb": {"border": "blue"},
    "LIFT-850_Jump_Pack": {"border": "blue"},
    "AX-AR-23_Guard_Dog": {"border": "blue"},
    "AX-LAS-5_Guard_Dog_Rover": {"border": "blue"},
    "AX-TX-13_Guard_Dog_Dog_Breath": {"border": "blue"},
    "M-102_Fast_Recon_Vehicle": {"border": "blue"},
    "EXO-49_Emancipator_Exosuit": {"border": "blue"},
    "EXO-45_Patriot_Exosuit": {"border": "blue"},
    "A-G-16_Gatling_Sentry": {"border": "green"},
    "A-MG-43_Machine_Gun_Sentry": {"border": "green"},
    "E-FLAM-40_Flame_Sentry": {"border": "green"},
    "A-MLS-4X_Rocket_Sentry": {"border": "green"},
    "A-AC-8_Autocannon_Sentry": {"border": "green"},
    "A-M-23_EMS_Mortar_Sentry": {"border": "green"},
    "A-M-12_Mortar_Sentry": {"border": "green"},
    "FX-12_Shield_Generator_Relay": {"border": "green"},
    "E-GL-21_Grenadier_Battlement": {"border": "green"},
    "E-AT-12_Anti-Tank_Emplacement": {"border": "green"},
    "E-MG-101_HMG_Emplacement": {"border": "green"},
    "A-ARC-3_Tesla_Tower": {"border": "green"},
    "MD-17_Anti-Tank_Mines": {"border": "green"},
    "MD-8_Gas_Mines": {"border": "green"},
    "MD-6_Anti-Personnel_Minefield": {"border": "green"},
    "MD-14_Incendiary_Mines": {"border": "green"},
    "Reinforce": {"border": "yellow"},
    "SOS_Beacon": {"border": "yellow"},
    "Resupply": {"border": "yellow"},
    "NUX-223_Hellbomb": {"border": "yellow"},
    "SSSD_Delivery": {"border": "yellow"},
    "Seismic_Probe": {"border": "yellow"},
    "Upload_Data": {"border": "yellow"},
    "Eagle_Rearm": {"border": "yellow"},
    "SEAF_Artillery": {"border": "yellow"},
    "GL-52_De-Escalator": {"border": "blue"},
    "AX_ARC-3_Guard_Dog_K9": {"border": "blue"},
    "Hive_Breaker_Drill": {"border": "yellow"},
    "Prospecting_Drill": {"border": "yellow"},
    "Super_Earth_Flag": {"border": "yellow"},
    # Control Group
    "PLAS-45_Epoch": {"border": "blue"},
    "LIFT-182_Warp_Pack": {"border": "blue"},
    "A-LAS-98_Laser_Sentry": {"border": "green"},
    # Dust Devils
    "S-11_Speargun": {"border": "blue"},
    "EAT-700_Expendable_Napalm": {"border": "blue"},
    "MS-11_Solo_Silo": {"border": "blue"}
}

# Normalized macro names (lowercase key → readable value)
NORMALIZED_MACROS = {k.lower(): v for k, v in {**DYNAMIC_MACROS, **STATIC_MACROS}.items()}

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
        response = requests.get(f"{target_server}/{macro}", timeout=1)
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