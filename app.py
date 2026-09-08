from pathlib import Path
import streamlit as st
import datetime
import json
import copy
import hashlib
from urllib.parse import urlparse
import requests

st.set_page_config(page_title="Ambulance Medication Inventory", page_icon="💊", layout="wide")

# ============================================================
# 1. MASTER MEDICATION DEFINITIONS
# ============================================================
# The original file lost this section.  Keep the master list here;
# inventory for each rig is generated separately below.
# "controlled" hides the medication from EMT / Basic users.
# ============================================================

MEDICATION_DEFINITIONS = [
    ("adenosine", "Adenosine", False, 2, 4),
    ("albuterol", "Albuterol", False, 2, 6),
    ("amiodarone", "Amiodarone", False, 2, 4),
    ("aspirin", "Aspirin", False, 2, 10),
    ("atropine", "Atropine", False, 2, 4),
    ("calcium_chloride", "Calcium Chloride", False, 1, 2),
    ("dextrose", "Dextrose", False, 2, 6),
    ("diltiazem", "Diltiazem", False, 2, 4),
    ("diphenhydramine", "Diphenhydramine", False, 2, 6),
    ("epinephrine_1_1000", "Epinephrine 1 mg/mL (1:1,000)", False, 4, 10),
    ("epinephrine_1_10000", "Epinephrine 0.1 mg/mL (1:10,000)", False, 2, 6),
    ("famotidine", "Famotidine", False, 2, 4),
    ("fentanyl", "Fentanyl", True, 2, 6),
    ("glucagon", "Glucagon", False, 1, 2),
    ("haloperidol", "Haloperidol", False, 2, 4),
    ("hydroxocobalamin", "Hydroxocobalamin", False, 0, 1),
    ("ipratropium", "Ipratropium", False, 2, 6),
    ("ketamine", "Ketamine", True, 1, 4),
    ("labetalol", "Labetalol", False, 2, 4),
    ("lactated_ringers", "Lactated Ringers", False, 2, 6),
    ("magnesium_sulfate", "Magnesium Sulfate", False, 2, 4),
    ("methylprednisolone", "Methylprednisolone", False, 2, 4),
    ("midazolam", "Midazolam", True, 2, 6),
    ("naloxone", "Naloxone", False, 2, 6),
    ("nitroglycerin", "Nitroglycerin", False, 2, 10),
    ("norepinephrine", "Norepinephrine", False, 2, 4),
    ("ondansetron", "Ondansetron", False, 2, 6),
    ("oxytocin", "Oxytocin", False, 1, 2),
    ("procainamide", "Procainamide", False, 1, 2),
    ("prochlorperazine", "Prochlorperazine", False, 1, 2),
    ("propofol", "Propofol", True, 1, 2),
    ("sodium_bicarbonate", "Sodium Bicarbonate", False, 2, 4),
    ("sterile_water", "Sterile Water", False, 1, 4),
    ("thiamine", "Thiamine", False, 1, 2),
    ("tranexamic_acid", "Tranexamic Acid (TXA)", False, 1, 2),
    ("valproate", "Valproate", False, 1, 2),
    ("diazepam", "Diazepam (Valium)", True, 1, 4),
    ("hydromorphone", "Hydromorphone (Dilaudid)", True, 1, 4),
    ("morphine", "Morphine", True, 1, 4),
    ("ketorolac", "Ketorolac", False, 2, 6),
    ("epinephrine_autoinjector", "Epinephrine Auto-Injector", False, 1, 2),
    ("glucose_gel", "Oral Glucose Gel", False, 1, 4),
]

MEDICATIONS = {
    med_id: {
        "id": med_id,
        "name": name,
        "controlled": controlled,
        "min": minimum,
        "max": maximum,
    }
    for med_id, name, controlled, minimum, maximum in MEDICATION_DEFINITIONS
}

RIGS = ["Rig #356", "Rig #357"]

# ============================================================
# 2. INVENTORY INITIALIZATION
# ============================================================
# The missing original inventory foundation caused the KeyError.
# New installations start with zero stock so nobody accidentally
# assumes a quantity that has not been verified.  Expiration defaults
# to one year from today and can be replaced in the grid/restock form.
# ============================================================

def default_expiry():
    return (datetime.date.today() + datetime.timedelta(days=365)).isoformat()


