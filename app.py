import os
import re
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from dotenv import load_dotenv

# Import our custom backend modules
import wordlists
from bias_detector import (
    scan_wordlist_bias,
    check_semantic_bias,
    calculate_score,
    combine_and_align_flags,
    generate_highlighted_html
)
from jd_generator import generate_job_description
from rewriter import rewrite_job_description
from pdf_export import generate_pdf_report

# Load environment variables
load_dotenv()

# =============================================================================
# STREAMLIT PAGE SETUP
# =============================================================================
st.set_page_config(
    page_title="HireEquity — AI Job Auditor",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if "role" not in st.session_state:
    st.session_state.role = ""
if "level" not in st.session_state:
    st.session_state.level = "Mid"
if "domain" not in st.session_state:
    st.session_state.domain = "Tech"
if "original_jd" not in st.session_state:
    st.session_state.original_jd = ""
if "flagged_items" not in st.session_state:
    st.session_state.flagged_items = []
if "original_score" not in st.session_state:
    st.session_state.original_score = 100
if "fixed_jd" not in st.session_state:
    st.session_state.fixed_jd = ""
if "fixed_score" not in st.session_state:
    st.session_state.fixed_score = 100
if "fixed_flagged_items" not in st.session_state:
    st.session_state.fixed_flagged_items = []
if "audit_run" not in st.session_state:
    st.session_state.audit_run = False
if "rewrite_run" not in st.session_state:
    st.session_state.rewrite_run = False

# =============================================================================
# CUSTOM CSS STYLING
# =============================================================================
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }

    /* Dark radial gradient and premium color palette adjustments */
    .stApp {
        background: radial-gradient(circle at top right, #1E1B4B 0%, #0F172A 100%) !important;
        color: #F8FAFC !important;
    }
    
    /* Sidebar styling override */
    [data-testid="stSidebar"] {
        background: #0B0F19 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Custom premium card container with glassmorphism */
    .premium-card {
        background: rgba(30, 41, 59, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 24px !important;
        margin-bottom: 24px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    .premium-card:hover {
        transform: translateY(-2px);
        border-color: rgba(255, 122, 0, 0.3) !important;
        box-shadow: 0 12px 40px 0 rgba(255, 122, 0, 0.08) !important;
    }
    
    .premium-card-title {
        font-size: 1.3rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #FF7A00 0%, #FFB800 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        margin-bottom: 16px !important;
        padding-bottom: 8px !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    /* Highlight markup styles */
    .bias-highlight {
        border-radius: 6px !important;
        padding: 3px 8px !important;
        font-weight: 600 !important;
        display: inline-block !important;
        margin: 2px 0px !important;
        font-size: 0.9em !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    
    .critical-highlight {
        background-color: rgba(239, 68, 68, 0.15) !important;
        color: #F87171 !important;
        border: 1px solid rgba(239, 68, 68, 0.4) !important;
        border-left: 4px solid #EF4444 !important;
    }
    
    .moderate-highlight {
        background-color: rgba(245, 158, 11, 0.15) !important;
        color: #FBBF24 !important;
        border: 1px solid rgba(245, 158, 11, 0.4) !important;
        border-left: 4px solid #F59E0B !important;
    }
    
    .minor-highlight {
        background-color: rgba(59, 130, 246, 0.15) !important;
        color: #60A5FA !important;
        border: 1px solid rgba(59, 130, 246, 0.4) !important;
        border-left: 4px solid #3B82F6 !important;
    }
    
    .clean-highlight {
        background-color: rgba(16, 185, 129, 0.15) !important;
        color: #34D399 !important;
        border: 1px solid rgba(16, 185, 129, 0.4) !important;
        border-left: 4px solid #10B981 !important;
    }
    
    /* JD preview containers - Clean Document Style */
    .jd-preview-text {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 18px !important;
        line-height: 1.8 !important;
        color: #E2E8F0 !important;
        white-space: pre-wrap !important;
        background: transparent !important;
        padding: 0px !important;
        border: none !important;
        border-radius: 0px !important;
        box-shadow: none !important;
        margin-bottom: 20px !important;
    }

    .jd-preview-html {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 18px !important;
        line-height: 1.8 !important;
        color: #E2E8F0 !important;
        background: transparent !important;
        padding: 0px !important;
        border: none !important;
        border-radius: 0px !important;
        box-shadow: none !important;
        margin-bottom: 20px !important;
    }
    
    /* Clean text display */
    p, li {
        color: #CBD5E1;
    }

    /* Streamlit forms and input field styling */
    .stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] {
        background-color: rgba(15, 23, 42, 0.6) !important;
        color: #F8FAFC !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox [data-baseweb="select"]:focus-within {
        border-color: #FF7A00 !important;
        box-shadow: 0 0 0 2px rgba(255, 122, 0, 0.2) !important;
    }
    
    /* Overhaul Streamlit default buttons to make them premium */
    .stButton button {
        background: linear-gradient(135deg, #FF7A00 0%, #FF5E00 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: 700 !important;
        letter-spacing: 0.03em !important;
        box-shadow: 0 4px 14px 0 rgba(255, 122, 0, 0.3) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px 0 rgba(255, 122, 0, 0.45) !important;
        background: linear-gradient(135deg, #FF8C1A 0%, #FF6F1A 100%) !important;
        border: none !important;
        color: white !important;
    }
    
    .stButton button:active {
        transform: translateY(1px) !important;
    }

    /* Custom HTML Metric Styling */
    .metric-container {
        display: flex;
        justify-content: space-between;
        gap: 16px;
        margin-bottom: 24px;
    }
    .metric-card {
        flex: 1;
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(8px);
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: rgba(255, 122, 0, 0.25);
        box-shadow: 0 12px 40px 0 rgba(255, 122, 0, 0.1);
    }
    .metric-val {
        font-size: 2.2rem;
        font-weight: 800;
        color: #F8FAFC;
        margin: 8px 0;
    }
    .metric-lbl {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #94A3B8;
    }
    .metric-change {
        font-size: 0.85rem;
        font-weight: 600;
    }
    .metric-change.positive {
        color: #10B981;
    }
    .metric-change.negative {
        color: #EF4444;
    }
    .metric-change.neutral {
        color: #94A3B8;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# =============================================================================
# SIDEBAR NAVIGATION
# =============================================================================
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #FF7A00; margin-bottom: 0px;'>HireEquity ⚖️</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 0.85rem; color: #94A3B8;'>AI Bias Auditor & Optimizer</p>", unsafe_allow_html=True)
    st.markdown("<hr style='margin-top: 10px; margin-bottom: 20px;'/>", unsafe_allow_html=True)
    
    page = st.radio(
        "Navigate Application",
        [
            "📝 Page 1: Generate/Paste JD",
            "🔍 Page 2: Bias Audit",
            "⚡ Page 3: Auto Fix & Compare",
            "📊 Page 4: Insights Dashboard"
        ]
    )

# Helper function to check if API key is ready
def check_api_key_configured():
    key = os.environ.get("GROQ_API_KEY", "")
    return len(key.strip()) > 0

# Helper function to clean markdown stars, underscores, hashes, etc.
def clean_display_text(text):
    if not text:
        return ""
    # Remove all asterisks (both bold and italic markdown)
    cleaned = text.replace("**", "").replace("*", "")
    # Remove markdown underscores
    cleaned = cleaned.replace("__", "").replace("_", "")
    
    # Remove markdown header hashes and bullet list dashes at the start of lines
    cleaned_lines = []
    for line in cleaned.split("\n"):
        line_str = line.strip()
        # Remove leading hashes
        while line_str.startswith("#"):
            line_str = line_str.lstrip("#").strip()
        # Format bullet dashes/dots if they look like raw markdown bullets
        if line_str.startswith("- "):
            line_str = "• " + line_str[2:].strip()
        elif line_str.startswith("* "):
            line_str = "• " + line_str[2:].strip()
        cleaned_lines.append(line_str)
        
    return "\n".join(cleaned_lines)

# Helper to escape HTML characters in JD rendering
def jd_text_escape(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

# =============================================================================
# PAGE 1: GENERATE OR PASTE JD
# =============================================================================
if page == "📝 Page 1: Generate/Paste JD":
    st.title("📝 Step 1: Provide Job Description")
    st.write("Generate a completely new job description using inclusive rules, or paste an existing JD to scan for potential bias.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown('<div class="premium-card-title">Option A: AI JD Generator</div>', unsafe_allow_html=True)
        
        role_input = st.text_input("Job Title / Role Name:", value=st.session_state.role, placeholder="e.g. Senior Backend Engineer")
        level_input = st.selectbox("Seniority Level:", ["Junior", "Mid", "Senior"], index=["Junior", "Mid", "Senior"].index(st.session_state.level))
        domain_input = st.selectbox("Industry Domain:", ["Tech", "Finance", "Healthcare", "Marketing", "Other"], index=["Tech", "Finance", "Healthcare", "Marketing", "Other"].index(st.session_state.domain))
        
        generate_btn = st.button("✨ Generate Inclusive JD", use_container_width=True)
        
        if generate_btn:
            if not check_api_key_configured():
                st.error("Please configure your Groq API Key in the '.env' file first.")
            elif not role_input:
                st.warning("Please provide a Job Title.")
            else:
                with st.spinner("AI generating job description..."):
                    try:
                        jd_text = generate_job_description(role_input, level_input, domain_input)
                        # Clean asterisks and markdown symbols
                        jd_text = clean_display_text(jd_text)
                        
                        # Store in state
                        st.session_state.role = role_input
                        st.session_state.level = level_input
                        st.session_state.domain = domain_input
                        st.session_state.original_jd = jd_text
                        
                        # Reset downstream page states
                        st.session_state.audit_run = False
                        st.session_state.rewrite_run = False
                        st.session_state.flagged_items = []
                        st.session_state.original_score = 100
                        st.session_state.fixed_jd = ""
                        st.session_state.fixed_score = 100
                        st.session_state.fixed_flagged_items = []
                        
                        st.toast("Job description generated successfully!", icon="✅")
                    except Exception as e:
                        st.error(f"Failed to generate JD: {e}")
                        st.toast("Generation failed", icon="❌")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown('<div class="premium-card-title">Option B: Paste Existing JD</div>', unsafe_allow_html=True)
        
        paste_text = st.text_area("Paste Job Description Text Here:", value=st.session_state.original_jd, height=220, placeholder="Paste your draft JD here to audit for bias...")
        
        # Word count calculation
        word_count = len(paste_text.split()) if paste_text else 0
        st.caption(f"Word Count: {word_count}")
        
        proceed_btn = st.button("💾 Keep & Proceed", use_container_width=True)
        
        if proceed_btn:
            if not paste_text.strip():
                st.warning("Job Description is empty.")
            else:
                # Clean asterisks and markdown symbols
                st.session_state.original_jd = clean_display_text(paste_text)
                
                # Check if it was generated or manually pasted to clean metadata
                if role_input:
                    st.session_state.role = role_input
                else:
                    st.session_state.role = "Custom Pasted Role"
                st.session_state.level = level_input
                st.session_state.domain = domain_input
                
                # Reset downstream
                st.session_state.audit_run = False
                st.session_state.rewrite_run = False
                st.session_state.flagged_items = []
                st.session_state.original_score = 100
                st.session_state.fixed_jd = ""
                st.session_state.fixed_score = 100
                st.session_state.fixed_flagged_items = []
                
                st.toast("Saved draft job description!", icon="💾")
        st.markdown('</div>', unsafe_allow_html=True)

    # Current JD Preview
    if st.session_state.original_jd:
        st.subheader("Current Active Job Description Draft")
        st.markdown(f'<div class="jd-preview-text">{clean_display_text(st.session_state.original_jd)}</div>', unsafe_allow_html=True)

# =============================================================================
# PAGE 2: BIAS AUDIT
# =============================================================================
elif page == "🔍 Page 2: Bias Audit":
    st.title("🔍 Step 2: Bias Audit Scanner")
    st.write("Scan the job description against our hardcoded Gaucher et al. list and evaluate subtle context bias with Groq AI.")
    
    if not st.session_state.original_jd:
        st.warning("No Job Description found. Please go to **Page 1** to generate or paste one first.")
    else:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown('<div class="premium-card-title">Run Dual-Engine Scan</div>', unsafe_allow_html=True)
        st.write("This executes an exact/partial match with the Gaucher wordlists AND calls Groq Llama3 to find semantic bias.")
        
        run_audit_btn = st.button("🚀 Run Dual-Engine Bias Audit", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if run_audit_btn:
            with st.spinner("Analyzing text and running semantic audit..."):
                try:
                    # 1. Wordlist scan
                    wordlist_flags = scan_wordlist_bias(st.session_state.original_jd)
                    
                    # 2. Semantic scan (Requires API Key)
                    semantic_flags = []
                    if check_api_key_configured():
                        semantic_flags = check_semantic_bias(st.session_state.original_jd)
                    else:
                        st.info("Groq API Key is not configured in '.env'. Running Wordlist audit only.")
                        
                    # 3. Combine and align positions
                    all_flags = combine_and_align_flags(st.session_state.original_jd, wordlist_flags, semantic_flags)
                    
                    # 4. Calculate Score
                    score = calculate_score(all_flags)
                    
                    # Save states
                    st.session_state.flagged_items = all_flags
                    st.session_state.original_score = score
                    st.session_state.audit_run = True
                    
                    st.toast("Audit complete!", icon="🔍")
                except Exception as e:
                    st.error(f"Audit failed: {e}")
                    st.toast("Audit failed", icon="❌")
                    
        if st.session_state.audit_run:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Overall Gauge Chart
                score_val = st.session_state.original_score
                
                # Dynamic Gauge color based on rating
                bar_color = "#EF4444"
                if score_val >= 80:
                    bar_color = "#10B981"
                elif score_val >= 50:
                    bar_color = "#F59E0B"
                    
                gauge_fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=score_val,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Original Inclusivity Score", 'font': {'size': 20, 'color': '#F1F5F9'}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#94A3B8"},
                        'bar': {'color': bar_color},
                        'bgcolor': "rgba(0,0,0,0)",
                        'borderwidth': 1,
                        'bordercolor': "#475569",
                        'steps': [
                            {'range': [0, 50], 'color': 'rgba(239, 68, 68, 0.15)'},
                            {'range': [50, 80], 'color': 'rgba(245, 158, 11, 0.15)'},
                            {'range': [80, 100], 'color': 'rgba(16, 185, 129, 0.15)'}
                        ],
                    }
                ))
                gauge_fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font={'color': "#F1F5F9", 'family': "sans-serif"},
                    height=280,
                    margin=dict(l=20, r=20, t=50, b=20)
                )
                st.plotly_chart(gauge_fig, use_container_width=True)
                
            with col2:
                # Per Category Bar Chart
                from collections import Counter
                category_counts = Counter([f['category'] for f in st.session_state.flagged_items])
                if category_counts:
                    cat_data = [{'Category': cat, 'Flags Found': count} for cat, count in category_counts.items()]
                    bar_fig = px.bar(
                        cat_data,
                        x='Category',
                        y='Flags Found',
                        title='Bias Flag Counts by Category',
                        color='Category',
                        color_discrete_sequence=px.colors.qualitative.Bold
                    )
                    bar_fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font={'color': "#F1F5F9"},
                        height=280,
                        margin=dict(l=20, r=20, t=50, b=20),
                        showlegend=False
                    )
                    st.plotly_chart(bar_fig, use_container_width=True)
                else:
                    st.success("No bias flags detected! Perfect score!")
            
            # HTML Highlight view
            st.subheader("Highlighted Job Description Analysis")
            st.caption("🔴 Red = Critical  |  🟡 Yellow = Moderate  |  🔵 Blue = Minor / Coded Word")
            
            highlighted_html = generate_highlighted_html(
                st.session_state.original_jd, 
                st.session_state.flagged_items
            )
            
            st.markdown(
                f'<div class="jd-preview-html">{highlighted_html}</div>', 
                unsafe_allow_html=True
            )
            
            # Flagged details table
            st.subheader("Detailed Flagged Phrases Table")
            if st.session_state.flagged_items:
                table_data = []
                for item in st.session_state.flagged_items:
                    table_data.append({
                        "Phrase": item["phrase"],
                        "Category": item["category"],
                        "Severity": item["severity"].upper(),
                        "Suggestion": item["suggestion"]
                    })
                st.dataframe(table_data, use_container_width=True)
            else:
                st.info("Clean text! No flags to display.")

# =============================================================================
# PAGE 3: AUTO FIX & COMPARE
# =============================================================================
elif page == "⚡ Page 3: Auto Fix & Compare":
    st.title("⚡ Step 3: AI Auto-Rewrite & Comparison")
    st.write("Let the AI re-write the job description to eliminate all detected biases, then compare the outcomes.")
    
    if not st.session_state.original_jd:
        st.warning("No Job Description found. Please go to **Page 1** first.")
    elif not st.session_state.audit_run:
        st.warning("Please run the Bias Audit on **Page 2** first before requesting an auto-fix.")
    else:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown('<div class="premium-card-title">Trigger Inclusivity Re-writer</div>', unsafe_allow_html=True)
        st.write("Groq will replace restrictive experience rules and bias-coded words with professional, inclusive alternatives.")
        
        rewrite_btn = st.button("🪄 Auto-Rewrite Job Description", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if rewrite_btn:
            if not check_api_key_configured():
                st.error("Groq API key is required to perform rewriting. Please configure it in your '.env' file.")
            else:
                with st.spinner("AI rewriting job description to remove biases..."):
                    try:
                        fixed_text = rewrite_job_description(
                            st.session_state.original_jd, 
                            st.session_state.flagged_items
                        )
                        # Clean asterisks and markdown symbols
                        fixed_text = clean_display_text(fixed_text)
                        
                        # Instantly audit the rewritten version
                        fixed_flags = scan_wordlist_bias(fixed_text)
                        # We assume semantic checks on clean text are low-severity or clean, 
                        # but we can scan it just to get a valid fixed score
                        fixed_score = calculate_score(fixed_flags)
                        
                        st.session_state.fixed_jd = fixed_text
                        st.session_state.fixed_score = fixed_score
                        st.session_state.fixed_flagged_items = fixed_flags
                        st.session_state.rewrite_run = True
                        
                        st.toast("Job description successfully optimized!", icon="🪄")
                    except Exception as e:
                        st.error(f"Failed to rewrite JD: {e}")
                        st.toast("Rewrite failed", icon="❌")
                        
        if st.session_state.rewrite_run:
            # Score Improvement Indicators using premium custom metric cards
            score_diff = st.session_state.fixed_score - st.session_state.original_score
            flag_diff = len(st.session_state.flagged_items) - len(st.session_state.fixed_flagged_items)
            
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-card">
                    <div class="metric-lbl">Original Inclusivity Score</div>
                    <div class="metric-val">{st.session_state.original_score}/100</div>
                    <div class="metric-change neutral">— Baseline</div>
                </div>
                <div class="metric-card">
                    <div class="metric-lbl">Optimized Inclusivity Score</div>
                    <div class="metric-val" style="color: #10B981;">{st.session_state.fixed_score}/100</div>
                    <div class="metric-change positive">+{score_diff} Points</div>
                </div>
                <div class="metric-card">
                    <div class="metric-lbl">Remaining Flags</div>
                    <div class="metric-val" style="color: { '#10B981' if len(st.session_state.fixed_flagged_items) == 0 else '#FBBF24' };">{len(st.session_state.fixed_flagged_items)}</div>
                    <div class="metric-change positive">-{flag_diff} Flags</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<hr/>", unsafe_allow_html=True)
            
            # Side-by-side Columns
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("Original Job Description (Strikethroughs)")
                
                # Strikethrough generator: Wrap original flags with HTML strikethrough tags
                strikethrough_flags = []
                for item in st.session_state.flagged_items:
                    flag_copy = dict(item)
                    strikethrough_flags.append(flag_copy)
                
                # Generate HTML but wrap flags in <s> tags to show strikethroughs
                positioned_flags = [f for f in strikethrough_flags if f["start"] >= 0]
                positioned_flags.sort(key=lambda x: x["start"])
                
                html_parts = []
                last_idx = 0
                for flag in positioned_flags:
                    start = flag["start"]
                    end = flag["end"]
                    if start < last_idx:
                        continue
                    html_parts.append(jd_text_escape(st.session_state.original_jd[last_idx:start]))
                    
                    badge_color = "critical-highlight"
                    if flag["severity"].lower() == "moderate":
                        badge_color = "moderate-highlight"
                    elif flag["severity"].lower() == "minor":
                        badge_color = "minor-highlight"
                        
                    html_parts.append(
                        f'<s><span class="bias-highlight {badge_color}">{jd_text_escape(st.session_state.original_jd[start:end])}</span></s>'
                    )
                    last_idx = end
                    
                html_parts.append(jd_text_escape(st.session_state.original_jd[last_idx:]))
                strikethrough_html = "".join(html_parts).replace("\n", "<br>")
                
                st.markdown(f'<div class="jd-preview-html">{strikethrough_html}</div>', unsafe_allow_html=True)
                
            with col2:
                st.subheader("Optimized Job Description (Clean)")
                st.markdown(f'<div class="jd-preview-text">{clean_display_text(st.session_state.fixed_jd)}</div>', unsafe_allow_html=True)
                
            # Quick Actions Section
            st.markdown("<br/>", unsafe_allow_html=True)
            a_col1, a_col2 = st.columns([1, 1])
            
            with a_col1:
                st.subheader("Copy to Clipboard")
                st.write("Copy the optimized, unbiased job description text below:")
                st.code(st.session_state.fixed_jd, language="markdown")
                
            with a_col2:
                st.subheader("Download PDF Report")
                st.write("Generate and download a formal, multi-page PDF Audit Report for your records.")
                
                # Compile metadata dict
                meta_dict = {
                    "role": st.session_state.role if st.session_state.role else "Job Title Not Set",
                    "level": st.session_state.level,
                    "domain": st.session_state.domain
                }
                
                # Generate PDF bytes
                try:
                    pdf_data = generate_pdf_report(
                        metadata=meta_dict,
                        original_score=st.session_state.original_score,
                        fixed_score=st.session_state.fixed_score,
                        flagged_items=st.session_state.flagged_items,
                        original_jd=st.session_state.original_jd,
                        fixed_jd=st.session_state.fixed_jd
                    )
                    
                    st.download_button(
                        label="📥 Download PDF Audit Report",
                        data=pdf_data,
                        file_name=f"HireEquity_Report_{st.session_state.role.replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Error compiling PDF: {e}")

# =============================================================================
# PAGE 4: INSIGHTS DASHBOARD
# =============================================================================
elif page == "📊 Page 4: Insights Dashboard":
    st.title("📊 Step 4: Insights & Analytics Dashboard")
    st.write("Assess how the language improvements affect predicted demographic appeals and category break-downs.")
    
    if not st.session_state.original_jd:
        st.warning("No Job Description found. Please go to **Page 1** first.")
    elif not st.session_state.audit_run:
        st.warning("Please run the Bias Audit on **Page 2** first.")
    elif not st.session_state.rewrite_run:
        st.warning("Please optimize the JD on **Page 3** to render before vs after insights.")
    else:
        # 1. Summary card
        improve_pct = st.session_state.fixed_score - st.session_state.original_score
        st.markdown(
            f"""
            <div class="premium-card" style="border-left: 5px solid #10B981;">
                <h3 style="margin-top: 0px; color: #10B981;">Inclusivity Improved by {improve_pct}%!</h3>
                <p>Your optimized job description has neutral, appealing language that welcomes a broader range of skilled applicants.</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Plotly Pie Chart of Bias category breakdown
            from collections import Counter
            category_counts = Counter([f['category'] for f in st.session_state.flagged_items])
            if category_counts:
                cat_data = [{'Category': cat, 'Flags Found': count} for cat, count in category_counts.items()]
                pie_fig = px.pie(
                    cat_data, 
                    values='Flags Found', 
                    names='Category', 
                    title='Original Bias Category Breakdown',
                    color_discrete_sequence=px.colors.qualitative.Safe
                )
                pie_fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font={'color': "#F1F5F9"},
                    height=300
                )
                st.plotly_chart(pie_fig, use_container_width=True)
            else:
                st.info("No flags existed to build a pie chart breakdown!")
                
        with col2:
            # Score comparison bar chart
            comparison_fig = go.Figure(data=[
                go.Bar(
                    name='Original JD', 
                    x=['Inclusivity Score'], 
                    y=[st.session_state.original_score], 
                    marker_color='#EF4444',
                    text=[f"{st.session_state.original_score}/100"],
                    textposition='auto'
                ),
                go.Bar(
                    name='Optimized JD', 
                    x=['Inclusivity Score'], 
                    y=[st.session_state.fixed_score], 
                    marker_color='#10B981',
                    text=[f"{st.session_state.fixed_score}/100"],
                    textposition='auto'
                )
            ])
            comparison_fig.update_layout(
                barmode='group', 
                title='Inclusivity Score Comparison (Before vs After)',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'color': '#F1F5F9'},
                height=300,
                yaxis=dict(range=[0, 110])
            )
            st.plotly_chart(comparison_fig, use_container_width=True)
            
        # Candidate Persona Predictor Section
        st.subheader("👥 Candidate Persona Predictor")
        st.write("Predicts the demographic appeal changes based on the density ratio of masculine vs feminine Gaucher coded words.")
        
        # Calculate counts
        # Original JD counts
        orig_text_lower = st.session_state.original_jd.lower()
        
        # Count words helper using regex word boundaries to avoid false positives (e.g. 'he' in 'the')
        def count_gendered_words(text, wordlist_arr):
            count = 0
            short_words_exact = {"he", "his", "him"}
            for word in wordlist_arr:
                if word in short_words_exact:
                    pattern = rf"\b{re.escape(word)}\b"
                else:
                    pattern = rf"\b{re.escape(word)}[a-zA-Z]*\b"
                count += len(re.findall(pattern, text, re.IGNORECASE))
            return count

        # Count original
        orig_masc = count_gendered_words(orig_text_lower, wordlists.MASCULINE_HIGH + wordlists.MASCULINE_MEDIUM)
        orig_fem = count_gendered_words(orig_text_lower, wordlists.FEMININE)
        
        # Fixed JD counts
        fixed_text_lower = st.session_state.fixed_jd.lower()
        fixed_masc = count_gendered_words(fixed_text_lower, wordlists.MASCULINE_HIGH + wordlists.MASCULINE_MEDIUM)
        fixed_fem = count_gendered_words(fixed_text_lower, wordlists.FEMININE)
        
        # Predict Appeal Ratios using smoothed logic:
        # Male ratio = (M + 1) / (M + F + 2)
        # Female ratio = (F + 1) / (M + F + 2)
        orig_total = orig_masc + orig_fem
        fixed_total = fixed_masc + fixed_fem
        
        orig_male_pct = round((orig_masc + 1) / (orig_total + 2) * 100)
        orig_female_pct = 100 - orig_male_pct
        
        fixed_male_pct = round((fixed_masc + 1) / (fixed_total + 2) * 100)
        fixed_female_pct = 100 - fixed_male_pct
        
        # Display Predictor Visual
        c_col1, c_col2 = st.columns([1, 1])
        
        with c_col1:
            st.markdown(
                f"""
                <div class="premium-card">
                    <h4 style="margin-top: 0px; text-align: center; color: #EF4444;">Before Fix (Draft JD)</h4>
                    <div style="text-align: center; margin: 15px 0;">
                        <span style="font-size: 2.2rem; font-weight: 700; color: #F8FAFC;">{orig_male_pct}%</span>
                        <span style="font-size: 1.2rem; color: #94A3B8;"> Male Appeal</span>
                    </div>
                    <div style="text-align: center; margin: 15px 0;">
                        <span style="font-size: 2.2rem; font-weight: 700; color: #F8FAFC;">{orig_female_pct}%</span>
                        <span style="font-size: 1.2rem; color: #94A3B8;"> Female Appeal</span>
                    </div>
                    <p style="text-align: center; font-size: 0.9rem; margin-top: 15px;">
                        Masculine words: <b>{orig_masc}</b> | Feminine words: <b>{orig_fem}</b>
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        with c_col2:
            st.markdown(
                f"""
                <div class="premium-card">
                    <h4 style="margin-top: 0px; text-align: center; color: #10B981;">After Fix (Optimized JD)</h4>
                    <div style="text-align: center; margin: 15px 0;">
                        <span style="font-size: 2.2rem; font-weight: 700; color: #F8FAFC;">{fixed_male_pct}%</span>
                        <span style="font-size: 1.2rem; color: #94A3B8;"> Male Appeal</span>
                    </div>
                    <div style="text-align: center; margin: 15px 0;">
                        <span style="font-size: 2.2rem; font-weight: 700; color: #F8FAFC;">{fixed_female_pct}%</span>
                        <span style="font-size: 1.2rem; color: #94A3B8;"> Female Appeal</span>
                    </div>
                    <p style="text-align: center; font-size: 0.9rem; margin-top: 15px;">
                        Masculine words: <b>{fixed_masc}</b> | Feminine words: <b>{fixed_fem}</b>
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        # Summary metrics using premium custom metric cards
        appeal_diff = fixed_female_pct - orig_female_pct
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-card">
                <div class="metric-lbl">Predicted Female Applicant Appeal</div>
                <div class="metric-val" style="color: #34D399;">{fixed_female_pct}%</div>
                <div class="metric-change positive">+{appeal_diff}% Increase</div>
            </div>
            <div class="metric-card">
                <div class="metric-lbl">Overall Inclusivity Score Boost</div>
                <div class="metric-val" style="color: #FF7A00;">+{improve_pct}%</div>
                <div class="metric-change positive">Optimized Appeal Index</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
            
        st.write(
            f"**Improvement Summary:** By removing masculine and exclusionary terms, you improved inclusivity by **{improve_pct}%**. "
            f"Predicted female appeal increased from **{orig_female_pct}%** to **{fixed_female_pct}%**, helping you tap into a much wider talent pool."
        )
# End of File
