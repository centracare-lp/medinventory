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

# Min/max are operational targets, not clinical dosing guidance.
# They are initialized from the existing inventory so the upgrade
# does not unexpectedly change the current stock levels. Set the
# desired minimum and maximum for each medication in the grid.
for rig in INITIAL_INVENTORY:
    for med_id, item in INITIAL_INVENTORY[rig].items():
        item.setdefault("min", 0)
        item.setdefault("max", item["count"])
        item.setdefault("usage", 0)
        item.setdefault("restocked", 0)

if "inventory" not in st.session_state:
    st.session_state["inventory"] = copy.deepcopy(INITIAL_INVENTORY)

if "shift_usage" not in st.session_state:
    st.session_state["shift_usage"] = {}

if "shift_restock" not in st.session_state:
    st.session_state["shift_restock"] = {}

if "activity_log" not in st.session_state:
    st.session_state["activity_log"] = []


# ============================================================
# 4. HELPER FUNCTIONS
# ============================================================

def build_visible_medication_list(rig, user_role):
    """Return the selected rig's medications in data-editor format."""
    visible = []

    for med_id, med_info in MEDICATIONS.items():
        if med_id not in st.session_state["inventory"][rig]:
            continue

        if med_info["controlled"] and user_role == "EMT / Basic":
            continue

        item = st.session_state["inventory"][rig][med_id]
        visible.append({
            "id": med_id,
            "name": med_info["name"],
            "min": item.get("min", 0),
            "max": item.get("max", item["count"]),
            "count": item["count"],
            "expiry": item["expiry"],
        })

    return visible


def visible_med_ids(rig, user_role):
    return [item["id"] for item in build_visible_medication_list(rig, user_role)]


def record_activity(rig, med_id, activity_type, quantity):
    """Record a usage/restock event for the active shift."""
    target = (
        st.session_state["shift_usage"]
        if activity_type == "usage"
        else st.session_state["shift_restock"]
    )

    key = (rig, med_id)
    target[key] = target.get(key, 0) + quantity

    st.session_state["activity_log"].append({
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "rig": rig,
        "med_id": med_id,
        "medication": MEDICATIONS[med_id]["name"],
        "type": activity_type,
        "quantity": quantity,
    })


def get_status(item):
    """Return a simple min/max inventory status."""
    count = item["count"]
    minimum = item.get("min", 0)
    maximum = item.get("max", count)

    if count <= minimum:
        return "🔴 At/Below Min"
    if count < maximum:
        return "🟡 Below Max"
    return "🟢 At Max"


def build_shift_summary(rig, user_role):
    """Create a plain-text summary suitable for copying or exporting."""
    inventory = st.session_state["inventory"][rig]
    usage = st.session_state["shift_usage"]
    restock = st.session_state["shift_restock"]

    lines = [
        f"AMBULANCE MEDICATION SHIFT SUMMARY — {rig}",
        f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "MEDICATION USAGE",
        "----------------",
    ]

    usage_rows = []
    for med_id, med_info in MEDICATIONS.items():
        if med_id not in inventory:
            continue
        if med_info["controlled"] and user_role == "EMT / Basic":
            continue
        qty = usage.get((rig, med_id), 0)
        if qty:
            usage_rows.append((med_info["name"], qty))

    if usage_rows:
        lines.extend(f"{name}: {qty}" for name, qty in usage_rows)
    else:
        lines.append("None recorded")

    lines.extend(["", "RESTOCK ACTIVITY", "-----------------"])

    restock_rows = []
    for med_id, med_info in MEDICATIONS.items():
        if med_id not in inventory:
            continue
        if med_info["controlled"] and user_role == "EMT / Basic":
            continue
        qty = restock.get((rig, med_id), 0)
        if qty:
            restock_rows.append((med_info["name"], qty))

    if restock_rows:
        lines.extend(f"{name}: {qty}" for name, qty in restock_rows)
    else:
        lines.append("None recorded")

    lines.extend(["", "RESTOCK NEEDED", "--------------"])

    needs_restock = []
    for med_id, med_info in MEDICATIONS.items():
        if med_id not in inventory:
            continue
        if med_info["controlled"] and user_role == "EMT / Basic":
            continue
        item = inventory[med_id]
        needed = max(0, item.get("max", item["count"]) - item["count"])
        if needed:
            needs_restock.append((med_info["name"], needed))

    if needs_restock:
        lines.extend(f"{name}: {qty}" for name, qty in needs_restock)
    else:
        lines.append("None")

    return "\n".join(lines)


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

