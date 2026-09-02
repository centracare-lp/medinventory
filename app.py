import streamlit as st
import datetime
import json

# --- 1. THE COMPLETE AMBULANCE INVENTORY MANIFEST ---
INITIAL_DATA = {
    "Rig #356": [
        {"name": "Adenosine", "count": 5, "expiry": "2027-05-12"},
        {"name": "Albuterol", "count": 2, "expiry": "2026-10-01"},
        {"name": "Amiodarone", "count": 3, "expiry": "2028-01-15"},
        {"name": "Aspirin", "count": 2, "expiry": "2026-12-31"},
        {"name": "Atropine", "count": 2, "expiry": "2027-05-12"},
        {"name": "Benadryl (IV)", "count": 1, "expiry": "2026-10-01"},
        {"name": "Benadryl (Oral)", "count": 2, "expiry": "2028-01-15"},
        {"name": "Calcium Chloride", "count": 3, "expiry": "2026-12-31"},
        {"name": "Calcium Gluconate", "count": 0, "expiry": "2027-05-12"},
        {"name": "Cardizem", "count": 1, "expiry": "2026-10-01"},
        {"name": "Dextrose (Oral)", "count": 2, "expiry": "2028-01-15"},
        {"name": "Dextrose (D10)", "count": 1, "expiry": "2026-12-31"},
        {"name": "Dextrose (D50)", "count": 1, "expiry": "2027-05-12"},
        {"name": "Diazepam (Valium)", "count": 2, "expiry": "2026-10-01"},
        {"name": "Dilaudid", "count": 1, "expiry": "2028-01-15"},
        {"name": "Droperidol", "count": 2, "expiry": "2026-12-31"},
        {"name": "DuoNeb", "count": 4, "expiry": "2027-05-12"},
        {"name": "Epi (IV) 1:10,000", "count": 2, "expiry": "2026-10-01"},
        {"name": "Epi (IM) 1:1,000", "count": 2, "expiry": "2028-01-15"},
        {"name": "Etomidate", "count": 8, "expiry": "2026-12-31"},
        {"name": "Fentanyl", "count": 4, "expiry": "2027-05-12"},
        {"name": "Glucagon", "count": 2, "expiry": "2026-10-01"},
        {"name": "Haldol", "count": 4, "expiry": "2028-01-15"},
        {"name": "Ketamine", "count": 2, "expiry": "2026-12-31"},
        {"name": "Labetalol", "count": 2, "expiry": "2027-05-12"},
        {"name": "Lidocaine", "count": 3, "expiry": "2026-10-01"},
        {"name": "Mag Sulfate", "count": 2, "expiry": "2028-01-15"},
        {"name": "Metoprolol", "count": 2, "expiry": "2026-12-31"},
        {"id": "29", "name": "Midazolam", "count": 2, "expiry": "2028-01-15"},
        {"name": "Narcan", "count": 2, "expiry": "2026-12-31"},
        {"name": "Nitro (Tabs)", "count": 2, "expiry": "2027-05-12"},
        {"name": "Nitro (IV)", "count": 2, "expiry": "2026-10-01"},
        {"name": "Propofol", "count": 1, "expiry": "2028-01-15"},
        {"name": "Racemic Epi", "count": 1, "expiry": "2026-12-31"},
        {"name": "Rocuronium", "count": 1, "expiry": "2027-05-12"},
        {"name": "Sodium Bicarbonate", "count": 2, "expiry": "2026-10-01"},
        {"name": "Succinylcholine", "count": 2, "expiry": "2028-01-15"},
        {"name": "Terbutaline", "count": 4, "expiry": "2026-12-31"},
        {"name": "Toradol", "count": 0, "expiry": "2027-05-12"},
        {"name": "Tetracaine (eye drop)", "count": 2, "expiry": "2026-10-01"},
        {"name": "Vecuronium", "count": 2, "expiry": "2028-01-15"},
        {"name": "Zofran", "count": 1, "expiry": "2026-12-31"}
    ],
    "Rig #357": [
        {"name": "Adenosine", "count": 5, "expiry": "2027-05-12"},
        {"name": "Albuterol", "count": 2, "expiry": "2026-10-01"},
        {"name": "Amiodarone", "count": 3, "expiry": "2028-01-15"},
        {"name": "Aspirin", "count": 2, "expiry": "2026-12-31"},
        {"name": "Atropine", "count": 2, "expiry": "2027-05-12"},
        {"name": "Benadryl (IV)", "count": 1, "expiry": "2026-10-01"},
        {"name": "Benadryl (Oral)", "count": 2, "expiry": "2028-01-15"},
        {"name": "Calcium Chloride", "count": 3, "expiry": "2026-12-31"},
        {"name": "Calcium Gluconate", "count": 0, "expiry": "2027-05-12"},
        {"name": "Cardizem", "count": 1, "expiry": "2026-10-01"},
        {"name": "Dextrose (Oral)", "count": 2, "expiry": "2028-01-15"},
        {"name": "Dextrose (D10)", "count": 1, "expiry": "2026-12-31"},
        {"name": "Dextrose (D50)", "count": 1, "expiry": "2027-05-12"},
        {"name": "Diazepam (Valium)", "count": 2, "expiry": "2026-10-01"},
        {"name": "Dilaudid", "count": 1, "expiry": "2028-01-15"},
        {"name": "Droperidol", "count": 2, "expiry": "2026-12-31"},
        {"name": "DuoNeb", "count": 4, "expiry": "2027-05-12"},
        {"name": "Epi (IV) 1:10,000", "count": 2, "expiry": "2026-10-01"},
        {"name": "Epi (IM) 1:1,000", "count": 2, "expiry": "2028-01-15"},
        {"name": "Etomidate", "count": 8, "expiry": "2026-12-31"},
        {"name": "Fentanyl", "count": 4, "expiry": "2027-05-12"},
        {"name": "Glucagon", "count": 2, "expiry": "2026-10-01"},
        {"name": "Haldol", "count": 4, "expiry": "2028-01-15"},
        {"name": "Ketamine", "count": 2, "expiry": "2026-12-31"},
        {"name": "Labetalol", "count": 2, "expiry": "2027-05-12"},
        {"name": "Lidocaine", "count": 3, "expiry": "2026-10-01"},
        {"name": "Mag Sulfate", "count": 2, "expiry": "2028-01-15"},
        {"name": "Metoprolol", "count": 2, "expiry": "2026-12-31"},
        {"name": "Midazolam", "count": 2, "expiry": "2028-01-15"},
        {"name": "Narcan", "count": 2, "expiry": "2026-12-31"},
        {"name": "Nitro (Tabs)", "count": 2, "expiry": "2027-05-12"},
        {"name": "Nitro (IV)", "count": 2, "expiry": "2026-10-01"},
        {"name": "Propofol", "count": 1, "expiry": "2028-01-15"},
        {"name": "Racemic Epi", "count": 1, "expiry": "2026-12-31"},
        {"name": "Rocuronium", "count": 1, "expiry": "2027-05-12"},
        {"name": "Sodium Bicarbonate", "count": 2, "expiry": "2026-10-01"},
        {"name": "Succinylcholine", "count": 2, "expiry": "2028-01-15"},
        {"name": "Terbutaline", "count": 4, "expiry": "2026-12-31"},
        {"name": "Toradol", "count": 0, "expiry": "2027-05-12"},
        {"name": "Tetracaine (eye drop)", "count": 2, "expiry": "2026-10-01"},
        {"name": "Vecuronium", "count": 2, "expiry": "2028-01-15"},
        {"name": "Zofran", "count": 1, "expiry": "2026-12-31"}
    ]
}

