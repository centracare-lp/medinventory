import streamlit as st
import datetime
import json
import urllib.request
import base64

# --- 1. FULL COMPLEMENT INVENTORY MANIFEST ---
INITIAL_DATA = {
    "Rig #356": [
        {"id": "1", "name": "Adenosine", "count": 5, "expiry": "2027-05-12"},
        {"id": "2", "name": "Albuterol", "count": 2, "expiry": "2026-10-01"},
        {"id": "3", "name": "Amiodarone", "count": 3, "expiry": "2028-01-15"},
        {"id": "4", "name": "Aspirin", "count": 2, "expiry": "2026-12-31"},
        {"id": "5", "name": "Atropine", "count": 2, "expiry": "2027-05-12"},
        {"id": "6", "name": "Benadryl (IV)", "count": 1, "expiry": "2026-10-01"},
        {"id": "7", "name": "Benadryl (Oral)", "count": 2, "expiry": "2028-01-15"},
        {"id": "8", "name": "Calcium Chloride", "count": 3, "expiry": "2026-12-31"},
        {"id": "9", "name": "Calcium Gluconate", "count": 0, "expiry": "2027-05-12"},
        {"id": "10", "name": "Cardizem", "count": 1, "expiry": "2026-10-01"},
        {"id": "11", "name": "Dextrose (Oral)", "count": 2, "expiry": "2028-01-15"},
        {"id": "12", "name": "Dextrose (D10)", "count": 1, "expiry": "2026-12-31"},
        {"id": "13", "name": "Dextrose (D50)", "count": 1, "expiry": "2027-05-12"},
        {"id": "14", "name": "Diazepam (Valium)", "count": 2, "expiry": "2026-10-01"},
        {"id": "15", "name": "Dilaudid", "count": 1, "expiry": "2028-01-15"},
        {"id": "16", "name": "Droperidol", "count": 2, "expiry": "2026-12-31"},
        {"id": "17", "name": "DuoNeb", "count": 4, "expiry": "2027-05-12"},
        {"id": "18", "name": "Epi (IV) 1:10,000", "count": 2, "expiry": "2026-10-01"},
        {"id": "19", "name": "Epi (IM) 1:1,000", "count": 2, "expiry": "2028-01-15"},
        {"id": "20", "name": "Etomidate", "count": 8, "expiry": "2026-12-31"},
        {"id": "21", "name": "Fentanyl", "count": 4, "expiry": "2027-05-12"},
        {"id": "22", "name": "Glucagon", "count": 2, "expiry": "2026-10-01"},
        {"id": "23", "name": "Haldol", "count": 4, "expiry": "2028-01-15"},
        {"id": "24", "name": "Ketamine", "count": 2, "expiry": "2026-12-31"},
        {"id": "25", "name": "Labetalol", "count": 2, "expiry": "2027-05-12"},
        {"id": "26", "name": "Lidocaine", "count": 3, "expiry": "2026-10-01"},
        {"id": "27", "name": "Mag Sulfate", "count": 2, "expiry": "2028-01-15"},
        {"id": "28", "name": "Metoprolol", "count": 2, "expiry": "2026-12-31"},
        {"id": "29", "name": "Midazolam", "count": 2, "expiry": "2028-01-15"},
        {"id": "30", "name": "Narcan", "count": 2, "expiry": "2026-12-31"},
        {"id": "31", "name": "Nitro (Tabs)", "count": 2, "expiry": "2027-05-12"},
        {"id": "32", "name": "Nitro (IV)", "count": 2, "expiry": "2026-10-01"},
        {"id": "33", "name": "Propofol", "count": 1, "expiry": "2028-01-15"},
        {"id": "34", "name": "Racemic Epi", "count": 1, "expiry": "2026-12-31"},
        {"id": "35", "name": "Rocuronium", "count": 1, "expiry": "2027-05-12"},
        {"id": "36", "name": "Sodium Bicarbonate", "count": 2, "expiry": "2026-10-01"},
        {"id": "37", "name": "Succinylcholine", "count": 2, "expiry": "2028-01-15"},
        {"id": "38", "name": "Terbutaline", "count": 4, "expiry": "2026-12-31"},
        {"id": "39", "name": "Toradol", "count": 0, "expiry": "2027-05-12"},
        {"id": "40", "name": "Tetracaine (eye drop)", "count": 2, "expiry": "2026-10-01"},
        {"id": "41", "name": "Vecuronium", "count": 2, "expiry": "2028-01-15"},
        {"id": "42", "name": "Zofran", "count": 1, "expiry": "2026-12-31"}
    ],
    "Rig #357": [
        {"id": "1", "name": "Adenosine", "count": 5, "expiry": "2027-05-12"},
        {"id": "2", "name": "Albuterol", "count": 2, "expiry": "2026-10-01"},
        {"id": "3", "name": "Amiodarone", "count": 3, "expiry": "2028-01-15"},
        {"id": "4", "name": "Aspirin", "count": 2, "expiry": "2026-12-31"},
        {"id": "5", "name": "Atropine", "count": 2, "expiry": "2027-05-12"},
        {"id": "6", "name": "Benadryl (IV)", "count": 1, "expiry": "2026-10-01"},
        {"id": "7", "name": "Benadryl (Oral)", "count": 2, "expiry": "2028-01-15"},
        {"id": "8", "name": "Calcium Chloride", "count": 3, "expiry": "2026-12-31"},
        {"id": "9", "name": "Calcium Gluconate", "count": 0, "expiry": "2027-05-12"},
        {"id": "10", "name": "Cardizem", "count": 1, "expiry": "2026-10-01"},
        {"id": "11", "name": "Dextrose (Oral)", "count": 2, "expiry": "2028-01-15"},
        {"id": "12", "name": "Dextrose (D10)", "count": 1, "expiry": "2026-12-31"},
        {"id": "13", "name": "Dextrose (D50)", "count": 1, "expiry": "2027-05-12"},
        {"id": "14", "name": "Diazepam (Valium)", "count": 2, "expiry": "2026-10-01"},
        {"id": "15", "name": "Dilaudid", "count": 1, "expiry": "2028-01-15"},
        {"id": "16", "name": "Droperidol", "count": 2, "expiry": "2026-12-31"},
        {"id": "17", "name": "DuoNeb", "count": 4, "expiry": "2027-05-12"},
        {"id": "18", "name": "Epi (IV) 1:10,000", "count": 2, "expiry": "2026-10-01"},
        {"id": "19", "name": "Epi (IM) 1:1,000", "count": 2, "expiry": "2028-01-15"},
        {"id": "20", "name": "Etomidate", "count": 8, "expiry": "2026-12-31"},
        {"id": "21", "name": "Fentanyl", "count": 4, "expiry": "2027-05-12"},
        {"id": "22", "name": "Glucagon", "count": 2, "expiry": "2026-10-01"},
        {"id": "23", "name": "Haldol", "count": 4, "expiry": "2028-01-15"},
        {"id": "24", "name": "Ketamine", "count": 2, "expiry": "2026-12-31"},
        {"id": "25", "name": "Labetalol", "count": 2, "expiry": "2027-05-12"},
        {"id": "26", "name": "Lidocaine", "count": 3, "expiry": "2026-10-01"},
        {"id": "27", "name": "Mag Sulfate", "count": 2, "expiry": "2028-01-15"},
        {"id": "28", "name": "Metoprolol", "count": 2, "expiry": "2026-12-31"},
        {"id": "29", "name": "Midazolam", "count": 2, "expiry": "2028-01-15"},
        {"id": "30", "name": "Narcan", "count": 2, "expiry": "2026-12-31"},
        {"id": "31", "name": "Nitro (Tabs)", "count": 2, "expiry": "2027-05-12"},
        {"id": "32", "name": "Nitro (IV)", "count": 2, "expiry": "2026-10-01"},
        {"id": "33", "name": "Propofol", "count": 1, "expiry": "2028-01-15"},
        {"id": "34", "name": "Racemic Epi", "count": 1, "expiry": "2026-12-31"},
        {"id": "35", "name": "Rocuronium", "count": 1, "expiry": "2027-05-12"},
        {"id": "36", "name": "Sodium Bicarbonate", "count": 2, "expiry": "2026-10-01"},
        {"id": "37", "name": "Succinylcholine", "count": 2, "expiry": "2028-01-15"},
        {"id": "38", "name": "Terbutaline", "count": 4, "expiry": "2026-12-31"},
        {"id": "39", "name": "Toradol", "count": 0, "expiry": "2027-05-12"},
        {"id": "40", "name": "Tetracaine (eye drop)", "count": 2, "expiry": "2026-10-01"},
        {"id": "41", "name": "Vecuronium", "count": 2, "expiry": "2028-01-15"},
        {"id": "42", "name": "Zofran", "count": 1, "expiry": "2026-12-31"}
    ]
}

