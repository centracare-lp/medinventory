import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. Page Configuration
st.set_page_config(page_title="Ambulance Med Tracker", page_icon="🚑", layout="centered")
st.title("🚑 Ambulance Rig Inventory")

# ⚡ CRITICAL: PASTE YOUR GOOGLE SHEET LINK HERE
# Cut everything from "/edit" onwards out and leave the bare base link
SPREADSHEET_BASE_URL = "https://google.com"

# Helper function to convert a standard Google Sheet link into a direct multi-tab CSV stream
def load_rig_data_via_csv(sheet_name):
    csv_url = f"{SPREADSHEET_BASE_URL}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    # Read the data via raw request and clean types
    df = pd.read_csv(csv_url)
    df["count"] = df["count"].fillna(0).astype(int)
    df["expiry"] = df["expiry"].astype(str)
    return df

# Helper function to prompt users on how to update numbers
def save_instructions():
    st.info("💡 **How to update quantities permanently:** Since we are using standard web sharing, use the app to search and scan items, then make adjustments directly inside your Google Sheets app or browser. Your Streamlit app will update instantly!")

# 3. Handle Selecting Active Rigs
rigs = ["Rig #356", "Rig #357"]
selected_rig = st.selectbox("🔑 Select Ambulance Unit to Update", options=rigs)

# Map selections directly to your Google Sheet worksheet tab IDs
sheet_tab = "Rig_356" if "356" in selected_rig else "Rig_357"

# Load the live pandas dataframe profile cleanly
try:
    df_inventory = load_rig_data_via_csv(sheet_tab)
except Exception as e:
    st.error(f"🚨 Connection Failed: Please verify your SPREADSHEET_BASE_URL variable setting or spreadsheet sharing privacy parameters.")
    st.stop()

# 4. Logistics Overview & Expiration Dashboard Checking Lookups
st.subheader("📋 Logistics Overview: Safety Alerts")

out_of_stock = []
low_stock = []
expiring_soon = []

today = datetime.today()
expiry_threshold = today + timedelta(days=15)

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
save_instructions()

for index, row in df_inventory.iterrows():
    med_name = row["name"]
    med_count = int(row["count"])
    med_expiry_str = row["expiry"]

    if search_query.lower() in med_name.lower():
        with st.container():
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
            st.markdown("---")
