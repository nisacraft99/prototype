# prototype.py — UMS Prototype (alle 25 User Stories)
# Requires: pip install streamlit
# Run: streamlit run prototype.py
# Streamlit >= 1.32.0 required for @st.dialog

import streamlit as st
from datetime import datetime, date, timedelta
import calendar as cal_module
import random

st.set_page_config(page_title="UMS Prototype", page_icon="🏢", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
[data-testid="stSidebar"] { background: #1a2332 !important; }
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p,
[data-testid="stSidebar"] span, [data-testid="stSidebar"] div { color: #e0e0e0 !important; }
[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.07) !important; border: 1px solid rgba(255,255,255,0.18) !important;
    color: #e0e0e0 !important; width: 100% !important; text-align: left !important;
    border-radius: 6px !important; margin-bottom: 2px !important;
}
[data-testid="stSidebar"] .stButton > button:hover { background: rgba(255,255,255,0.16) !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.15) !important; }
.console-header { font-weight: 700; font-size: 13px; color: #90caf9 !important; text-transform: uppercase;
    letter-spacing: 1px; margin: 10px 0 4px 0; padding-left: 4px; }
.notif-box { background: #fffde7; border-left: 4px solid #f9a825; padding: 8px 12px;
    margin: 4px 0; border-radius: 4px; font-size: 13px; color: #333; }
.role-chip-Director { background:#e3f2fd; color:#1565c0; padding:3px 10px;
    border-radius:12px; font-weight:700; font-size:13px; display:inline-block; }
.role-chip-Manager { background:#e8f5e9; color:#2e7d32; padding:3px 10px;
    border-radius:12px; font-weight:700; font-size:13px; display:inline-block; }
.role-chip-Agent { background:#fff3e0; color:#e65100; padding:3px 10px;
    border-radius:12px; font-weight:700; font-size:13px; display:inline-block; }
.cal-day { border: 1px solid #e0e0e0; border-radius: 6px; padding: 4px; min-height: 60px;
    background: white; margin: 2px; }
.cal-today { border: 2px solid #1976d2 !important; }
</style>
""", unsafe_allow_html=True)

# ====================== CONSTANTS ======================
LOCATIONS = ["Berlin", "Munich", "Hamburg", "Frankfurt"]
MANAGERS_BY_LOC = {
    "Berlin": ["Schmidt, Anna", "Müller, Thomas"],
    "Munich": ["Weber, Lisa", "Fischer, Max"],
    "Hamburg": ["Bauer, Klaus", "Richter, Eva"],
    "Frankfurt": ["Wolf, Stefan", "Neumann, Julia"],
}
AGENTS_BY_LOC = {
    "Berlin": ["Klein, Peter", "Wagner, Maria"],
    "Munich": ["Becker, Hans", "Hoffmann, Sara"],
    "Hamburg": ["Schäfer, Tom", "Koch, Lena"],
    "Frankfurt": ["Braun, Felix", "Krause, Anna"],
}
SUBDIVISIONS_BY_LOC = {
    "Berlin": ["North Team", "South Team"],
    "Munich": ["Alpha Team", "Beta Team"],
    "Hamburg": ["Harbor Team", "City Team"],
    "Frankfurt": ["Finance Team", "Tech Team"],
}
URGENCY_ORDER = {"high": 0, "medium": 1, "low": 2}
URGENCY_ICON = {"high": "🔴", "medium": "🟡", "low": "🟢"}
ALL_MANAGERS = [m for ms in MANAGERS_BY_LOC.values() for m in ms]
ALL_AGENTS = [a for ag in AGENTS_BY_LOC.values() for a in ag]

# ====================== SESSION STATE ======================
def init():
    today = date.today()
    defs = {
        "role": "Director",
        "screen": "home",
        "sel_sm": None, "sel_tm": None,
        "sel_action_id": None, "sel_action_type": None,
        "sel_employee": None, "sel_eval_id": None,
        "cal_offset": 0, "cal_user": None,
        "notifs": [],
        "sm_q": "", "sm_q_active": False,
        "tm_q": "", "tm_q_active": False,
        "eval_results": [],
    }
    for k, v in defs.items():
        if k not in st.session_state:
            st.session_state[k] = v

    if "sms" not in st.session_state:
        st.session_state.sms = [
            {"id": f"SM-00{i}", "title": t, "location": loc,
             "participants": MANAGERS_BY_LOC[loc][:1], "deadline": str(today + timedelta(days=d)),
             "accepted_by": [], "declined_by": []}
            for i, (t, loc, d) in enumerate([
                ("Q1 Strategy Review", "Berlin", 14),
                ("Annual Performance Planning", "Munich", 30),
                ("Team Alignment", "Hamburg", 7),
                ("Budget Review", "Frankfurt", 45),
                ("Project Kickoff", "Berlin", 60),
            ], 1)
        ]
    if "tms" not in st.session_state:
        st.session_state.tms = [
            {"id": f"TM-00{i}", "title": t, "location": loc, "subdivision": sub,
             "participants": [], "deadline": str(today + timedelta(days=d)),
             "accepted_by": [], "declined_by": []}
            for i, (t, loc, sub, d) in enumerate([
                ("Weekly Standup", "Berlin", "North Team", 3),
                ("Sprint Planning", "Munich", "Alpha Team", 10),
                ("Team Building", "Hamburg", "Harbor Team", 20),
                ("Training Session", "Frankfurt", "Finance Team", 5),
                ("Monthly Review", "Berlin", "South Team", 35),
            ], 1)
        ]
    if "sm_actions" not in st.session_state:
        st.session_state.sm_actions = {
            "SM-001": [
                {"id": "A-001", "topic": "Market Analysis", "root_cause": "Q1 performance gap",
                 "action": "Conduct competitive analysis", "urgency": "high"},
                {"id": "A-002", "topic": "Budget Reallocation", "root_cause": "Overspend Q4",
                 "action": "Review and rebalance budget", "urgency": "medium"},
            ],
            "SM-002": [{"id": "A-003", "topic": "KPI Review", "root_cause": "Targets not met",
                        "action": "Revise KPI framework", "urgency": "high"}],
            "SM-003": [], "SM-004": [], "SM-005": [],
        }
    if "tm_actions" not in st.session_state:
        st.session_state.tm_actions = {
            "TM-001": [{"id": "A-010", "topic": "Sprint Goals", "root_cause": "Unclear objectives",
                        "action": "Define sprint goals clearly", "urgency": "high"}],
            "TM-002": [{"id": "A-011", "topic": "Capacity Planning", "root_cause": "Understaffing",
                        "action": "Request additional resources", "urgency": "medium"}],
            "TM-003": [], "TM-004": [], "TM-005": [],
        }
    if "evaluations" not in st.session_state:
        st.session_state.evaluations = [
            {"id": f"EV-00{i}", "employee": emp, "date": str(today - timedelta(days=d)),
             "efficiency": e, "reliability": r, "communication": c, "comment": cmt, "appealed": False}
            for i, (emp, d, e, r, c, cmt) in enumerate([
                ("Schmidt, Anna", 5, 4, 5, 3, "Good performance overall."),
                ("Müller, Thomas", 10, 3, 4, 4, "Needs improvement in deadlines."),
                ("Weber, Lisa", 2, 5, 5, 5, "Excellent team player."),
            ], 1)
        ]
    if "my_evals" not in st.session_state:
        st.session_state.my_evals = [
            {"id": f"MEV-00{i}", "date": str(today - timedelta(days=d)),
             "efficiency": e, "reliability": r, "communication": c, "comment": cmt, "appealed": False, "appeal_text": ""}
            for i, (d, e, r, c, cmt) in enumerate([
                (3, 4, 5, 4, "Strong contribution to projects."),
                (10, 3, 3, 4, "Room for improvement in communication."),
            ], 1)
        ]

init()

# ====================== HELPERS ======================
def go(screen, **kw):
    st.session_state.screen = screen
    for k, v in kw.items():
        st.session_state[k] = v
    st.rerun()

def notif(msg):
    st.session_state.notifs.insert(0, {"text": msg, "ts": datetime.now().strftime("%H:%M")})
    if len(st.session_state.notifs) > 30:
        st.session_state.notifs.pop()

def role():
    return st.session_state.role

def get_sm(sm_id):
    return next((s for s in st.session_state.sms if s["id"] == sm_id), None)

def get_tm(tm_id):
    return next((t for t in st.session_state.tms if t["id"] == tm_id), None)

# ====================== DIALOGS ======================
@st.dialog("Create Strategic Meeting")
def dlg_create_sm():
    title = st.text_input("Title *", max_chars=50)
    deadline = st.date_input("Deadline *", min_value=date.today() + timedelta(days=1))
    location = st.selectbox("Location *", LOCATIONS)
    parts = st.multiselect("Participants *", MANAGERS_BY_LOC[location])
    if st.button("Create", type="primary"):
        if not title.strip() or not parts:
            st.error("All fields are mandatory.")
        else:
            new_id = f"SM-{len(st.session_state.sms)+1:03d}"
            st.session_state.sms.append({"id": new_id, "title": title, "location": location,
                "participants": parts, "deadline": str(deadline), "accepted_by": [], "declined_by": []})
            st.session_state.sm_actions[new_id] = []
            notif(f"SM '{title}' created (ID: {new_id})")
            st.rerun()
    if st.button("Cancel"):
        st.rerun()

@st.dialog("Edit Strategic Meeting")
def dlg_edit_sm(sm):
    title = st.text_input("Title", value=sm["title"], max_chars=50)
    st.info(f"📍 Location: **{sm['location']}** — cannot be changed")
    st.info(f"🔑 ID: **{sm['id']}** — cannot be changed")
    deadline = st.date_input("Deadline", min_value=date.today() + timedelta(days=1))
    parts = st.multiselect("Participants", MANAGERS_BY_LOC[sm["location"]], default=sm["participants"])
    if st.button("Save", type="primary"):
        sm["title"] = title; sm["deadline"] = str(deadline); sm["participants"] = parts
        notif(f"SM '{title}' updated.")
        st.rerun()
    if st.button("Cancel"):
        st.rerun()

@st.dialog("Delete Strategic Meeting")
def dlg_delete_sm(sm_id):
    sm = get_sm(sm_id)
    st.warning(f'Are you sure to delete this SM?\n\n**"{sm["title"] if sm else sm_id}"**')
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Yes", type="primary"):
            st.session_state.sms = [s for s in st.session_state.sms if s["id"] != sm_id]
            notif(f"SM {sm_id} deleted.")
            go("sm_dashboard")
    with c2:
        if st.button("No"):
            st.rerun()

@st.dialog("Create Team Meeting")
def dlg_create_tm():
    title = st.text_input("Title *", max_chars=50)
    deadline = st.date_input("Deadline *", min_value=date.today() + timedelta(days=1))
    location = st.selectbox("Location *", LOCATIONS)
    st.caption("Select either a Subdivision OR Participants — not both.")
    subdivision = st.selectbox("Subdivision", ["(none)"] + SUBDIVISIONS_BY_LOC[location])
    participants = st.multiselect("Participants", AGENTS_BY_LOC[location],
                                   disabled=(subdivision != "(none)"))
    if subdivision != "(none)":
        st.info("Participants field deactivated (subdivision selected).")
    elif participants:
        st.info("Subdivision field deactivated (participant selected).")
    if st.button("Create", type="primary"):
        if not title.strip() or (subdivision == "(none)" and not participants):
            st.error("All mandatory fields must be filled.")
        else:
            new_id = f"TM-{len(st.session_state.tms)+1:03d}"
            st.session_state.tms.append({"id": new_id, "title": title, "location": location,
                "subdivision": "" if subdivision == "(none)" else subdivision,
                "participants": [] if subdivision != "(none)" else participants,
                "deadline": str(deadline), "accepted_by": [], "declined_by": []})
            st.session_state.tm_actions[new_id] = []
            notif(f"TM '{title}' created (ID: {new_id})")
            st.rerun()
    if st.button("Cancel"):
        st.rerun()

@st.dialog("Edit Team Meeting")
def dlg_edit_tm(tm):
    title = st.text_input("Title", value=tm["title"], max_chars=50)
    st.info(f"📍 Location: **{tm['location']}** — cannot be changed")
    st.info(f"🔑 ID: **{tm['id']}** — cannot be changed")
    deadline = st.date_input("Deadline", min_value=date.today() + timedelta(days=1))
    parts = st.multiselect("Participants", AGENTS_BY_LOC[tm["location"]], default=tm.get("participants", []))
    if st.button("Save", type="primary"):
        tm["title"] = title; tm["deadline"] = str(deadline); tm["participants"] = parts
        notif(f"TM '{title}' updated.")
        st.rerun()
    if st.button("Cancel"):
        st.rerun()

@st.dialog("Delete Team Meeting")
def dlg_delete_tm(tm_id):
    tm = get_tm(tm_id)
    st.warning(f'Are you sure to delete this TM?\n\n**"{tm["title"] if tm else tm_id}"**')
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Yes", type="primary"):
            st.session_state.tms = [t for t in st.session_state.tms if t["id"] != tm_id]
            notif(f"TM {tm_id} deleted.")
            go("tm_dashboard")
    with c2:
        if st.button("No"):
            st.rerun()

@st.dialog("Add Action")
def dlg_create_action(meeting_id, mtype):
    topic = st.text_area("Topic *", max_chars=200)
    root_cause = st.text_area("Root Cause *", max_chars=200)
    action = st.text_area("Action *", max_chars=200)
    urgency = st.selectbox("Urgency", ["high", "medium", "low"])
    if st.button("Save", type="primary"):
        if not topic.strip() or not action.strip():
            st.error("All fields are mandatory.")
        else:
            store = st.session_state.sm_actions if mtype == "sm" else st.session_state.tm_actions
            new_id = f"A-{random.randint(100,999)}"
            store.setdefault(meeting_id, []).append(
                {"id": new_id, "topic": topic, "root_cause": root_cause, "action": action, "urgency": urgency})
            st.rerun()
    if st.button("Cancel"):
        st.rerun()

@st.dialog("Edit Action")
def dlg_edit_action(action, meeting_id, mtype):
    topic = st.text_area("Topic", value=action["topic"], max_chars=200)
    root_cause = st.text_area("Root Cause", value=action["root_cause"], max_chars=200)
    act_text = st.text_area("Action", value=action["action"], max_chars=200)
    urgency = st.selectbox("Urgency", ["high", "medium", "low"],
                            index=["high", "medium", "low"].index(action["urgency"]))
    if st.button("Save", type="primary"):
        store = st.session_state.sm_actions if mtype == "sm" else st.session_state.tm_actions
        for a in store.get(meeting_id, []):
            if a["id"] == action["id"]:
                a["topic"] = topic; a["root_cause"] = root_cause
                a["action"] = act_text; a["urgency"] = urgency
        st.rerun()
    if st.button("Cancel"):
        st.rerun()

@st.dialog("Delete Action")
def dlg_delete_action(action_id, meeting_id, mtype):
    st.warning("Are you sure to delete this action?")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Yes", type="primary"):
            store = st.session_state.sm_actions if mtype == "sm" else st.session_state.tm_actions
            store[meeting_id] = [a for a in store.get(meeting_id, []) if a["id"] != action_id]
            st.rerun()
    with c2:
        if st.button("No"):
            st.rerun()

@st.dialog("Meeting Options")
def dlg_meeting_actions(meeting, mtype):
    r = role()
    st.subheader(f"{'🔴 SM' if mtype == 'sm' else '🔵 TM'}: {meeting['title']}")
    st.write(f"**Deadline:** {meeting['deadline']}  |  **Location:** {meeting['location']}")
    st.markdown("---")

    accepted = st.session_state.get("__user__", "You") in meeting.get("accepted_by", [])
    declined = st.session_state.get("__user__", "You") in meeting.get("declined_by", [])

    # Accept / Decline (not Director for SM; not for TM by director)
    can_accept_decline = (
        (r == "Manager" and mtype == "sm") or
        (r == "Agent" and mtype == "tm")
    )
    can_cancel = (
        (r == "Director") or
        (r == "Manager" and mtype == "tm")
    )

    if can_accept_decline:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Accept", disabled=accepted):
                meeting.setdefault("accepted_by", []).append("You")
                notif(f"ACCEPTED: User [You] accepted the {'SM' if mtype=='sm' else 'TM'} with the title {meeting['title']}")
                st.rerun()
        with c2:
            if st.button("❌ Decline", disabled=declined):
                meeting.setdefault("declined_by", []).append("You")
                notif(f"DECLINED: User [You] declined the {'SM' if mtype=='sm' else 'TM'} with the title {meeting['title']}")
                st.rerun()
        if accepted:
            st.success("You have accepted this meeting.")
        if declined:
            st.error("You have declined this meeting.")

    elif r == "Director":
        st.info("As Director, you can view all meetings but can only cancel them.")

    if can_cancel:
        st.markdown("---")
        if st.button("🚫 Cancel Meeting", type="secondary"):
            meeting["status"] = "cancelled"
            notif(f"CANCELLED: {'SM' if mtype=='sm' else 'TM'} with the title {meeting['title']}")
            st.success("Meeting cancelled. Participants notified.")
            st.rerun()

    if st.button("Close"):
        st.rerun()

@st.dialog("Appeal Evaluation")
def dlg_appeal(eval_id):
    st.write("Enter your appeal comment (mandatory, max 500 characters):")
    text = st.text_area("Comment", max_chars=500)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Save", type="primary"):
            if not text.strip():
                st.error("To raise an appeal, a comment is mandatory")
            else:
                for ev in st.session_state.my_evals:
                    if ev["id"] == eval_id:
                        ev["appealed"] = True
                        ev["appeal_text"] = text
                notif("The appeal was successfully sent")
                notif("EVALUATION: A user you evaluated has raised an appeal")
                st.rerun()
    with c2:
        if st.button("Cancel"):
            st.rerun()

# ====================== SIDEBAR ======================
def render_sidebar():
    r = role()
    with st.sidebar:
        st.markdown("## 🏢 UMS")
        st.markdown(f"<div class='role-chip-{r}'>{r}</div>", unsafe_allow_html=True)
        st.markdown("---")

        new_role = st.selectbox("Switch Role", ["Director", "Manager", "Agent"],
                                 index=["Director", "Manager", "Agent"].index(r))
        if new_role != r:
            st.session_state.role = new_role
            st.session_state.screen = "home"
            st.rerun()

        if st.session_state.notifs:
            with st.expander(f"🔔 Notifications ({len(st.session_state.notifs)})"):
                for n in st.session_state.notifs[:5]:
                    st.caption(f"[{n['ts']}] {n['text']}")
                if st.button("Clear all", key="clear_notifs"):
                    st.session_state.notifs = []
                    st.rerun()

        st.markdown("---")
        st.markdown("**NAVIGATION**")

        # US-25: role-based console and module visibility
        # Operations — Director + Manager (view only for Manager)
        if r in ["Director", "Manager"]:
            with st.expander("⚙️ Operations", expanded=False):
                label = "Strategic Meeting" if r == "Director" else "Strategic Meeting (view)"
                if st.button(label, key="nav_sm", use_container_width=True):
                    go("sm_dashboard")

        # Coordination — all roles
        with st.expander("🤝 Coordination", expanded=False):
            label_tm = "Team Meeting" if r == "Manager" else "Team Meeting (view)"
            if st.button(label_tm, key="nav_tm", use_container_width=True):
                go("tm_dashboard")

        # Scheduling — all roles
        with st.expander("📅 Scheduling", expanded=False):
            if st.button("Calendar", key="nav_cal", use_container_width=True):
                go("calendar")

        # Performance — Director + Manager see Evaluate, Manager + Agent see My Evaluations
        with st.expander("📊 Performance", expanded=False):
            if r in ["Director", "Manager"]:
                if st.button("Evaluate Employees", key="nav_eval", use_container_width=True):
                    go("evaluate_dashboard")
            if r in ["Manager", "Agent"]:
                if st.button("My Evaluations", key="nav_myeval", use_container_width=True):
                    go("my_evaluations")
            if r == "Director":
                st.caption("My Evaluations not visible for Director.")

        st.markdown("---")
        if st.button("🏠 Home", key="nav_home"):
            go("home")

# ====================== HOME ======================
def show_home():
    r = role()
    st.title("🏢 Welcome to User Management System (UMS)")
    st.markdown(f"<div class='role-chip-{r}' style='font-size:16px;padding:6px 16px'>{r}</div>",
                unsafe_allow_html=True)
    st.markdown("")
    st.info("Use the **navigation bar on the left** to access the modules.")

    module_map = {
        "Director": ["⚙️ Strategic Meeting (create, edit, delete)", "👥 Team Meeting (view)",
                     "📅 Calendar (view, reschedule, cancel)", "📊 Evaluate Employees"],
        "Manager": ["⚙️ Strategic Meeting (view)", "👥 Team Meeting (create, edit, delete)",
                    "📅 Calendar (view, reschedule, accept/decline)", "📊 Evaluate Employees",
                    "📈 My Evaluations"],
        "Agent": ["👥 Team Meeting (view)", "📅 Calendar (view, accept/decline)", "📈 My Evaluations"],
    }
    st.subheader("Your available modules")
    for m in module_map.get(r, []):
        st.write(f"- {m}")

    if st.session_state.notifs:
        st.markdown("---")
        st.subheader("Recent Notifications")
        for n in st.session_state.notifs[:3]:
            st.markdown(f"<div class='notif-box'>[{n['ts']}] {n['text']}</div>", unsafe_allow_html=True)

# ====================== SM DASHBOARD (US-5) ======================
def show_sm_dashboard():
    r = role()
    st.title("📋 Strategic Meeting — Dashboard")

    c1, c2, c3 = st.columns([5, 1, 1])
    with c1:
        q = st.text_input("🔍 Search by title or ID", value=st.session_state.sm_q, key="sm_q_input")
    with c2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Search", key="sm_search"):
            st.session_state.sm_q = q; st.session_state.sm_q_active = True; st.rerun()
    with c3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Reset", key="sm_reset"):
            st.session_state.sm_q = ""; st.session_state.sm_q_active = False; st.rerun()

    if r == "Director":
        if st.button("➕ Create SM", type="primary"):
            dlg_create_sm()
    elif r == "Manager":
        st.caption("You have viewing permissions only.")

    sms = st.session_state.sms
    if r == "Manager":
        sms = [s for s in sms if MANAGERS_BY_LOC["Berlin"][0] in s.get("participants", [])]
    if st.session_state.sm_q_active and st.session_state.sm_q:
        q2 = st.session_state.sm_q.lower()
        sms = [s for s in sms if q2 in s["title"].lower() or q2 in s["id"].lower()]
    sms = sorted(sms, key=lambda x: x["id"])

    if not sms:
        st.info("No Strategic Meetings found.")
        return

    st.markdown("---")
    hcols = st.columns([1, 3, 2, 3, 2])
    for c, h in zip(hcols, ["ID", "Title", "Location", "Participants", "Deadline"]):
        c.markdown(f"**{h}**")
    st.markdown("---")
    for sm in sms:
        rc = st.columns([1, 3, 2, 3, 2])
        with rc[0]:
            if st.button(sm["id"], key=f"sm_{sm['id']}"):
                go("sm_detail", sel_sm=sm["id"])
        rc[1].write(sm["title"])
        rc[2].write(sm["location"])
        rc[3].write(", ".join(sm["participants"][:2]) + ("..." if len(sm["participants"]) > 2 else ""))
        rc[4].write(sm["deadline"])

# ====================== SM DETAIL (US-2, 3, 4, 6, 7, 8, 9) ======================
def show_sm_detail():
    r = role()
    sm = get_sm(st.session_state.sel_sm)
    if not sm:
        st.error("SM not found.")
        return

    if st.button("← Back to SM Dashboard"):
        go("sm_dashboard")

    st.title(f"📋 {sm['title']}")
    if sm.get("status") == "cancelled":
        st.error("🚫 This meeting has been cancelled.")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("ID", sm["id"])
    m2.metric("Deadline", sm["deadline"])
    m3.metric("Location", sm["location"])
    m4.metric("Participants", len(sm["participants"]))
    st.write("**Participants:**", ", ".join(sm["participants"]))

    # Calendar accept/decline/cancel for this meeting
    if r == "Manager":
        cc1, cc2 = st.columns(2)
        with cc1:
            if "You" not in sm.get("accepted_by", []):
                if st.button("✅ Accept SM"):
                    sm.setdefault("accepted_by", []).append("You")
                    notif(f"ACCEPTED: User [You] accepted the SM with the title {sm['title']}")
                    st.rerun()
            else:
                st.success("✅ You accepted this meeting")
        with cc2:
            if "You" not in sm.get("declined_by", []):
                if st.button("❌ Decline SM"):
                    sm.setdefault("declined_by", []).append("You")
                    notif(f"DECLINED: User [You] declined the SM with the title {sm['title']}")
                    st.rerun()
            else:
                st.error("❌ You declined this meeting")

    if r == "Director":
        bc1, bc2, bc3 = st.columns([1, 1, 1])
        with bc1:
            if st.button("✏️ Edit SM"):
                dlg_edit_sm(sm)
        with bc2:
            if st.button("🗑️ Delete SM"):
                dlg_delete_sm(sm["id"])
        with bc3:
            if st.button("🚫 Cancel SM"):
                sm["status"] = "cancelled"
                notif(f"CANCELLED: SM with the title {sm['title']}")
                st.rerun()

    st.markdown("---")
    st.subheader("Actions")
    if r == "Director":
        if st.button("➕ Add Action"):
            dlg_create_action(sm["id"], "sm")
    elif r == "Manager":
        st.caption("You can view actions but cannot create them.")

    actions = sorted(st.session_state.sm_actions.get(sm["id"], []),
                     key=lambda a: URGENCY_ORDER.get(a["urgency"], 9))
    if not actions:
        st.info("No actions yet.")
    else:
        hc = st.columns([1, 3, 2, 2])
        for c, h in zip(hc, ["ID", "Topic", "Urgency", ""]): c.markdown(f"**{h}**")
        st.markdown("---")
        for ac in actions:
            ac_cols = st.columns([1, 3, 2, 2])
            with ac_cols[0]:
                if st.button(ac["id"], key=f"ac_sm_{ac['id']}"):
                    go("action_detail", sel_action_id=ac["id"], sel_action_type="sm")
            ac_cols[1].write(ac["topic"])
            ac_cols[2].write(f"{URGENCY_ICON.get(ac['urgency'],'')} {ac['urgency']}")
            with ac_cols[3]:
                if r == "Director":
                    e1, e2 = st.columns(2)
                    with e1:
                        if st.button("✏️", key=f"edit_ac_{ac['id']}"):
                            dlg_edit_action(ac, sm["id"], "sm")
                    with e2:
                        if st.button("🗑️", key=f"del_ac_{ac['id']}"):
                            dlg_delete_action(ac["id"], sm["id"], "sm")

# ====================== ACTION DETAIL ======================
def show_action_detail():
    r = role()
    aid = st.session_state.sel_action_id
    mtype = st.session_state.sel_action_type
    mid = st.session_state.sel_sm if mtype == "sm" else st.session_state.sel_tm
    store = st.session_state.sm_actions if mtype == "sm" else st.session_state.tm_actions
    ac = next((a for a in store.get(mid, []) if a["id"] == aid), None)
    if not ac:
        st.error("Action not found.")
        return

    back = "sm_detail" if mtype == "sm" else "tm_detail"
    if st.button(f"← Back to {'SM' if mtype=='sm' else 'TM'} Detail"):
        go(back)

    st.title(f"🎯 Action: {ac['topic']}")
    c1, c2 = st.columns(2)
    c1.metric("Action ID", ac["id"])
    c2.metric("Urgency", f"{URGENCY_ICON.get(ac['urgency'],'')} {ac['urgency']}")
    st.markdown(f"**Root Cause:** {ac['root_cause']}")
    st.markdown(f"**Action:** {ac['action']}")

    can_edit = (mtype == "sm" and r == "Director") or (mtype == "tm" and r == "Manager")
    if can_edit:
        e1, e2 = st.columns(2)
        with e1:
            if st.button("✏️ Edit Action"):
                dlg_edit_action(ac, mid, mtype)
        with e2:
            if st.button("🗑️ Delete Action"):
                dlg_delete_action(aid, mid, mtype)

# ====================== TM DASHBOARD (US-14) ======================
def show_tm_dashboard():
    r = role()
    st.title("👥 Team Meeting — Dashboard")

    c1, c2, c3 = st.columns([5, 1, 1])
    with c1:
        q = st.text_input("🔍 Search by title or ID", value=st.session_state.tm_q, key="tm_q_input")
    with c2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Search", key="tm_search"):
            st.session_state.tm_q = q; st.session_state.tm_q_active = True; st.rerun()
    with c3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Reset", key="tm_reset"):
            st.session_state.tm_q = ""; st.session_state.tm_q_active = False; st.rerun()

    if r == "Manager":
        if st.button("➕ Create TM", type="primary"):
            dlg_create_tm()
    elif r in ["Director", "Agent"]:
        st.caption("You have viewing permissions only.")

    tms = st.session_state.tms
    if r == "Manager":
        tms = [t for t in tms]  # manager sees own; simplified for demo
    elif r == "Agent":
        tms = [t for t in tms if "Klein, Peter" in t.get("participants", []) or t.get("subdivision")]
    if st.session_state.tm_q_active and st.session_state.tm_q:
        q2 = st.session_state.tm_q.lower()
        tms = [t for t in tms if q2 in t["title"].lower() or q2 in t["id"].lower()]
    tms = sorted(tms, key=lambda x: x["id"])

    if not tms:
        st.info("No Team Meetings found.")
        return

    st.markdown("---")
    hcols = st.columns([1, 3, 2, 3, 2])
    for c, h in zip(hcols, ["ID", "Title", "Location", "Subdivision / Participants", "Deadline"]):
        c.markdown(f"**{h}**")
    st.markdown("---")
    for tm in tms:
        rc = st.columns([1, 3, 2, 3, 2])
        with rc[0]:
            if st.button(tm["id"], key=f"tm_{tm['id']}"):
                go("tm_detail", sel_tm=tm["id"])
        rc[1].write(tm["title"])
        rc[2].write(tm["location"])
        rc[3].write(tm.get("subdivision") or ", ".join(tm.get("participants", [])[:2]))
        rc[4].write(tm["deadline"])

# ====================== TM DETAIL (US-11, 12, 13, 15, 16, 17, 18) ======================
def show_tm_detail():
    r = role()
    tm = get_tm(st.session_state.sel_tm)
    if not tm:
        st.error("TM not found.")
        return

    if st.button("← Back to TM Dashboard"):
        go("tm_dashboard")

    st.title(f"👥 {tm['title']}")
    if tm.get("status") == "cancelled":
        st.error("🚫 This meeting has been cancelled.")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("ID", tm["id"])
    m2.metric("Deadline", tm["deadline"])
    m3.metric("Location", tm["location"])
    m4.metric("Subdivision" if tm.get("subdivision") else "Participants",
              tm.get("subdivision") or ", ".join(tm.get("participants", [])))

    # Accept/Decline for Agent
    if r == "Agent":
        cc1, cc2 = st.columns(2)
        with cc1:
            if "You" not in tm.get("accepted_by", []):
                if st.button("✅ Accept TM"):
                    tm.setdefault("accepted_by", []).append("You")
                    notif(f"ACCEPTED: User [You] accepted the TM with the title {tm['title']}")
                    st.rerun()
            else:
                st.success("✅ You accepted this meeting")
        with cc2:
            if "You" not in tm.get("declined_by", []):
                if st.button("❌ Decline TM"):
                    tm.setdefault("declined_by", []).append("You")
                    notif(f"DECLINED: User [You] declined the TM with the title {tm['title']}")
                    st.rerun()
            else:
                st.error("❌ You declined this meeting")

    if r == "Manager":
        bc1, bc2, bc3 = st.columns([1, 1, 1])
        with bc1:
            if st.button("✏️ Edit TM"):
                dlg_edit_tm(tm)
        with bc2:
            if st.button("🗑️ Delete TM"):
                dlg_delete_tm(tm["id"])
        with bc3:
            if st.button("🚫 Cancel TM"):
                tm["status"] = "cancelled"
                notif(f"CANCELLED: TM with the title {tm['title']}")
                st.rerun()
    elif r == "Director":
        st.caption("Director has viewing permissions only. You can cancel in Calendar View.")

    st.markdown("---")
    st.subheader("Actions")
    if r == "Manager":
        if st.button("➕ Add Action"):
            dlg_create_action(tm["id"], "tm")

    actions = sorted(st.session_state.tm_actions.get(tm["id"], []),
                     key=lambda a: URGENCY_ORDER.get(a["urgency"], 9))
    if not actions:
        st.info("No actions yet.")
    else:
        hc = st.columns([1, 3, 2, 2])
        for c, h in zip(hc, ["ID", "Topic", "Urgency", ""]): c.markdown(f"**{h}**")
        st.markdown("---")
        for ac in actions:
            ac_cols = st.columns([1, 3, 2, 2])
            with ac_cols[0]:
                if st.button(ac["id"], key=f"ac_tm_{ac['id']}"):
                    go("action_detail", sel_action_id=ac["id"], sel_action_type="tm")
            ac_cols[1].write(ac["topic"])
            ac_cols[2].write(f"{URGENCY_ICON.get(ac['urgency'],'')} {ac['urgency']}")
            with ac_cols[3]:
                if r == "Manager":
                    e1, e2 = st.columns(2)
                    with e1:
                        if st.button("✏️", key=f"edit_tma_{ac['id']}"):
                            dlg_edit_action(ac, tm["id"], "tm")
                    with e2:
                        if st.button("🗑️", key=f"del_tma_{ac['id']}"):
                            dlg_delete_action(ac["id"], tm["id"], "tm")

# ====================== CALENDAR (US-19, 20, 21, 22) ======================
def show_calendar():
    r = role()
    st.title("📅 Calendar View")

    today = date.today()
    offset = st.session_state.cal_offset
    # Calculate target month
    month_delta = today.month - 1 + offset
    year = today.year + month_delta // 12
    month = month_delta % 12 + 1
    target_first = date(year, month, 1)

    # Navigation arrows
    nav1, nav2, nav3 = st.columns([1, 6, 1])
    with nav1:
        if st.button("◀", disabled=(offset <= -3)):
            st.session_state.cal_offset -= 1; st.rerun()
    with nav2:
        st.markdown(f"<h3 style='text-align:center'>{target_first.strftime('%B %Y')}</h3>",
                    unsafe_allow_html=True)
    with nav3:
        if st.button("▶", disabled=(offset >= 6)):
            st.session_state.cal_offset += 1; st.rerun()

    # US-20: Search other calendar
    if r in ["Director", "Manager"]:
        st.markdown("---")
        sc1, sc2 = st.columns([4, 1])
        with sc1:
            search_name = st.text_input("🔍 Search user calendar", placeholder="Enter name...",
                                         value=st.session_state.cal_user or "")
        with sc2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Search User"):
                if not search_name.strip():
                    st.session_state.cal_user = None
                elif search_name not in ALL_MANAGERS + ALL_AGENTS:
                    st.error("The user you searched for does not exist")
                elif r == "Manager" and search_name not in ALL_AGENTS:
                    st.error("You do not have permission to view this user's calendar")
                else:
                    st.session_state.cal_user = search_name
                    st.rerun()
        if st.session_state.cal_user:
            st.info(f"📆 Viewing calendar of: **{st.session_state.cal_user}**")
            if st.button("← Back to my calendar"):
                st.session_state.cal_user = None; st.rerun()

    # Build day → meetings map
    meetings_by_day: dict = {}
    for sm in st.session_state.sms:
        try:
            d = datetime.strptime(sm["deadline"], "%Y-%m-%d").date()
        except Exception:
            continue
        if d.year == year and d.month == month:
            if r in ["Director", "Manager"]:
                meetings_by_day.setdefault(d.day, []).append(("sm", sm))
    for tm in st.session_state.tms:
        try:
            d = datetime.strptime(tm["deadline"], "%Y-%m-%d").date()
        except Exception:
            continue
        if d.year == year and d.month == month:
            meetings_by_day.setdefault(d.day, []).append(("tm", tm))

    # Calendar grid
    st.markdown("---")
    _, days_in_month = cal_module.monthrange(year, month)
    first_weekday = target_first.weekday()
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    hcols = st.columns(7)
    for i, dn in enumerate(day_names):
        hcols[i].markdown(f"<center><b>{dn}</b></center>", unsafe_allow_html=True)

    day = 1
    blank = first_weekday
    while day <= days_in_month:
        cols = st.columns(7)
        for ci in range(7):
            if blank > 0:
                blank -= 1
                cols[ci].write("")
            elif day <= days_in_month:
                with cols[ci]:
                    is_today = (date(year, month, day) == today)
                    label = f"**📍{day}**" if is_today else str(day)
                    st.markdown(label)
                    for mtype, meeting in meetings_by_day.get(day, []):
                        icon = "🔴" if mtype == "sm" else "🔵"
                        short = meeting["title"][:12] + ("…" if len(meeting["title"]) > 12 else "")
                        cancelled = meeting.get("status") == "cancelled"
                        btn_label = f"~~{icon} {short}~~" if cancelled else f"{icon} {short}"
                        if st.button(btn_label, key=f"cal_{mtype}_{meeting['id']}_{year}_{month}_{day}"):
                            dlg_meeting_actions(meeting, mtype)
                day += 1

    # US-21: Reschedule (drag & drop simulation)
    if r in ["Director", "Manager"]:
        st.markdown("---")
        st.subheader("✋ Reschedule Meeting")
        all_meetings = []
        if r == "Director":
            all_meetings += [(f"🔴 SM: {s['title']} ({s['id']})", s["id"], "sm") for s in st.session_state.sms]
            all_meetings += [(f"🔵 TM: {t['title']} ({t['id']})", t["id"], "tm") for t in st.session_state.tms]
        elif r == "Manager":
            all_meetings += [(f"🔵 TM: {t['title']} ({t['id']})", t["id"], "tm") for t in st.session_state.tms]

        if all_meetings:
            rc1, rc2, rc3 = st.columns([3, 2, 1])
            with rc1:
                sel = st.selectbox("Select meeting to reschedule", [m[0] for m in all_meetings])
            with rc2:
                new_date = st.date_input("New date", min_value=today)
            with rc3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Reschedule", type="primary"):
                    sm_tm = next(m for m in all_meetings if m[0] == sel)
                    mid, mtype = sm_tm[1], sm_tm[2]
                    store = st.session_state.sms if mtype == "sm" else st.session_state.tms
                    for m in store:
                        if m["id"] == mid:
                            m["deadline"] = str(new_date)
                    notif(f"RESCHEDULED: {'SM' if mtype=='sm' else 'TM'} with the title {sel.split(': ')[1].split(' (')[0]}")
                    st.success("✅ Meeting rescheduled. All participants notified.")
                    st.rerun()

# ====================== EVALUATE EMPLOYEES (US-23) ======================
def show_evaluate_dashboard():
    r = role()
    st.title("📊 Evaluate Employees")

    # Director: location filter + search managers
    if r == "Director":
        c1, c2, c3 = st.columns([2, 3, 1])
        with c1:
            loc_filter = st.selectbox("Filter by location", ["All"] + LOCATIONS)
        with c2:
            search_q = st.text_input("Search manager name")
        with c3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Search", key="eval_search"):
                pool = [m for loc, ms in MANAGERS_BY_LOC.items()
                        for m in ms if loc_filter == "All" or loc == loc_filter]
                if search_q:
                    pool = [p for p in pool if search_q.lower() in p.lower()]
                st.session_state.eval_results = pool

    # Manager: search subordinate agents (no location filter visible)
    elif r == "Manager":
        c1, c2 = st.columns([4, 1])
        with c1:
            search_q = st.text_input("Search subordinate agent")
        with c2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Search", key="eval_search_mgr"):
                pool = [a for ag in AGENTS_BY_LOC.values() for a in ag]
                if search_q:
                    pool = [p for p in pool if search_q.lower() in p.lower()]
                st.session_state.eval_results = pool

    # Show search results
    if st.session_state.eval_results:
        st.markdown("**Results:**")
        for emp in st.session_state.eval_results:
            if st.button(f"👤 {emp}", key=f"emp_{emp}"):
                go("evaluate_form", sel_employee=emp)

    # Evaluation list
    st.markdown("---")
    st.subheader("Evaluations Created by Me")
    evals = st.session_state.evaluations
    if not evals:
        st.info("No evaluations created yet.")
    else:
        hc = st.columns([1, 3, 2])
        for c, h in zip(hc, ["ID", "Employee", "Date"]): c.markdown(f"**{h}**")
        st.markdown("---")
        for ev in evals:
            rc = st.columns([1, 3, 2])
            rc[0].write(ev["id"]); rc[1].write(ev["employee"]); rc[2].write(ev["date"])

# ====================== EVALUATE FORM ======================
def show_evaluate_form():
    emp = st.session_state.sel_employee
    st.title(f"📊 Evaluate: {emp}")

    if st.button("← Back"):
        go("evaluate_dashboard")

    st.markdown("---")
    with st.form("eval_form"):
        st.subheader("Performance Ratings (all mandatory)")
        eff = st.slider("Efficiency", 1, 5, 3)
        rel = st.slider("Reliability", 1, 5, 3)
        com = st.slider("Communication", 1, 5, 3)
        comment = st.text_area("Comment (optional)", max_chars=300)
        c1, c2 = st.columns(2)
        with c1: save = st.form_submit_button("Save", type="primary")
        with c2: cancel = st.form_submit_button("Cancel")

        if save:
            new_id = f"EV-{len(st.session_state.evaluations)+1:03d}"
            st.session_state.evaluations.append({
                "id": new_id, "employee": emp, "date": str(date.today()),
                "efficiency": eff, "reliability": rel, "communication": com,
                "comment": comment, "appealed": False
            })
            notif("the evaluation was successfully saved")
            notif(f"EVALUATION: A new evaluation was created for you")
            st.session_state.eval_results = []
            go("evaluate_dashboard")
        if cancel:
            go("evaluate_dashboard")

# ====================== MY EVALUATIONS (US-24) ======================
def show_my_evaluations():
    st.title("📈 My Evaluations")
    evals = sorted(st.session_state.my_evals, key=lambda e: e["date"], reverse=True)

    if not evals:
        st.info("No evaluations found.")
        return

    hc = st.columns([1, 2])
    for c, h in zip(hc, ["ID", "Date"]): c.markdown(f"**{h}**")
    st.markdown("---")
    for ev in evals:
        rc = st.columns([1, 2])
        with rc[0]:
            if st.button(ev["id"], key=f"myev_{ev['id']}"):
                go("my_eval_detail", sel_eval_id=ev["id"])
        rc[1].write(ev["date"])
        if ev.get("appealed"):
            st.caption("   ↳ ✅ Appeal submitted")

def show_my_eval_detail():
    eval_id = st.session_state.sel_eval_id
    ev = next((e for e in st.session_state.my_evals if e["id"] == eval_id), None)
    if not ev:
        st.error("Evaluation not found.")
        return

    if st.button("← Back to My Evaluations"):
        go("my_evaluations")

    st.title(f"📈 Evaluation {ev['id']}")
    st.write(f"**Date:** {ev['date']}")
    st.markdown("---")

    c1, c2, c3 = st.columns(3)
    c1.metric("Efficiency", f"{ev['efficiency']} / 5")
    c2.metric("Reliability", f"{ev['reliability']} / 5")
    c3.metric("Communication", f"{ev['communication']} / 5")
    if ev.get("comment"):
        st.markdown(f"**Comment:** {ev['comment']}")

    st.markdown("---")
    try:
        eval_date = datetime.strptime(ev["date"], "%Y-%m-%d").date()
        can_appeal = (date.today() - eval_date).days <= 7
    except Exception:
        can_appeal = False

    if ev.get("appealed"):
        st.success(f"✅ Appeal already submitted: *{ev['appeal_text']}*")
    elif can_appeal:
        if st.button("📝 Raise Appeal"):
            dlg_appeal(eval_id)
    else:
        st.warning("⏳ Appeal period expired (evaluation older than 1 week).")

# ====================== ROUTING ======================
render_sidebar()

screen = st.session_state.screen
routes = {
    "home": show_home,
    "sm_dashboard": show_sm_dashboard,
    "sm_detail": show_sm_detail,
    "action_detail": show_action_detail,
    "tm_dashboard": show_tm_dashboard,
    "tm_detail": show_tm_detail,
    "calendar": show_calendar,
    "evaluate_dashboard": show_evaluate_dashboard,
    "evaluate_form": show_evaluate_form,
    "my_evaluations": show_my_evaluations,
    "my_eval_detail": show_my_eval_detail,
}
routes.get(screen, show_home)()