NARCOTICS = ["Diazepam (Valium)", "Dilaudid", "Fentanyl", "Ketamine", "Midazolam", "Propofol"]

# --- 2. LAYOUT INITIALIZATION ---
st.set_page_config(page_title="Ambulance Med Check", layout="wide")

if "med_data" not in st.session_state:
    st.session_state["med_data"] = json.loads(json.dumps(INITIAL_DATA))

# --- 3. ZERO-DEPENDENCY NATIVE STORAGE SYNC ---
def load_synchronized_data():
    if st.session_state.get("data_synced_once"):
        return st.session_state["med_data"]
        
    if "GITHUB_TOKEN" in st.secrets and "GITHUB_REPO" in st.secrets:
        try:
            token = st.secrets["GITHUB_TOKEN"]
            repo = st.secrets["GITHUB_REPO"]
            f_path = st.secrets.get("GITHUB_FILE_PATH", "med_data.json")
            url = f"https://github.com{repo}/contents/{f_path}"
            
            req = urllib.request.Request(url)
            req.add_header("Authorization", f"token {token}")
            req.add_header("Accept", "application/vnd.github.v3+json")
            
            with urllib.request.urlopen(req, timeout=5) as response:
                res_data = json.loads(response.read().decode())
                content_bytes = base64.b64decode(res_data["content"])
                st.session_state["med_data"] = json.loads(content_bytes.decode())
                st.session_state["github_sha"] = res_data["sha"]
        except Exception:
            pass # Gracefully run from inline template if repo link stalls
            
    st.session_state["data_synced_once"] = True
    return st.session_state["med_data"]

