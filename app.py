import streamlit as st
import datetime

# --- 1. THE COMPLETE REPOSITORY MEDICATION DATASET ---
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
st.title("🚑 Ambulance Med Check Dashboard")

# Safeguard runtime cache initialization
if "med_data" not in st.session_state:
    st.session_state["med_data"] = INITIAL_DATA

current_inventory = st.session_state["med_data"]

# --- 3. CONTROLS INTERFACE ---
st.sidebar.header("🛡️ Operations Hub")
user_role = st.sidebar.selectbox("Select Certification Level", ["EMT / Basic", "Paramedic"])
selected_rig = st.sidebar.radio("Active Ambulance Unit", ["Rig #356", "Rig #357"])

# Expiration Boundaries Setup
today = datetime.date.today()
fifteen_days_out = today + datetime.timedelta(days=15)
rig_meds = current_inventory[selected_rig]

# --- SECTION 1: METRICS & ALERTS ---
st.subheader("⚠️ Critical Discrepancy & Expiration Logs")

empty_meds = []
low_meds = []
expiring_meds = []
all_expiration_dates = []

for med in rig_meds:
    try:
        exp_date = datetime.datetime.strptime(med["expiry"], "%Y-%m-%d").date()
        all_expiration_dates.append(exp_date)
    except ValueError:
        continue
        
    if med["count"] == 0:
        empty_meds.append(med["name"])
    elif med["count"] == 1:
        low_meds.append(med["name"])
        
    if exp_date <= fifteen_days_out:
        expiring_meds.append(f"{med['name']} ({med['expiry']})")

earliest_expiry_date = min(all_expiration_dates) if all_expiration_dates else "N/A"

col1, col2, col3, col4 = st.columns(4)
col1.metric("Earliest System Expiration", str(earliest_expiry_date))
col2.error(f"🚨 Out of Stock ({len(empty_meds)})")
col3.warning(f"⚠️ Low Inventory ({len(low_meds)})")
col4.info(f"⏳ Expiring Soon ({len(expiring_meds)})")

if empty_meds:
    st.error(f"**CRITICAL - EMPTY:** {', '.join(empty_meds)}")
if low_meds:
    st.warning(f"**NOTICE - LOW STOCK (1 Left):** {', '.join(low_meds)}")
if expiring_meds:
    st.info(f"**NOTICE - EXPIRING < 15 DAYS:** {', '.join(expiring_meds)}")

st.divider()

# --- SECTION 2: LIVE MANAGEMENT MATRIX ---
st.subheader(f"📊 Active Operations Matrix — {selected_rig}")

for m in rig_meds:
    is_narc = m["name"] in NARCOTICS
    if is_narc and user_role == "EMT / Basic":
        continue  # Narcotic protection wall
        
    # Generate contextual color tags based on item status
    status_indicator = "🟢 OK"
    if m["count"] == 0:
        status_indicator = "🔴 EMPTY"
    elif m["count"] == 1:
        status_indicator = "🟡 LOW"

    expander_title = f"{status_indicator} | {m['name']} — Available: {m['count']} | Expiry: {m['expiry']}"
    if is_narc:
        expander_title = f"🔒 {expander_title} (Paramedic Only)"

    with st.expander(expander_title):
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("**Track Medication Consumption**")
