import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta

# 1. Page Configuration Layout
st.set_page_config(page_title="Ambulance Med Tracker", page_icon="🚑", layout="centered")
st.title("🚑 Ambulance Rig Inventory")

# 2. Hardcoded Master Fallback Array (Your exact 42 medication profiles)
def get_original_master_data():
    return [
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

# 3. File System I/O Handlers
LOCAL_FILE_PATH = "inventory_records.json"

def load_data_from_disk():
    """Reads inventory profile off hard drive file system. Automatically falls back to master array if file missing."""
    if os.path.exists(LOCAL_FILE_PATH):
        try:
            with open(LOCAL_FILE_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    
    # Initialize brand new schema file structure
    initial_data = {
        "Rig #356": get_original_master_data(),
        "Rig #357": get_original_master_data()
    }
    save_data_to_disk(initial_data)
    return initial_data

def save_data_to_disk(data):
    """Commits active variables onto hard drive workspace."""
    with open(LOCAL_FILE_PATH, "w") as f:
        json.dump(data, f, indent=4)

# 4. Sync Memory Operations State
if "rig_inventories" not in st.session_state:
    st.session_state.rig_inventories = load_data_from_disk()

# 5. Global Metrics & Compliance Alert Dashboard
st.subheader("📋 Logistics Overview: Safety Alerts")

out_of_stock = []
low_stock = []
expiring_soon = []

today = datetime.today()
expiry_threshold = today + timedelta(days=15)

# Calculate status across BOTH rigs simultaneously
for rig_name, items in st.session_state.rig_inventories.items():
    for item in items:
        if int(item["count"]) == 0:
            out_of_stock.append(f"{item['name']} ({rig_name})")
        elif int(item["count"]) == 1:
            low_stock.append(f"{item['name']} ({rig_name})")
        
        if int(item["count"]) > 0:
            try:
                med_expiry = datetime.strptime(item["expiry"].strip(), "%Y-%m-%d")
                if med_expiry <= expiry_threshold:
                    days_left = (med_expiry - today).days
                    days_str = "Today" if days_left == 0 else f"{days_left}d left"
                    expiring_soon.append(f"{item['name']} ({rig_name}) - Exp: {item['expiry']} ({days_str})")
            except ValueError:
                pass

# Render header card panels
metric_col1, metric_col2, metric_col3 = st.columns(3)
with metric_col1:
    st.metric(label="Out of Stock (0 Left)", value=len(out_of_stock))
with metric_col2:
    st.metric(label="Low Stock (1 Left)", value=len(low_stock))
with metric_col3:
    st.metric(label="Expiring within 15 Days", value=len(expiring_soon))

if out_of_stock:
    st.error(f"**🛑 Out of Stock:** {', '.join(out_of_stock)}")
if low_stock:
    st.warning(f"**⚠️ Critical Low Stock:** {', '.join(low_stock)}")
if expiring_soon:
    st.info(f"**⏳ Expiring within 15 Days:**\n" + "\n".join([f"- {m}" for m in expiring_soon]))
if not out_of_stock and not low_stock and not expiring_soon:
    st.success("✅ All vehicles are fully stocked and medications are up to date.")

st.markdown("---")

# 6. Active Selection Inputs
selected_rig = st.selectbox("🔑 Select Ambulance Unit to Update", options=["Rig #356", "Rig #357"])
current_inventory = st.session_state.rig_inventories[selected_rig]

search_query = st.text_input("🔍 Search Medications...", placeholder=f"Search items inside {selected_rig}...").strip()

# 7. Dynamic Inventory List Render Engine
st.subheader(f"Current Live Stock: {selected_rig}")

for i, med in enumerate(current_inventory):
    if search_query.lower() in med["name"].lower():
        with st.container():
            col1, col2 = st.columns(2)
            
            with col1:
                is_expiring_soon = False
                try:
                    med_expiry = datetime.strptime(med["expiry"].strip(), "%Y-%m-%d")
                    if med_expiry <= expiry_threshold and int(med["count"]) > 0:
                        is_expiring_soon = True
                except ValueError:
                    pass

                if int(med["count"]) == 0:
                    st.markdown(f"### 🛑 {med['name']} *(EMPTY)*")
                elif is_expiring_soon:
                    st.markdown(f"### ⏳ {med['name']} *(EXPIRING SOON)*")
                elif int(med["count"]) == 1:
                    st.markdown(f"### ⚠️ {med['name']} *(LOW)*")
                else:
                    st.markdown(f"### {med['name']}")
                
                st.write(f"**Stock:** {med['count']} | **Exp:** {med['expiry']}")
            
            with col2:
                btn_disabled = int(med["count"]) == 0
                if st.button(f"Use 1", key=f"use_{selected_rig}_{med['id']}_{i}", disabled=btn_disabled):
                    med["count"] = int(med["count"]) - 1
                    # Save states locally instantly
                    save_data_to_disk(st.session_state.rig_inventories)
                    st.rerun()
            st.markdown("---")

# 8. Interactive Restock Workflow Form Panel
st.subheader(f"Log Restock / Shipments into {selected_rig}")

with st.form("restock_form", clear_on_submit=True):
    med_names = [med["name"] for med in current_inventory]
    selected_name = st.selectbox("Select Medication to Restock", options=med_names)
    
    col_qty, col_exp = st.columns(2)
    with col_qty:
        qty_to_add = st.number_input("Quantity Added", min_value=1, value=1, step=1)
    with col_exp:
        change_exp = st.checkbox("Update Expiration Date?")
        new_exp_date = st.date_input("New Expiration Date", value=datetime.today())

    submit_button = st.form_submit_button(label="Save Restock Entry", type="primary")

    if submit_button:
        for med in current_inventory:
            if med["name"] == selected_name:
                med["count"] = int(med["count"]) + int(qty_to_add)
                if change_exp:
                    med["expiry"] = new_exp_date.strftime("%Y-%m-%d")
        
        # Save record entries back to JSON file
        save_data_to_disk(st.session_state.rig_inventories)
        st.success(f"Successfully saved restock record updates locally!")
        st.rerun()
