import os
import json
import time
from datetime import datetime
from parser import extract_text
from analyzer import get_complete_analysis 
from reporter import create_visual_report

def save_report(role, report_content):
    if not os.path.exists("reports"):
        os.makedirs("reports")
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    clean_role = role.strip().replace(" ", "_").lower()
    filename = f"reports/{clean_role}_{date_str}.json"
    
    report_data = {
        "date": date_str,
        "target_role": role,
        "analysis": report_content
    }
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=4)
    return filename

def run_pathwise_ai(pdf_filename, target_role):
    # Setup paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    uploads_dir = os.path.join(base_dir, "uploads")
    pdf_path = os.path.join(uploads_dir, pdf_filename.strip())
    
    print(f"\n🔍 Analyzing Role: {target_role.upper()}...")
    try:
        # 1. Extraction
        raw_text = extract_text(pdf_path)
        
        # 2. AI Analysis via Groq
        # This now returns text that ALREADY includes the links
        report_content = get_complete_analysis(raw_text, target_role)
        
        # 3. Save JSON
        json_file = save_report(target_role, report_content)
        
        # 4. Generate PDF
        create_visual_report(json_file)
        
        print(f"✅ Success! Report saved to {json_file}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("\n🚀 PATHWISE AI: GROQ EDITION")
    user_file = input("Resume filename (Sinchana_Resume.pdf): ") or "Sinchana_Resume.pdf"
    roles = input("Enter roles (comma separated): ")
    
    if roles:
        role_list = [r.strip() for r in roles.split(",")]
        for role in role_list:
            run_pathwise_ai(user_file, role)
            # Groq is fast, so we only need a tiny 2-second sleep
            time.sleep(2)