backup_data = {
    "inventory": st.session_state["inventory"],
    "shift_usage": st.session_state["shift_usage"],
    "shift_restock": st.session_state["shift_restock"],
    "activity_log": st.session_state["activity_log"],
}

# Convert tuple keys to strings so the backup is valid JSON.
backup_data["shift_usage"] = {
    f"{rig}|{med_id}": qty
    for (rig, med_id), qty in st.session_state["shift_usage"].items()
}
backup_data["shift_restock"] = {
    f"{rig}|{med_id}": qty
    for (rig, med_id), qty in st.session_state["shift_restock"].items()
}

json_string = json.dumps(backup_data, indent=4)

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
visible_meds = build_visible_medication_list(selected_rig, user_role)


# ============================================================
# 9. COMPUTE ALERTS
# ============================================================

empty_meds = []
min_meds = []
expiring_meds = []
all_expiration_dates = []

for med in visible_meds:
    item = raw_inventory[med["id"]]

    try:
        exp_date = datetime.datetime.strptime(
            med["expiry"], "%Y-%m-%d"
        ).date()
        all_expiration_dates.append(exp_date)
    except ValueError:
        continue

    if med["count"] == 0:
        empty_meds.append(med["name"])

    if med["count"] <= med["min"]:
        min_meds.append(med["name"])

    if exp_date <= fifteen_days_out:
        expiring_meds.append(
            "%s (%s)" % (med["name"], med["expiry"])
        )

if all_expiration_dates:
    earliest_expiry_date = min(all_expiration_dates)
else:
    earliest_expiry_date = "N/A"


# ============================================================
# 10. METRICS & ALERTS
# ============================================================

st.subheader("⚠️ Inventory & Expiration Status")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Earliest Expiration Date", str(earliest_expiry_date))
col2.error("🚨 Out of Stock (%d)" % len(empty_meds))
col3.warning("⚠️ At/Below Min (%d)" % len(min_meds))
col4.info("⏳ Expiring Soon (%d)" % len(expiring_meds))

if empty_meds:
    st.error("**CRITICAL - EMPTY:** %s" % ", ".join(empty_meds))

if min_meds:
    st.warning("**NOTICE - AT/BELOW MIN:** %s" % ", ".join(min_meds))

if expiring_meds:
    st.info("**NOTICE - EXPIRING < 15 DAYS:** %s" % ", ".join(expiring_meds))

st.divider()


# ============================================================
# 11. INVENTORY / MIN-MAX GRID
# ============================================================

st.subheader("📊 Active Operations Grid — %s" % selected_rig)
st.markdown(
    "Set the operational **Min/Max**, current quantity, and expiration date. "
    "Usage and restocking are recorded separately below."
)

edited_data = st.data_editor(
    visible_meds,
    column_config={
        "id": st.column_config.TextColumn("Medication ID", disabled=True),
        "name": st.column_config.TextColumn("Medication Name", disabled=True),
        "min": st.column_config.NumberColumn(
            "Min", min_value=0, step=1, required=True
        ),
        "max": st.column_config.NumberColumn(
            "Max", min_value=0, step=1, required=True
        ),
        "count": st.column_config.NumberColumn(
            "Current", min_value=0, step=1, required=True
        ),
        "expiry": st.column_config.TextColumn(
            "Expiration Date (YYYY-MM-DD)", required=True
        ),
    },
    hide_index=True,
    use_container_width=True,
    key=f"grid_editor_{selected_rig}"
)

if st.button("💾 Save Inventory / Min-Max Changes", type="primary"):
    validation_errors = []

    for updated_item in edited_data:
        med_id = updated_item["id"]
        if med_id not in raw_inventory:
            continue

        minimum = int(updated_item["min"])
        maximum = int(updated_item["max"])
        current = int(updated_item["count"])

        if maximum < minimum:
            validation_errors.append(
                f"{updated_item['name']}: Max cannot be less than Min."
            )
            continue

        try:
            datetime.datetime.strptime(updated_item["expiry"], "%Y-%m-%d")
        except ValueError:
            validation_errors.append(
                f"{updated_item['name']}: Expiration must be YYYY-MM-DD."
            )
            continue

        raw_inventory[med_id]["min"] = minimum
        raw_inventory[med_id]["max"] = maximum
        raw_inventory[med_id]["count"] = current
        raw_inventory[med_id]["expiry"] = updated_item["expiry"]

    if validation_errors:
        for error in validation_errors:
            st.error(error)
    else:
        st.success("✅ Inventory and Min/Max changes saved.")
        st.rerun()


