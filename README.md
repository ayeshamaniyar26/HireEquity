# HireEquity — AI Powered Job Description Generator and Bias Auditor


HireEquity is a professional, AI-powered tool designed to audit, optimize, and generate inclusive job descriptions (JDs). It helps organizations expand their talent pool by eliminating subtle language biases—including gender bias, ageism, ableism, elitism, and overly restrictive qualifications.

---

## 1. About the Project

HireEquity provides HR professionals, recruiters, and hiring managers with a modern workspace to screen job drafts or generate new ones from scratch using inclusive writing principles. By combining a fast, rule-based static wordlist scanner with advanced semantic analysis (powered by Groq and Llama 3.1), the application audits drafts in real-time, calculates an Inclusivity Score, and provides a single-click rewrite to replace exclusionary terms with highly engaging, neutral alternatives.

## 2. Problem Statement

Many traditional job descriptions contain subtle, coded language that inadvertently discourages qualified candidates from applying. 
- **Gendered Language:** Research (Gaucher et al., 2011) shows that masculine-coded words (like *rockstar, dominant, competitive*) lower appeal for female applicants.
- **Ageism & Ableism:** Phrasing such as *digital native* or *physically fit/stand for long hours* screens out older candidates and individuals with disabilities.
- **Elitism & Restrictiveness:** Demanding *ivy league graduates* or *10 years of experience* for mid-level tasks artificially narrows the applicant pool.

Manually reviewing and rephrasing these documents is time-consuming and requires specialized DEI expertise.

## 3. What It Does

HireEquity automates the audit and correction process in a 4-step workflow:
1. **Provide JD (Page 1):** Paste an existing draft or generate a completely new one using the AI JD Generator.
2. **Bias Audit (Page 2):** Run a dual-engine scan (Gaucher static list + Llama 3.1 semantic analysis). The app highlights biased phrases by severity (Critical, Moderate, Minor) and lists dynamic suggestions.
3. **Auto Fix & Compare (Page 3):** Optimize the JD with a single click. View a side-by-side comparison of the original text (with strikethroughs) against the clean optimized version. Copy the text or download a multi-page PDF Audit Report.
4. **Insights Dashboard (Page 4):** Review visual analytics, score comparisons (before vs after), and predicted demographic appeal changes based on masculine vs feminine word density ratios.

## 4. Tech Stack

- **Frontend/UI:** Streamlit (Python-based framework)
- **Styling:** Custom CSS (Plus Jakarta Sans font, dark slate gradient themes, and glassmorphic layouts)
- **AI Core:** Groq API (using the `llama-3.1-8b-instant` model)
- **Data Visualization:** Plotly Express & Plotly Graph Objects (Interactive Pie & Bar charts)
- **Document Export:** ReportLab (for structured PDF report generation)
- **Environment Management:** Python-Dotenv

## 5. Dataset Used

The application relies on a comprehensive, custom-compiled dictionary (`BIAS_DICTIONARY` in `wordlists.py`) derived from:
- **Gaucher et al. (2011)** list of gendered (masculine/feminine) coded words.
- Age-related bias words (*recent graduate*, *digital native*, *youthful*).
- Educational and professional elitism filters (*ivy league*, *only IIT*, *tier-1*).
- Ableist phrases (*able-bodied*, *no disability*, *stand for long hours*).
- Restrictive experience requirements (*10+ years experience*).

## 6. How to Run Locally

### Prerequisites
- Python 3.8 or higher installed on your machine.
- A Groq API Key (get one from [console.groq.com](https://console.groq.com)).

### Step 1: Clone and Navigate
Clone this repository and open the project directory:
```bash
git clone https://github.com/ayeshamaniyar26/HireEquity.git
cd HireEquity
```

### Step 2: Set Up Virtual Environment (Optional but Recommended)
```bash
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Create a `.env` file in the root directory (based on `.env.example`):
```env
GROQ_API_KEY=your_actual_groq_api_key_here
```

### Step 5: Launch the Application
Run the Streamlit application:
```bash
streamlit run app.py
```
Open your browser and navigate to `http://localhost:8501`.

## 7. Project Structure

```text
HireEquity/
│
├── app.py                # Main Streamlit application entrypoint & pages
├── bias_detector.py      # Dual-engine static and semantic scanner
├── jd_generator.py       # AI Prompt configuration for generating inclusive JDs
├── rewriter.py           # Optimization engine for rephrasing biased text
├── pdf_export.py         # Multi-page ReportLab PDF layout generator
├── wordlists.py          # Unified DEI bias dictionary & Gaucher lists
│
├── requirements.txt      # Python dependencies
├── .env.example          # Sample environment template
├── .gitignore            # Excluded files list
└── README.md             # Documentation
```

## 8. Features

- **Inclusive AI Generation:** Creates fresh, compliant JDs for any role, seniority, and industry.
- **Interactive Visual Highlights:** Color-coded inline text reviews mapping to severity.
- **Executive Scorecard Table:** Tabular breakdown of flagged phrases, categories, and suggested replacements.
- **Score Delta Metrics:** Live comparisons showing original score vs optimized score.
- **Demographic Appeal Predictor:** Dynamic male/female appeal index forecasts before and after fixes.
- **Automated PDF Compiler:** Prints a formal 3-page scorecard and remediation guide.

## 9. Screenshots Placeholder

*Include application screenshot links here to display them on your GitHub repository page:*

| Page 1: JD Input | Page 2: Bias Audit |
|---|---|
| ![Page 1 Placeholder](https://via.placeholder.com/600x400.png?text=Step+1:+Provide+Job+Description) | ![Page 2 Placeholder](https://via.placeholder.com/600x400.png?text=Step+2:+Bias+Audit+Scanner) |

| Page 3: Auto Fix and Compare| Page 4: Insights |
|---|---|
| ![Page 3 Placeholder](https://via.placeholder.com/600x400.png?text=Step+3:+AI+Auto-Rewrite) | ![Page 4 Placeholder](https://via.placeholder.com/600x400.png?text=Step+4:+Insights+Dashboard) |

## 10. License

This project is licensed under the MIT License - see the LICENSE file for details.
