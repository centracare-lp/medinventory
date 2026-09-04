```python
import streamlit as st
import datetime
import json
import copy


# ============================================================
# 1. MASTER MEDICATION DEFINITIONS
# ============================================================
#
# This is the master list of medications carried by the service.
# Each medication is defined ONLY ONCE.
#
# "controlled" identifies medications that should be restricted
# from the EMT/Basic view.
#
# The inventory quantities and expiration dates are stored
# separately for each ambulance below.
# ============================================================

MEDICATIONS = {
    "adenosine": {
        "name": "Adenosine",
        "controlled": False,
    },
    "albuterol": {
        "name": "Albuterol",
        "controlled": False,
    },
    "amiodarone": {
        "name": "Amiodarone",
        "controlled": False,
    },
    "aspirin": {
        "name": "Aspirin",
        "controlled": False,
    },
    "atropine": {
        "name": "Atropine",
        "controlled": False,
    },
    "benadryl_iv": {
        "name": "Benadryl (IV)",
        "controlled": False,
    },
    "benadryl_oral": {
        "name": "Benadryl (Oral)",
        "controlled": False,
    },
    "calcium_chloride": {
        "name": "Calcium Chloride",
        "controlled": False,
    },
    "calcium_gluconate": {
        "name": "Calcium Gluconate",
        "controlled": False,
    },
    "cardizem": {
        "name": "Cardizem",
        "controlled": False,
    },
    "dextrose_oral": {
        "name": "Dextrose (Oral)",
        "controlled": False,
    },
    "dextrose_d10": {
        "name": "Dextrose (D10)",
        "controlled": False,
    },
    "dextrose_d50": {
        "name": "Dextrose (D50)",
        "controlled": False,
    },
    "diazepam": {
        "name": "Diazepam (Valium)",
        "controlled": True,
    },
    "dilaudid": {
        "name": "Dilaudid",
        "controlled": True,
    },
    "droperidol": {
        "name": "Droperidol",
        "controlled": False,
    },
    "duoneb": {
        "name": "DuoNeb",
        "controlled": False,
    },
    "epi_iv": {
        "name": "Epi (IV) 1:10,000",
        "controlled": False,
    },
    "epi_im": {
        "name": "Epi (IM) 1:1,000",
        "controlled": False,
    },
    "etomidate": {
        "name": "Etomidate",
        "controlled": False,
    },
    "fentanyl": {
        "name": "Fentanyl",
        "controlled": True,
    },
    "glucagon": {
        "name": "Glucagon",
        "controlled": False,
    },
    "haldol": {
        "name": "Haldol",
        "controlled": False,
    },
    "ketamine": {
        "name": "Ketamine",
        "controlled": True,
    },
    "labetalol": {
        "name": "Labetalol",
        "controlled": False,
    },
    "lidocaine": {
        "name": "Lidocaine",
        "controlled": False,
    },
    "mag_sulfate": {
        "name": "Mag Sulfate",
        "controlled": False,
    },
    "metoprolol": {
        "name": "Metoprolol",
        "controlled": False,
    },
    "midazolam": {
        "name": "Midazolam",
        "controlled": True,
    },
    "narcan": {
        "name": "Narcan",
        "controlled": False,
    },
    "nitro_tabs": {
        "name": "Nitro (Tabs)",
        "controlled": False,
    },
    "nitro_iv": {
        "name": "Nitro (IV)",
        "controlled": False,
    },
    "propofol": {
        "name": "Propofol",
        "controlled": True,
    },
    "racemic_epi": {
        "name": "Racemic Epi",
        "controlled": False,
    },
    "rocuronium": {
        "name": "Rocuronium",
        "controlled": False,
    },
    "sodium_bicarbonate": {
        "name": "Sodium Bicarbonate",
        "controlled": False,
    },
    "succinylcholine": {
        "name": "Succinylcholine",
        "controlled": False,
    },
    "terbutaline": {
        "name": "Terbutaline",
        "controlled": False,
    },
    "toradol": {
        "name": "Toradol",
        "controlled": False,
    },
    "tetracaine": {
        "name": "Tetracaine (eye drop)",
        "controlled": False,
    },
    "vecuronium": {
        "name": "Vecuronium",
        "controlled": False,
    },
    "zofran": {
        "name": "Zofran",
        "controlled": False,
    },
}


# ============================================================
# 2. INITIAL INVENTORY
# ============================================================
#
# The medication definitions above are shared by all rigs.
# Only the inventory-specific information lives here:
#
#     count
#     expiry
#
# This means adding a new rig does NOT require duplicating the
# entire medication manifest.
# ============================================================

INITIAL_INVENTORY = {
    "Rig #356": {
        "adenosine": {"count": 5, "expiry": "2027-05-12"},
        "albuterol": {"count": 2, "expiry": "2026-10-01"},
        "amiodarone": {"count": 3, "expiry": "2028-01-15"},
        "aspirin": {"count": 2, "expiry": "2026-12-31"},
        "atropine": {"count": 2, "expiry": "2027-05-12"},
        "benadryl_iv": {"count": 1, "expiry": "2026-10-01"},
        "benadryl_oral": {"count": 2, "expiry": "2028-01-15"},
        "calcium_chloride": {"count": 3, "expiry": "2026-12-31"},
        "calcium_gluconate": {"count": 0, "expiry": "2027-05-12"},
        "cardizem": {"count": 1, "expiry": "2026-10-01"},
        "dextrose_oral": {"count": 2, "expiry": "2028-01-15"},
        "dextrose_d10": {"count": 1, "expiry": "2026-12-31"},
        "dextrose_d50": {"count": 1, "expiry": "2027-05-12"},
        "diazepam": {"count": 2, "expiry": "2026-10-01"},
        "dilaudid": {"count": 1, "expiry": "2028-01-15"},
        "droperidol": {"count": 2, "expiry": "2026-12-31"},
        "duoneb": {"count": 4, "expiry": "2027-05-12"},
        "epi_iv": {"count": 2, "expiry": "2026-10-01"},
        "epi_im": {"count": 2, "expiry": "2028-01-15"},
        "etomidate": {"count": 8, "expiry": "2026-12-31"},
        "fentanyl": {"count": 4, "expiry": "2027-05-12"},
        "glucagon": {"count": 2, "expiry": "2026-10-01"},
        "haldol": {"count": 4, "expiry": "2028-01-15"},
        "ketamine": {"count": 2, "expiry": "2026-12-31"},
        "labetalol": {"count": 2, "expiry": "2027-05-12"},
        "lidocaine": {"count": 3, "expiry": "2026-10-01"},
        "mag_sulfate": {"count": 2, "expiry": "2028-01-15"},
        "metoprolol": {"count": 2, "expiry": "2026-12-31"},
        "midazolam": {"count": 2, "expiry": "2028-01-15"},
        "narcan": {"count": 2, "expiry": "2026-12-31"},
        "nitro_tabs": {"count": 2, "expiry": "2027-05-12"},
        "nitro_iv": {"count": 2, "expiry": "2026-10-01"},
        "propofol": {"count": 1, "expiry": "2028-01-15"},
        "racemic_epi": {"count": 1, "expiry": "2026-12-31"},
        "rocuronium": {"count": 1, "expiry": "2027-05-12"},
        "sodium_bicarbonate": {"count": 2, "expiry": "2026-10-01"},
        "succinylcholine": {"count": 2, "expiry": "2028-01-15"},
        "terbutaline": {"count": 4, "expiry": "2026-12-31"},
        "toradol": {"count": 0, "expiry": "2027-05-12"},
        "tetracaine": {"count": 2, "expiry": "2026-10-01"},
        "vecuronium": {"count": 2, "expiry": "2028-01-15"},
        "zofran": {"count": 1, "expiry": "2026-12-31"},
    },

    "Rig #357": {
        "adenosine": {"count": 5, "expiry": "2027-05-12"},
        "albuterol": {"count": 2, "expiry": "2026-10-01"},
        "amiodarone": {"count": 3, "expiry": "2028-01-15"},
        "aspirin": {"count": 2, "expiry": "2026-12-31"},
        "atropine": {"count": 2, "expiry": "2027-05-12"},
        "benadryl_iv": {"count": 1, "expiry": "2026-10-01"},
        "benadryl_oral": {"count": 2, "expiry": "2028-01-15"},
        "calcium_chloride": {"count": 3, "expiry": "2026-12-31"},
        "calcium_gluconate": {"count": 0, "expiry": "2027-05-12"},
        "cardizem": {"count": 1, "expiry": "2026-10-01"},
        "dextrose_oral": {"count": 2, "expiry": "2028-01-15"},
        "dextrose_d10": {"count": 1, "expiry": "2026-12-31"},
        "dextrose_d50": {"count": 1, "expiry": "2027-05-12"},
        "diazepam": {"count": 2, "expiry": "2026-10-01"},
        "dilaudid": {"count": 1, "expiry": "2028-01-15"},
        "droperidol": {"count": 2, "expiry": "2026-12-31"},
        "duoneb": {"count": 4, "expiry": "2027-05-12"},
        "epi_iv": {"count": 2, "expiry": "2026-10-01"},
        "epi_im": {"count": 2, "expiry": "2028-01-15"},
        "etomidate": {"count": 8, "expiry": "2026-12-31"},
        "fentanyl": {"count": 4, "expiry": "2027-05-12"},
        "glucagon": {"count": 2, "expiry": "2026-10-01"},
        "haldol": {"count": 4, "expiry": "2028-01-15"},
        "ketamine": {"count": 2, "expiry": "2026-12-31"},
        "labetalol": {"count": 2, "expiry": "2027-05-12"},
        "lidocaine": {"count": 3, "expiry": "2026-10-01"},
        "mag_sulfate": {"count": 2, "expiry": "2028-01-15"},
        "metoprolol": {"count": 2, "expiry": "2026-12-31"},
        "midazolam": {"count": 2, "expiry": "2028-01-15"},
        "narcan": {"count": 2, "expiry": "2026-12-31"},
        "nitro_tabs": {"count": 2, "expiry": "2027-05-12"},
        "nitro_iv": {"count": 2, "expiry": "2026-10-01"},
        "propofol": {"count": 1, "expiry": "2028-01-15"},
        "racemic_epi": {"count": 1, "expiry": "2026-12-31"},
        "rocuronium": {"count": 1, "expiry": "2027-05-12"},
        "sodium_bicarbonate": {"count": 2, "expiry": "2026-10-01"},
        "succinylcholine": {"count": 2, "expiry": "2028-01-15"},
        "terbutaline": {"count": 4, "expiry": "2026-12-31"},
        "toradol": {"count": 0, "expiry": "2027-05-12"},
        "tetracaine": {"count": 2, "expiry": "2026-10-01"},
        "vecuronium": {"count": 2, "expiry": "2028-01-15"},
        "zofran": {"count": 1, "expiry": "2026-12-31"},
    },
}


# ============================================================
# 3. SESSION STATE INITIALIZATION
# ============================================================

if "inventory" not in st.session_state:
    st.session_state["inventory"] = copy.deepcopy(INITIAL_INVENTORY)


# ============================================================
# 4. HELPER FUNCTION
# ============================================================

def build_visible_medication_list(rig, user_role):
    """
    Converts the structured inventory data into a flat list
    suitable for Streamlit's data_editor.
    """

    visible = []

    for med_id, med_info in MEDICATIONS.items():

        # Make sure the medication exists in the selected rig.
        if med_id not in st.session_state["inventory"][rig]:
            continue

        # Hide controlled medications from EMT/Basic users.
        if med_info["controlled"] and user_role == "EMT / Basic":
            continue

        inventory_item = st.session_state["inventory"][rig][med_id]

        visible.append({
            "id": med_id,
            "name": med_info["name"],
            "count": inventory_item["count"],
            "expiry": inventory_item["expiry"],
        })

    return visible


# ============================================================
# 5. USER INTERFACE
# ============================================================

st.title("🚑 Ambulance Med Check Dashboard")

st.sidebar.header("🛡️ Operations Hub")

user_role = st.sidebar.selectbox(
    "Select Your Certification Level",
    ["EMT / Basic", "Paramedic"]
)

selected_rig = st.sidebar.radio(
    "Active Ambulance Unit",
    ["Rig #356", "Rig #357"]
)


# ============================================================
# 6. BACKUP UTILITY
# ============================================================

st.sidebar.markdown("---")
st.sidebar.subheader("💾 Backup Utility")

json_string = json.dumps(
    st.session_state["inventory"],
    indent=4
)

st.sidebar.download_button(
    label="⬇️ Download Backup Database",
    data=json_string,
    file_name="ambulance_med_data.json",
    mime="application/json"
)


# ============================================================
# 7. DATE CALCULATIONS
# ============================================================

today = datetime.date.today()

fifteen_days_out = today + datetime.timedelta(days=15)


# ============================================================
# 8. BUILD CURRENT VIEW
# ============================================================

raw_inventory = st.session_state["inventory"][selected_rig]

visible_meds = build_visible_medication_list(
    selected_rig,
    user_role
)


# ============================================================
# 9. COMPUTE ALERTS
# ============================================================

empty_meds = []
low_meds = []
expiring_meds = []
all_expiration_dates = []


for med in visible_meds:

    try:
        exp_date = datetime.datetime.strptime(
            med["expiry"],
            "%Y-%m-%d"
        ).date()

        all_expiration_dates.append(exp_date)

    except ValueError:
        continue

    # Inventory alerts
    if med["count"] == 0:
        empty_meds.append(med["name"])

    elif med["count"] == 1:
        low_meds.append(med["name"])

    # Expiration alert
    if exp_date <= fifteen_days_out:
        expiring_meds.append(
            "%s (%s)" % (
                med["name"],
                med["expiry"]
            )
        )


if all_expiration_dates:
    earliest_expiry_date = min(all_expiration_dates)
else:
    earliest_expiry_date = "N/A"


# ============================================================
# 10. METRICS & ALERTS
# ============================================================

st.subheader("⚠️ Critical Discrepancy & Expiration Logs")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Earliest Expiration Date",
    str(earliest_expiry_date)
)

col2.error(
    "🚨 Out of Stock (%d)" % len(empty_meds)
)

col3.warning(
    "⚠️ Low Inventory (%d)" % len(low_meds)
)

col4.info(
    "⏳ Expiring Soon (%d)" % len(expiring_meds)
)


if empty_meds:
    st.error(
        "**CRITICAL - EMPTY:** %s"
        % ", ".join(empty_meds)
    )


if low_meds:
    st.warning(
        "**NOTICE - LOW STOCK (1 Left):** %s"
        % ", ".join(low_meds)
    )


if expiring_meds:
    st.info(
        "**NOTICE - EXPIRING < 15 DAYS:** %s"
        % ", ".join(expiring_meds)
    )


st.divider()


# ============================================================
# 11. INTERACTIVE MEDICATION GRID
# ============================================================

st.subheader(
    "📊 Active Operations Grid — %s"
    % selected_rig
)

st.markdown(
    "Adjust quantities and expiration dates directly "
    "inside the data grid below:"
)


edited_data = st.data_editor(
    visible_meds,

    column_config={
        "id": st.column_config.TextColumn(
            "Medication ID",
            disabled=True
        ),

        "name": st.column_config.TextColumn(
            "Medication Name",
            disabled=True
        ),

        "count": st.column_config.NumberColumn(
            "Quantity on Hand",
            min_value=0,
            step=1,
            required=True
        ),

        "expiry": st.column_config.TextColumn(
            "Expiration Date (YYYY-MM-DD)",
            required=True
        ),
    },

    hide_index=True,
    use_container_width=True,
    key="grid_editor"
)


# ============================================================
# 12. SAVE MATRIX CHANGES
# ============================================================

if st.button(
    "💾 Save Matrix Changes",
    type="primary"
):

    for updated_item in edited_data:

        med_id = updated_item["id"]

        if med_id in raw_inventory:

            raw_inventory[med_id]["count"] = (
                updated_item["count"]
            )

            raw_inventory[med_id]["expiry"] = (
                updated_item["expiry"]
            )

    st.success(
        "✅ Changes committed to current session cache successfully!"
    )

    st.rerun()


st.divider()


# ============================================================
# 13. SHIFT SUMMARY
# ============================================================

st.subheader("📋 Shift Summary Text Exporter")

st.info(
    "Shift Summary functionality will be added in the next development step."
)
```
