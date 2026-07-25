# Pathwise AI 2.0 🚀

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://pathwise-ai-2.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Groq AI](https://img.shields.io/badge/LLM-Groq%20API-orange.svg)](https://groq.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Pathwise AI 2.0** is an intelligent, AI-powered career guidance, resume calibration, and roadmap generator designed to bridge the gap between job seekers and industry expectations.

🔗 **Live App:** [https://pathwise-ai-2.streamlit.app/](https://pathwise-ai-2.streamlit.app/)

---

## ✨ Key Features

* 📄 **Resume Parsing & Calibration:** Automatically extracts text from uploaded PDF resumes and analyzes skill match against targeted tech roles.
* 🗺️ **Multi-Phase Skill Roadmaps:** Generates step-by-step, actionable career development plans customized to identified skill gaps.
* 🤖 **Embedded AI Mentor:** Interactive AI assistant powered by Groq to answer real-time questions about career paths, technical skills, and project ideas.
* 📊 **ATS Resume Architect:** Evaluates formatting, keyword density, and structural readiness for Applicant Tracking Systems.
* 📩 **Email Reports:** Sends comprehensive analysis and PDF reports directly to user inbox.

---

## 🛠️ Tech Stack

* **Frontend / UI:** Streamlit
* **AI Engine:** Groq API (Llama 3 Models)
* **Data & Storage:** SQLite3
* **PDF Processing & Generation:** PyPDF2, fpdf2
* **Language:** Python

---

## 📁 Repository Structure

```text
PathwiseAI/
│── .streamlit/         # Streamlit configuration
│── docs/               # Project documentation & research papers
│── reports/            # Generated JSON and PDF analysis reports
│── src/                # Core authentication and database modules
│── uploads/            # Sample resume uploads
│── analyzer.py         # AI analysis logic
│── app.py              # Main Streamlit application
│── mailer.py            # Email service configuration
│── parser.py            # PDF resume parsing logic
│── reporter.py          # PDF report generator
│── requirements.txt    # Application dependencies
└── README.md           # Project documentation

🚀 Local Installation & Setup
If you wish to run Pathwise AI 2.0 on your local machine:

1. Clone the Repository
Bash
git clone [https://github.com/Sinchana9632/Pathwise-AI-2.0.git](https://github.com/Sinchana9632/Pathwise-AI-2.0.git)
cd Pathwise-AI-2.0

2. Set Up Virtual Environment
Bash
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1

3. Install Dependencies
Bash
pip install -r requirements.txt

4. Configure Environment Variables
Create a .env file in the root directory:

Code snippet
GROQ_API_KEY=your_groq_api_key_here
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password

5. Launch the Application
Bash
streamlit run app.py

🔒 Security & Best Practices
Never commit .env files or personal API keys to source control.

.gitignore is configured to exclude local databases, uploads, virtual environments, and sensitive configuration parameters.

🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check out the Issues Page.

📜 License
This project is open-source and available under the MIT License.
