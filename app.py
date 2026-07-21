import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session
import random
import json
import os
import csv
from io import TextIOWrapper
from datetime import datetime
nm
app = Flask(__name__)
app.secret_key = "pms_secret_key_123"

# Configurations
GROUPS_FILE = "groups.json"
PREFS_FILE = "preferences.json"
PROPOSALS_FILE = "proposals.json"
MENTOR_NAMES = {
    "1": "Dr. Manish Gudadhe", 
    "2": "Prof. Abhinav Muley", 
    "3": "Dr. Jayshri Harde",
    "4": "Dr. Ashish Dandekar", 
    "5": "Prof. Leena Mandurkar", 
    "6": "Prof. Bhagyashree Hambarde",
    "7": "Dr. Tejal Irkhede", 
    "8": "Prof. Kalyani Satone", 
    "9": "Dr. Nischal Puri"
}

# ---------------------------
# Database & JSON Helpers
# ---------------------------





def get_db_connection():
    conn = sqlite3.connect("PMS.db")
    conn.row_factory = sqlite3.Row
    return conn

def load_json(filename, default):
    if not os.path.exists(filename) or os.path.getsize(filename) == 0:
        return default
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return default

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# CRITICAL FIX: To prevent 'load_json is undefined' error in HTML templates
@app.context_processor
def inject_helpers():
    return dict(load_json=load_json)

# ---------------------------
# Logic Functions
# ---------------------------
def build_batches(students_list):
    total = len(students_list)
    if total == 0: return [], [], [], []
    base = total // 4
    rem = total % 4
    s1 = base + (1 if rem > 0 else 0)
    s2 = base + (1 if rem > 1 else 0)
    s3 = base + (1 if rem > 2 else 0)
    return students_list[:s1], students_list[s1:s1+s2], students_list[s1+s2:s1+s2+s3], students_list[s1+s2+s3:]

def generate_groups_logic(b1, b2, b3, b4):
    m2, m3, m4 = list(b2), list(b3), list(b4)
    random.shuffle(m2); random.shuffle(m3); random.shuffle(m4)
    groups = []
    for i, leader in enumerate(b1):
        groups.append({
            "id": i + 1,
            "leader_uid": str(leader["UID"]),
            "members": {
                "B2": str(m2[i]["UID"]) if i < len(m2) else None,
                "B3": str(m3[i]["UID"]) if i < len(m3) else None,
                "B4": str(m4[i]["UID"]) if i < len(m4) else None
            },
            "mentor_id": None,
            "preferences": {}
        })
    return groups

# ---------------------------
# General Routes
# ---------------------------

@app.route('/')
def welcome(): return render_template("welcome.html")

@app.route('/history')
def history():
    conn = get_db_connection()
    projects_rows = conn.execute("SELECT * FROM projects ORDER BY session_year DESC, id ASC").fetchall()
    projects_list = [dict(row) for row in projects_rows]
    sessions_rows = conn.execute("SELECT DISTINCT session_year FROM projects ORDER BY session_year DESC").fetchall()
    available_sessions = [row[0] for row in sessions_rows]
    conn.close()
    return render_template("history.html", projects=projects_list, sessions_list=available_sessions)

@app.route('/faculty_details')
def faculty_details():
    faculty_list = []
    for m_id, name in MENTOR_NAMES.items():
        faculty_list.append({
            "id": m_id, "name": name,
            "designation": "Assistant Professor" if "Prof." in name else "Associate Professor",
            "department": "CSE (Data Science)"
        })
    return render_template("faculty_details.html", faculty=faculty_list)

