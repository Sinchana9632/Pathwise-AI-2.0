from fpdf import FPDF
import json
import os

def create_visual_report(json_path):
    # 1. Load your saved JSON record
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # --- VALIDATION GUARD ---
    if "Error" in data['analysis'] or "overloaded" in data['analysis']:
        print(f"❌ Skipping PDF generation: {json_path} contains invalid AI data.")
        return

    # Clean the text for PDF compatibility (removes non-ASCII characters)
    clean_analysis = data['analysis'].encode('ascii', 'ignore').decode('ascii')

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15) # Safety margin
    
    # 2. Design Header
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(33, 150, 243) # PathWise Blue
    pdf.cell(0, 15, "PATHWISE AI: STRATEGIC CAREER REPORT", ln=True, align='C')
    pdf.ln(10)
    
    # 3. Add Details
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Target Role: {data['target_role'].upper()}", ln=True)
    pdf.cell(0, 10, f"Analysis Date: {data['date']}", ln=True)
    pdf.ln(5)
    
    # 4. Content Logic
    pdf.set_font("Arial", size=11)
    
    for line in clean_analysis.split('\n'):
        line = line.strip()
        if not line: 
            pdf.ln(2) # Add small space for empty lines
            continue

        if "http" in line and " - " in line:
            # Splits "Python - http://..." into parts
            parts = line.split(" - ", 1)
            skill_name = parts[0]
            url = parts[1].strip()
            
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", 'B', 11)
            pdf.write(8, f"{skill_name}: ") # Write the skill name
            
            # Formatting the Link (Blue & Underlined)
            pdf.set_text_color(0, 0, 255) 
            pdf.set_font("Arial", 'U', 10) # Slightly smaller font for long URLs
            
            # Use write with a link, but check if it's too long
            # If the URL is massive, we use multi_cell instead of write
            if len(url) > 80:
                pdf.ln(8)
                pdf.multi_cell(0, 8, url, link=url)
            else:
                pdf.write(8, url, link=url)
                pdf.ln(10)
                
        elif "http" in line:
            pdf.set_text_color(0, 0, 255)
            pdf.set_font("Arial", 'U', 10)
            pdf.multi_cell(0, 8, line, link=line.strip())
            pdf.ln(2)
        else:
            # Regular text like Match Score or Project Idea
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", '', 11)
            # Using multi_cell here is the "Safety Net" that prevents your crash
            pdf.multi_cell(0, 8, line)
            pdf.ln(2)

    # 5. Engineering Action Plan
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(230, 230, 230) 
    pdf.cell(0, 10, "ENGINEERING ACTION PLAN", ln=True, fill=True)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 8, "Review the Match Score above. If below 80, prioritize the 'Missing Skills' section and complete the suggested project to strengthen your resume.")
    
    # 6. Save the PDF
    pdf_output = json_path.replace(".json", ".pdf")
    pdf.output(pdf_output)
    print(f"✅ Professional PDF generated: {pdf_output}")