def save_synchronized_data(updated_data):
    st.session_state["med_data"] = updated_data
    if "GITHUB_TOKEN" in st.secrets and "GITHUB_REPO" in st.secrets:
        try:
            token = st.secrets["GITHUB_TOKEN"]
            repo = st.secrets["GITHUB_REPO"]
            f_path = st.secrets.get("GITHUB_FILE_PATH", "med_data.json")
            url = f"https://github.com{repo}/contents/{f_path}"
            
            if "github_sha" not in st.session_state:
                try:
                    req_get = urllib.request.Request(url)
                    req_get.add_header("Authorization", f"token {token}")
                    with urllib.request.urlopen(req_get, timeout=3) as r:
                        st.session_state["github_sha"] = json.loads(r.read().decode())["sha"]
                except:
                    st.session_state["github_sha"] = ""

            json_bytes = json.dumps(updated_data, indent=4).encode('utf-8')
            encoded_content = base64.b64encode(json_bytes).decode('utf-8')
            
            payload = {
                "message": "EMS Logistics Update",
                "content": encoded_content
            }
            if st.session_state.get("github_sha"):
                payload["sha"] = st.session_state["github_sha"]
                
            req_put = urllib.request.Request(url, method="PUT", data=json.dumps(payload).encode('utf-8'))
