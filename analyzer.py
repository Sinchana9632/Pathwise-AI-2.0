import streamlit as st
import json
import time
from groq import Groq
from fpdf import FPDF
from datetime import datetime
import PyPDF2 # Ensure you have this installed: pip install PyPDF2
import os
import streamlit as st

# 1. PAGE CONFIG & STYLING
st.set_page_config(page_title="PathWise AI", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #FFFFFF; }
    .main-title {
        font-size: 55px; font-weight: 800;
        background: -webkit-linear-gradient(#2196F3, #f44336);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center;
    }
    .stFileUploader { background: rgba(255, 255, 255, 0.05); border-radius: 15px; padding: 20px; border: 1px solid rgba(255, 255, 255, 0.1); }
    </style>
    """, unsafe_allow_html=True)

# 2. HELPER FUNCTIONS (Your Analyzer & Reporter Logic)
def extract_text_from_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def format_links_locally(ai_text):
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

def generate_pdf_report(analysis_text, target_role):
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
    
    return pdf.output(dest='S').encode('latin-1') # Return as bytes for download

# 3. SIDEBAR
with st.sidebar:
    st.title("Control Center ⚙️")
   # Reads from .env file automatically, or leaves it blank for user input
    default_key = os.getenv("GROQ_API_KEY", "")
    groq_key = st.text_input("Enter Groq API Key", type="password", value=default_key)
    st.info("System Status: **Active**")

# 4. MAIN UI
st.markdown('<h1 class="main-title">PATHWISE AI</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Bridge the gap between college and corporate world.</p>", unsafe_allow_html=True)
st.divider()

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📁 Upload Resume")
    uploaded_file = st.file_uploader("Drop your PDF here", type="pdf")

with col2:
    st.subheader("🎯 Target Role")
    target_role = st.text_input("e.g. Frontend Developer")
    
    if st.button("Generate Strategic Report"):
        if uploaded_file and groq_key:
            with st.spinner("Llama 3.1 is analyzing your path..."):
                # 1. Parse
                raw_text = extract_text_from_pdf(uploaded_file)
                
                # 2. Analyze
                client = Groq(api_key=groq_key)
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": "You are a career expert. Output ONLY: Match Score (X/100), 3 Missing Skills, and 1 Project Idea."},
                        {"role": "user", "content": f"Resume: {raw_text[:3000]}\nRole: {target_role}"}
                    ],
                    temperature=0.1,
                )
                ai_response = completion.choices[0].message.content
                final_analysis = format_links_locally(ai_response)
                
                # 3. Display
                st.markdown("### Analysis Result")
                st.text(final_analysis)
                
                # 4. PDF Generation
                pdf_bytes = generate_pdf_report(final_analysis, target_role)
                st.download_button(label="📥 Download PDF Report", data=pdf_bytes, file_name="PathWise_Report.pdf", mime="application/pdf")
        else:
            st.error("Please provide both a Resume and an API Key!")