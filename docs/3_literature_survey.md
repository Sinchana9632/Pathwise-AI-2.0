# Chapter 3: Literature Survey

## 3.1 Research Papers Reviewed

### Paper 1: Evaluation of LLMs in Recruitment Pipeline Alignment
* **Authors:** Ramesh Chandra Tripathi, Chandramma (2024/2026 update)
* **Title:** *Optimizing Resume Parsing Processes by Leveraging Large Language Models*
* **Source:** IEEE Xplore / ResearchGate Academic Publication
* **Core Focus:** This paper evaluates the performance shift when moving from conventional rule-based Natural Language Processing (NLP) string-matching scanners over to Generative Large Language Models (LLMs) for unstructured resume profile extraction.

### Paper 2: Systematic Framework Gaps in Conversational Tutoring
* **Authors:** Amrita Ganguly, Nafisa Mehjabin, Aqdas Malik, Aditya Johri (December 2025)
* **Title:** *Conversational AI agents in education: an umbrella review of current utilization, challenges, and future directions for ethical and responsible use*
* **Source:** AI and Ethics / Springer Nature / Semantic Scholar
* **Core Focus:** A massive umbrella review compiling findings from 34 major review articles to analyze data privacy, usability frameworks, and student engagement models when deploying conversational AI interfaces for personalized skill development and training.

## 3.2 Existing Products Reviewed
To map out current technical implementations available to end-users, we analyzed the following systems:
* **Teal HQ & Resume Worded:** Commercial platforms utilizing rigid keyword extraction modules and structural style rules to calculate static compliance grades.
* **Enhancv / VisualCV:** Layout editors focusing heavily on stylistic enhancements and isolated generative text rewrites.
* **Public Chat Interfaces (ChatGPT / Claude Web UIs):** General-purpose LLMs that provide unstructured resume advice but function on an ephemeral, transactional basis.

## 3.3 Comparative Analysis
The table below contrasts our proposed engineering design with standard choices found in the market and existing research literature:

| Architectural Feature | Traditional ATS Graders | Public Web Chat Interfaces | PathWise AI 2.0 (Proposed) |
| :--- | :--- | :--- | :--- |
| **Parsing Engine** | Strict Regular Expressions | Contextual Semantic Reading | **Contextual Semantic Reading** |
| **State Retention** | Flat Structural User Profiles| Completely Stateless (Amnesia)| **Relational Database (`SQLite`)**|
| **Learning Interactivity**| Static Diagnostic Checklist | Freeform Q&A Session | **Stateful AI Mentor Workspace** |
| **User Engagement** | Passive (User must log in) | Passive (User must initiate) | **Proactive Automated Python Emails**|
| **Financial/Privacy Model**| Expensive Monthly Paywalls | Cloud Token Tier Caps | **Bring-Your-Own-Key (BYOK) Utility**|

## 3.4 Key Findings
* **The Error Rate of String Matching:** Literature proves that traditional regular expression systems achieve poor accuracy on unstructured profiles because they depend entirely on fixed positional coordinates or literal string matches, dropping match rates significantly on multi-column layouts.
* **The Semantic Advantage:** Utilizing deep reasoning language paths to track candidate data helps evaluate true intent, which has been shown to double profile adjustment visibility, boosting contextual semantic alignment by an average of **85%**.
* **The Framework Deficit:** The 2025 umbrella review explicitly emphasizes a critical gap in educational AI frameworks: a distinct **"lack of end-to-end design guidance and weak specific usability tracking methods."** Simply put, if a conversational system lacks an underlying memory state tracker, student guidance becomes fragmented, leading to high user abandonment.

## 3.5 Research Gaps
While the computer science community has thoroughly explored individual modules—such as utilizing an LLM to parse text or using a chatbot for standalone mock interviews—there is a major architectural gap in open-source systems. 

Existing solutions fail to provide a **cohesive, unified pipeline** where a persistent relational database acts as the direct connective tissue between a contextual resume parser and an interactive conversation coach. PathWise AI 2.0 is specifically designed to fill this gap.