@app.route('/students_list')
def student_list_view():
    conn = get_db_connection()
    sessions = [s['upload_session'] for s in conn.execute("SELECT DISTINCT upload_session FROM student_register WHERE upload_session IS NOT NULL").fetchall()]
    selected_session = request.args.get('session')
    if not selected_session and sessions: selected_session = sessions[-1]
    
    students = []
    if selected_session:
        students = [dict(s) for s in conn.execute("SELECT * FROM student_register WHERE upload_session = ? ORDER BY CGPA DESC", (selected_session,)).fetchall()]
    conn.close()
    
    b1, b2, b3, b4 = build_batches(students)
    batches = [{'name': 'Batch 1 (Leaders)', 'data': b1}, {'name': 'Batch 2', 'data': b2}, {'name': 'Batch 3', 'data': b3}, {'name': 'Batch 4', 'data': b4}]
    return render_template("students_list.html", batches=batches, sessions=sessions, current_session=selected_session)

# ---------------------------
# Admin Section
# ---------------------------
@app.route('/chat/<session_name>/<group_id>', methods=['GET', 'POST'])
def chat(session_name, group_id):
    if 'role' not in session:
        return redirect(url_for('welcome'))

    CHAT_FILE = "chat_history.json"
    
    # 1. Load existing chats (Empty dict if file missing)
    all_chats = load_json(CHAT_FILE, {})
    
    # Unique key for this specific group's chat
    chat_key = f"{session_name}_{group_id}"
    
    if request.method == 'POST':
        msg_text = request.form.get('message', '').strip()
        if msg_text:
            if chat_key not in all_chats:
                all_chats[chat_key] = []
            
            # Message structure
            new_msg = {
                "sender": session.get('user_name'),
                "role": session.get('role'), # 'mentor' or 'student'
                "text": msg_text,
                "time": datetime.now().strftime("%I:%M %p")
            }
            
            all_chats[chat_key].append(new_msg)
            save_json(CHAT_FILE, all_chats)
            
            # Post-Redirect-Get pattern (Double submit rokne ke liye)
            return redirect(url_for('chat', session_name=session_name, group_id=group_id))

    # Messages fetch karein
    messages = all_chats.get(chat_key, [])
    
    return render_template("chat.html", 
                           messages=messages, 
                           session_name=session_name, 
                           group_id=group_id)


@app.route('/adm_login', methods=['GET', 'POST'])
def adm_login():
    if request.method == 'POST':
        email, pwd = request.form.get('email'), request.form.get('password')
        conn = get_db_connection()
        admin = conn.execute("SELECT * FROM admin_login WHERE email=? AND password=?", (email, pwd)).fetchone()
        conn.close()
        if admin:
            session.update({'role': 'admin', 'user_id': admin['email']})
            return redirect(url_for('admin_dashboard'))
        flash("Invalid Credentials")
    return render_template("adm_login.html")

@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'admin': return redirect(url_for('adm_login'))
    conn = get_db_connection()
    sessions = [s['upload_session'] for s in conn.execute("SELECT DISTINCT upload_session FROM student_register WHERE upload_session IS NOT NULL").fetchall()]
    sel_session = request.args.get('session')
    if not sel_session and sessions: sel_session = sessions[-1]

    if not sel_session:
        conn.close()
        return render_template("admin_dashboard.html", sessions=[], current_session=None, b1=[], b2=[], b3=[], b4=[], groups=[])

    students = [dict(s) for s in conn.execute("SELECT * FROM student_register WHERE upload_session = ? ORDER BY CGPA DESC", (sel_session,)).fetchall()]
    conn.close()
    
    b1, b2, b3, b4 = build_batches(students)
    all_data = load_json(GROUPS_FILE, {})
    session_data = all_data.get(sel_session, {"locked": False, "groups": []})
    
    uid_map = {str(s["UID"]): s for s in students}
    display_groups = []
    for g in session_data.get("groups", []):
        m_list = []
        members_dict = g.get("members", {})
        for role in ["B2", "B3", "B4"]:
            m_uid = str(members_dict.get(role))
            if m_uid and m_uid != "None" and m_uid in uid_map: m_list.append(uid_map[m_uid])
            else: m_list.append(None)

        display_groups.append({
            "id": g["id"], "leader": uid_map.get(str(g.get("leader_uid"))),
            "member_list": m_list, "mentor_id": str(g.get("mentor_id")) if g.get("mentor_id") else None,
            "preferences": g.get("preferences", {})
        })

    return render_template("admin_dashboard.html", b1=b1, b2=b2, b3=b3, b4=b4, groups=display_groups, sessions=sessions, current_session=sel_session, locked=session_data.get("locked", False), mentor_names=MENTOR_NAMES)

