# app.py
import streamlit as st
from dotenv import load_dotenv
load_dotenv()
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from src.ext import extract_text_from_pdf
from src.pre import extract_contract_metadata
from src.utils import classify_clauses, classify_clauses_ml, CUAD_CATEGORIES

# ====================== PREMIUM DARK THEME ======================
st.set_page_config(page_title="AI Contract Analyzer", layout="wide", page_icon="📄")

st.markdown("""
<style>

/* ===== Global App ===== */
.stApp, .main {
    background:
      radial-gradient(circle at top right, rgba(59,130,246,0.16), transparent 28%),
      radial-gradient(circle at bottom left, rgba(251,191,36,0.08), transparent 25%),
      linear-gradient(135deg, #040814 0%, #0b1120 45%, #111827 100%);
    color: #f8fafc;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 1450px;
}

/* ===== Sidebar ===== */
section[data-testid="stSidebar"] {
    background:
      linear-gradient(180deg, #050b18 0%, #0f172a 100%);
    border-right: 1px solid rgba(255,255,255,0.05);
}

section[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}

/* ===== Header ===== */
.header {
    background:
      linear-gradient(135deg, rgba(10,15,30,0.95), rgba(30,64,175,0.92), rgba(37,99,235,0.88));
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 26px;
    padding: 32px 36px;
    margin-bottom: 30px;
    box-shadow:
      0 25px 60px rgba(0,0,0,0.45),
      inset 0 1px 0 rgba(255,255,255,0.08);
}

.header h1 {
    margin: 0;
    font-size: 2.8rem;
    font-weight: 800;
    letter-spacing: -0.5px;
}

.header p {
    margin-top: 8px;
    color: rgba(255,255,255,0.88);
    font-size: 1.05rem;
}

/* ===== Metric Cards ===== */
div[data-testid="metric-container"] {
    background: rgba(15,23,42,0.82);
    border: 1px solid rgba(251,191,36,0.14);
    border-radius: 22px;
    padding: 16px;
    box-shadow:
      0 14px 34px rgba(0,0,0,0.35),
      inset 0 1px 0 rgba(255,255,255,0.04);
}

/* ===== Premium Cards ===== */
.card, .sidebar-card {
    background: rgba(15,23,42,0.72);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 22px;
    box-shadow:
      0 16px 40px rgba(0,0,0,0.32);
}

/* ===== Buttons ===== */
.stButton > button {
    width: 100%;
    border: none;
    border-radius: 16px;
    padding: 0.78rem 1rem;
    font-weight: 800;
    letter-spacing: 0.3px;
    color: #111827;
    background: linear-gradient(135deg, #facc15, #f59e0b);
    box-shadow:
      0 14px 26px rgba(245,158,11,0.34),
      inset 0 1px 0 rgba(255,255,255,0.38);
    transition: all 0.22s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    background: linear-gradient(135deg, #fde047, #f59e0b);
    box-shadow:
      0 18px 34px rgba(245,158,11,0.42);
}

/* ===== Tabs ===== */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    margin-bottom: 16px;
}

.stTabs [data-baseweb="tab"] {
    background: rgba(30,41,59,0.8);
    color: #cbd5e1;
    border-radius: 14px;
    padding: 10px 18px;
    border: 1px solid rgba(255,255,255,0.04);
    font-weight: 700;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #1d4ed8, #2563eb);
    color: white !important;
    box-shadow: 0 10px 24px rgba(37,99,235,0.34);
}

/* ===== Expanders ===== */
details {
    background: rgba(15,23,42,0.8);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 16px;
    padding: 6px 12px;
    margin-bottom: 10px;
}

/* ===== DataFrame ===== */
[data-testid="stDataFrame"] {
    border-radius: 18px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.05);
    box-shadow: 0 12px 28px rgba(0,0,0,0.28);
}

/* ===== Inputs ===== */
.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] {
    background: rgba(15,23,42,0.82);
    color: white;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.04);
}

/* ===== File Upload ===== */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.02);
    border: 1px dashed rgba(251,191,36,0.28);
    border-radius: 18px;
    padding: 12px;
}

/* ===== Alerts ===== */
.stSuccess, .stInfo, .stWarning, .stError {
    border-radius: 16px;
}

/* ===== Risk Banner ===== */
.risk-banner {
    background: linear-gradient(135deg, #7f1d1d, #dc2626);
    border-radius: 16px;
    padding: 16px;
    color: white;
    font-weight: 800;
    box-shadow: 0 12px 26px rgba(220,38,38,0.28);
}

/* ===== Scrollbar ===== */
::-webkit-scrollbar {
    width: 10px;
}
::-webkit-scrollbar-track {
    background: #0f172a;
}
::-webkit-scrollbar-thumb {
    background: linear-gradient(#2563eb, #f59e0b);
    border-radius: 20px;
}

</style>
""", unsafe_allow_html=True)
# ====================== PREMIUM SIDEBAR ======================
with st.sidebar:
    # Premium elegant icon
    st.image("https://cdn-icons-png.flaticon.com/512/10473/10473879.png", width=115)
    st.title("Command Center")
  
    uploaded_file = st.file_uploader("Upload Contract PDF", type=["pdf"], label_visibility="collapsed")
  
    analyze_button = False
    if uploaded_file:
        st.markdown(f'''
            <div class="sidebar-card" style="padding:16px; border-radius:16px; color:white; text-align:center; margin-bottom:12px;">
                📄 {uploaded_file.name}
            </div>
        ''', unsafe_allow_html=True)
        analyze_button = st.button("🚀 Initiate Deep Analysis", use_container_width=True)
    else:
        st.markdown('''
            <div class="sidebar-card" style="padding:16px; border-radius:16px; color:#94a3b8; text-align:center; font-size:0.95rem;">
                No file uploaded yet
            </div>
        ''', unsafe_allow_html=True)
  
    st.divider()
    st.markdown('<div class="sidebar-card" style="background: linear-gradient(135deg, #1e40af, #3b82f6); padding:14px; border-radius:14px; color:white; text-align:center;">Analyzing 41 CUAD Categories</div>', unsafe_allow_html=True)
    
    use_ml = st.checkbox("🚀 Use Trained ML Model (93% accuracy)", value=True)

