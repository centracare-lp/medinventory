from pathlib import Path
import streamlit as st
import datetime
import json
import copy
import hashlib


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


# ============================================================
# PERSISTENT USER DATABASE & PERMISSIONS
# ============================================================
#
# Streamlit Community Cloud uses an ephemeral filesystem. A local
# users.json file can therefore be lost when the app is redeployed
# or the container is restarted.
#
# User accounts are stored in Supabase instead. Configure these
# secrets in Streamlit Cloud:
#
# [supabase]
# url = "https://YOUR_PROJECT.supabase.co"
# service_role_key = "YOUR_SERVICE_ROLE_KEY"
#
# See the included supabase_users_schema.sql file for the table
# definition.
# ============================================================

import requests

SUPABASE_URL = st.secrets.get("supabase", {}).get("url", "").rstrip("/")
SUPABASE_SERVICE_ROLE_KEY = st.secrets.get("supabase", {}).get(
    "service_role_key", ""
)
SUPABASE_TABLE = "app_users"

PERMISSION_LABELS = {
    "manage_users": "Manage users",
    "manage_minmax": "Manage medication Min/Max",
    "edit_inventory": "Edit inventory",
    "record_usage": "Record medication usage",
    "record_restock": "Record medication restock",
}

DEFAULT_ADMIN = {
    "name": "Administrator",
    "initials": "ADM",
    "pin_hash": hashlib.sha256("1234".encode()).hexdigest(),
    "permissions": list(PERMISSION_LABELS.keys()),
    "active": True,
}

def hash_pin(pin):
    return hashlib.sha256(str(pin).encode()).hexdigest()

def supabase_configured():
    return bool(SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY)

def supabase_headers():
    return {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
    }

def load_users():
    """Load authorized users from the persistent Supabase database."""
    if not supabase_configured():
        st.error(
            "Persistent user database is not configured. "
            "Add [supabase] url and service_role_key to Streamlit Secrets."
        )
        return []

    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}",
            headers={**supabase_headers(), "Accept": "application/json"},
            params={
                "select": "name,initials,pin_hash,permissions,active",
                "order": "initials.asc",
            },
            timeout=10,
        )
        response.raise_for_status()
        rows = response.json()

        if not isinstance(rows, list):
            raise ValueError("Supabase returned an invalid user database.")

        users = []
        for row in rows:
            users.append({
                "name": row["name"],
                "initials": row["initials"],
                "pin_hash": row["pin_hash"],
                "permissions": row.get("permissions") or [],
                "active": bool(row.get("active", True)),
            })

        # Bootstrap the first administrator if the table is empty.
        if not users:
            if save_users([copy.deepcopy(DEFAULT_ADMIN)]):
                return [copy.deepcopy(DEFAULT_ADMIN)]
            return []

        return users

    except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
        st.error(
            "Unable to load the persistent user database from Supabase. "
            f"Details: {exc}"
        )
        return []

def save_users(users):
    """Persist the complete in-memory user list to Supabase."""
    if not supabase_configured():
        st.error(
            "Cannot save users because the Supabase database is not configured."
        )
        return False

    rows = [
        {
            "name": user["name"],
            "initials": user["initials"].upper(),
            "pin_hash": user["pin_hash"],
            "permissions": user.get("permissions", []),
            "active": bool(user.get("active", True)),
        }
        for user in users
    ]

    try:
        # Upsert by initials. This keeps accounts persistent across
        # Streamlit restarts and deployments.
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}",
            headers={
                **supabase_headers(),
                "Prefer": "resolution=merge-duplicates,return=minimal",
            },
            json=rows,
            timeout=10,
        )
        response.raise_for_status()
        return True

    except requests.RequestException as exc:
        st.error(
            "Unable to save the user database to Supabase. "
            f"Details: {exc}"
        )
        return False

def current_user():
    return st.session_state.get("current_user")

def has_permission(permission):
    user = current_user()
    return bool(
        user
        and user.get("active", False)
        and permission in user.get("permissions", [])
    )

if "users" not in st.session_state:
    st.session_state.users = load_users()

st.session_state.setdefault("current_user", None)
st.session_state.setdefault("minmax_unlocked", False)