def build_empty_inventory():
    return {
        med_id: {
            "count": 0,
            "min": med["min"],
            "max": med["max"],
            "expiry": default_expiry(),
            "usage": 0,
            "restocked": 0,
        }
        for med_id, med in MEDICATIONS.items()
    }


def build_initial_inventory():
    return {rig: build_empty_inventory() for rig in RIGS}


def normalize_inventory(data):
    """Repair old/missing inventory records without destroying valid data."""
    if not isinstance(data, dict):
        data = {}
    normalized = {}
    for rig in RIGS:
        source = data.get(rig, {})
        normalized[rig] = {}
        for med_id, med in MEDICATIONS.items():
            old = source.get(med_id, {}) if isinstance(source, dict) else {}
            normalized[rig][med_id] = {
                "count": max(0, int(old.get("count", 0))),
                "min": max(0, int(old.get("min", med["min"]))),
                "max": max(0, int(old.get("max", med["max"]))),
                "expiry": str(old.get("expiry", default_expiry())),
                "usage": max(0, int(old.get("usage", 0))),
                "restocked": max(0, int(old.get("restocked", 0))),
            }
            if normalized[rig][med_id]["max"] < normalized[rig][med_id]["min"]:
                normalized[rig][med_id]["max"] = normalized[rig][med_id]["min"]
    return normalized


def initialize_inventory_state():
    if "inventory" not in st.session_state:
        st.session_state.inventory = build_initial_inventory()
    else:
        st.session_state.inventory = normalize_inventory(st.session_state.inventory)

    st.session_state.setdefault("shift_usage", {})
    st.session_state.setdefault("shift_restock", {})
    st.session_state.setdefault("activity_log", [])
    st.session_state.setdefault("minmax_unlocked", False)


# ============================================================
# 3. PERSISTENT USER DATABASE & PERMISSIONS
# ============================================================

SUPABASE_URL = st.secrets.get("supabase", {}).get("url", "").strip().rstrip("/")
SUPABASE_SERVICE_ROLE_KEY = st.secrets.get("supabase", {}).get("service_role_key", "").strip()
SUPABASE_TABLE = "app_users"


def validate_supabase_url(url):
    if not url:
        return "", "Supabase URL is missing from Streamlit Secrets."
    if not url.startswith(("https://", "http://")):
        url = "https://" + url
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        return "", "Supabase URL must look like https://YOUR_PROJECT_REF.supabase.co"
    host = parsed.netloc.lower()
    if not host.endswith(".supabase.co") or any(ch in host for ch in [" ", "=", '"', "'", "<", ">", "\t", "\r", "\n"]):
        return "", "The Supabase URL is invalid. Use the Project URL from Supabase → Settings → API."
    if parsed.path not in ("", "/") or parsed.query or parsed.fragment:
        return "", "Supabase URL should contain only the project URL."
    return url.rstrip("/"), ""


SUPABASE_URL, SUPABASE_URL_ERROR = validate_supabase_url(SUPABASE_URL)

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
    return bool(SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY and not SUPABASE_URL_ERROR)


def supabase_headers():
    return {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
    }


def load_users():
    if not supabase_configured():
        return []
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}",
            headers={**supabase_headers(), "Accept": "application/json"},
            params={"select": "name,initials,pin_hash,permissions,active", "order": "initials.asc"},
            timeout=10,
        )
        response.raise_for_status()
        rows = response.json()
        if not isinstance(rows, list):
            raise ValueError("Supabase returned an invalid user database.")
        users = [
            {
                "name": row["name"],
                "initials": row["initials"],
                "pin_hash": row["pin_hash"],
                "permissions": row.get("permissions") or [],
                "active": bool(row.get("active", True)),
            }
            for row in rows
        ]
        if not users:
            if save_users([copy.deepcopy(DEFAULT_ADMIN)]):
                return [copy.deepcopy(DEFAULT_ADMIN)]
        return users
    except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
        st.error(f"Unable to load the persistent user database from Supabase. Details: {exc}")
        return []


def save_users(users):
    if not supabase_configured():
        st.error("Cannot save users because the Supabase database is not configured.")
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
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}",
            headers={**supabase_headers(), "Prefer": "resolution=merge-duplicates,return=minimal"},
            json=rows,
            timeout=10,
        )
        response.raise_for_status()
        return True
    except requests.RequestException as exc:
        st.error(f"Unable to save the user database to Supabase. Details: {exc}")
        return False


