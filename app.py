import streamlit as st
import datetime

# --- EMERGENCY SELF-CONTAINED DATA MANIFEST ---
INITIAL_DATA = {
    "Rig #356": [
        {"id": "1", "name": "Adenosine", "count": 5, "expiry": "2027-05-12"},
        {"id": "2", "name": "Albuterol", "count": 2, "expiry": "2026-10-01"},
        {"id": "3", "name": "Amiodarone", "count": 3, "expiry": "2028-01-15"},
        {"id": "4", "name": "Aspirin", "count": 2, "expiry": "2026-12-31"},
        {"id": "14", "name": "Diazepam (Valium)", "count": 2, "expiry": "2026-10-01"},
        {"id": "21", "name": "Fentanyl", "count": 4, "expiry": "2027-05-12"}
    ],
    "Rig #357": [
        {"id": "1", "name": "Adenosine", "count": 5, "expiry": "2027-05-12"},
        {"id": "2", "name": "Albuterol", "count": 2, "expiry": "2026-10-01"},
        {"id": "14", "name": "Diazepam (Valium)", "count": 2, "expiry": "2026-10-01"}
    ]
}

NARCOTICS = ["Diazepam (Valium)", "Fentanyl"]

st.set_page_config(page_title="Ambulance Med Check", layout="wide")
st.title("🚑 Ambulance Med Check Dashboard (Fallback Mode)")

# Initialize session storage safely
if "med_data" not in st.session_state:
    st.session_state["med_data"] = INITIAL_DATA

current_inventory = st.session_state["med_data"]

# Sidebar Selection Rules
st.sidebar.header("🛡️ Operations Hub")
user_role = st.sidebar.selectbox("Select Certification Level", ["EMT / Basic", "Paramedic"])
selected_rig = st.sidebar.radio("Active Ambulance Unit", ["Rig #356", "Rig #357"])

# Timeline Check Setup
today = datetime.date.today()
fifteen_days_out = today + datetime.timedelta(days=15)
rig_meds = current_inventory[selected_rig]

# --- ALERTS SECTION ---
empty_meds = []
low_meds = []
expiring_meds = []

for med in rig_meds:
    if med["count"] == 0:
        empty_meds.append(med["name"])
    elif med["count"] == 1:
        low_meds.append(med["name"])
        
    exp_date = datetime.datetime.strptime(med["expiry"], "%Y-%m-%d").date()
    if exp_date <= fifteen_days_out:
        expiring_meds.append(f"{med['name']} ({med['expiry']})")

if empty_meds:
    st.error(f"🚨 **OUT OF STOCK:** {', '.join(empty_meds)}")
if low_meds:
    st.warning(f"⚠️ **LOW STOCK (1 Left):** {', '.join(low_meds)}")
if expiring_meds:
    st.info(f"⏳ **EXPIRING SOON:** {', '.join(expiring_meds)}")

st.divider()

# --- MATRIX SELECTION LAYER ---
st.subheader(f"📊 Medication Controls - {selected_rig}")
for m in rig_meds:
    is_narc = m["name"] in NARCOTICS
    if is_narc and user_role == "EMT / Basic":
        continue
        
    with st.expander(f"{'🔒 ' if is_narc else '💊 '} {m['name']} — Total: {m['count']} | Expiry: {m['expiry']}"):
        c1, c2 = st.columns(2)
        with c1:
            qty_used = st.number_input("Log Quantity Consumed", min_value=0, max_value=m['count'], step=1, key=f"use_{selected_rig}_{m['id']}")
            initials = st.text_input("Paramedic/EMT Initials", max_chars=4, key=f"init_{selected_rig}_{m['id']}")
            if st.button("Submit Usage Details", key=f"btn_use_{selected_rig}_{m['id']}"):
                if qty_used > 0 and initials:
                    m["count"] -= qty_used
                    st.success("Usage updated!")
                    st.rerun()
        with c2:
            qty_add = st.number_input("Log Quantity Restocked", min_value=0, step=1, key=f"add_{selected_rig}_{m['id']}")
            if st.button("Confirm Restock", key=f"btn_add_{selected_rig}_{m['id']}"):
                if qty_add > 0:
                    m["count"] += qty_add
                    st.success("Restock inventory updated!")
                    st.rerun()
