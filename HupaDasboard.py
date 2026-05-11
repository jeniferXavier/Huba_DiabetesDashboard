import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ======================================================
# PAGE CONFIG
# ======================================================

st.set_page_config(
    page_title="AI Diabetes Intelligence Dashboard",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================================================
# CUSTOM CSS
# ======================================================

st.markdown("""
<style>

.main {
    background-color: #081229;
}

/* Sidebar */

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0B1F3A 0%, #102B50 100%);
    border-right: 1px solid #1E3A5F;
}

section[data-testid="stSidebar"] div.stButton > button {
    width: 100%;
    border-radius: 12px;
    background-color: #112D4E;
    color: white;
    border: 1px solid #1E4D7A;
    padding: 12px;
    margin-bottom: 8px;
    font-weight: 600;
}

section[data-testid="stSidebar"] div.stButton > button:hover {
    background-color: #1B4F8C;
    color: white;
}

/* Titles */

h1, h2, h3, h4 {
    color: white;
    font-family: 'Segoe UI';
}

/* KPI Cards */

.kpi-card {
    background: #EAF3FF;
    padding: 18px;
    border-radius: 22px;
    border: 1px solid #D6E6FF;
    box-shadow: 0px 4px 18px rgba(0,0,0,0.15);
    text-align: center;
}

.kpi-title {
    color: #1B3B6F;
    font-size: 16px;
    font-weight: 600;
}

.kpi-value {
    color: #081229;
    font-size: 32px;
    font-weight: bold;
}

/* Chart Containers */

[data-testid="stVerticalBlockBorderWrapper"] {
    background: #F4F8FF;
    border-radius: 24px;
    padding: 18px;
    border: 1px solid #D9E6FF;
    box-shadow: 0px 6px 20px rgba(0,0,0,0.12);
    margin-bottom: 20px;
}

/* Insight Box */

.insight-box {
    background: #EAF3FF;
    padding: 20px;
    border-radius: 20px;
    border-left: 6px solid #1B4F8C;
    color: #081229;
    box-shadow: 0px 4px 14px rgba(0,0,0,0.12);
}

</style>
""", unsafe_allow_html=True)

# ======================================================
# HELPER FUNCTIONS
# ======================================================

def chart_container(title, fig):

    with st.container(border=True):

        st.markdown(f"### {title}")

        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#081229'
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={'displayModeBar': False}
        )


def kpi_card(title, value):

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ======================================================
# LOAD DATA
# ======================================================

@st.cache_data
def load_data():

    df = pd.read_excel("cleaned_hupa_diabetes_recent1.xlsb")
    demo = pd.read_csv("cleaned_demographics.csv")

    df['time'] = pd.to_datetime(df['time'])

    if 'patient_id' in demo.columns:
        df = df.merge(demo, on='patient_id', how='left')

    return df

df = load_data()

# ======================================================
# SIDEBAR
# ======================================================

st.sidebar.title("🧠 AI Diabetes Analytics")

st.sidebar.markdown("## 📂 Navigation")

if 'menu' not in st.session_state:
    st.session_state.menu = 'Dataset Overview'

if st.sidebar.button('📘 Dataset Overview'):
    st.session_state.menu = 'Dataset Overview'

if st.sidebar.button('📊 Descriptive Analytics'):
    st.session_state.menu = 'Descriptive Analytics'

if st.sidebar.button('🤖 Predictive Analytics'):
    st.session_state.menu = 'Predictive Analytics'

if st.sidebar.button('🧠 Prescriptive Analytics'):
    st.session_state.menu = 'Prescriptive Analytics'

analysis_type = st.session_state.menu

patient_list = ['All Patients'] + list(df['patient_id'].unique())

selected_patient = st.sidebar.selectbox(
    "Select Patient",
    patient_list
)

if selected_patient != 'All Patients':
    df = df[df['patient_id'] == selected_patient]

# ======================================================
# HEADER
# ======================================================

st.title("🩺 AI-Powered Diabetes Intelligence Dashboard")
st.markdown("### HUPA-UCM Continuous Glucose Monitoring Analytics")

# ======================================================
# KPI SECTION
# ======================================================

avg_glucose = round(df['glucose'].mean(), 2)
max_glucose = round(df['glucose'].max(), 2)
min_glucose = round(df['glucose'].min(), 2)
avg_steps = round(df['steps'].mean(), 0)

col1, col2, col3, col4 = st.columns(4)

with col1:
    kpi_card("Average Glucose", avg_glucose)

with col2:
    kpi_card("Maximum Glucose", max_glucose)

with col3:
    kpi_card("Minimum Glucose", min_glucose)

with col4:
    kpi_card("Average Steps", avg_steps)

st.markdown("<br>", unsafe_allow_html=True)

# ======================================================
# DATASET OVERVIEW
# ======================================================

