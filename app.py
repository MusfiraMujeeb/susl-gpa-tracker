import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime
import time

# --- PAGE CONFIG (must be first) ---
st.set_page_config(page_title="SUSL GPA Tracker", page_icon="🎓", layout="wide")

# --- CUSTOM CSS FOR MODERN UI ---
st.markdown("""
<style>
    /* Global Font & Padding */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 1000px;
    }

    /* Header Styling */
    h1 {
        font-weight: 800;
        letter-spacing: -1px;
        color: #1E293B;
    }

    /* Metric Cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #ffffff, #f3f4f6);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.05), -5px -5px 15px rgba(255,255,255,0.8);
        border: 1px solid #F1F5F9;
        text-align: center;
        transition: transform 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        font-weight: 700 !important;
        color: #64748B !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        background: -webkit-linear-gradient(45deg, #3B82F6, #8B5CF6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Glassmorphism Semester Cards (Expanders) */
    div[data-testid="stExpander"] {
        border: none !important;
        border-radius: 16px !important;
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07) !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        margin-bottom: 16px !important;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    div[data-testid="stExpander"]:hover {
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.12) !important;
    }
    
    /* The clickable header of the semester card */
    div[data-testid="stExpander"] summary {
        font-size: 1.05rem;
        font-weight: 700;
        color: #1E293B;
        padding: 16px 20px !important;
        background-color: transparent !important;
        border-left: 6px solid #6366F1; /* Indigo accent bar */
    }
    div[data-testid="stExpander"] summary:hover {
        background-color: rgba(241, 245, 249, 0.5) !important;
    }
    
    /* Remove default border from inside the expander */
    div[data-testid="stExpanderDetails"] {
        padding: 10px 20px 20px 20px !important;
        border-top: 1px solid rgba(0,0,0,0.05) !important;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        border: none;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: all 0.2s;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
        color: white;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(79, 70, 229, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# --- CONFIGURATION ---
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except Exception:
    st.error("⚠️ Supabase credentials not found! Please check your secrets.")
    st.stop()

GRADE_SCALE = {
    "A+": 4.0, "A": 4.0, "A-": 3.7,
    "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7,
    "D": 1.0, "E": 0.0
}
YEAR_WEIGHTS = {1: 0.2, 2: 0.3, 3: 0.3, 4: 0.2}
PASS_MIN_GP = 2.0

# --- SUPABASE CLIENT ---
def get_supabase_client():
    if "supabase_client" not in st.session_state:
        st.session_state.supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return st.session_state.supabase_client

supabase = get_supabase_client()

# --- AUTH HELPERS ---
def restore_session():
    if "session" in st.session_state and st.session_state.session:
        return st.session_state.session
    try:
        session = supabase.auth.get_session()
        if session:
            st.session_state.session = session
            return session
    except Exception:
        pass
    return None

def sign_out():
    try: supabase.auth.sign_out()
    except Exception: pass
    for key in ["session", "supabase_client"]:
        st.session_state.pop(key, None)
    st.rerun()

def show_auth_ui():
    st.markdown("<h1 style='text-align:center; margin-top: 10vh;'>🎓 SUSL GPA Tracker</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#64748B; font-size: 1.1rem;'>BSc (Hons) in Information Systems · Faculty of Computing</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<div style='background: white; padding: 30px; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.08); margin-top: 20px;'>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔑 Login", "✨ Sign Up"])
        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password")
                if st.form_submit_button("Login", type="primary", use_container_width=True):
                    if not email or not password: st.error("Please fill in both fields.")
                    else:
                        try:
                            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
                            st.session_state.session = response.session
                            st.rerun()
                        except Exception as e: st.error(f"❌ Login failed: {e}")
        with tab2:
            with st.form("signup_form"):
                new_email = st.text_input("Email", placeholder="you@example.com", key="signup_email")
                new_password = st.text_input("Password (min 6 chars)", type="password", key="signup_password")
                if st.form_submit_button("Create Account", type="primary", use_container_width=True):
                    if not new_email or not new_password: st.error("Please fill in both fields.")
                    elif len(new_password) < 6: st.error("Password must be at least 6 characters.")
                    else:
                        try:
                            response = supabase.auth.sign_up({"email": new_email, "password": new_password})
                            if response.session:
                                st.session_state.session = response.session
                                st.success("Account created! Welcome 🎉")
                                st.rerun()
                            else: st.success("Account created! Please check your email to confirm.")
                        except Exception as e: st.error(f"❌ Sign up failed: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

# --- AUTH GATE ---
session = restore_session()
if session is None:
    show_auth_ui()
    st.stop()

user = session.user
user_id = user.id

# --- DATABASE FUNCTIONS ---
def load_all_courses():
    for attempt in range(3):
        try:
            response = (supabase.table("courses").select("*").order("year").order("semester_id").order("code").execute())
            return response.data
        except Exception:
            if attempt < 2: time.sleep(2)
            else: st.error("Error loading data."); return []

def save_all_courses(semesters_data):
    all_courses = []
    for sem in semesters_data:
        for course in sem["courses"]:
            all_courses.append({
                "id": course["id"], "user_id": user_id, "semester_id": sem["id"],
                "semester_name": sem["name"], "year": sem["year"], "code": course["code"],
                "title": course["title"],
                "credits": float(course.get("credits", 0)) if pd.notna(course.get("credits")) else 0.0,
                "marks": float(course.get("marks", 0)) if pd.notna(course.get("marks")) else 0.0,
                "grade": str(course.get("grade", "")) if pd.notna(course.get("grade")) else "",
                "ngpa": bool(course.get("ngpa", False))
            })
    if not all_courses: return
    for attempt in range(3):
        try:
            supabase.table("courses").delete().eq("user_id", user_id).execute()
            time.sleep(0.5)
            for i in range(0, len(all_courses), 20):
                supabase.table("courses").insert(all_courses[i:i + 20]).execute()
                time.sleep(0.3)
            return
        except Exception:
            if attempt < 2: time.sleep(2)
            else: st.error("Error saving data.")

def seed_database_for_user():
    try:
        response = supabase.table("courses").select("id").limit(1).execute()
        if len(response.data) > 0: return
    except Exception: pass

    def C(cid, code, title, credits, ngpa=False):
        return {"id": cid, "code": code, "title": title, "credits": credits, "marks": 0, "grade": "", "ngpa": ngpa}

    default_sems = [
        {"id": "sem1", "name": "Year 1 — Semester 1", "year": 1, "courses": [
            C("c1","IS1101","Fundamentals of Information Systems",2), C("c2","IS1102","Structured Programming Techniques",2),
            C("c3","IS1103","Structured Programming Practicum",1), C("c4","IS1104","Theories of Information Systems",2),
            C("c5","IS1105","Computer System Organization",2), C("c6","IS1106","Foundations of Web Technologies",2),
            C("c7","IS1107","Personal Productivity with IT",1), C("c8","IS1108","Fundamentals of Mathematics",2),
            C("c9","IS1109","Statistics & Probability Theory",2), C("n1","IS1110","Communication Skills I",2,ngpa=True),
            C("n2","IS1111","Academic Integrity",1,ngpa=True), C("n3","IS-EGP1101","General English I",2,ngpa=True),
        ]},
        {"id":"sem2","name":"Year 1 — Semester 2","year":1,"courses":[
            C("c10","IS2101","Object Oriented Programming",2), C("c11","IS2102","Object Oriented Programming Practicum",1),
            C("c12","IS2103","Emerging IS Technologies",1), C("c13","IS2104","Database Systems",2),
            C("c14","IS2105","Database Management Systems Practicum",1), C("c15","IS2106","System Analysis & Design",1),
            C("c16","IS2107","Social & Professional Issues",1), C("c17","IS2108","Human Computer Interaction",2),
            C("c18","IS2109","Information Assurance & Security",2), C("c19","IS2110","Software Project Initiation & Planning",1),
            C("c20","IS2111","Advanced Mathematics",2), C("n4","IS2112","Communication Skills II",2,ngpa=True),
            C("n5","IS-EGP1201","General English II",2,ngpa=True),
        ]},
        {"id":"sem3","name":"Year 2 — Semester 1","year":2,"courses":[
            C("c21","IS3101","Object Oriented Analysis & Design",2), C("c22","IS3102","Data Structures & Algorithms",2),
            C("c23","IS3103","IT Governance",2), C("c24","IS3104","Software Engineering",2),
            C("c25","IS3105","IS Risk Management",2), C("c26","IS3106","IS Sustainability",1),
            C("c27","IS3107","Management Information Systems",2), C("c28","IS3108","E-Business",1),
            C("c29","IS3109","Digital Innovation",2), C("n6","IS-EAP2101","Academic English I",2,ngpa=True),
        ]},
        {"id":"sem4","name":"Year 2 — Semester 2","year":2,"courses":[
            C("c30","IS4101","IT Auditing",2), C("c31","IS4102","Web Application Development",2),
            C("c32","IS4103","Operating Systems",2), C("c33","IS4104","System Administration and Maintenance",2),
            C("c34","IS4105","IT Procurement Management",1), C("c35","IS4106","Software Architecture",2),
            C("c36","IS4107","Professionalism & Ethics in Computing",1), C("c37","IS4108","IS Strategies",1),
            C("c38","IS4109","Agile Software Development",2), C("c39","IS4110","Capstone Project",2),
            C("n7","IS-EAP2201","Academic English II",2,ngpa=True),
        ]},
        {"id":"sem5","name":"Year 3 — Semester 1","year":3,"courses":[
            C("c40","IS5101","Entrepreneurship & Innovation",1), C("c41","IS5102","Enterprise Architecture",1),
            C("c42","IS5103","High Performance Computing",2), C("c43","IS5104","Software Process Management",1),
            C("c44","IS5105","Business Process Management",2), C("c45","IS5106","UI/UX Practicum",1),
            C("c46","IS5107","Project Management Practicum",1), C("c47","IS5108","Business Intelligence",2),
            C("c48","IS5109","IS Project for Community",1), C("n8","IS-EBP3101","Business English",2,ngpa=True),
        ]},
        {"id":"sem6","name": "Year 3 — Semester 2","year":3,"courses":[C("c49","IS6101","Industrial Training",6)]},
        {"id":"sem7","name": "Year 4 — Semester 1","year":4,"courses":[
            C("c50","IS7101","Research Methodologies",2), C("c51","IS7102","IT Law",1),
            C("c52","IS7103","Business Process Simulation",2), C("c53","IS7104","Enterprise Modelling Ontologies",2),
            C("c54","IS7105","Organizational Behavior & Management",1), C("c55","IS7106","Cloud Computing",2),
        ]},
        {"id":"sem8","name": "Year 4 — Semester 2","year":4,"courses":[
            C("c56","IS8101","Research Project in IS",8), C("c57","IS8102","Business/IT Alignment",2),
            C("c58","IS8103","Human Resource Management",2), C("c59","IS8104","Scientific Communication",1),
            C("c60","IS8105","IS Economics",2), C("c61","IS8106","Computer System Security",2),
        ]},
    ]
    save_all_courses(default_sems)

# --- CALCULATIONS ---
def calculate_gpa(courses):
    total_points = 0; gpa_credits = 0; earned_credits = 0
    for c in courses:
        cr = float(c.get("credits", 0))
        grade = c.get("grade", "")
        ngpa = c.get("ngpa", False)
        if not grade or ngpa: continue
        gp = GRADE_SCALE.get(grade, 0.0)
        if gp >= PASS_MIN_GP: earned_credits += cr
        gpa_credits += cr; total_points += gp * cr
    gpa = total_points / gpa_credits if gpa_credits > 0 else 0.0
    return gpa, gpa_credits, earned_credits, total_points

def calculate_fgpa(semesters):
    year_points = {1: 0, 2: 0, 3: 0, 4: 0}
    year_credits = {1: 0, 2: 0, 3: 0, 4: 0}
    for sem in semesters:
        year = sem["year"]
        for c in sem["courses"]:
            if not c.get("grade") or c.get("ngpa"): continue
            cr = float(c.get("credits", 0))
            gp = GRADE_SCALE.get(c["grade"], 0.0)
            year_points[year] += gp * cr; year_credits[year] += cr
    total_weighted = 0; total_weight = 0
    for y in [1, 2, 3, 4]:
        if year_credits[y] > 0:
            y_gpa = year_points[y] / year_credits[y]
            total_weighted += y_gpa * YEAR_WEIGHTS[y]; total_weight += YEAR_WEIGHTS[y]
    return total_weighted / total_weight if total_weight > 0 else 0.0

# --- MAIN APP ---
seed_database_for_user()
all_courses = load_all_courses()

semesters_dict = {}
for course in all_courses:
    sid = course["semester_id"]
    if sid not in semesters_dict:
        semesters_dict[sid] = {"id": sid, "name": course["semester_name"], "year": course["year"], "courses": []}
    semesters_dict[sid]["courses"].append(course)
semesters_list = sorted(semesters_dict.values(), key=lambda s: (s["year"], s["id"]))

# --- HEADER ---
col_a, col_b = st.columns([4, 1])
with col_a:
    st.markdown(f"<h1>🎓 SUSL GPA Tracker</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#64748B; font-size:1.05rem; margin-top:-10px;'>Signed in as <b>{user.email}</b></p>", unsafe_allow_html=True)
with col_b:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Sign Out", use_container_width=True):
        sign_out()

# --- METRICS ---
total_points = 0; total_gpa_credits = 0; total_earned = 0; pending = 0
for sem in semesters_list:
    _, gpa_cr, earned, pts = calculate_gpa(sem["courses"])
    total_points += pts; total_gpa_credits += gpa_cr; total_earned += earned
    for c in sem["courses"]:
        if not c.get("grade") and not c.get("ngpa"): pending += 1

running_gpa = total_points / total_gpa_credits if total_gpa_credits > 0 else 0.0
fgpa = calculate_fgpa(semesters_list)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Running GPA", f"{running_gpa:.2f}")
c2.metric("Final GPA (FGPA)", f"{fgpa:.2f}")
c3.metric("Earned Credits", f"{total_earned:.1f}")
c4.metric("Pending Results", pending)

st.markdown("<br><br>", unsafe_allow_html=True)

# --- SEMESTER EDITORS ---
for i, sem in enumerate(semesters_list):
    sem_gpa, sem_cr, _, _ = calculate_gpa(sem["courses"])
    
    # Cleaned up label (removed class text)
    label = f"📘 {sem['name']}   |   GPA: {sem_gpa:.2f}   ·   Credits: {sem_cr:.1f}"
    
    with st.expander(label, expanded=(i < 2)):
        df = pd.DataFrame(sem["courses"])
        # Removed "marks" from columns
        for col in ["id", "code", "title", "credits", "grade", "ngpa"]:
            if col not in df.columns:
                df[col] = "" if col != "credits" else 0
                
        display_df = df[["code", "title", "credits", "grade", "ngpa"]].copy()

        edited_df = st.data_editor(
            display_df,
            num_rows="dynamic",
            column_config={
                "code": st.column_config.TextColumn("Code", width="small"),
                "title": st.column_config.TextColumn("Course Name", width="large"),
                "credits": st.column_config.NumberColumn("Credits", min_value=0, step=0.5, width="small"),
                "grade": st.column_config.SelectboxColumn("Grade", options=["", "A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D", "E", "P"], width="small"),
                "ngpa": st.column_config.CheckboxColumn("NGPA", width="small"),
            },
            key=f"editor_{sem['id']}",
            hide_index=True,
        )

        if st.button(f"💾 Save {sem['name']}", key=f"save_{sem['id']}", type="primary"):
            new_courses = edited_df.to_dict("records")
            new_courses = [c for c in new_courses if str(c.get("code", "")).strip() or str(c.get("title", "")).strip()]
            for c in new_courses:
                if not c.get("id") or pd.isna(c["id"]):
                    c["id"] = f"c_{datetime.now().timestamp()}_{c['code']}"
                c["credits"] = float(c["credits"]) if pd.notna(c.get("credits")) else 0.0
                c["marks"] = 0.0 # Default empty marks since we removed the column
                c["grade"] = str(c["grade"]) if pd.notna(c.get("grade")) else ""
                c["ngpa"] = bool(c.get("ngpa", False))

            semesters_list[i]["courses"] = new_courses
            save_all_courses(semesters_list)
            st.success("Saved successfully!")
            st.rerun()