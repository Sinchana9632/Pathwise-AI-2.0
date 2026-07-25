# Chapter 2: Existing System Study

## 2.1 Existing Systems Review
Currently, students preparing for corporate placements rely on two main categories of online tools:
1. **Automated Resume Screeners (ATS Graders):** Platforms like Teal HQ, Resume Worded, and Enhancv.
2. **Generic Conversational AI:** Free public LLM windows like standard ChatGPT or Claude interfaces.

## 2.2 Current Solutions Available
* **Teal HQ / Resume Worded:** These platforms allow users to upload a PDF resume, parse the text, and generate a static optimization score based on specific job-description keywords.
* **AI Chatbots:** Students paste their resumes directly into public AI chat prompts to ask for structural feedback and generic interview preparation questions.

## 2.3 Limitations of Existing Systems
* **Strict Keyword Dependence:** Older ATS graders look for exact string matches. If a student has the right technical skill but uses a valid synonym, the platform flags it as a failure.
* **Proprietary Paywalls:** Advanced AI insights, deep portfolio tailoring, and daily tracking metrics are locked behind expensive premium subscriptions.
* **Transactional Memory Loss ("Amnesia"):** Standard AI tools treat every interaction as a one-off event. They do not store user history or profile growth across multiple sessions.

## 2.4 Gaps Identified
* **The Learning Break Dropout:** Existing tools score a resume and then leave the user entirely alone during their learning period. Because there is no daily tracking or follow-up loop inside the app, students easily lose motivation.
* **Isolated Interfaces:** Resume grading, progress tracking, and interview preparation are split across completely disconnected tools and spreadsheets, forcing the user to manually manage their own data.

## 2.5 Need for Proposed System
There is a clear need for an integrated placement preparation platform that combines contextual AI intelligence with long-term memory. Students need a system that doesn't just score their resume once, but actively tracks their growth, keeps them accountable daily, and stays with them throughout their entire preparation timeline.

## 2.6 Proposed Solution (PathWise AI 2.0)
PathWise AI 2.0 bridges these industry gaps through a stateful, database-backed web application architecture:
* **Relational Memory Layer:** Utilizes an SQLite database (`pathwise.db`) to securely store user accounts, historical evaluation scores, and specific skill deficiencies.
* **Active Daily Retention Loop:** Instead of a silent study break, the platform keeps students engaged by offering a 15-minute daily technical interview sprint based on their stored skill gaps.
* **Automated Email Engagement:** Features an automated background email utility to deliver daily micro-challenges and progress updates directly to the student's inbox, ensuring consistent study habits while respecting data privacy standards.
* **Unified Dashboard:** Merges advanced contextual parsing (Llama 3.1) and a continuous AI Mentor Chatbot into one single dashboard workspace.