# ====================== HERO HEADER ======================
st.markdown("""
    <div class="header">
        <h1>📄 AI Contract Analyzer</h1>
        <p style="margin:8px 0 0 0; font-size:1.1rem; opacity:0.95;">
            Review contracts in minutes, not hours — with AI-powered clause intelligence
        </p>
    </div>
""", unsafe_allow_html=True)

# ====================== MAIN LOGIC ======================
if uploaded_file and analyze_button:
    try:
        with st.spinner("🕵️ AI is conducting deep-scan analysis..."):
            contract_text = extract_text_from_pdf(uploaded_file)
            metadata = extract_contract_metadata(contract_text)
          
            if use_ml:
                analysis = classify_clauses_ml(contract_text)
            else:
                analysis = classify_clauses(contract_text)
        risks = [a for a in analysis if a.risk_level in ["high", "critical"]]
        risk_score = min(100, (len(risks) * 25) + (len(analysis) // 3))

        col1, col2, col3, col4 = st.columns([1,1,1.5,1])
        with col1:
            st.metric("📑 Total Clauses", len(analysis), label_visibility="visible")
        with col2:
            st.metric("⚠️ High Risks", len(risks), delta=len(risks), delta_color="inverse")
        with col3:
            # ==================== THICK & PREMIUM RISK GAUGE ====================
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=risk_score,
                title={'text': "Overall Risk Score", 'font': {'size': 24, 'family': 'Arial Black'}},
                delta={'reference': 50, 'increasing': {'color': "#ef4444"}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1},
                    'bar': {'color': "#eab308", 'thickness': 0.38},   # ← Thick & Premium
                    'bgcolor': "rgba(15,23,42,0.4)",
                    'steps': [
                        {'range': [0, 40], 'color': "#10b981"},
                        {'range': [40, 70], 'color': "#f59e0b"},
                        {'range': [70, 100], 'color': "#ef4444"}
                    ],
                    'threshold': {'line': {'color': "#fff", 'width': 5}, 'thickness': 0.82, 'value': 85}
                }
            ))
            st.plotly_chart(fig_gauge, use_container_width=True)
        with col4:
            st.metric("🌍 Governing Law", metadata.governing_law or "Not specified")

        # ====================== CONTRACT METADATA ======================
        st.markdown("### 📋 Contract Metadata")
        meta_dict = metadata.model_dump() if hasattr(metadata, 'model_dump') else metadata
        st.json(meta_dict, expanded=True)
        st.markdown("<br>", unsafe_allow_html=True)

        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Risk Analysis", "📑 Clause Inventory", "📈 Visualizations", "📝 Executive Summary", "📥 Export"])

        with tab1:
            if risks:
                st.markdown(f'<div class="risk-banner">⚠️ Found {len(risks)} Critical Issues</div>', unsafe_allow_html=True)
                for r in risks:
                    with st.expander(f"🚩 {r.category.upper()} — {r.risk_level.upper()}"):
                        st.markdown(f"**Risk Analysis:** {r.risk_explanation}")
                        st.info(f"**Clause Evidence:** {r.clause_text}")
                        st.caption(f"**Contractual Obligations:** {r.party_obligations}")
            else:
                st.success("✅ No critical risks found!")

        with tab2:
            st.subheader("Detailed Clause Breakdown")
            if analysis:
                df = pd.DataFrame([a.model_dump() for a in analysis])
                st.dataframe(df, use_container_width=True)

        with tab3:
            st.subheader("Legal Data Visualizations")
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                fig_pie = px.pie(names=['High Risk', 'Normal'], values=[len(risks), max(0, len(analysis)-len(risks))])
                st.plotly_chart(fig_pie, use_container_width=True)
            with col_v2:
                if analysis:
                    cat_counts = pd.Series([a.category for a in analysis]).value_counts().head(8)
                    fig_bar = px.bar(x=cat_counts.values, y=cat_counts.index, orientation='h', labels={'x': 'Count', 'y': 'Category'})
                    st.plotly_chart(fig_bar, use_container_width=True)

        with tab4:
            st.subheader("📝 Executive Summary")
            st.markdown(f"""
            **Contract Overview** Agreement between **{metadata.party_1}** and **{metadata.party_2}**.
            Effective Date: **{metadata.effective_date}** Total Clauses: **{len(analysis)}** | High/Critical Risks: **{len(risks)}** Overall Risk Level: **{'HIGH' if risk_score > 70 else 'MEDIUM' if risk_score > 40 else 'LOW'}**
            """)

        with tab5:
            json_data = json.dumps([a.model_dump() for a in analysis], indent=2)
            st.download_button("📥 Download Full Analysis (JSON)", data=json_data,
                               file_name=f"{uploaded_file.name}_analysis.json", mime="application/json")

    except Exception as e:
        st.error(f"❌ Analysis Error: {str(e)}")

