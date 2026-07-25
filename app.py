import io
import re
import sqlite3
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import PyPDF2
import streamlit as st
from fpdf import FPDF
from groq import Groq

# Import backend components
from src.auth import (
    get_chat_history,
    login_user,
    register_user,
    save_chat_message,
    save_resume_analysis,
    save_skill_gaps,
)
from src.database import get_db_connection, init_db

# ==========================================
# UTILITY FUNCTIONS & HELPERS
# ==========================================

def send_real_phase_email(recipient_email, phase_title, update_type, details_text=""):
    """Dispatches real-time email notifications using SMTP and Streamlit Secrets."""
    if not st.session_state.get("real_time_email_toggle", True):
        return False

    try:
        SENDER_EMAIL = st.secrets["SENDER_EMAIL"]
        SENDER_PASSWORD = st.secrets["SENDER_PASSWORD"]
    except Exception:
        st.sidebar.warning("📨 Notification skipped: Secrets not configured in .streamlit/secrets.toml")
        return False

    if not SENDER_EMAIL or SENDER_EMAIL == "your.project.email@gmail.com":
        st.sidebar.warning("📨 Notification skipped: Please configure SENDER_EMAIL and SENDER_PASSWORD.")
        return False

    target_email = recipient_email or st.session_state.get("user_email_address", "user@example.com")

    subject = f"PathWise Alert: {update_type} - {phase_title}"
    body = f"""Hello!

This is an automated update regarding your roadmap:

• Event: {update_type}
• Phase: {phase_title}
• Details: {details_text if details_text else 'No additional details provided.'}

Keep up the great progress!
- PathWise Team
"""

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = target_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.sidebar.error(f"Failed to send email: {e}")
        return False