def current_user():
    return st.session_state.get("current_user")


def has_permission(permission):
    user = current_user()
    return bool(user and user.get("active", False) and permission in user.get("permissions", []))


def is_mobile_device():
    """Best-effort device detection so phones get a purpose-built compact UI."""
    try:
        user_agent = st.context.headers.get("User-Agent", "").lower()
        mobile_terms = (
            "android", "iphone", "ipad", "ipod", "mobile",
            "windows phone", "opera mini", "iemobile"
        )
        return any(term in user_agent for term in mobile_terms)
    except Exception:
        return False


if "users" not in st.session_state:
    st.session_state.users = load_users()
st.session_state.setdefault("current_user", None)
initialize_inventory_state()

# ============================================================
# 4. HELPERS
# ============================================================

def visible_med_ids(rig, role):
    del rig  # reserved for future rig-specific medication rules
    return [
        med_id for med_id, med in MEDICATIONS.items()
        if role == "Paramedic" or not med["controlled"]
    ]


def build_visible_medication_list(rig, role):
    return [
        {
            "id": med_id,
            "name": MEDICATIONS[med_id]["name"],
            "min": st.session_state.inventory[rig][med_id]["min"],
            "max": st.session_state.inventory[rig][med_id]["max"],
            "count": st.session_state.inventory[rig][med_id]["count"],
            "expiry": st.session_state.inventory[rig][med_id]["expiry"],
        }
        for med_id in visible_med_ids(rig, role)
    ]


def record_activity(rig, med_id, action, quantity, expiration=None):
    event = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": (current_user() or {}).get("initials", "SYSTEM"),
        "rig": rig,
        "medication": MEDICATIONS[med_id]["name"],
        "medication_id": med_id,
        "action": action,
        "quantity": int(quantity),
    }
    if expiration:
        event["expiration"] = expiration
    st.session_state.activity_log.append(event)


def get_status(item):
    count = int(item.get("count", 0))
    minimum = int(item.get("min", 0))
    if count == 0:
        return "OUT OF STOCK"
    if count <= minimum:
        return "AT / BELOW MIN"
    return "OK"


def shift_totals(rig, med_id, action):
    store = st.session_state.shift_usage if action == "usage" else st.session_state.shift_restock
    return store.get((rig, med_id), 0)


def build_shift_summary(rig, role):
    inventory = st.session_state.inventory[rig]
    ids = visible_med_ids(rig, role)
    lines = [
        f"AMBULANCE MEDICATION SHIFT SUMMARY — {rig}",
        f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Certification view: {role}",
        "",
        "CURRENT INVENTORY",
        "Medication | Current | Min | Max | Expiration | Status",
        "-" * 90,
    ]
    for med_id in ids:
        item = inventory[med_id]
        lines.append(
            f"{MEDICATIONS[med_id]['name']} | {item['count']} | {item['min']} | {item['max']} | {item['expiry']} | {get_status(item)}"
        )
    lines.extend(["", "SHIFT ACTIVITY"])
    activity = [e for e in st.session_state.activity_log if e["rig"] == rig]
    if activity:
        for event in reversed(activity[-50:]):
            lines.append(
                f"{event['timestamp']} | {event['user']} | {event['action'].upper()} | {event['medication']} | {event['quantity']}"
            )
    else:
        lines.append("No usage or restock activity recorded.")
    return "\n".join(lines)