@app.route('/admin/upload_csv', methods=['POST'])
def upload_csv():
    if session.get('role') != 'admin': return redirect(url_for('adm_login'))
    session_name, file = request.form.get('session_name'), request.files.get('file')
    if not session_name or not file: return redirect(url_for('admin_dashboard'))
    try:
        csv_file = TextIOWrapper(file, encoding='utf-8')
        reader = csv.DictReader(csv_file)
        conn = get_db_connection()
        for row in reader:
            conn.execute("INSERT OR REPLACE INTO student_register (UID, SName, Password, CGPA, upload_session) VALUES (?, ?, ?, ?, ?)",
                         (row['UID'], row['SName'], row['Password'], float(row['CGPA']), session_name))
        conn.commit(); conn.close()
        flash(f"Successfully imported students for {session_name}!", "success")
    except Exception as e: flash(f"Error: {str(e)}", "error")
    return redirect(url_for('admin_dashboard', session=session_name))

@app.route('/admin/delete_batch', methods=['POST'])
def delete_batch():
    if session.get('role') != 'admin': return redirect(url_for('adm_login'))
    target_session = request.form.get('session_name')
    if target_session:
        conn = get_db_connection()
        conn.execute("DELETE FROM student_register WHERE upload_session = ?", (target_session,))
        conn.commit(); conn.close()
        all_groups = load_json(GROUPS_FILE, {})
        if target_session in all_groups:
            del all_groups[target_session]
            save_json(GROUPS_FILE, all_groups)
        flash(f"Session '{target_session}' deleted!", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/generate_groups_action')
def generate_groups_action():
    sel_session = request.args.get('session')
    conn = get_db_connection()
    students = [dict(s) for s in conn.execute("SELECT * FROM student_register WHERE upload_session = ? ORDER BY CGPA DESC", (sel_session,)).fetchall()]
    conn.close()
    b1, b2, b3, b4 = build_batches(students)
    all_data = load_json(GROUPS_FILE, {})
    all_data[sel_session] = {"locked": False, "groups": generate_groups_logic(b1, b2, b3, b4)}
    save_json(GROUPS_FILE, all_data)
    return redirect(url_for('admin_dashboard', session=sel_session))

@app.route('/admin/allocate_and_lock', methods=['POST'])
def allocate_and_lock():
    sel_session = request.args.get('session')
    all_data = load_json(GROUPS_FILE, {})
    session_data = all_data.get(sel_session)
    if not session_data: return redirect(url_for('admin_dashboard'))
    conn = get_db_connection()
    students_cgpa = {str(s['UID']): float(s['CGPA']) for s in conn.execute("SELECT UID, CGPA FROM student_register WHERE upload_session=?", (sel_session,)).fetchall()}
    conn.close()
    sorted_groups = sorted(session_data["groups"], key=lambda g: students_cgpa.get(str(g["leader_uid"]), 0.0), reverse=True)
    mentor_loads = {str(m_id): 0 for m_id in MENTOR_NAMES.keys()}
    max_cap = (len(sorted_groups) // len(MENTOR_NAMES)) + 1
    for g in sorted_groups:
        assigned = False
        sorted_prefs = sorted(g.get("preferences", {}).items(), key=lambda x: int(x[1]))
        for m_id, rank in sorted_prefs:
            if mentor_loads.get(str(m_id), 0) < max_cap:
                g["mentor_id"] = str(m_id); mentor_loads[str(m_id)] += 1
                assigned = True; break
        if not assigned:
            fallback = min(mentor_loads, key=mentor_loads.get)
            g["mentor_id"] = fallback; mentor_loads[fallback] += 1
    session_data["locked"] = True
    all_data[sel_session] = session_data
    save_json(GROUPS_FILE, all_data)
    flash(f"Mentors Allocated & Locked!", "success")
    return redirect(url_for('admin_dashboard', session=sel_session))

# ---------------------------
# Student Section
# ---------------------------

@app.route('/stu_login', methods=['GET', 'POST'])
def stu_login():
    if request.method == 'POST':
        uid, pwd = request.form.get('uid'), request.form.get('password')
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM student_register WHERE UID=? AND Password=?", (uid, pwd)).fetchone()
        conn.close()
        if user:
            u_sess = user['upload_session']
            all_groups = load_json(GROUPS_FILE, {}).get(u_sess, {}).get("groups", [])
            if any(str(g['leader_uid']) == str(uid) for g in all_groups):
                session.update({'role': 'student', 'user_id': user['UID'], 'user_name': user['SName'], 'user_session': u_sess})
                return redirect(url_for('student_dashboard'))
            flash("Access Denied: Only Group Leaders can login.")
        else: flash("Invalid Credentials.")
    return render_template("stu_login.html")

@app.route('/student_dashboard')
def student_dashboard():
    if session.get('role') != 'student': return redirect(url_for('stu_login'))
    uid, u_sess = str(session['user_id']), session.get('user_session')
    all_data = load_json(GROUPS_FILE, {})
    session_data = all_data.get(u_sess, {"locked": False, "groups": []})
    conn = get_db_connection()
    uid_map = {str(s["UID"]): dict(s) for s in conn.execute("SELECT * FROM student_register WHERE upload_session=?", (u_sess,)).fetchall()}
    conn.close()
    my_group = next((g for g in session_data["groups"] if str(g["leader_uid"]) == uid), None)
    display = None
    if my_group:
        m_list = [uid_map[str(my_group["members"][k])] for k in ["B2", "B3", "B4"] if str(my_group["members"].get(k)) in uid_map]
        display = {"id": my_group["id"], "leader": uid_map.get(uid), "members": m_list, "mentor_name": MENTOR_NAMES.get(str(my_group.get("mentor_id"))), "preferences": my_group.get("preferences", {})}
    submitted = (u_sess in load_json(PREFS_FILE, {}) and uid in load_json(PREFS_FILE, {})[u_sess])
    return render_template("stu_interface.html", group=display, locked=session_data.get("locked", False), submitted=submitted)

@app.route('/submit_preferences', methods=['POST'])
def submit_preferences():
    if session.get('role') != 'student': return redirect(url_for('stu_login'))
    uid, u_sess = str(session.get("user_id")), session.get("user_session")
    all_data = load_json(GROUPS_FILE, {})
    group = next((g for g in all_data.get(u_sess, {}).get("groups", []) if str(g["leader_uid"]) == uid), None)
    if group:
        prefs = {str(m_id): int(request.form.get(f"mentor_{m_id}")) for m_id in MENTOR_NAMES.keys() if request.form.get(f"mentor_{m_id}")}
        group["preferences"] = prefs; save_json(GROUPS_FILE, all_data)
        all_prefs = load_json(PREFS_FILE, {})
        if u_sess not in all_prefs: all_prefs[u_sess] = {}
        all_prefs[u_sess][uid] = {"preferences": prefs, "timestamp": datetime.now().isoformat()}
        save_json(PREFS_FILE, all_prefs)
        flash("✅ Preferences submitted!")
    return redirect(url_for('student_dashboard'))

# ---------------------------
# Mentor Section
# ---------------------------

@app.route('/men_login', methods=['GET', 'POST'])
def men_login():
    if request.method == 'POST':
        m_id, pwd = request.form.get('mentor_id'), request.form.get('password')
        if m_id in MENTOR_NAMES and pwd == "pass123":
            session.update({'role': 'mentor', 'user_id': m_id, 'user_name': MENTOR_NAMES[m_id]})
            return redirect(url_for('mentor_dashboard'))
        flash("Invalid Mentor Credentials", "error")
    return render_template("men_login.html")

@app.route('/mentor_dashboard')
def mentor_dashboard():
    if session.get('role') != 'mentor': 
        return redirect(url_for('men_login'))
    
    m_id = str(session.get('user_id'))
    mentor_name = session.get('user_name')
    
    # 1. Database se students fetch karein names dikhane ke liye
    conn = get_db_connection()
    students_rows = conn.execute("SELECT UID, SName, CGPA FROM student_register").fetchall()
    conn.close()
    uid_map = {str(s["UID"]): dict(s) for s in students_rows}
    
    # 2. JSON Files load karein (Groups aur Proposals)
    all_groups_data = load_json(GROUPS_FILE, {})
    all_proposals = load_json("proposals.json", {}) # Isse project title dikhega
    
    my_assigned_groups = []

    for s_name, s_data in all_groups_data.items():
        # Sirf wahi batches jo finalize (locked) ho chuke hain
        if s_data.get("locked"):
            for g in s_data.get("groups", []):
                if str(g.get("mentor_id")) == m_id:
                    # Members ki list taiyaar karein
                    members = []
                    for r in ["B2", "B3", "B4"]:
                        m_uid = g["members"].get(r)
                        if m_uid and str(m_uid) in uid_map:
                            members.append(uid_map[str(m_uid)])
                    
                    # Project Proposal check karein
                    proposal = all_proposals.get(s_name, {}).get(str(g["id"]), None)

                    # Data ko list mein add karein (Keys check karein HTML ke liye)
                    my_assigned_groups.append({
                        "session": s_name,         # HTML mein {{ g.session }}
                        "group_id": g["id"],       # HTML mein {{ g.group_id }}
                        "leader": uid_map.get(str(g["leader_uid"]), {"SName": "Unknown"}),
                        "members": members,
                        "project": proposal        # Project Title & Aim ke liye
                    })

    return render_template("mentor_dashboard.html", 
                           mentor_name=mentor_name, 
                           groups=my_assigned_groups)


@app.route('/submit_proposal', methods=['POST'])
def submit_proposal():
    if session.get('role') != 'student': 
        return redirect(url_for('stu_login'))
    
    u_sess = session.get('user_session')
    gid = request.form.get('group_id')
    title = request.form.get('title')
    aim = request.form.get('aim')

    if not gid or not title:
        flash("Group ID or Title missing!", "error")
        return redirect(url_for('student_dashboard'))

    all_props = load_json(PROPOSALS_FILE, {})
    
    if u_sess not in all_props:
        all_props[u_sess] = {}
    
    # Data save kar rahe hain
    all_props[u_sess][str(gid)] = {
        "title": title,
        "aim": aim,
        "status": "Pending",
        "admin_feedback": "",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    save_json(PROPOSALS_FILE, all_props)
    flash("Success: Project Proposal submitted!", "success")
    return redirect(url_for('student_dashboard'))


@app.route('/mentor/review_proposal/<session_name>/<group_id>/<action>', methods=['POST'])
def review_proposal(session_name, group_id, action):
    if session.get('role') != 'mentor': 
        return redirect(url_for('men_login'))
    
    all_props = load_json(PROPOSALS_FILE, {})
    
    if session_name in all_props and group_id in all_props[session_name]:
        if action == 'approve':
            all_props[session_name][group_id]['status'] = 'Accepted'
            all_props[session_name][group_id]['admin_feedback'] = ""
            flash(f"Proposal for Group {group_id} has been Approved!", "success")
        elif action == 'reject':
            all_props[session_name][group_id]['status'] = 'Rejected'
            feedback = request.form.get('feedback', 'No feedback provided.')
            all_props[session_name][group_id]['admin_feedback'] = feedback
            flash(f"Proposal for Group {group_id} has been Rejected.", "error")
            
        save_json(PROPOSALS_FILE, all_props)
    
    return redirect(url_for('mentor_dashboard'))
   
# ---------------------------
# System Routes
# ---------------------------

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('welcome'))

if __name__ == '__main__':
    app.run(debug=True)