# ============================================================
# USER ACCESS / USER MANAGEMENT
# ============================================================
with st.sidebar.expander("👤 User Access", expanded=True):
    user = current_user()

    if user:
        st.success(f"Signed in: {user['name']} ({user['initials']})")
        if st.button("🔒 Sign Out", key="sign_out"):
            st.session_state.current_user = None
            st.session_state.minmax_unlocked = False
            st.rerun()
    else:
        login_initials = st.text_input(
            "Initials", max_chars=5, key="login_initials"
        ).strip().upper()
        login_pin = st.text_input("PIN", type="password", key="login_pin")

        if st.button("Sign In", key="sign_in"):
            match = next(
                (
                    u for u in st.session_state.users
                    if u["active"]
                    and u["initials"].upper() == login_initials
                    and u["pin_hash"] == hash_pin(login_pin)
                ),
                None,
            )
            if match:
                st.session_state.current_user = copy.deepcopy(match)
                st.session_state.minmax_unlocked = False
                st.rerun()
            else:
                st.error("Invalid initials or PIN.")

    if has_permission("manage_users"):
        st.divider()
        st.subheader("User Management")

        with st.form("add_user_form", clear_on_submit=True):
            new_name = st.text_input("Name")
            new_initials = st.text_input(
                "Initials", max_chars=5
            ).strip().upper()
            new_pin = st.text_input("PIN", type="password")
            new_pin_confirm = st.text_input(
                "Confirm PIN", type="password"
            )
            new_permissions = st.multiselect(
                "Permissions",
                list(PERMISSION_LABELS.keys()),
                format_func=lambda p: PERMISSION_LABELS[p],
                default=["record_usage", "record_restock"],
            )

            if st.form_submit_button("➕ Add Authorized User"):
                initials_used = {
                    u["initials"].upper() for u in st.session_state.users
                }

                if not new_name.strip() or not new_initials:
                    st.error("Name and initials are required.")
                elif new_initials in initials_used:
                    st.error("Those initials are already in use.")
                elif len(new_pin) < 4:
                    st.error("PIN must be at least 4 characters.")
                elif new_pin != new_pin_confirm:
                    st.error("PIN confirmation does not match.")
                else:
                    st.session_state.users.append({
                        "name": new_name.strip(),
                        "initials": new_initials,
                        "pin_hash": hash_pin(new_pin),
                        "permissions": new_permissions,
                        "active": True,
                    })
                    save_users(st.session_state.users)
                    st.success("Authorized user added.")
                    st.rerun()

        st.caption("Persistent database: Supabase")
        st.caption("PINs are stored as SHA-256 hashes.")
        st.caption("Authorized users")
        for i, managed_user in enumerate(st.session_state.users):
            with st.container(border=True):
                st.write(
                    f"**{managed_user['name']}** "
                    f"({managed_user['initials']})"
                )
                st.caption(
                    ", ".join(
                        PERMISSION_LABELS[p]
                        for p in managed_user["permissions"]
                        if p in PERMISSION_LABELS
                    ) or "No permissions"
                )

                left, right = st.columns(2)

                is_self = (
                    user is not None
                    and user["initials"] == managed_user["initials"]
                )

                with left:
                    if st.button(
                        "Disable" if managed_user["active"] else "Enable",
                        key=f"toggle_user_{i}",
                        disabled=is_self,
                    ):
                        st.session_state.users[i]["active"] = (
                            not managed_user["active"]
                        )
                        save_users(st.session_state.users)
                        st.rerun()

                with right:
                    if st.button(
                        "Reset PIN", key=f"reset_pin_button_{i}"
                    ):
                        st.session_state[f"reset_pin_open_{i}"] = True

                if st.session_state.get(f"reset_pin_open_{i}", False):
                    with st.form(f"reset_pin_form_{i}"):
                        p1 = st.text_input(
                            "New PIN", type="password"
                        )
                        p2 = st.text_input(
                            "Confirm New PIN", type="password"
                        )

                        if st.form_submit_button("Save New PIN"):
                            if len(p1) < 4:
                                st.error("PIN must be at least 4 characters.")
                            elif p1 != p2:
                                st.error("PIN confirmation does not match.")
                            else:
                                st.session_state.users[i]["pin_hash"] = hash_pin(p1)
                                save_users(st.session_state.users)
                                st.session_state.pop(
                                    f"reset_pin_open_{i}", None
                                )
                                st.success("PIN reset.")
                                st.rerun()

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


# ============================================================
# MIN/MAX ADMIN LOCK
# ============================================================
if has_permission("manage_minmax"):
    st.sidebar.divider()
    st.sidebar.subheader("🔐 Min/Max Settings")

    if st.session_state.minmax_unlocked:
        st.sidebar.success("Min/Max editing is UNLOCKED.")
        if st.sidebar.button(
            "🔒 Lock Min/Max", key="lock_minmax"
        ):
            st.session_state.minmax_unlocked = False
            st.rerun()
    else:
        if st.sidebar.button(
            "🔓 Unlock Min/Max", key="unlock_minmax"
        ):
            st.session_state.minmax_unlocked = True
            st.rerun()
else:
    st.sidebar.caption(
        "Min/Max settings are restricted to users with the "
        "'Manage medication Min/Max' permission."
    )

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
            "Min",
            min_value=0,
            step=1,
            required=True,
            disabled=not (
                has_permission("manage_minmax")
                and st.session_state.get("minmax_unlocked", False)
            ),
        ),
        "max": st.column_config.NumberColumn(
            "Max",
            min_value=0,
            step=1,
            required=True,
            disabled=not (
                has_permission("manage_minmax")
                and st.session_state.get("minmax_unlocked", False)
            ),
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
    disabled=not has_permission("edit_inventory"),
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

        if has_permission("manage_minmax") and st.session_state.get("minmax_unlocked", False):
            raw_inventory[med_id]["min"] = minimum
            raw_inventory[med_id]["max"] = maximum

        if has_permission("edit_inventory"):
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

    if st.button(
        "➖ Record Usage",
        disabled=not has_permission("record_usage"),
    ):
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

    if st.button(
        "➕ Record Restock",
        disabled=not has_permission("record_restock"),
    ):
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