NARCOTICS = ["Diazepam (Valium)", "Dilaudid", "Fentanyl", "Ketamine", "Midazolam", "Propofol"]

# Stable session initialization step
if "med_data" not in st.session_state:
    st.session_state["med_data"] = json.loads(json.dumps(INITIAL_DATA))

# --- 2. USER INTERFACE GENERATION ---
st.title("🚑 Ambulance Med Check Dashboard")

st.sidebar.header("🛡️ Operations Hub")
user_role = st.sidebar.selectbox("Select Your Certification Level", ["EMT / Basic", "Paramedic"])
selected_rig = st.sidebar.radio("Active Ambulance Unit", ["Rig #356", "Rig #357"])

# Sidebar Data Export JSON Utility
st.sidebar.markdown("---")
st.sidebar.subheader("💾 Backup Utility")
json_string = json.dumps(st.session_state["med_data"], indent=4)
st.sidebar.download_button(
    label="⬇️ Download Backup Database",
    data=json_string,
    file_name="ambulance_med_data.json",
    mime="application/json"
)

today = datetime.date.today()
fifteen_days_out = today + datetime.timedelta(days=15)

# --- FILTER PRIVILEGES & COMPUTE ALERTS ---
raw_meds = st.session_state["med_data"][selected_rig]
visible_meds = []

