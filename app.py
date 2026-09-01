import streamlit as st
import json
import os
from datetime import datetime, timedelta

# 1. Page Configuration & Layout Customizations
st.set_page_config(page_title="EMS Med Tracker", page_icon="🚑", layout="centered")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; padding-horizontal: 0.5rem !important; }
    h1 { font-size: 22px !important; text-align: center; color: #d9534f; margin-bottom: 5px !important; }
    h3 { font-size: 16px !important; margin-bottom: 2px !important; margin-top: 2px !important; }
    div[data-testid="stMetricValue"] { font-size: 18px !important; }
    div[data-testid="stMetricLabel"] { font-size: 11px !important; }
    .stButton>button { width: 100% !important; padding: 0.4rem !important; font-size: 14px !important; height: 42px !important; }
    hr { margin: 8px 0px !important; }
    div.stForm { padding: 12px !important; border-radius: 8px !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🚑 Ambulance Med Tracker")

# 2. Hardcoded Master Meds Database
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

# 3. Secure File I/O Engine
LOCAL_FILE_PATH = "inventory_records.json"

def load_data_from_disk():
    if os.path.exists(LOCAL_FILE_PATH):
        try:
            with open(LOCAL_FILE_PATH, "r") as f:
                content = json.load(f)
                if content and "Rig #356" in content:
                    return content
        except Exception:
            pass
    fallback_data = {"Rig #356": get_original_master_data(), "Rig #357": get_original_master_data()}
    with open(LOCAL_FILE_PATH, "w") as f:
        json.dump(fallback_data, f, indent=4)
    return fallback_data

def save_data_to_disk(data):
    with open(LOCAL_FILE_PATH, "w") as f:
        json.dump(data, f, indent=4)

# Initialize Session State
if "rig_inventories" not in st.session_state:
    st.session_state.rig_inventories = load_data_from_disk()

# 4. Global Inventory Alert Calculations
out_of_stock = []
low_stock = []
expiring_soon = []

today = datetime.today()
expiry_threshold_15d = today + timedelta(days=15)

for rig_name, items in st.session_state.rig_inventories.items():
    for item in items:
        c = int(item["count"])
        if c == 0:
            out_of_stock.append({"rig": rig_name, "name": item["name"]})
        elif c == 1:
            low_stock.append({"rig": rig_name, "name": item["name"]})
        
        if c > 0:
            try:
                med_expiry = datetime.strptime(item["expiry"].strip(), "%Y-%m-%d")
                if med_expiry <= expiry_threshold_15d:
                    days_left = (med_expiry - today).days
                    days_str = "Today" if days_left == 0 else f"{days_left}d left"
                    expiring_soon.append({"rig": rig_name, "name": item["name"], "days": days_left, "str": days_str})
            except ValueError:
                pass

# 5. Core Vehicle & Crew Identifiers
col_rig, col_sig = st.columns(2)
with col_rig:
    selected_rig = st.selectbox("🔑 Active Vehicle", options=["Rig #356", "Rig #357"])
with col_sig:
    crew_signature = st.text_input("✍️ Paramedic Sig", placeholder="Name/Initials", max_chars=15).strip()

# 6. Safety Metrics Summary Panel
with st.expander("📋 View Safety Alerts Summary", expanded=True):
    m1, m2, m3 = st.columns(3)
    m1.metric("Empty", len([x for x in out_of_stock if x['rig'] == selected_rig]))
    m2.metric("Low", len([x for x in low_stock if x['rig'] == selected_rig]))
    m3.metric("<15d Exp", len([x for x in expiring_soon if x['rig'] == selected_rig]))

    rig_empty_list = [x['name'] for x in out_of_stock if x['rig'] == selected_rig]
    rig_low_list = [x['name'] for x in low_stock if x['rig'] == selected_rig]
    rig_exp_list = [f"{x['name']} ({x['str']})" for x in expiring_soon if x['rig'] == selected_rig]

    if rig_empty_list:
        st.error(f"**🛑 Empty:** {', '.join(rig_empty_list)}")
    if rig_low_list:
        st.warning(f"**⚠️ Low Stock:** {', '.join(rig_low_list)}")
    if rig_exp_list:
        st.info(f"**⏳ Expiring (<15d):**\n" + "\n".join([f"- {m}" for m in rig_exp_list]))

# 7. SMS Communication Block Builder
st.subheader("📱 Export Text Report")

text_report = f"🚑 EMS REPORT: {selected_rig}\n"
text_report += f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
text_report += f"✍️ Signed: {crew_signature if crew_signature else 'Not Signed'}\n"
text_report += "---------------------\n"

text_alerts = []
for x in out_of_stock:
    if x['rig'] == selected_rig:
        text_alerts.append(f"• {x['name']}: OUT OF STOCK")
for x in low_stock:
    if x['rig'] == selected_rig:
        text_alerts.append(f"• {x['name']}: 1 LEFT")
for x in expiring_soon:
    if x['rig'] == selected_rig and x['days'] <= 5:
        text_alerts.append(f"• {x['name']}: EXPIRES IN {x['days']} DAYS")

if text_alerts:
    text_report += "\n".join(text_alerts)
else:
    text_report += "✅ All meds are checked and up to code."

st.text_area(label="Tap box below, select all, and copy to text:", value=text_report, height=130)

st.markdown("---")

# 8. Action Windows (Re-engineered to use stable, retro-compatible expanders)
st.subheader("⚙️ Quick Transaction Entry Windows")

with st.expander("💉 Open Medication Usage Log Window"):
    st.info(f"Deducting clinical volumes from: **{selected_rig}**")
    current_meds_list = st.session_state.rig_inventories[selected_rig]
    available_to_use = [m["name"] for m in current_meds_list if int(m["count"]) > 0]
    
    if available_to_use:
        with st.form("inline_usage_form", clear_on_submit=True):
            use_name = st.selectbox("Select Medication Administered", options=available_to_use)
            qty_used = st.number_input("Quantity Used", min_value=1, value=1, step=1)
            
            if st.form_submit_button(label="Commit and Save Medication Usage", type="primary"):
                for idx, med in enumerate(st.session_state.rig_inventories[selected_rig]):
                    if med["name"] == use_name:
                        current_count = int(med["count"])
                        new_count = max(0, current_count - qty_used)
                        st.session_state.rig_inventories[selected_rig][idx]["count"] = new_count
                        save_data_to_disk(st.session_state.rig_inventories)
                        st.success(f"Deducted {qty_used} from {use_name}!")
                        st.rerun()
                        break
    else:
        st.warning("No medications currently available with stock greater than 0.")