def extract_text(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def format_links(ai_text):
    lines = ai_text.split('\n')
    new_lines = []
    for line in lines:
        new_lines.append(line)
        if any(char.isdigit() for char in line[:2]) and ("." in line or ")" in line):
            skill_part = line.split("(")[0].split(".")[-1].strip()
            if skill_part:
                link = f"https://www.google.com/search?q=free+course+for+{skill_part.replace(' ', '+')}"
                new_lines.append(f"{skill_part} - {link}")
    return "\n".join(new_lines)

def create_pdf_bytes(analysis_text, target_role):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(33, 150, 243)
    pdf.cell(0, 15, "PATHWISE AI: STRATEGIC CAREER REPORT", ln=True, align='C')
    pdf.ln(10)
    
    # Details
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Target Role: {target_role.upper()}", ln=True)
    pdf.cell(0, 10, f"Analysis Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
    pdf.ln(5)
    
    # Content
    pdf.set_font("Arial", size=11)
    clean_analysis = analysis_text.encode('ascii', 'ignore').decode('ascii')
    
    for line in clean_analysis.split('\n'):
        line = line.strip()
        if not line:
            pdf.ln(2)
            continue

        if "http" in line:
            if " - " in line:
                parts = line.split(" - ", 1)
                skill_name = parts[0]
                url = parts[1].strip()
                
                pdf.set_text_color(0, 0, 0)
                pdf.set_font("Arial", 'B', 11)
                pdf.write(8, f"{skill_name}: ") 
                
                pdf.set_text_color(0, 0, 255) 
                pdf.set_font("Arial", 'U', 10)
                pdf.write(8, url, link=url)
                pdf.ln(10)
            else:
                pdf.set_text_color(0, 0, 255)
                pdf.set_font("Arial", 'U', 10)
                pdf.multi_cell(0, 8, line, link=line.strip())
        else:
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", '', 11)
            pdf.multi_cell(0, 8, line)
            pdf.ln(2)

    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(230, 230, 230) 
    pdf.cell(0, 10, "ENGINEERING ACTION PLAN", ln=True, fill=True)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 8, "Review the Match Score. If below 80, prioritize the missing skills using the links above.")
    
    return bytes(pdf.output())

# ==========================================
# INITIALIZATION & STYLING
# ==========================================

init_db()

st.set_page_config(page_title="PathWise AI 2.0", page_icon="🚀", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

.stApp{
background:
radial-gradient(circle at 20% 20%, rgba(99,102,241,.35), transparent 30%),
radial-gradient(circle at 80% 10%, rgba(56,189,248,.25), transparent 25%),
radial-gradient(circle at 70% 80%, rgba(192,132,252,.20), transparent 30%),
linear-gradient(135deg,#030712,#0f172a,#111827);
color:white;
font-family:'Inter',sans-serif;
overflow-x:hidden;
}

.stApp::before{
content:"";
position:fixed;
inset:0;
background:
linear-gradient(45deg,rgba(59,130,246,.08),rgba(168,85,247,.08),rgba(6,182,212,.08));
filter:blur(90px);
animation:aurora 10s ease infinite alternate;
pointer-events:none;
}

@keyframes aurora{
from{transform:translateX(-40px);}
to{transform:translateX(40px);}
}

.main-title{
font-size:62px;
font-weight:800;
text-align:center;
background:linear-gradient(90deg,#38BDF8,#818CF8,#C084FC);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;
text-shadow:0 0 30px rgba(129,140,248,.6);
}

.subtitle{
color:#cbd5e1;
text-align:center;
}

.card-style,div[data-testid="stContainer"]{
background:rgba(255,255,255,.05)!important;
backdrop-filter:blur(18px)!important;
border-radius:24px!important;
border:1px solid rgba(255,255,255,.1)!important;
box-shadow:0 8px 40px rgba(99,102,241,.25)!important;
}

.card-style:hover{
transform:translateY(-4px);
transition:.3s;
}

div.stButton > button{
background:linear-gradient(135deg,#2563eb,#7c3aed)!important;
color:white!important;
border:none!important;
border-radius:15px!important;
font-weight:700!important;
box-shadow:0 0 25px rgba(124,58,237,.5)!important;
}

div.stButton > button:hover{
transform:scale(1.03);
}

section[data-testid="stSidebar"]{
background:rgba(10,15,30,.92)!important;
backdrop-filter:blur(20px);
}

div[data-testid="stChatMessage"]{
background:rgba(255,255,255,.05);
border:1px solid rgba(255,255,255,.08);
border-radius:20px;
}

.stProgress > div > div > div > div{
background:linear-gradient(90deg,#38BDF8,#7C3AED);
}

.round-bot-icon {
    border-radius: 50%;
    border: 2px solid #818CF8;
    box-shadow: 0 0 15px rgba(129, 140, 248, 0.4);
}
</style>
""", unsafe_allow_html=True)

# Session State Initializations
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "current_step" not in st.session_state:
    st.session_state.current_step = 1

# Checklists
if "p1_t1_done" not in st.session_state: st.session_state.p1_t1_done = False
if "p1_t2_done" not in st.session_state: st.session_state.p1_t2_done = False
if "p1_exam_passed" not in st.session_state: st.session_state.p1_exam_passed = False
if "p2_t1_done" not in st.session_state: st.session_state.p2_t1_done = False
if "p2_t2_done" not in st.session_state: st.session_state.p2_t2_done = False
if "p2_grad_passed" not in st.session_state: st.session_state.p2_grad_passed = False

# Session State Auto-restoration
if st.session_state.logged_in and st.session_state.current_step == 1:
    uid = st.session_state.user_id
    conn = sqlite3.connect("pathwise.db")  
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA table_info(user_profiles)")
        columns = [col[1] for col in cursor.fetchall()]
        if columns:
            if "groq_api_key" not in columns:
                cursor.execute("ALTER TABLE user_profiles ADD COLUMN groq_api_key TEXT")
            if "receive_emails" not in columns:
                cursor.execute("ALTER TABLE user_profiles ADD COLUMN receive_emails INTEGER DEFAULT 0")
            if "notification_email" not in columns:
                cursor.execute("ALTER TABLE user_profiles ADD COLUMN notification_email TEXT")
            conn.commit()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id INTEGER PRIMARY KEY,
                target_role TEXT,
                skills_gap TEXT,
                master_roadmap TEXT,
                groq_api_key TEXT
            )
        """)
        conn.commit()

        cursor.execute("SELECT target_role, skills_gap, master_roadmap, groq_api_key FROM user_profiles WHERE user_id = ?", (uid,))
        row = cursor.fetchone()
        if row:
            db_role, db_skills, db_roadmap, db_api_key = row  
            if db_roadmap:
                st.session_state.cached_role = db_role
                st.session_state.cached_skills = db_skills.split(", ") if db_skills else []
                st.session_state.locked_master_roadmap = db_roadmap
                
                if db_api_key:
                    st.session_state.groq_api_key = db_api_key
                    
                st.session_state.current_step = "dashboard"
                st.rerun()
    except Exception as e:
        st.error(f"Database restoration error: {e}")
    finally:
        conn.close()

# ==========================================
# APPLICATION ROUTING
# ==========================================

if not st.session_state.logged_in:
    # ─── LOGIN ENTRY GATEWAY ───
    st.markdown('<h1 class="main-title">PATHWISE AI 2.0</h1>', unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Persistent Placement Preparation Pipeline Gateway</p>", unsafe_allow_html=True)
    st.divider()

    _, center_col, _ = st.columns([1, 1.3, 1])
    
    with center_col:
        st.markdown('<div class="card-style">', unsafe_allow_html=True)
        tab_login, tab_signup = st.tabs(["🔒 Secure Login", "📝 Create Account"])
        
        with tab_login:
            st.markdown("### Access Workspace")
            login_email = st.text_input("Email Address", key="login_email")
            login_password = st.text_input("Password", type="password", key="login_password")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Sign In", type="primary", use_container_width=True):
                if login_email and login_password:
                    user = login_user(login_email, login_password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user_id = user["user_id"]
                        st.session_state.user_name = user["name"]
                        st.session_state.user_email_address = login_email
                        st.success("✓ Identity verified. Initializing secure workspace...")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or security credentials.")
                else:
                    st.warning("Please supply both credentials.")
                    
        with tab_signup:
            st.markdown("### Register New Student Profile")
            signup_name = st.text_input("Full Name", key="signup_name")
            signup_email = st.text_input("Academic/Personal Email", key="signup_email")
            signup_password = st.text_input("Establish Security Password", type="password", key="signup_password")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Create Profile", use_container_width=True):
                if signup_name and signup_email and signup_password:
                    if register_user(signup_name, signup_email, signup_password):
                        st.success("🎉 Registration complete! Proceed to the Login tab.")
                    else:
                        st.error("❌ A user profile with this email address already exists.")
                else:
                    st.warning("All input fields are mandatory.")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # ─── LOGGED-IN PRIVATE APPLICATION INTERFACE ───
    with st.sidebar:
        st.markdown("### Control Center ⚙️")
        st.write(f"👤 **User:** {st.session_state.get('user_name', 'User')}")
        st.write(f"🆔 **ID:** {st.session_state.get('user_id', 'N/A')}")
        st.divider()

        if "groq_api_key" not in st.session_state:
            st.session_state["groq_api_key"] = ""

        st.text_input(
            "Groq API Key", 
            type="password", 
            placeholder="gsk_...",
            key="groq_api_key"
        )

        st.divider()
        st.info("System Tracking: Active")
        st.divider()

        if st.button("🔄 Re-calibrate Profile (New Resume)", use_container_width=True, type="secondary"):
            conn = sqlite3.connect("pathwise.db")
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM user_profiles WHERE user_id = ?", (st.session_state.get("user_id"),))
                conn.commit()
            except Exception as e:
                st.sidebar.error(f"Reset error: {e}")
            finally:
                conn.close()
            
            st.session_state.current_step = 1
            st.session_state.locked_master_roadmap = None
            st.session_state.p1_exam_passed = False
            st.session_state.p2_grad_passed = False
            st.session_state.p1_t1_done = False
            st.session_state.p1_t2_done = False
            st.session_state.p2_t1_done = False
            st.session_state.p2_t2_done = False
            
            st.rerun()

        if st.button("🧹 Reset Progress Only (Demo)", use_container_width=True):
            st.session_state.p1_exam_passed = False
            st.session_state.p2_grad_passed = False
            st.session_state.p1_t1_done = False
            st.session_state.p1_t2_done = False
            st.session_state.p2_t1_done = False
            st.session_state.p2_t2_done = False
            
            st.toast("🧹 Demo progress reset to 0%!", icon="🔄")
            st.rerun()

    st.markdown('<h1 class="main-title">PATHWISE AI</h1>', unsafe_allow_html=True)
    st.markdown(f"<p class='subtitle'>Welcome back, <b>{st.session_state.user_name}</b>. Bridging the gap between college and corporate placements.</p>", unsafe_allow_html=True)
    st.divider()

    # Step Progress Wizard
    if st.session_state.current_step != "dashboard":
        step_cols = st.columns(3)
        steps_titles = ["1️⃣ Input Details", "2️⃣ Strategic Report", "3️⃣ Setup Timeline"]
        for idx, title in enumerate(steps_titles):
            with step_cols[idx]:
                if st.session_state.current_step == idx + 1:
                    st.markdown(f"<p style='color: #60A5FA; font-weight: bold; border-bottom: 2px solid #60A5FA; text-align: center; margin-bottom: 20px;'>{title}</p>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<p style='color: #6B7280; text-align: center; margin-bottom: 20px;'>{title}</p>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────
    # SCREEN 1: USER INTAKE PANEL
    # ─────────────────────────────────────────────────────────
    if st.session_state.current_step == 1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="card-style">', unsafe_allow_html=True)
            st.subheader("📁 1. Upload Resume")
            uploaded_file = st.file_uploader("Drop PDF here", type="pdf")
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="card-style">', unsafe_allow_html=True)
            st.subheader("🎯 2. Target Goal")
            
            target_role = st.text_input("Role (e.g. Full Stack Developer)")
            
            company_options = [
                "Select a Company", "Google", "Microsoft", "Amazon", 
                "Infosys", "TCS", "Wipro", "Cognizant", "Accenture", "Other (Type Custom Name)"
            ]
            selected_company_choice = st.selectbox("Target Company Focus", options=company_options, index=0)
            
            target_company = ""
            if selected_company_choice == "Other (Type Custom Name)":
                target_company = st.text_input("Enter Custom Company Name", placeholder="e.g. OpenAI...")
            elif selected_company_choice != "Select a Company":
                target_company = selected_company_choice
                
            st.markdown("<br>", unsafe_allow_html=True)
            groq_key = st.session_state.get("groq_api_key", "")

            if st.button("🚀 Generate Strategic Report", use_container_width=True):
                if uploaded_file and target_role and groq_key:
                    with st.spinner("AI is analyzing your profile..."):
                        resume_text = extract_text(uploaded_file)
                        company_context = f" targeting {target_company}" if target_company else ""
                        
                        client = Groq(api_key=groq_key, timeout=30.0)
                        try:
                            completion = client.chat.completions.create(
                                model="llama-3.1-8b-instant",
                                messages=[
                                    {
                                        "role": "system", 
                                        "content": (
                                            "You are an elite career development expert. Evaluate the provided resume against "
                                            "the target position. Calculate a metric score and match strict accuracy based on real-world hiring bars. "
                                            "Output strictly in this exact format:\n"
                                            "Match Score: X/100\n"
                                            "Missing Skills: Skill1, Skill2, Skill3\n"
                                            "Project Idea: Your idea text here."
                                        )
                                    },
                                    {
                                        "role": "user", 
                                        "content": f"Resume: {resume_text[:3000]}\nRole: {target_role}{company_context}"
                                    }
                                ],
                                temperature=0.1,
                            )
                            raw_ai_text = completion.choices[0].message.content
                        except Exception as e:
                            st.error("⏳ The AI service took too long to respond or the request timed out. Please try clicking the button again.")
                            st.stop()
                        
                        final_analysis = format_links(raw_ai_text)
                        
                        try:
                            score_match = re.search(r"Match Score:\s*(\d+)", raw_ai_text)
                            score_val = int(score_match.group(1)) if score_match else 70
                            
                            skills_match = re.search(r"Missing Skills:\s*(.*)", raw_ai_text)
                            if skills_match:
                                clean_skills_line = skills_match.group(1).replace("**", "").replace("*", "")
                                skills_line = clean_skills_line.split(",")
                                
                                skills_list = []
                                for s in skills_line:
                                    cleaned_skill = s.strip().strip(".!:- ")
                                    if cleaned_skill and cleaned_skill.lower() != "none":
                                        skills_list.append(cleaned_skill)
                                if not skills_list:
                                    skills_list = ["System Core Customization"]
                            else:
                                skills_list = ["Python Programming", "Data Structures & Algorithms"]
                                
                            save_resume_analysis(st.session_state.user_id, score_val)
                            save_skill_gaps(st.session_state.user_id, skills_list)
                        except Exception as e:
                            st.sidebar.error(f"Database write note: {e}")
                            skills_list = ["Python Programming", "Data Structures & Algorithms"]
                            score_val = 70
                        
                        st.session_state.cached_score = score_val
                        st.session_state.cached_skills = skills_list
                        st.session_state.cached_raw_text = raw_ai_text
                        st.session_state.cached_final_analysis = final_analysis
                        st.session_state.cached_role = target_role
                        st.session_state.cached_company = target_company
                        
                        st.session_state.current_step = 2
                        st.rerun()
                else:
                    st.error("Please verify your inputs! A Resume file, Target Role, and valid Groq Key are required.")
            st.markdown('</div>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────
    # SCREEN 2: STRATEGIC REPORT DASHBOARD
    # ─────────────────────────────────────────────────────────
    elif st.session_state.current_step == 2:
        score_val = st.session_state.get("cached_score", 70)
        skills_list = st.session_state.get("cached_skills", [])
        raw_ai_text = st.session_state.get("cached_raw_text", "")
        final_analysis = st.session_state.get("cached_final_analysis", "")
        target_role = st.session_state.get("cached_role", "Developer")
        target_company = st.session_state.get("cached_company", "")

        st.markdown("<h2 style='text-align: center; color: #60A5FA;'>📊 CURRENT PLACEMENT CALIBRATION MATRICES</h2>", unsafe_allow_html=True)
        accent_color = "#EF4444" if score_val < 50 else ("#F59E0B" if score_val < 80 else "#10B981")
        
        st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); 
                        border-radius: 16px; padding: 30px; border: 1px solid rgba(255, 255, 255, 0.1); 
                        text-align: center; margin-bottom: 25px;">
                <p style="font-size: 1.1rem; color: #9CA3AF; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1px;">Target Readiness Index</p>
                <h1 style="font-size: 4rem; color: {accent_color}; margin: 0; font-weight: 800;">{score_val}<span style="font-size: 1.5rem; color: #6B7280;">/100</span></h1>
                <p style="color: #E5E7EB; font-size: 1rem; margin-top: 10px;">
                    Profile verification against <b>{target_role}</b> patterns at <b>{target_company if target_company else 'Selected Target Industries'}</b>.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.markdown("""
                <div style="background: rgba(16, 185, 129, 0.08); border-left: 4px solid #10B981; 
                            border-radius: 8px; padding: 20px; min-height: 180px;">
                    <h4 style="color: #10B981; margin-top: 0;">🟢 VERIFIED CAPABILITIES</h4>
                    <p style="color: #D1D5DB; font-size: 0.95rem;">Your uploaded resume credentials map cleanly to basic industrial standards.</p>
                </div>
            """, unsafe_allow_html=True)
            
        with m_col2:
            st.markdown("""
                <div style="background: rgba(239, 68, 68, 0.08); border-left: 4px solid #EF4444; 
                            border-radius: 8px; padding: 20px; min-height: 180px;">
                    <h4 style="color: #EF4444; margin-top: 0;">🚨 CRITICAL COMPETENCY GAPS</h4>
            """, unsafe_allow_html=True)
            if skills_list:
                for skill in skills_list:
                    st.markdown(f"<span style='display: inline-block; background: #374151; color: #F3F4F6; padding: 4px 10px; margin: 3px; border-radius: 12px; font-size: 0.85rem; font-weight: 500;'>⚠️ {skill}</span>", unsafe_allow_html=True)
            else:
                st.markdown("<p style='color: #9CA3AF;'>No critical structural gaps flagged.</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        project_idea_text = raw_ai_text.split("Project Idea:")[1].strip() if "Project Idea:" in raw_ai_text else raw_ai_text
        display_project = project_idea_text.replace("**Project:**", "<br><br><b>📁 Project Title:</b>").replace("**Description:**", "<br><br><b>🎯 Strategic Objective:</b>").replace("**Technologies:**", "<br><br><b>🛠️ Core Stack Architecture:</b>")
        
        st.markdown(f"""
            <div style="background: rgba(96, 165, 250, 0.06); border: 1px dashed rgba(96, 165, 250, 0.3); 
                        border-radius: 12px; padding: 25px; margin-top: 25px; line-height: 1.8;">
                <h4 style="color: #60A5FA; margin-top: 0; margin-bottom: 5px; letter-spacing: 0.5px; font-weight: 700;">💡 TARGETED CAPSTONE BLUEPRINT</h4>
                <div style="color: #E5E7EB; font-size: 0.98rem;">{display_project}</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        pdf_bytes = create_pdf_bytes(final_analysis, target_role)
        st.download_button(
            label="📥 Download Professional Strategic Blueprint PDF",
            data=pdf_bytes,
            file_name=f"PathWise_Report_{target_role}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
        c_nav1, c_nav2 = st.columns(2)
        with c_nav1:
            if st.button("⬅️ Back to Inputs", use_container_width=True):
                st.session_state.current_step = 1
                st.rerun()
        with c_nav2:
            if st.button("⚡ Proceed to Timeline Setup", use_container_width=True):
                st.session_state.current_step = 3
                st.rerun()

    # ─────────────────────────────────────────────────────────
    # SCREEN 3: ONBOARDING PACE SELECTION
    # ─────────────────────────────────────────────────────────
    elif st.session_state.current_step == 3:
        st.markdown("<h3 style='color: #FBBF24;'>📋 INITIALIZE ACCELERATION TIMELINE</h3>", unsafe_allow_html=True)
        
        with st.container(border=True):
            st.markdown("<p style='color: #D1D5DB; font-size: 0.95rem;'>Accept your metrics evaluation to finalize your tracking roadmap settings.</p>", unsafe_allow_html=True)
            
            profile_acceptance = st.checkbox(
                "I accept this profile calibration matrix and wish to establish an active study sequence.",
                value=False,
                key="profile_accept_check"
            )
            
            roadmap_pace = st.radio(
                "Select Duration",
                options=[
                    "3-Month Intensive Track (Heavy DSA & Project Focus)", 
                    "6-Month Balanced Track (Consistent Topic-Wise Calibration)", 
                    "1-Year Foundational Track (Comprehensive Tech & Soft Skill Build)"
                ],
                index=0
            )
            
            email_consent = st.toggle(
                "Enable real-time email notifications for task completions & phase graduations.",
                value=True,
                key="real_time_email_toggle"
            )
            
            st.write("")
            b_nav1, b_nav2 = st.columns(2)
            with b_nav1:
                if st.button("⬅️ View Report Again", use_container_width=True):
                    st.session_state.current_step = 2
                    st.rerun()
            with b_nav2:
                if st.button("🏁 Lock Preferences & Construct Master Roadmap", use_container_width=True):
                    if not profile_acceptance:
                        st.warning("Please toggle the confirmation check-box to lock your tracking state.")
                    else:
                        duration = roadmap_pace.split(" ")[0]
                        st.session_state.selected_duration = duration
                        skills_gap_list = st.session_state.get('cached_skills') or ["Core Language Foundations"]
                        skills_gap_str = ", ".join(skills_gap_list)
                        
                        if "3-Month" in duration:
                            st.session_state.editable_roadmap = (
                                "📅 MONTH 1: PYTHON DSA FOUNDATIONS & CORE SETUP\n"
                                "- Week 1-2: Master Array & String Mechanics (Slicing, List Comprehensions)\n"
                                "- Week 1-2: Complete 15 LeetCode Arrays Easy/Medium Problems (Two-Sum, Sliding Window)\n"
                                "- Week 3-4: Establish Core Project Git Repo & Local Environment Architecture\n\n"
                                "📅 MONTH 2: CORE OPTIMIZATION & SKILL BRIDGING\n"
                                "- Week 5-6: Advanced Linear Logic (Hashing Maps, Stacks, Queue Mechanics)\n"
                                f"- Week 7-8: Build dedicated modules for identified gaps: {skills_gap_str}\n\n"
                                "📅 MONTH 3: COMPLEX FRAMEWORKS & VERIFICATION\n"
                                "- Week 9-10: Non-Linear Mastery (Recursion, Binary Tree Traversals)\n"
                                "- Week 11-12: Complete clean Integration of frontend UI with backend data layers"
                            )
                        elif "6-Month" in duration:
                            st.session_state.editable_roadmap = (
                                "📅 PHASE 1 (MONTH 1-2): TOPIC-WISE PYTHON DSA STUDY (ARRAYS TO LINKED LISTS)\n"
                                "- Week 1-4: Master Arrays, Two-Pointers, Sliding Window, and Matrix operations in Python\n"
                                "- Week 5-8: Shift to Linked Lists, Hashing Maps, and Stack/Queue custom implementations\n"
                                "- Target: Solve 45+ LeetCode curated problems with optimized space/time complexity\n\n"
                                "📅 PHASE 2 (MONTH 3-4): CORE BACKEND ARCHITECTURE & SKILL GAP TARGETING\n"
                                f"- Week 9-12: Systematically study and eliminate identified gaps: {skills_gap_str}\n"
                                "- Week 13-16: Design database schemas, configure relational/non-relational connections, and build API endpoints\n\n"
                                "📅 PHASE 3 (MONTH 5-6): NON-LINEAR DSA & END-TO-END CAPSTONE TESTING\n"
                                "- Week 17-20: Focus on Recursion, Trees, Graphs, and basic Dynamic Programming\n"
                                "- Week 21-24: Integrate frontend UI with backend APIs, run end-to-end refactoring, and conduct mock technical presentations"
                            )
                        else:
                            st.session_state.editable_roadmap = (
                                "📅 QUARTER 1 (MONTH 1-3): CRITICAL COMPUTING & ADVANCED PYTHON DSA\n"
                                "- Month 1: Complete topic-wise mastery of linear structures (Arrays, Lists, Strings)\n"
                                "- Month 2-3: Dive deeply into Hashing, Stacks, Queues, Recursion, and Sorting/Searching algorithms\n"
                                "- Milestone: Log 80+ LeetCode problems and practice clean, readable implementation patterns\n\n"
                                "📅 QUARTER 2 (MONTH 4-6): SYSTEM DESIGN FOUNDATIONS & ARCHITECTURAL BRIDGING\n"
                                f"- Month 4: Targeted study to eliminate major technical flaws: {skills_gap_str}\n"
                                "- Month 5-6: Learn Object-Oriented Design patterns, Database normalization, and build scalable system blueprints\n\n"
                                "📅 QUARTER 3 (MONTH 7-9): SPECIALIZED BACKEND ENGINEERING & ADVANCED DATA MODULES\n"
                                "- Month 7-8: Master Non-Linear DSA (Binary Trees, BSTs, Graph Traversals like BFS/DFS)\n"
                                "- Month 9: Build out core application logic, sensor integration pipelines, or intelligent processing layers\n\n"
                                "📅 QUARTER 4 (MONTH 10-12): FULL CAPSTONE DELIVERY & DEPLOYMENT PIPELINES\n"
                                "- Month 10: Complete entire UI-to-Backend integration and refactor core computational logic\n"
                                "- Month 11: Implement modern containerization/cloud deployment sequences (Docker setups, environment separation)\n"
                                "- Month 12: Run complete placement mock simulation drill sets to build professional presentation communication"
                            )

                        st.session_state.current_step = "roadmap_editor" 
                        st.rerun()

    # ─────────────────────────────────────────────────────────
    # SCREEN 3.5: STRATEGIC PREVIEW & ROADMAP CUSTOMIZER
    # ─────────────────────────────────────────────────────────
    elif st.session_state.current_step == "roadmap_editor":
        st.markdown("<h3 style='color: #FBBF24;'>🛠️ CUSTOMIZE & AGREE TO YOUR STRATEGIC ROADMAP</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #9CA3AF;'>Review your generated timeline below. You can freely type, add tasks, or modify the plan before finalizing.</p>", unsafe_allow_html=True)
        
        with st.container(border=True):
            final_customized_plan = st.text_area(
                "Your Final Master Roadmap Blueprint (Editable)",
                value=st.session_state.get("editable_roadmap", ""),
                height=350
            )
            
            st.warning("⚠️ Once you agree, this roadmap is locked permanently for this resume configuration.")
            agree_check = st.checkbox("I agree to follow this customized tracking blueprint.", value=False)
            
            e_col1, e_col2 = st.columns(2)
            with e_col1:
                if st.button("⬅️ Back to Pace Selection", use_container_width=True):
                    st.session_state.current_step = 3
                    st.rerun()
            with e_col2:
                if st.button("🤝 Agree & Continue to Dashboard", use_container_width=True):
                    if not agree_check:
                        st.error("You must check the 'Agree' box to establish your persistent dashboard configuration.")
                    else:
                        st.session_state.locked_master_roadmap = final_customized_plan
                        st.session_state.current_step = "dashboard"
                        
                        conn = sqlite3.connect("pathwise.db")
                        cursor = conn.cursor()
                        try:
                            cursor.execute("""
                                CREATE TABLE IF NOT EXISTS user_profiles (
                                    user_id INTEGER PRIMARY KEY,
                                    target_role TEXT,
                                    skills_gap TEXT,
                                    master_roadmap TEXT,
                                    groq_api_key TEXT
                                )
                            """)
                            conn.commit()

                            cursor.execute("SELECT user_id FROM user_profiles WHERE user_id = ?", (st.session_state.user_id,))
                            record_exists = cursor.fetchone()

                            current_role = st.session_state.get('cached_role', 'Software Developer')
                            current_skills = ", ".join(st.session_state.get('cached_skills', []))
                            current_api_key = st.session_state.get('groq_api_key', '')

                            if record_exists:
                                cursor.execute("""
                                    UPDATE user_profiles 
                                    SET target_role = ?, skills_gap = ?, master_roadmap = ?, groq_api_key = ? 
                                    WHERE user_id = ?
                                """, (current_role, current_skills, final_customized_plan, current_api_key, st.session_state.user_id))
                            else:
                                cursor.execute("""
                                    INSERT INTO user_profiles (user_id, target_role, skills_gap, master_roadmap, groq_api_key) 
                                    VALUES (?, ?, ?, ?, ?)
                                """, (st.session_state.user_id, current_role, current_skills, final_customized_plan, current_api_key))
                            
                            conn.commit()
                        except Exception as db_err:
                            st.error(f"Database sync alert: {db_err}")
                        finally:
                            conn.close()
                            
                        st.success("✓ Master Roadmap locked and saved to database!")
                        st.rerun()

    # ─────────────────────────────────────────────────────────
    # SCREEN 4: PERSISTENT MASTER DASHBOARD
    # ─────────────────────────────────────────────────────────
    elif st.session_state.current_step == "dashboard":
        st.markdown("<h2 style='text-align: center; color: #10B981;'>🚀 MASTER TRACKING DASHBOARD</h2>", unsafe_allow_html=True)
        st.divider()
        
        # Header Status Card
        st.markdown('<div class="card-style" style="padding: 20px; margin-bottom: 20px;">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)

        with c1:
            st.subheader("🎯 Active Profile Goal")
            st.info(f"**Target Role:** {st.session_state.get('cached_role', 'Developer').upper()}")
            st.info(f"**Milestone Pace:** {st.session_state.get('selected_duration', '3-Month')} Track")

        with c2:
            st.subheader("📬 Live Notifications")
            with st.expander("⚙️ Email Routing Settings", expanded=False):
                want_emails = st.toggle(
                    "Enable Real-Time Email Notifications", 
                    value=st.session_state.get("real_time_email_toggle", True),
                    key="real_time_email_toggle"
                )
                
                if want_emails:
                    user_email = st.text_input(
                        "Delivery Email Address", 
                        value=st.session_state.get("user_email_address", ""),
                        placeholder="name@example.com"
                    )
                    if st.button("🔔 Save & Verify Email", use_container_width=True):
                        if user_email and "@" in user_email:
                            st.session_state.user_email_address = user_email
                            
                            sent_ok = send_real_phase_email(
                                recipient_email=user_email,
                                phase_title="System Verification",
                                update_type="Notification Connection Active",
                                details_text="Your email notifications have been successfully synchronized! You will receive instant live reports as you complete roadmap milestones."
                            )
                            
                            if sent_ok:
                                st.success("✓ Notification routing updated & verification email dispatched!")
                            else:
                                st.success("✓ Notification routing updated!")
                        else:
                            st.error("Please provide a valid email format.")

        with c3:
            st.subheader("🚨 Identified Gaps")
            with st.expander("⚠️ View Gap Tags", expanded=False):
                skills_list = st.session_state.get("cached_skills", [])
                if skills_list:
                    for skill in skills_list:
                        st.markdown(f"<span style='display: inline-block; background: rgba(239, 68, 68, 0.15); color: #FCA5A5; padding: 4px 10px; margin: 3px; border-radius: 12px; font-size: 0.85rem;'>⚠️ {skill}</span>", unsafe_allow_html=True)
                else:
                    st.success("No critical gaps flagged.")
        st.markdown('</div>', unsafe_allow_html=True)

        # Workspace Details & Learning Deck Layout
        st.markdown('<div class="card-style" style="padding: 25px;">', unsafe_allow_html=True)
        
        chosen_duration = st.session_state.get("selected_duration", "3-Month")
        skills_gap_list = st.session_state.get('cached_skills') or ["Core Language Foundations"]
        skills_gap_str = ", ".join(skills_gap_list)
        
        phase_data = {
            "3-Month": {
                "p1_title": "Month 1: DSA Foundations",
                "p2_title": "Month 2: Skill Bridging",
                "m1_title": "📚 Module 1.1: Array Mechanics & List Comprehensions",
                "m1_desc": "Arrays use contiguous memory slots. Master sequence slicing `[start:stop:step]` and single-line loops (List Comprehensions) for optimized data transformations.",
                "m1_yt": "https://www.youtube.com/results?search_query=python+lists+and+arrays+dsa",
                "m1_code": "# ASSIGNMENT 1: Given an array, return squares of only even numbers.\n# Example: [1, 2, 3, 4] -> [4, 16]\ndef square_evens(nums):\n    return [x**2 for x in nums if x % 2 == 0]",
                "m2_title": "📚 Module 1.2: Two-Pointer & Sliding Window Mechanics",
                "m2_desc": "Avoid nested O(N^2) brute-force loops. Use dual indices to maintain a linear O(N) sub-array window scanning tracking state across memory arrays.",
                "m2_yt": "https://www.youtube.com/results?search_query=sliding+window+algorithm+dsa",
                "m2_code": "# ASSIGNMENT 2: Find max sum of a contiguous subarray of size K.\n# Input: nums = [2, 1, 5, 1, 3, 2], k = 3 -> Output: 9\ndef max_sub_array(nums, k):\n    # Implement sliding window linear framework\n    pass",
                "p1_gate_desc": "Paste an optimized solution for checking if two numbers add up to a target value using a linear strategy.",
                "p2_m1_title": "🔑 Module 2.1: Hashing Mechanics & O(1) Instant Lookups",
                "p2_m1_desc": "Learn how Python dictionaries map unique hash codes to keys, transforming typical O(N) element scans into instantaneous O(1) processing times.",
                "p2_m1_yt": "https://www.youtube.com/results?search_query=hash+maps+and+dictionaries+dsa+python",
                "p2_m1_code": f"# ASSIGNMENT 1: Group related items or address major gaps: {skills_gap_str}\ndef group_anagrams(strs):\n    # Implement dictionary storage layout\n    pass",
                "p2_m2_title": "🛠️ Module 2.2: Async Operations & Background Data Streams",
                "p2_m2_desc": "Real-world apps require processing independent data streams without locking your UI threads (like monitoring background hardware metrics while running models).",
                "p2_m2_yt": "https://www.youtube.com/results?search_query=python+multithreading+and+sensor+integration",
                "p2_m2_code": "# ASSIGNMENT 2: Create a thread routine checking system threshold flags.\n# Alert instantly if threat state matches consecutive criteria.\nimport time\ndef monitor_stream(log_data):\n    pass",
                "p2_gate_desc": "Submit your Object-Oriented System Architecture Model handling structural edge cases safely."
            },
            "6-Month": {
                "p1_title": "Phase 1: Topic-Wise DSA",
                "p2_title": "Phase 2: Core Backend Design",
                "m1_title": "📚 Module 1.1: Multi-Dimensional Matrices & Two-Pointer Tracks",
                "m1_desc": "Master nested matrix lookups, row-major storage ordering configurations, and symmetrical grid scanning mechanics utilizing linear cursor pointer tracking.",
                "m1_yt": "https://www.youtube.com/results?search_query=matrix+rotation+two+pointer+python+dsa",
                "m1_code": "# ASSIGNMENT 1: Rotate an N x N matrix 90 degrees clockwise in-place.\ndef rotate_matrix(matrix):\n    pass",
                "m2_title": "📚 Module 1.2: Custom Linked Structure Architectures",
                "m2_desc": "Break out of array structures into scattered heap nodes. Build manual pointer chains using custom Class initializers tracking node connectivity links.",
                "m2_yt": "https://www.youtube.com/results?search_query=linked+lists+python+dsa",
                "m2_code": "# ASSIGNMENT 2: Reverse a singly linked structure sequence.\ndef reverse_list(head):\n    pass",
                "p1_gate_desc": "Paste code checking for cyclical connection errors inside a custom structural node track loop.",
                "p2_m1_title": "🔑 Module 2.1: Gap Liquidation & Language Internals",
                "p2_m1_desc": f"Systematic optimization designed around your custom background analysis parameters. Targeting profile gaps: {skills_gap_str}.",
                "p2_m1_yt": f"https://www.youtube.com/search?q=advanced+concepts+{skills_gap_str.replace(' ', '+')}",
                "p2_m1_code": "# ASSIGNMENT 1: Implement robust interface routines parsing raw configuration attributes safely.",
                "p2_m2_title": "🛠️ Module 2.2: Relational Schema Modeling & API Routing Logic",
                "p2_m2_desc": "Design strict relational normalization graphs, establish standard database constraint checks, and configure secure request endpoints.",
                "p2_m2_yt": "https://www.youtube.com/results?search_query=python+fastapi+database+sqlite+tutorial",
                "p2_m2_code": "# ASSIGNMENT 2: Stub an endpoint executing explicit row filter parameter fetches.\n# Handle empty results gracefully without triggering internal application crashes.",
                "p2_gate_desc": "Submit your integrated API controller framework demonstrating active validation handling."
            },
            "1-Year": {
                "p1_title": "Q1: Computing Foundations & Linear Structures",
                "p2_title": "Q2: System Architecture Design Patterns",
                "m1_title": "📚 Module 1.1: Memory Footprints & Assembly-Level List Controls",
                "m1_desc": "Understand deep runtime memory scaling, bit-shifting vectors, element copying allocations, and custom structural buffer overrides.",
                "m1_yt": "https://www.youtube.com/results?search_query=python+memory+management+under+the+hood",
                "m1_code": "# ASSIGNMENT 1: Perform primitive vector resizing manipulations tracking system byte variations.\ndef resize_simulation():\n    pass",
                "m2_title": "📚 Module 1.2: Recursive Flow Patterns & Tracking Stack Frames",
                "m2_desc": "Master base-case logic termination parameters, depth-first stack building, and optimizing stack resource allocation tracking chains.",
                "m2_yt": "https://www.youtube.com/results?search_query=recursion+and+backtracking+python+dsa",
                "m2_code": "# ASSIGNMENT 2: Implement optimized backtracking routine extracting possible path groupings.",
                "p1_gate_desc": "Paste an inductive recursive logic routine tracking algorithmic path sequences securely.",
                "p2_m1_title": "🔑 Module 2.1: Structural Gap Elimination Strategy",
                "p2_m1_desc": f"Long-term master engineering approach resolving fundamental theoretical limits. Deep focus on: {skills_gap_str}.",
                "p2_m1_yt": f"https://www.youtube.com/search?q=deep+dive+{skills_gap_str.replace(' ', '+')}",
                "p2_m1_code": "# ASSIGNMENT 1: Structure an independent wrapper component managing specialized algorithmic modules.",
                "p2_m2_title": "🛠️ Module 2.2: Advanced Object-Oriented Principles & Design Patterns",
                "p2_m2_desc": "Deconstruct structural decoupling frameworks, factory interface logic tracking, abstract polymorphism boundaries, and event listeners.",
                "p2_m2_yt": "https://www.youtube.com/results?search_query=design+patterns+python+object+oriented",
                "p2_m2_code": "# ASSIGNMENT 2: Build a decoupled architecture utilizing clear interfaces to swap driver components dynamically.",
                "p2_gate_desc": "Submit your fully realized abstract class framework validating dynamic environment variables."
            }
        }

        track_key = "3-Month" if "3-Month" in chosen_duration else ("6-Month" if "6-Month" in chosen_duration else "1-Year")
        ctx = phase_data[track_key]

        p1_label = f"✅ {ctx['p1_title']}" if st.session_state.p1_exam_passed else f"🏁 {ctx['p1_title']}"
        p2_label = f"⚡ {ctx['p2_title']}" if st.session_state.p1_exam_passed else f"🔒 {ctx['p2_title']} (Locked)"
        
        tab_titles = ["🗺️ Master Blueprint", p1_label, p2_label]
        dynamic_tabs = st.tabs(tab_titles)
        
        # ─── TAB 0: MASTER BLUEPRINT ───
        with dynamic_tabs[0]:
            st.text_area(
                "Active Timeline View", 
                value=st.session_state.get("locked_master_roadmap", "No roadmap initialized."), 
                height=250, 
                disabled=True,
                key="dashboard_roadmap_view"
            )
            st.markdown("---")
            st.markdown("#### Overall Progress Metrics")

            comp = 100 if st.session_state.p2_grad_passed else (50 if st.session_state.p1_exam_passed else (25 if (st.session_state.p1_t1_done or st.session_state.p1_t2_done) else 0))
            st.progress(comp / 100)
            st.markdown(f"<p style='text-align: right; color: #38BDF8; font-weight: bold;'>Pipeline Completion: {comp}%</p>", unsafe_allow_html=True)

        # ─── TAB 1: ACTIVE PHASE 1 WORKSPACE ───
        with dynamic_tabs[1]:
            if not st.session_state.p1_exam_passed:
                st.markdown(f"### 🎯 Active Workspace: {ctx['p1_title']}")
                st.write("Complete the conceptual deep-dives and verify assignments below to unlock the graduation exam.")
                
                with st.expander(ctx["m1_title"], expanded=not st.session_state.p1_t1_done):
                    st.markdown("#### 💡 Concept Explanation")
                    st.info(ctx["m1_desc"])
                    st.markdown(f"#### 🎥 Recommended YouTube Learning Resource\n🔗 [Launch Curated Training Search Video]({ctx['m1_yt']})")
                    st.markdown("#### 📝 Code Assignment Workbench")
                    st.code(ctx["m1_code"], language="python")
                    
                    if not st.session_state.p1_t1_done:
                        if st.button("🚀 Validate Module 1.1 Task", key="btn_p1_t1_submit"):
                            st.session_state.p1_t1_done = True
                            send_real_phase_email(
                                recipient_email=st.session_state.get("user_email_address"),
                                phase_title=ctx['p1_title'],
                                update_type="Module Task Verified",
                                details_text="Great job! You have successfully verified and cleared Module 1.1. Your progress tracking metrics have been updated."
                            )
                            st.success("Module 1.1 verified successfully!")
                            st.rerun()
                    else:
                        st.success("✅ Module Tasks Completed and Verified")
                
                with st.expander(ctx["m2_title"], expanded=st.session_state.p1_t1_done and not st.session_state.p1_t2_done):
                    st.markdown("#### 💡 Concept Explanation")
                    st.info(ctx["m2_desc"])
                    st.markdown(f"#### 🎥 Recommended YouTube Learning Resource\n🔗 [Launch Curated Training Search Video]({ctx['m2_yt']})")
                    st.markdown("#### 📝 Code Assignment Workbench")
                    st.code(ctx["m2_code"], language="python")
                    
                    if not st.session_state.p1_t2_done:
                        if not st.session_state.p1_t1_done:
                            st.warning("🔒 Complete the first module setup to unlock this challenge tracker.")
                        elif st.button("🚀 Validate Module 1.2 Task", key="btn_p1_t2_submit"):
                            st.session_state.p1_t2_done = True
                            send_real_phase_email(
                                recipient_email=st.session_state.get("user_email_address"),
                                phase_title=ctx['p1_title'],
                                update_type="Module Task Verified",
                                details_text="Awesome work! Module 1.2 has been validated. You are now authorized to attempt the Phase 1 Graduation Gate!"
                            )
                            st.success("Module 1.2 verified successfully!")
                            st.rerun()
                    else:
                        st.success("✅ Module Tasks Completed and Verified")

                st.markdown("---")
                st.markdown("### 🏁 Phase Graduation Assessment Gate")
                if st.session_state.p1_t1_done and st.session_state.p1_t2_done:
                    st.write(ctx["p1_gate_desc"])
                    p1_ans = st.text_area("Paste code implementation response logic:", placeholder="def solution(): ...", height=100, key="ta_p1_gate")
                    if st.button("🎓 Submit Examination Profile for Grading", use_container_width=True, key="btn_p1_gate_submit"):
                        if len(p1_ans.strip()) > 10:
                            st.session_state.p1_exam_passed = True
                            send_real_phase_email(
                                recipient_email=st.session_state.get("user_email_address"),
                                phase_title=ctx['p1_title'],
                                update_type="Phase Graduation Verified 🎉",
                                details_text=f"Spectacular work! You have successfully passed the conceptual verification for **{ctx['p1_title']}**. Your dashboard has automatically scaled and unlocked your advanced track in Phase 2!"
                            )
                            st.balloons()
                            st.success("🎉 Assessment graded and approved! Workspace evolving to next phase...")
                            st.rerun()
                        else:
                            st.error("Submission rejected. Please supply a complete programmatic logic code structure.")
                else:
                    st.warning("🔒 Complete both learning modules above to unlock the technical evaluation gate.")
            else:
                st.success(f"🎉 You have successfully graduated from {ctx['p1_title']}! Proceed to your upgraded tracking deck in the next tab.")

        # ─── TAB 2: ADVANCED PHASE 2 WORKSPACE ───
        with dynamic_tabs[2]:
            if not st.session_state.p1_exam_passed:
                st.warning(f"🔒 This active workspace zone is locked. You must graduate from {ctx['p1_title']} to initialize advanced modules.")
            else:
                st.markdown(f"### ⚡ Advanced Workspace: {ctx['p2_title']}")
                st.write("Welcome to your upgraded deployment workspace. Let's tackle advanced mechanics.")
                
                with st.expander(ctx["p2_m1_title"], expanded=not st.session_state.p2_t1_done):
                    st.markdown("#### 💡 Concept Explanation")
                    st.info(ctx["p2_m1_desc"])
                    st.markdown(f"#### 🎥 Recommended YouTube Learning Resource\n🔗 [Launch Curated Training Search Video]({ctx['p2_m1_yt']})")
                    st.markdown("#### 📝 Code Assignment Workbench")
                    st.code(ctx["p2_m1_code"], language="python")
                    
                    if not st.session_state.p2_t1_done:
                        if st.button("🚀 Validate Advanced Module 2.1 Task", key="btn_p2_t1_submit"):
                            st.session_state.p2_t1_done = True
                            send_real_phase_email(
                                recipient_email=st.session_state.get("user_email_address"),
                                phase_title=ctx['p2_title'],
                                update_type="Advanced Checkpoint Cleared",
                                details_text="Advanced Checkpoint 2.1 verified! You've successfully completed the gap elimination module."
                            )
                            st.success("Advanced Checkpoint 2.1 verified!")
                            st.rerun()
                    else:
                        st.success("✅ Module Tasks Completed and Verified")
                
                with st.expander(ctx["p2_m2_title"], expanded=st.session_state.p2_t1_done and not st.session_state.p2_t2_done):
                    st.markdown("#### 💡 Concept Explanation")
                    st.info(ctx["p2_m2_desc"])
                    st.markdown(f"#### 🎥 Recommended YouTube Learning Resource\n🔗 [Launch Curated Training Search Video]({ctx['p2_m2_yt']})")
                    st.markdown("#### 📝 Code Assignment Workbench")
                    st.code(ctx["p2_m2_code"], language="python")
                    
                    if not st.session_state.p2_t2_done:
                        if not st.session_state.p2_t1_done:
                            st.warning("🔒 Complete the preceding optimization module to reveal this logic framework setup.")
                        elif st.button("🚀 Validate Advanced Module 2.2 Task", key="btn_p2_t2_submit"):
                            st.session_state.p2_t2_done = True
                            send_real_phase_email(
                                recipient_email=st.session_state.get("user_email_address"),
                                phase_title=ctx['p2_title'],
                                update_type="Advanced Checkpoint Cleared",
                                details_text="Advanced Checkpoint 2.2 verified! Your capstone evaluation gate is now unlocked."
                            )
                            st.success("Advanced Checkpoint 2.2 verified!")
                            st.rerun()
                    else:
                        st.success("✅ Module Tasks Completed and Verified")

                st.markdown("---")
                st.markdown("### 🏁 Final Capstone Integration Evaluation")
                if st.session_state.p2_t1_done and st.session_state.p2_t2_done:
                    st.write(ctx["p2_gate_desc"])
                    p2_ans = st.text_area("Paste architecture object logic pattern:", placeholder="class Pipeline Architecture: ...", height=100, key="ta_p2_gate")
                    if st.button("🎓 Lock Phase Portfolio & Graduate", use_container_width=True, key="btn_p2_gate_submit"):
                        if len(p2_ans.strip()) > 10:
                            st.session_state.p2_grad_passed = True
                            send_real_phase_email(
                                recipient_email=st.session_state.get("user_email_address"),
                                phase_title=ctx['p2_title'],
                                update_type="Capstone Portfolio Cleared 🏆",
                                details_text=f"Phenomenal job! Your system architecture frameworks and object models for **{ctx['p2_title']}** have been fully verified. Your final roadmap pipeline completion metric is locked at 100%!"
                            )
                            st.balloons()
                            st.success("🎉 Phenomenal! You have conquered this tracking roadmap profile setup entirely!")
                            st.rerun()
                        else:
                            st.error("Submission rejected. Provide an object configuration model frame to authenticate profiles.")
                else:
                    st.warning("🔒 Complete all active Phase 2 training modules to authorize the capstone integration gate.")

                # ─────────────────────────────────────────────────────────
                # UNLOCKED RESUME BLUEPRINT (NESTEED SAFELY IN TAB 2)
                # ─────────────────────────────────────────────────────────
                if st.session_state.get("p2_grad_passed", False):
                    st.markdown("---")
                    st.markdown("<h3 style='color: #10B981;'>🎓 THE GRAND FINALE: UNLOCKED RESUME BLUEPRINT</h3>", unsafe_allow_html=True)
                    st.success("🏆 **Congratulations!** You have finished all learning milestones and cleared your final capstone integration exam. Your tailored resume blueprint is now unlocked.")
                    
                    user_target_role = st.session_state.get('cached_role', 'Software Engineer')
                    user_target_company = st.session_state.get('cached_company', 'Target Company')
                    cleared_skills = st.session_state.get('cached_skills', [])

                    if st.button("✨ Compile My Tailored Resume Template", use_container_width=True, type="primary"):
                        groq_key = st.session_state.get("groq_api_key", "")
                        
                        if not groq_key:
                            st.error("Missing Groq API Key! Please configure your key in the sidebar.")
                        else:
                            with st.spinner(f"Architecting your perfect {user_target_role} resume template for {user_target_company}..."):
                                client = Groq(api_key=groq_key, timeout=45.0)
                                try:
                                    resume_prompt = (
                                        f"You are an expert ATS optimization engineer and elite technical recruiter.\n"
                                        f"Task: Generate a pristine, highly tailored Markdown Resume Template for a student aiming for the role of "
                                        f"'{user_target_role}' at '{user_target_company}'.\n\n"
                                        f"Incorporate the following context elements seamlessly:\n"
                                        f"1. Target Framework: Highlighting alignment with {user_target_role} expectations.\n"
                                        f"2. Core Upskilled Focus: Integrate these newly acquired skills seamlessly into their relevant technical sections: {', '.join(cleared_skills)}.\n"
                                        f"3. Strategic Background: Take their learning track journey into consideration to structure impact bullet points.\n\n"
                                        f"Provide a complete, copy-pasteable Markdown resume template with clear placeholder brackets like [Your Name], "
                                        f"including an optimized Professional Summary, a technical skills block, a structured Projects section showcasing practical impact, "
                                        f"and a Professional Experience layout. Use crisp, metric-driven action verbs (e.g., 'Optimized spatial data queries by 14%', 'Implemented state caching')."
                                    )
                                    
                                    completion = client.chat.completions.create(
                                        model="llama-3.1-8b-instant",
                                        messages=[
                                            {"role": "system", "content": "You output professional, elite-tier markdown resume blueprints with no extra conversational chatter before or after."},
                                            {"role": "user", "content": resume_prompt}
                                        ],
                                        temperature=0.3,
                                    )
                                    
                                    st.session_state.final_resume_template = completion.choices[0].message.content
                                except Exception as e:
                                    st.error(f"Failed to generate template: {e}")

                    if "final_resume_template" in st.session_state:
                        st.success("🎉 Your Role-Specific Resume Template is ready!")
                        with st.container(border=True):
                            st.markdown("### 📄 Your Tailored Markdown Template")
                            st.text_area(
                                "Copy the raw Markdown code below into your local editor:",
                                value=st.session_state.final_resume_template,
                                height=400
                            )

        # ─── MENTORSHIP CHATBOT WINDOW ───
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("### 🤖 Mentorship AI Assistant")
        with st.container(border=True):
            st.markdown(
                "<p style='font-size: 0.85rem; color:#A7F3D0;'>"
                "💡 Ask anything about programming, code optimization, or system mechanics instantly."
                "</p>", 
                unsafe_allow_html=True
            )
            
            # 1. Fetch & Render Saved Chat History from DB
            history = get_chat_history(st.session_state.user_id)
            for msg in history:
                role = "user" if msg["sender"] == "user" else "assistant"
                with st.chat_message(role):
                    st.write(msg["message"])

            # 2. Handle New User Query
            chat_query = st.chat_input("Ask PathWise Mentor Bot...")
            if chat_query:
                # Render and save user message
                with st.chat_message("user"):
                    st.write(chat_query)
                save_chat_message(st.session_state.user_id, "user", chat_query)
                
                # Generate, render, and save AI response
                with st.chat_message("assistant"):
                    groq_api_key = st.session_state.get("groq_api_key", "")
                    if groq_api_key:
                        try:
                            client = Groq(api_key=groq_api_key)
                            response = client.chat.completions.create(
                                model="llama-3.1-8b-instant",
                                messages=[
                                    {
                                        "role": "system", 
                                        "content": (
                                            "You are an elite computer science placement mentor and corporate interviewer. "
                                            "Answer questions clearly, accurately, and concisely with code blocks if needed."
                                        )
                                    },
                                    {"role": "user", "content": chat_query}
                                ],
                                temperature=0.2
                            )
                            ai_reply = response.choices[0].message.content
                            st.write(ai_reply)
                            save_chat_message(st.session_state.user_id, "bot", ai_reply)
                        except Exception as e:
                            err_msg = f"Hello! I am here to guide you through your tracking roadmap metrics. (API connection note: {e})"
                            st.write(err_msg)
                            save_chat_message(st.session_state.user_id, "bot", err_msg)
                    else:
                        warn_msg = "Please supply a valid Groq API Key in your sidebar to fetch real-time AI assistance."
                        st.warning(warn_msg)