empty_meds = []
low_meds = []
expiring_meds = []
all_expiration_dates = []

for med in raw_meds:
    is_narc = med["name"] in NARCOTICS
    if is_narc and user_role == "EMT / Basic":
        continue  # Narcotic wall filter
        
    visible_meds.append(med)
    
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
        expiring_meds.append("%s (%s)" % (med['name'], med['expiry']))

earliest_expiry_date = min(all_expiration_dates) if all_expiration_dates else "N/A"

# --- SECTION 1: METRICS & ALERTS ---
st.subheader("⚠️ Critical Discrepancy & Expiration Logs")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Earliest Expiration Date", str(earliest_expiry_date))
col2.error("🚨 Out of Stock (%d)" % len(empty_meds))
col3.warning("⚠️ Low Inventory (%d)" % len(low_meds))
col4.info("⏳ Expiring Soon (%d)" % len(expiring_meds))

if empty_meds:
    st.error("**CRITICAL - EMPTY:** %s" % ', '.join(empty_meds))
if low_meds:
    st.warning("**NOTICE - LOW STOCK (1 Left):** %s" % ', '.join(low_meds))
if expiring_meds:
    st.info("**NOTICE - EXPIRING < 15 DAYS:** %s" % ', '.join(expiring_meds))

st.divider()

# --- SECTION 2: THE FLAT INTERACTIVE MATRIX GRID ---
st.subheader("📊 Active Operations Grid — %s" % selected_rig)
st.markdown("Adjust quantities and expiration dates directly inside the data grid below:")

# Display the flat matrix grid using Streamlit's robust native data editor
edited_data = st.data_editor(
    visible_meds,
    column_config={
        "name": st.column_config.TextColumn("Medication Name", disabled=True),
        "count": st.column_config.NumberColumn("Quantity on Hand", min_value=0, step=1, required=True),
        "expiry": st.column_config.TextColumn("Expiration Date (YYYY-MM-DD)", required=True),
    },
    hide_index=True,
    use_container_width=True,
    key="grid_editor"
)

# Process row mutations safely without dynamic key tracking drops
if st.button("💾 Save Matrix Changes", type="primary"):
    # Re-merge the updated visible records back into the master workspace state
    for updated_item in edited_data:
        for original_item in raw_meds:
            if original_item["name"] == updated_item["name"]:
                original_item["count"] = updated_item["count"]
                original_item["expiry"] = updated_item["expiry"]
    
    st.success("✅ Changes committed to current session cache successfully!")
    st.rerun()

st.divider()

# --- SECTION 3: SUMMARY EXPORTER BLOCK ---
st.subheader("📋 Shift Summary Text Exporter")
