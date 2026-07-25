import streamlit as st
import os
from groq import Groq
from fpdf import FPDF
import PyPDF2
from datetime import datetime

# 1. PAGE CONFIG & STYLING (The "Insane" UI Vibe)
st.set_page_config(page_title="PathWise AI", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #FFFFFF; }
    .main-title {
        font-size: 60px; font-weight: 800;
        background: -webkit-linear-gradient(#2196F3, #f44336);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px;
    }
    .stFileUploader { background: rgba(255, 255, 255, 0.05); border-radius: 15px; padding: 20px; border: 1px solid rgba(255, 255, 255, 0.1); }
    .result-card { background: rgba(255, 255, 255, 0.03); padding: 20px; border-radius: 10px; border-left: 5px solid #2196F3; }
    </style>
    """, unsafe_allow_html=True)

# 2. CORE LOGIC FUNCTIONS (Integrated from your files)

def extract_text_from_pdf(uploaded_file):
    """Integrated from your parser.py logic"""
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error: {e}"

def format_links_locally(ai_text):
    """Integrated from your analyzer.py logic"""
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

def generate_pdf_bytes(analysis_text, target_role):
    """Integrated from your reporter.py logic"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(33, 150, 243)
    pdf.cell(0, 15, "PATHWISE AI: STRATEGIC CAREER REPORT", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Target Role: {target_role.upper()}", ln=True)
    pdf.cell(0, 10, f"Analysis Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", size=11)
    clean_text = analysis_text.encode('ascii', 'ignore').decode('ascii')
    for line in clean_text.split('\n'):
        pdf.multi_cell(0, 8, line)
    
    return pdf.output(dest='S').encode('latin-1')

# 3. SIDEBAR (Control Center)
with st.sidebar:
    st.title("Control Center ⚙️")
    # Using the key you provided in your analyzer file
    # Reads from .env file automatically, or leaves it blank for user input
    default_key = os.getenv("GROQ_API_KEY", "")
    groq_key = st.text_input("Enter Groq API Key", type="password", value=default_key)
    st.divider()
    st.success("System: Ready")

# 4. MAIN DASHBOARD
st.markdown('<h1 class="main-title">PATHWISE AI</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>Bridging the gap between college and the corporate world.</p>", unsafe_allow_html=True)
st.write("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📁 Upload Resume")
    uploaded_file = st.file_uploader("Drop PDF here", type="pdf")

with col2:
    st.subheader("🎯 Target Career")
    target_role = st.text_input("e.g. Frontend Developer", placeholder="What is your dream job?")

if st.button("🚀 GENERATE STRATEGIC REPORT"):
    if uploaded_file and target_role and groq_key:
        with st.spinner("AI is analyzing your path..."):
            # Step 1: Parse
            resume_text = extract_text_from_pdf(uploaded_file)
            
            # Step 2: Analyze (Groq)
            try:
                client = Groq(api_key=groq_key)
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": "You are a career expert. Output ONLY: Match Score (X/100), 3 Missing Skills, and 1 Project Idea."},
                        {"role": "user", "content": f"Resume: {resume_text[:3000]}\nRole: {target_role}"}
                    ],
                    temperature=0.1,
                )
                raw_ai_response = completion.choices[0].message.content
                final_analysis = format_links_locally(raw_ai_response)
                
                # Step 3: UI Display
                st.markdown("---")
                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                st.subheader("Analysis Complete")
                st.text(final_analysis)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Step 4: PDF Generation & Download
                pdf_data = generate_pdf_bytes(final_analysis, target_role)
                st.download_button(
                    label="📥 Download Professional Report",
                    data=pdf_data,
                    file_name=f"PathWise_{target_role.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Analysis failed: {e}")
    else:
        st.warning("Please upload a resume, specify a role, and ensure your API key is active.")

# 5. FOOTER
st.write("---")
st.caption("Developed as part of the 2027 Graduation Roadmap.")