# ============================================================
# 12. SEPARATE USAGE & RESTOCK
# ============================================================

st.divider()
st.subheader("💉 Medication Usage")
st.caption("Record medication removed/used during the shift. This decreases Current inventory and is tracked separately from restocking.")

available_ids = visible_med_ids(selected_rig, user_role)

if available_ids:
    usage_med_id = st.selectbox(
        "Medication Used",
        available_ids,
        format_func=lambda med_id: MEDICATIONS[med_id]["name"],
        key="usage_med"
    )
    usage_qty = st.number_input(
        "Quantity Used",
        min_value=1,
        step=1,
        value=1,
        key="usage_qty"
    )

    if st.button("➖ Record Usage"):
        current_count = raw_inventory[usage_med_id]["count"]
        if usage_qty > current_count:
            st.error(
                f"Cannot record {usage_qty}. Only {current_count} on hand."
            )
        else:
            raw_inventory[usage_med_id]["count"] = current_count - usage_qty
            raw_inventory[usage_med_id]["usage"] = (
                raw_inventory[usage_med_id].get("usage", 0) + usage_qty
            )
            record_activity(selected_rig, usage_med_id, "usage", usage_qty)
            st.success(
                f"Recorded {usage_qty} × {MEDICATIONS[usage_med_id]['name']} as used."
            )
            st.session_state.pop(f"grid_editor_{selected_rig}", None)
            st.rerun()


st.subheader("📦 Medication Restock")
st.caption("Record medication added to the rig. Restocking is tracked separately from usage and increases Current inventory.")

if available_ids:
    restock_med_id = st.selectbox(
        "Medication Restocked",
        available_ids,
        format_func=lambda med_id: MEDICATIONS[med_id]["name"],
        key="restock_med"
    )
    restock_qty = st.number_input(
        "Quantity Restocked",
        min_value=1,
        step=1,
        value=1,
        key="restock_qty"
    )

    if st.button("➕ Record Restock"):
        raw_inventory[restock_med_id]["count"] += restock_qty
        raw_inventory[restock_med_id]["restocked"] = (
            raw_inventory[restock_med_id].get("restocked", 0) + restock_qty
        )
        record_activity(selected_rig, restock_med_id, "restock", restock_qty)
        st.success(
            f"Recorded {restock_qty} × {MEDICATIONS[restock_med_id]['name']} as restocked."
        )
        st.session_state.pop(f"grid_editor_{selected_rig}", None)
        st.rerun()


# ============================================================
# 13. RESTOCK NEEDS
# ============================================================

st.divider()
st.subheader("📦 Restock Needs")

restock_rows = []
for med in visible_meds:
    item = raw_inventory[med["id"]]
    needed = max(0, item.get("max", item["count"]) - item["count"])
    if needed > 0:
        restock_rows.append({
            "Medication": med["name"],
            "Current": item["count"],
            "Min": item.get("min", 0),
            "Max": item.get("max", item["count"]),
            "Restock Needed": needed,
            "Status": get_status(item),
        })

if restock_rows:
    st.dataframe(restock_rows, hide_index=True, use_container_width=True)
else:
    st.success("✅ All visible medications are at their Max target.")


# ============================================================
# 14. SHIFT SUMMARY
# ============================================================

st.divider()
st.subheader("📋 Shift Summary Text Exporter")

summary_text = build_shift_summary(selected_rig, user_role)
st.text_area("Shift Summary", summary_text, height=350)

st.download_button(
    label="⬇️ Download Shift Summary",
    data=summary_text,
    file_name=f"{selected_rig.replace('#', '').replace(' ', '_')}_shift_summary.txt",
    mime="text/plain"
)


# ============================================================
# 15. SHIFT ACTIVITY LOG
# ============================================================

with st.expander("📝 View Shift Activity Log"):
    rig_activity = [
        event for event in st.session_state["activity_log"]
        if event["rig"] == selected_rig
    ]

    if rig_activity:
        st.dataframe(
            list(reversed(rig_activity)),
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No usage or restock activity has been recorded for this rig yet.")