if analysis_type == 'Dataset Overview':

    st.subheader("📘 Dataset Overview")

    col1, col2 = st.columns(2)

    if 'gender' in df.columns:

        gender_chart = px.pie(
            df,
            names='gender',
            template='plotly_white'
        )

        with col1:
            chart_container("👥 Gender Distribution", gender_chart)

    if 'age' in df.columns:

        age_chart = px.histogram(
            df,
            x='age',
            nbins=20,
            template='plotly_white'
        )

        with col2:
            chart_container("📈 Age Distribution", age_chart)

    overview_chart = px.line(
        df,
        x='time',
        y='glucose',
        color='patient_id',
        template='plotly_white'
    )

    chart_container(
        "📊 Overall Glucose Trends Across Patients",
        overview_chart
    )

# ======================================================
# DESCRIPTIVE ANALYTICS
# ======================================================

elif analysis_type == "Descriptive Analytics":

    st.subheader("📊 Descriptive Analytics Dashboard")

    tir = ((df['glucose'] >= 70) &
           (df['glucose'] <= 180)).mean() * 100

    fig_tir = go.Figure(go.Indicator(
        mode="gauge+number",
        value=tir,
        title={'text': "Time In Range (%)"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#1B4F8C"}
        }
    ))

    chart_container("🎯 Time In Range", fig_tir)

    fig_glucose = px.line(
        df,
        x='time',
        y='glucose',
        template='plotly_white'
    )

    fig_glucose.add_hline(
        y=70,
        line_dash='dash',
        line_color='red'
    )

    fig_glucose.add_hline(
        y=180,
        line_dash='dash',
        line_color='orange'
    )

    chart_container(
        "📈 24-Hour Glucose Trend",
        fig_glucose
    )

    hypo = df[df['glucose'] < 70]

    fig_hypo = px.histogram(
        hypo,
        x='glucose',
        nbins=20,
        template='plotly_white'
    )

    chart_container(
        "⚠️ Hypoglycemia Frequency",
        fig_hypo
    )

    fig_hr = px.scatter(
        df,
        x='heart_rate',
        y='glucose_roc',
        color='glucose',
        size='steps',
        template='plotly_white'
    )

    chart_container(
        "❤️ Heart Rate vs Glucose ROC",
        fig_hr
    )

# ======================================================
# PREDICTIVE ANALYTICS
# ======================================================

elif analysis_type == "Predictive Analytics":

    st.subheader("🤖 Predictive Analytics Dashboard")

    df['risk_score'] = (
        abs(df['glucose_roc']) * 0.4 +
        abs(df['glucose_rolling_std_1h']) * 0.4 +
        abs(df['heart_rate']) * 0.2
    )

    fig_risk = px.line(
        df,
        x='time',
        y='risk_score',
        template='plotly_white'
    )

    chart_container(
        "🚨 Predicted Hypoglycemia Risk",
        fig_risk
    )

    fig_var = px.scatter(
        df,
        x='glucose_rolling_std_1h',
        y='glucose',
        color='steps',
        size='heart_rate',
        template='plotly_white'
    )

    chart_container(
        "📊 Glucose Variability Prediction",
        fig_var
    )

# ======================================================
# PRESCRIPTIVE ANALYTICS
# ======================================================

elif analysis_type == "Prescriptive Analytics":

    st.subheader("🧠 Prescriptive Intervention Dashboard")

    df['Risk_Level'] = np.where(
        df['glucose_rolling_std_1h'] > 30,
        'High Risk',
        'Stable'
    )

    fig_intervention = px.scatter(
        df,
        x='time',
        y='glucose_rolling_std_1h',
        color='Risk_Level',
        size='glucose',
        template='plotly_white'
    )

    fig_intervention.add_hline(
        y=30,
        line_dash='dash',
        line_color='red'
    )

    chart_container(
        "🚨 Glucose Variability Intervention",
        fig_intervention
    )

    fig_activity = px.scatter(
        df,
        x='calories',
        y='basal_rate',
        color='glucose',
        size='steps',
        template='plotly_white'
    )

    chart_container(
        "🏃 Activity vs Insulin Requirement",
        fig_activity
    )

# ======================================================
# INSIGHTS PANEL
# ======================================================

st.markdown("---")

st.subheader("📌 Clinical Insights")

st.markdown("""
<div class='insight-box'>

<b>Key Clinical Findings:</b><br><br>

• Increased glucose variability strongly predicts future glycemic instability.<br><br>

• Moderate physical activity improves insulin sensitivity and reduces glucose fluctuations.<br><br>

• High carbohydrate meals significantly increase post-meal glucose excursions.<br><br>

• Sleep duration between 7–8 hours improves Time-In-Range.<br><br>

• Predictive alerts enable proactive intervention and reduce severe hypoglycemia risk.

</div>
""", unsafe_allow_html=True)

# ======================================================
# FOOTER
# ======================================================

st.markdown("---")

st.caption(
    "Developed for HUPA-UCM Diabetes Intelligence Analytics | PyCore Python Hackathon 2026"
)
