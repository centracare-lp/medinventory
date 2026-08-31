import streamlit as st
from streamlit_gsheets import GSheetsConnection  # Run: pip install streamlit-shadow-connection or streamlit-gsheets
import pandas as pd
from datetime import datetime, timedelta

# 1. Page Configuration
st.set_page_config(page_title="Ambulance Med Tracker", page_icon="🚑", layout="centered")
st.title("🚑 Ambulance Rig Inventory")

# 2. Establish Google Sheets Database Connection
# This reads your secrets.toml spreadsheet URL automatically
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("⚠️ Database connection configurations missing. Please check your secrets setup workflow.")
    st.stop()

# Helper function to pull the freshest data from a specific tab row
def load_rig_data(sheet_name):
    # ttl=0 forces Streamlit to clear its cache and pull live numbers on every button click
    return conn.read(worksheet=sheet_name, ttl=0)

# Helper function to write changes securely back to Google Cloud
def save_rig_data(df, sheet_name):
    conn.update(worksheet=sheet_name, data=df)

# 3. Handle Initializing Master Lists or Picking Active Rigs
rigs = ["Rig #356", "Rig #357"]
selected_rig = st.selectbox("🔑 Select Ambulance Unit to Update", options=rigs)

# Map human labels directly to matching Google Sheet worksheet tab IDs
sheet_tab = "Rig_356" if "356" in selected_rig else "Rig_357"

# Load the live pandas dataframe profile for the chosen vehicle
try:
    df_inventory = load_rig_data(sheet_tab)
    # Ensure types match up safely for analytical checking blocks
    df_inventory["count"] = df_inventory["count"].astype(int)
    df_inventory["expiry"] = df_inventory["expiry"].astype(str)
except Exception as e:
    st.error(f"Failed to read data worksheet tab '{sheet_tab}'. Verify your sharing permissions settings.")
    st.stop()

# 4. Logistics Overview & Expiration Dashboard Checking Lookups
st.subheader("📋 Logistics Overview: Safety Alerts")

out_of_stock = []
low_stock = []
expiring_soon = []

today = datetime.today()
expiry_threshold = today + timedelta(days=15)

# Calculate system metrics dynamically from the live pulled dataset row loops
for index, row in df_inventory.iterrows():
    med_name = row["name"]
    med_count = int(row["count"])
    med_expiry_str = row["expiry"]

    if med_count == 0:
        out_of_stock.append(f"{med_name}")
    elif med_count == 1:
        low_stock.append(f"{med_name}")

    if med_count > 0:
        try:
            med_expiry = datetime.strptime(med_expiry_str.strip(), "%Y-%m-%d")
            if med_expiry <= expiry_threshold:
                days_left = (med_expiry - today).days
                days_str = "Today" if days_left == 0 else f"{days_left}d left"
                expiring_soon.append(f"{med_name} - Exp: {med_expiry_str} ({days_str})")
        except ValueError:
            pass

# Render header metrics layout counters
metric_col1, metric_col2, metric_col3 = st.columns(3)
with metric_col1:
    st.metric(label="Out of Stock (0 Left)", value=len(out_of_stock))
with metric_col2:
    st.metric(label="Low Stock (1 Left)", value=len(low_stock))
with metric_col3:
    st.metric(label="Expiring within 15 Days", value=len(expiring_soon))

if out_of_stock:
    st.error(f"**🛑 Out of Stock ({selected_rig}):** {', '.join(out_of_stock)}")
if low_stock:
    st.warning(f"**⚠️ Critical Low Stock ({selected_rig}):** {', '.join(low_stock)}")
if expiring_soon:
    st.info(f"**⏳ Expiring within 15 Days ({selected_rig}):**\n" + "\n".join([f"- {m}" for m in expiring_soon]))
if not out_of_stock and not low_stock and not expiring_soon:
    st.success(f"✅ {selected_rig} is completely stocked and medications are up to date.")

st.markdown("---")

# 5. Dynamic Search Bar Filter
search_query = st.text_input("🔍 Search Medications...", placeholder=f"Search items inside {selected_rig}...").strip()

# 6. Active Inventory Display List
st.subheader(f"Current Live Stock: {selected_rig}")

for index, row in df_inventory.iterrows():
    med_id = row["id"]
    med_name = row["name"]
    med_count = int(row["count"])
    med_expiry_str = row["expiry"]

    if search_query.lower() in med_name.lower():
        with st.container():
            col1, col2 = st.columns(2)
            
            with col1:
                is_expiring_soon = False
                try:
                    med_expiry = datetime.strptime(med_expiry_str.strip(), "%Y-%m-%d")
                    if med_expiry <= expiry_threshold and med_count > 0:
                        is_expiring_soon = True
                except ValueError:
                    pass

                if med_count == 0:
                    st.markdown(f"### 🛑 {med_name} *(EMPTY)*")
                elif is_expiring_soon:
                    st.markdown(f"### ⏳ {med_name} *(EXPIRING SOON)*")
                elif med_count == 1:
                    st.markdown(f"### ⚠️ {med_name} *(LOW)*")
                else:
                    st.markdown(f"### {med_name}")
                
                st.write(f"**Stock:** {med_count} | **Exp:** {med_expiry_str}")
            
            with col2:
                btn_disabled = med_count == 0
                # When clicked, update the localized dataframe row and commit it straight to Google Sheets
                if st.button(f"Use 1", key=f"use_{selected_rig}_{med_id}_{index}", disabled=btn_disabled):
                    df_inventory.at[index, "count"] = med_count - 1
                    save_rig_data(df_inventory, sheet_tab)
                    st.rerun()
            st.markdown("---")

# 7. Restock Form Section
st.subheader(f"Log Restock / Shipments into {selected_rig}")

with st.form("restock_form", clear_on_submit=True):
    med_names = df_inventory["name"].tolist()
    selected_name = st.selectbox("Select Medication to Restock", options=med_names)
    
    col_qty, col_exp = st.columns(2)
    with col_qty:
        qty_to_add = st.number_input("Quantity Added", min_value=1, value=1, step=1)
    with col_exp:
        change_exp = st.checkbox("Update Expiration Date?")
        new_exp_date = st.date_input("New Expiration Date", value=datetime.today())

    submit_button = st.form_submit_button(label="Save Restock Entry", type="primary")

    if submit_button:
        # Locate the targeted matching row row item index
        matched_idx = df_inventory[df_inventory["name"] == selected_name].index
        if not matched_idx.empty:
            target_idx = matched_idx[0]
            df_inventory.at[target_idx, "count"] += int(qty_to_add)
            if change_exp:
                df_inventory.at[target_idx, "expiry"] = new_exp_date.strftime("%Y-%m-%d")
            
            save_rig_data(df_inventory, sheet_tab)
            st.success(f"Successfully committed restock records for {selected_name} to cloud servers!")
            st.rerun()