def parse_date(value):
    try:
        return datetime.datetime.strptime(str(value), "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


# ============================================================
# 5. LOGIN / USER ACCESS
# ============================================================
# Authentication is intentionally the first screen.  This is especially
# useful on phones, where the inventory should not be visible until the
# user has signed in.
# ============================================================

if not current_user():
    st.markdown("<div style='text-align:center; padding-top:2rem;'>", unsafe_allow_html=True)
    st.title("💊 Ambulance Medication Inventory")
    st.caption("Authorized Personnel Only")
    st.markdown("</div>", unsafe_allow_html=True)

    _, login_col, _ = st.columns([1, 2, 1])
    with login_col:
        with st.container(border=True):
            st.subheader("🔐 Sign In")
            login_initials = st.text_input(
                "Initials", max_chars=5, key="login_initials",
                placeholder="Enter your initials"
            ).strip().upper()
            login_pin = st.text_input(
                "PIN", type="password", key="login_pin",
                placeholder="Enter your PIN"
            )
            if st.button("🔓 Sign In", type="primary", use_container_width=True, key="sign_in"):
                match = next(
                    (
                        u for u in st.session_state.users
                        if u.get("active")
                        and u.get("initials", "").upper() == login_initials
                        and u.get("pin_hash") == hash_pin(login_pin)
                    ),
                    None,
                )
                if match:
                    st.session_state.current_user = copy.deepcopy(match)
                    st.session_state.minmax_unlocked = False
                    st.rerun()
                else:
                    st.error("Invalid initials or PIN.")
        st.caption("Authorized user accounts are managed by an administrator.")
    st.stop()

# ============================================================
# AUTHENTICATED USER MANAGEMENT
# ============================================================
with st.sidebar.expander("👤 User Access", expanded=True):
    user = current_user()
    st.success(f"Signed in: {user['name']} ({user['initials']})")
    if st.button("🔒 Sign Out", key="sign_out", use_container_width=True):
        st.session_state.current_user = None
        st.session_state.minmax_unlocked = False
        st.rerun()

    if has_permission("manage_users"):
        st.divider()
        st.subheader("User Management")
        with st.form("add_user_form", clear_on_submit=True):
            new_name = st.text_input("Name")
            new_initials = st.text_input("Initials", max_chars=5).strip().upper()
            new_pin = st.text_input("PIN", type="password")
            new_pin_confirm = st.text_input("Confirm PIN", type="password")
            new_permissions = st.multiselect(
                "Permissions",
                list(PERMISSION_LABELS.keys()),
                format_func=lambda p: PERMISSION_LABELS[p],
                default=["record_usage", "record_restock"],
            )
            if st.form_submit_button("➕ Add Authorized User"):
                initials_used = {u["initials"].upper() for u in st.session_state.users}
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
                    if save_users(st.session_state.users):
                        st.success("Authorized user added.")
                        st.rerun()

        for i, managed_user in enumerate(st.session_state.users):
            with st.container(border=True):
                st.write(f"**{managed_user['name']}** ({managed_user['initials']})")
                st.caption(
                    ", ".join(
                        PERMISSION_LABELS[p]
                        for p in managed_user.get("permissions", [])
                        if p in PERMISSION_LABELS
                    ) or "No permissions"
                )
                left, middle, right = st.columns(3)
                is_self = user["initials"] == managed_user["initials"]
                with left:
                    if st.button(
                        "Disable" if managed_user["active"] else "Enable",
                        key=f"toggle_user_{i}", disabled=is_self,
                    ):
                        st.session_state.users[i]["active"] = not managed_user["active"]
                        save_users(st.session_state.users)
                        st.rerun()
                with middle:
                    if st.button("Edit Access", key=f"edit_access_button_{i}"):
                        st.session_state[f"edit_access_open_{i}"] = not st.session_state.get(
                            f"edit_access_open_{i}", False
                        )
                with right:
                    if st.button("Reset PIN", key=f"reset_pin_button_{i}"):
                        st.session_state[f"reset_pin_open_{i}"] = True

                if st.session_state.get(f"edit_access_open_{i}", False):
                    with st.form(f"edit_access_form_{i}"):
                        current_permissions = [
                            p for p in managed_user.get("permissions", [])
                            if p in PERMISSION_LABELS
                        ]
                        edited_permissions = st.multiselect(
                            "Permissions",
                            list(PERMISSION_LABELS.keys()),
                            format_func=lambda p: PERMISSION_LABELS[p],
                            default=current_permissions,
                            key=f"edit_permissions_{i}",
                        )
                        if is_self:
                            st.caption(
                                "Your own Manage users permission cannot be removed here. "
                                "This prevents an administrator from accidentally locking themselves out."
                            )
                        if st.form_submit_button("💾 Save Access Changes"):
                            if is_self and "manage_users" not in edited_permissions:
                                st.error("Keep Manage users enabled for your own account.")
                            else:
                                st.session_state.users[i]["permissions"] = edited_permissions
                                if is_self:
                                    st.session_state.current_user = copy.deepcopy(st.session_state.users[i])
                                if save_users(st.session_state.users):
                                    st.success(f"Access updated for {managed_user['name']}.")
                                    st.session_state.pop(f"edit_access_open_{i}", None)
                                    st.rerun()

                if st.session_state.get(f"reset_pin_open_{i}", False):
                    with st.form(f"reset_pin_form_{i}"):
                        p1 = st.text_input("New PIN", type="password")
                        p2 = st.text_input("Confirm New PIN", type="password")
                        if st.form_submit_button("Save New PIN"):
                            if len(p1) < 4:
                                st.error("PIN must be at least 4 characters.")
                            elif p1 != p2:
                                st.error("PIN confirmation does not match.")
                            else:
                                st.session_state.users[i]["pin_hash"] = hash_pin(p1)
                                save_users(st.session_state.users)
                                st.session_state.pop(f"reset_pin_open_{i}", None)
                                st.success("PIN reset.")
                                st.rerun()

# ============================================================
# 6. OPERATIONS HUB
# ============================================================

mobile_device = is_mobile_device()

st.title("💊 Ambulance Medication Inventory")
st.caption("Operational medication inventory, usage, restocking, Min/Max controls, expiration tracking, and shift summaries.")

if mobile_device:
    st.info("📱 Mobile mode — simplified for quick use on a phone.")

with st.sidebar:
    st.header("🛡️ Operations Hub")
    user_role = st.selectbox("Select Your Certification Level", ["EMT / Basic", "Paramedic"])
    selected_rig = st.radio("Active Ambulance Unit", RIGS)

# ============================================================
# 6. BACKUP UTILITY
# ============================================================

st.sidebar.markdown("---")
st.sidebar.subheader("💾 Backup Utility")
backup_data = {
    "version": 2,
    "created": datetime.datetime.now().isoformat(timespec="seconds"),
    "inventory": st.session_state.inventory,
    "shift_usage": {f"{rig}|{med_id}": qty for (rig, med_id), qty in st.session_state.shift_usage.items()},
    "shift_restock": {f"{rig}|{med_id}": qty for (rig, med_id), qty in st.session_state.shift_restock.items()},
    "activity_log": st.session_state.activity_log,
}
st.sidebar.download_button(
    "⬇️ Download Backup Database",
    data=json.dumps(backup_data, indent=2),
    file_name="ambulance_med_data.json",
    mime="application/json",
)

# ============================================================
# 7. CURRENT VIEW / ALERTS
# ============================================================

raw_inventory = st.session_state.inventory[selected_rig]
visible_meds = build_visible_medication_list(selected_rig, user_role)
today = datetime.date.today()
fifteen_days_out = today + datetime.timedelta(days=15)

empty_meds, min_meds, expiring_meds, all_expiration_dates = [], [], [], []
for med in visible_meds:
    exp_date = parse_date(med["expiry"])
    if exp_date:
        all_expiration_dates.append(exp_date)
        if exp_date <= fifteen_days_out:
            expiring_meds.append(f"{med['name']} ({med['expiry']})")
    if med["count"] == 0:
        empty_meds.append(med["name"])
    if med["count"] <= med["min"]:
        min_meds.append(med["name"])

st.subheader("⚠️ Inventory & Expiration Status")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Earliest Expiration Date", str(min(all_expiration_dates)) if all_expiration_dates else "N/A")
col2.metric("🚨 Out of Stock", len(empty_meds))
col3.metric("⚠️ At/Below Min", len(min_meds))
col4.metric("⏳ Expiring ≤ 15 Days", len(expiring_meds))
if empty_meds:
    st.error("**CRITICAL — EMPTY:** " + ", ".join(empty_meds))
if min_meds:
    st.warning("**NOTICE — AT/BELOW MIN:** " + ", ".join(min_meds))
if expiring_meds:
    st.info("**NOTICE — EXPIRING ≤ 15 DAYS:** " + ", ".join(expiring_meds))

# ============================================================
# 8. MIN/MAX ADMIN LOCK + INVENTORY VIEW
# ============================================================

st.divider()
if has_permission("manage_minmax"):
    st.sidebar.divider()
    st.sidebar.subheader("🔐 Min/Max Settings")
    if st.session_state.minmax_unlocked:
        st.sidebar.success("Min/Max editing is UNLOCKED.")
        if st.sidebar.button("🔒 Lock Min/Max", key="lock_minmax"):
            st.session_state.minmax_unlocked = False
            st.rerun()
    elif st.sidebar.button("🔓 Unlock Min/Max", key="unlock_minmax"):
        st.session_state.minmax_unlocked = True
        st.rerun()

if mobile_device:
    st.subheader(f"📱 Quick Inventory — {selected_rig}")
    st.caption("Tap a medication to view or update its current quantity and expiration date.")

    mobile_med_id = st.selectbox(
        "Medication",
        [m["id"] for m in visible_meds],
        format_func=lambda x: MEDICATIONS[x]["name"],
        key=f"mobile_med_{selected_rig}",
    )
    mobile_item = raw_inventory[mobile_med_id]
    mobile_status = get_status(mobile_item)
    status_text = {
        "OUT OF STOCK": "🚨 OUT OF STOCK",
        "AT / BELOW MIN": "⚠️ AT / BELOW MIN",
        "OK": "🟢 OK",
    }[mobile_status]

    c1, c2, c3 = st.columns(3)
    c1.metric("Current", mobile_item["count"])
    c2.metric("Min", mobile_item["min"])
    c3.metric("Max", mobile_item["max"])
    st.info(f"{status_text}  •  Expires {mobile_item['expiry']}")

    if has_permission("edit_inventory") or has_permission("manage_minmax"):
        with st.form(f"mobile_inventory_form_{selected_rig}"):
            mobile_count = st.number_input(
                "Current Quantity", min_value=0, step=1,
                value=int(mobile_item["count"]),
                disabled=not has_permission("edit_inventory"),
            )
            mobile_expiry = st.date_input(
                "Expiration Date",
                value=parse_date(mobile_item["expiry"]) or today + datetime.timedelta(days=365),
                disabled=not has_permission("edit_inventory"),
            )
            if has_permission("manage_minmax") and st.session_state.minmax_unlocked:
                m1, m2 = st.columns(2)
                with m1:
                    mobile_min = st.number_input("Min", min_value=0, step=1, value=int(mobile_item["min"]))
                with m2:
                    mobile_max = st.number_input("Max", min_value=0, step=1, value=int(mobile_item["max"]))
            else:
                mobile_min, mobile_max = mobile_item["min"], mobile_item["max"]

            if st.form_submit_button("💾 Save Medication", type="primary", use_container_width=True):
                if mobile_max < mobile_min:
                    st.error("Max cannot be less than Min.")
                else:
                    if has_permission("manage_minmax") and st.session_state.minmax_unlocked:
                        mobile_item["min"], mobile_item["max"] = int(mobile_min), int(mobile_max)
                    if has_permission("edit_inventory"):
                        mobile_item["count"] = int(mobile_count)
                        mobile_item["expiry"] = mobile_expiry.isoformat()
                    st.success("Medication inventory saved.")
                    st.rerun()

    with st.expander("📋 View All Medications", expanded=False):
        for med in visible_meds:
            item = raw_inventory[med["id"]]
            st.markdown(
                f"**{med['name']}**  \n"
                f"Current: **{item['count']}**  •  Min: {item['min']}  •  Max: {item['max']}  \n"
                f"Expires: {item['expiry']}  •  **{get_status(item)}**"
            )
            st.divider()
else:
    st.subheader(f"📊 Active Operations Grid — {selected_rig}")
    st.caption("Edit current quantity and expiration only if you have inventory permission. Min/Max requires the separate Min/Max permission and unlock.")

    edited_data = st.data_editor(
        visible_meds,
        column_config={
            "id": st.column_config.TextColumn("Medication ID", disabled=True),
            "name": st.column_config.TextColumn("Medication Name", disabled=True),
            "min": st.column_config.NumberColumn("Min", min_value=0, step=1, disabled=not (has_permission("manage_minmax") and st.session_state.minmax_unlocked)),
            "max": st.column_config.NumberColumn("Max", min_value=0, step=1, disabled=not (has_permission("manage_minmax") and st.session_state.minmax_unlocked)),
            "count": st.column_config.NumberColumn("Current", min_value=0, step=1, disabled=not has_permission("edit_inventory")),
            "expiry": st.column_config.TextColumn("Expiration Date (YYYY-MM-DD)", disabled=not has_permission("edit_inventory")),
        },
        hide_index=True,
        use_container_width=True,
        key=f"grid_editor_{selected_rig}",
    )

    if st.button("💾 Save Inventory / Min-Max Changes", type="primary", disabled=not (has_permission("edit_inventory") or has_permission("manage_minmax"))):
        errors = []
        for row in edited_data:
            med_id = row["id"]
            minimum, maximum, count = int(row["min"]), int(row["max"]), int(row["count"])
            expiry = str(row["expiry"])
            if maximum < minimum:
                errors.append(f"{row['name']}: Max cannot be less than Min.")
                continue
            if parse_date(expiry) is None:
                errors.append(f"{row['name']}: Expiration must be YYYY-MM-DD.")
                continue
            item = raw_inventory[med_id]
            if has_permission("manage_minmax") and st.session_state.minmax_unlocked:
                item["min"], item["max"] = minimum, maximum
            if has_permission("edit_inventory"):
                item["count"], item["expiry"] = max(0, count), expiry
        if errors:
            for error in errors:
                st.error(error)
        else:
            st.success("✅ Inventory and Min/Max changes saved.")
            st.rerun()

# ============================================================
# 9. SEPARATE USAGE / RESTOCK
# ============================================================

st.divider()
available_ids = visible_med_ids(selected_rig, user_role)

if mobile_device:
    usage_tab, restock_tab = st.tabs(["💉 Record Usage", "📦 Record Restock"])
    with usage_tab:
        st.caption("Record medication removed/used during the shift. Quantity cannot exceed stock on hand.")
        if available_ids:
            usage_med_id = st.selectbox("Medication Used", available_ids, format_func=lambda x: MEDICATIONS[x]["name"], key="mobile_usage_med")
            usage_qty = st.number_input("Quantity Used", min_value=1, step=1, value=1, key="mobile_usage_qty")
            if st.button("➖ Record Usage", disabled=not has_permission("record_usage"), key="mobile_record_usage", use_container_width=True):
                item = raw_inventory[usage_med_id]
                if usage_qty > item["count"]:
                    st.error(f"Cannot record {usage_qty}. Only {item['count']} on hand.")
                else:
                    item["count"] -= int(usage_qty)
                    item["usage"] += int(usage_qty)
                    st.session_state.shift_usage[(selected_rig, usage_med_id)] = shift_totals(selected_rig, usage_med_id, "usage") + int(usage_qty)
                    record_activity(selected_rig, usage_med_id, "usage", usage_qty)
                    st.success(f"Recorded {usage_qty} × {MEDICATIONS[usage_med_id]['name']} as used.")
                    st.rerun()

    with restock_tab:
        st.caption("Record medication added to the rig. If stock already exists, the earliest expiration is retained.")
        if available_ids:
            restock_med_id = st.selectbox("Medication Restocked", available_ids, format_func=lambda x: MEDICATIONS[x]["name"], key="mobile_restock_med")
            restock_qty = st.number_input("Quantity Restocked", min_value=1, step=1, value=1, key="mobile_restock_qty")
            restock_expiry = st.date_input("Expiration of Incoming Stock", value=today + datetime.timedelta(days=365), key="mobile_restock_expiry")
            if st.button("➕ Record Restock", disabled=not has_permission("record_restock"), key="mobile_record_restock", use_container_width=True):
                item = raw_inventory[restock_med_id]
                incoming = restock_expiry
                old_expiry = parse_date(item.get("expiry"))
                if item["count"] <= 0 or old_expiry is None:
                    item["expiry"] = incoming.isoformat()
                else:
                    item["expiry"] = min(old_expiry, incoming).isoformat()
                item["count"] += int(restock_qty)
                item["restocked"] += int(restock_qty)
                st.session_state.shift_restock[(selected_rig, restock_med_id)] = shift_totals(selected_rig, restock_med_id, "restock") + int(restock_qty)
                record_activity(selected_rig, restock_med_id, "restock", restock_qty, incoming.isoformat())
                st.success(f"Recorded {restock_qty} × {MEDICATIONS[restock_med_id]['name']} as restocked. Active expiration: {item['expiry']}.")
                st.rerun()
else:
    left, right = st.columns(2)
    with left:
        st.subheader("💉 Medication Usage")
        st.caption("Record medication removed/used during the shift. Quantity cannot exceed stock on hand.")
        if available_ids:
            usage_med_id = st.selectbox("Medication Used", available_ids, format_func=lambda x: MEDICATIONS[x]["name"], key="usage_med")
            usage_qty = st.number_input("Quantity Used", min_value=1, step=1, value=1, key="usage_qty")
            if st.button("➖ Record Usage", disabled=not has_permission("record_usage"), key="record_usage_button"):
                item = raw_inventory[usage_med_id]
                if usage_qty > item["count"]:
                    st.error(f"Cannot record {usage_qty}. Only {item['count']} on hand.")
                else:
                    item["count"] -= int(usage_qty)
                    item["usage"] += int(usage_qty)
                    st.session_state.shift_usage[(selected_rig, usage_med_id)] = shift_totals(selected_rig, usage_med_id, "usage") + int(usage_qty)
                    record_activity(selected_rig, usage_med_id, "usage", usage_qty)
                    st.success(f"Recorded {usage_qty} × {MEDICATIONS[usage_med_id]['name']} as used.")
                    st.rerun()

    with right:
        st.subheader("📦 Medication Restock")
        st.caption("Record medication added to the rig. If the rig already has stock, the earliest expiration is retained.")
        if available_ids:
            restock_med_id = st.selectbox("Medication Restocked", available_ids, format_func=lambda x: MEDICATIONS[x]["name"], key="restock_med")
            restock_qty = st.number_input("Quantity Restocked", min_value=1, step=1, value=1, key="restock_qty")
            restock_expiry = st.date_input("Expiration of Incoming Stock", value=today + datetime.timedelta(days=365), key="restock_expiry")
            if st.button("➕ Record Restock", disabled=not has_permission("record_restock"), key="record_restock_button"):
                item = raw_inventory[restock_med_id]
                incoming = restock_expiry
                old_expiry = parse_date(item.get("expiry"))
                if item["count"] <= 0 or old_expiry is None:
                    item["expiry"] = incoming.isoformat()
                else:
                    item["expiry"] = min(old_expiry, incoming).isoformat()
                item["count"] += int(restock_qty)
                item["restocked"] += int(restock_qty)
                st.session_state.shift_restock[(selected_rig, restock_med_id)] = shift_totals(selected_rig, restock_med_id, "restock") + int(restock_qty)
                record_activity(selected_rig, restock_med_id, "restock", restock_qty, incoming.isoformat())
                st.success(f"Recorded {restock_qty} × {MEDICATIONS[restock_med_id]['name']} as restocked. Active expiration: {item['expiry']}.")
                st.rerun()

# ============================================================
# 10. RESTOCK NEEDS + COPY-PASTE REQUEST
# ============================================================

st.divider()
st.subheader("📦 Restock Needs")
restock_rows = []
for med in visible_meds:
    item = raw_inventory[med["id"]]
    needed = max(0, item["max"] - item["count"])
    if needed > 0:
        restock_rows.append({
            "Medication": med["name"],
            "Current": item["count"],
            "Min": item["min"],
            "Max": item["max"],
            "Restock Needed": needed,
            "Expiration": item["expiry"],
            "Status": get_status(item),
        })
if restock_rows:
    st.dataframe(restock_rows, hide_index=True, use_container_width=True)
    request_lines = [f"Ambulance medication restock request — {selected_rig}", ""]
    for row in restock_rows:
        request_lines.append(f"{row['Medication']}: {row['Restock Needed']} (current {row['Current']}, max {row['Max']})")
    request_text = "\n".join(request_lines)
    st.text_area("Supervisor Restock Request", request_text, height=180)
else:
    st.success("✅ All visible medications are at their Max target.")

# ============================================================
# 11. SHIFT SUMMARY + ACTIVITY
# ============================================================

st.divider()
st.subheader("📋 Shift Summary Text Exporter")
summary_text = build_shift_summary(selected_rig, user_role)
st.text_area("Shift Summary", summary_text, height=350)
st.download_button(
    "⬇️ Download Shift Summary",
    data=summary_text,
    file_name=f"{selected_rig.replace('#', '').replace(' ', '_')}_shift_summary.txt",
    mime="text/plain",
)

with st.expander("📝 View Shift Activity Log"):
    rig_activity = [event for event in st.session_state.activity_log if event["rig"] == selected_rig]
    if rig_activity:
        st.dataframe(list(reversed(rig_activity)), hide_index=True, use_container_width=True)
    else:
        st.info("No usage or restock activity has been recorded for this rig yet.")