elif uploaded_file and not analyze_button:
    col_left, col_right = st.columns([1.2, 1])
    with col_left:
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1e2937, #334155); 
                        padding: 30px; border-radius: 20px; border: 1px solid #64748b; 
                        box-shadow: 0 15px 35px rgba(0,0,0,0.5); text-align: center;">
                <h3 style="margin:0 0 15px 0; color:#eab308;">📤 Document Ready for Analysis</h3>
                <p style="font-size:1.1rem;">
                    Your file has been successfully uploaded.<br>
                    Click the <strong>🚀 Initiate Deep Analysis</strong> button in the sidebar to start AI-powered scanning.
                </p>
                <div style="background:#0f172a; padding:18px; border-radius:12px; display:inline-block; margin-top:15px;">
                    📄 <strong>{uploaded_file.name}</strong>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.image(
            "https://img.freepik.com/free-vector/ai-powered-contract-analysis-concept-illustration_114360-1631.jpg",
            caption="AI is ready to analyze your contract",
            width=420
        )

else:
    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns([1.5, 1])
    with col_l:
        st.markdown("### 🔍 Getting Started")
        st.info("Upload a legal document in the sidebar to begin AI-powered risk assessment.")
        st.markdown("""
        **What this analyzer identifies:**
        * **Hidden Liabilities**
        * **Unfavorable Termination Clauses**
        * **Missing Metadata (Dates, Values)**
        * **Compliance with 41 CUAD Categories**
        """)
    with col_r:
        st.image("https://images.pexels.com/photos/3760067/pexels-photo-3760067.jpeg",
                 caption="Powered by Gemini 3 Flash Intelligence")