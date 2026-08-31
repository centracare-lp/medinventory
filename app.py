import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. Page Configuration
st.set_page_config(page_title="Ambulance Med Tracker", page_icon="🚑", layout="centered")
st.title("🚑 Ambulance Rig Inventory")

# 2. Master Medication Template (Your 42 original items)
@st.cache_data
def get_master_med_list():
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

# 3. Initialize Independent Rig Storage Systems (Rig #356 & Rig #357)
if "rig_inventories" not in st.session_state:
    st.session_state.rig_inventories = {
        "Rig #356": [item.copy() for item in get_master_med_list()],
        "Rig #357": [item.copy() for item in get_master_med_list()]
    }

# 4. Logistics Overview & Expiration Dashboard
st.subheader("📋 Logistics Overview: Safety Alerts")

out_of_stock = []
low_stock = []
expiring_soon = []

today = datetime.today()
expiry_threshold = today + timedelta(days=15)

# Scan both rigs simultaneously for alerts
for rig, items in st.session_state.rig_inventories.items():
    for item in items:
        # Check stock counts
        if item["count"] == 0:
            out_of_stock.append(f"{item['name']} ({rig})")
        elif item["count"] == 1:
            low_stock.append(f"{item['name']} ({rig})")
        
        # Check expiration status (ignore if count is 0 anyway)
        if item["count"] > 0:
            try:
                med_expiry = datetime.strptime(item["expiry"], "%Y-%m-%d")
                if med_expiry <= expiry_threshold:
                    days_left = (med_expiry - today).days
                    days_str = "Today" if days_left == 0 else f"{days_left}d left"
                    expiring_soon.append(f"{item['name']} ({rig}) - Exp: {item['expiry']} ({days_str})")
            except ValueError:
                pass

# Render top layout stats
metric_col1, metric_col2, metric_col3 = st.columns(3)
with metric_col1:
    st.metric(label="Out of Stock (0 Left)", value=len(out_of_stock))
with metric_col2:
    st.metric(label="Low Stock (1 Left)", value=len(low_stock))
with metric_col3:
    st.metric(label="Expiring within 15 Days", value=len(expiring_soon))

# Display active notifications
if out_of_stock:
    st.error(f"**🛑 Out of Stock:** {', '.join(out_of_stock)}")
if low_stock:
    st.warning(f"**⚠️ Critical Low Stock:** {', '.join(low_stock)}")
if expiring_soon:
    st.info(f"**⏳ Expiring within 15 Days:**\n" + "\n".join([f"- {m}" for m in expiring_soon]))

if not out_of_stock and not low_stock and not expiring_soon:
    st.success("✅ All rigs are fully stocked and medications are up to date.")

st.markdown("---")

# 5. Rig Selection Dropdown
selected_rig = st.selectbox("🔑 Select Ambulance Unit to Update", options=list(st.session_state.rig_inventories.keys()))
current_inventory = st.session_state.rig_inventories[selected_rig]

# 6. Dynamic Search Bar Filter
search_query = st.text_input("🔍 Search Medications...", placeholder=f"Search items inside {selected_rig}...").strip()

# 7. Active Inventory List
st.subheader(f"Current Live Stock: {selected_rig}")

for i, med in enumerate(current_inventory):
    if search_query.lower() in med["name"].lower():
        with st.container():
            col1, col2 = st.columns(2)
            
            with col1:
                # Calculate if item row itself is expiring soon to highlight inline
                is_expiring_soon = False
                try:
                    med_expiry = datetime.strptime(med["expiry"], "%Y-%m-%d")
                    if med_expiry <= expiry_threshold and med["count"] > 0:
                        is_expiring_soon = True
                except ValueError:
                    pass

                # Name labels with inline status flags
                if med["count"] == 0:
                    st.markdown(f"### 🛑 {med['name']} *(EMPTY)*")
                elif is_expiring_soon:
                    st.markdown(f"### ⏳ {med['name']} *(EXPIRING SOON)*")
                elif med["count"] == 1:
                    st.markdown(f"### ⚠️ {med['name']} *(LOW)*")
                else:
                    st.markdown(f"### {med['name']}")
                
                st.write(f"**Stock:** {med['count']} | **Exp:** {med['expiry']}")
            
            with col2:
                btn_disabled = med["count"] == 0
                if st.button(f"Use 1", key=f"use_{selected_rig}_{med['id']}_{i}", disabled=btn_disabled):
                    med["count"] -= 1
                    st.rerun()
            st.markdown("---")

# 8. Restock Form Section (Fixed Indentation Block)
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
                med["count"] += qty_to_add
                if change_exp:
                    med["expiry"] = new_exp_date.strftime("%Y-%m-%d")
        st.success(f"Successfully updated {selected_name} on {selected_rig}!")
        st.rerun()
