import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

h1, h2, h3, h4 {
    color: white;
    font-family: 'Segoe UI';
}

.metric-card {
    background: linear-gradient(145deg, #112D4E, #0B1F3A);
    padding: 20px;
    border-radius: 20px;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.3);
    border: 1px solid #1E3A5F;
}

.insight-box {
    background: #112D4E;
    padding: 15px;
    border-radius: 15px;
    border-left: 5px solid #4FC3F7;
    color: white;
}
.chart-card {
    background: linear-gradient(145deg, #112D4E, #0B1F3A);
    padding: 20px;
    border-radius: 25px;
    border: 1px solid #1E3A5F;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.35);
    margin-bottom: 25px;
    transition: 0.3s ease;
}

.chart-card:hover {
    transform: translateY(-5px);
    box-shadow: 0px 10px 24px rgba(0,0,0,0.45);
}

</style>
""", unsafe_allow_html=True)

# ======================================================
# LOAD DATA
# ======================================================

@st.cache_data

def load_data():
    df = pd.read_excel("cleaned_hupa_diabetes_recent1.xlsb")    
    demo = pd.read_csv('cleaned_demographics.csv')

    df['time'] = pd.to_datetime(df['time'])

    # Merge demographics
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
# DATASET OVERVIEW
# ======================================================

if analysis_type == 'Dataset Overview':

    st.subheader('📘 Dataset Overview')

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric('Total Patients', df['patient_id'].nunique())

    with col2:
        st.metric('Total Records', len(df))

    with col3:
        st.metric('Average Glucose', round(df['glucose'].mean(),2))

    with col4:
        st.metric('Average TIR', round(((df['glucose'].between(70,180)).mean()*100),2))

    # Demographics charts
    if 'gender' in df.columns:

        gender_chart = px.pie(
            df,
            names='gender',
            title='Gender Distribution',
            template='plotly_dark'
        )

        st.plotly_chart(gender_chart, use_container_width=True)

    if 'age' in df.columns:

        age_chart = px.histogram(
            df,
            x='age',
            nbins=20,
            title='Age Distribution',
            template='plotly_dark'
        )

        st.plotly_chart(age_chart, use_container_width=True)

    overview_chart = px.line(
        df,
        x='time',
        y='glucose',
        color='patient_id',
        title='Overall Glucose Trends Across Patients',
        template='plotly_dark'
    )

    st.plotly_chart(overview_chart, use_container_width=True)

# ======================================================
# HEADER
# ======================================================

st.title("🩺 AI-Powered Diabetes Intelligence Dashboard")
st.markdown("### HUPA-UCM Continuous Glucose Monitoring Analytics")

# ======================================================
# KPI SECTION
# ======================================================

col1, col2, col3, col4 = st.columns(4)

avg_glucose = round(df['glucose'].mean(), 2)
max_glucose = round(df['glucose'].max(), 2)
min_glucose = round(df['glucose'].min(), 2)
avg_steps = round(df['steps'].mean(), 0)

with col1:
    st.metric("Average Glucose", avg_glucose)

with col2:
    st.metric("Maximum Glucose", max_glucose)

with col3:
    st.metric("Minimum Glucose", min_glucose)

with col4:
    st.metric("Average Steps", avg_steps)

# ======================================================
# DESCRIPTIVE ANALYTICS
# ======================================================

if analysis_type == "Descriptive Analytics":

    st.subheader("📊 Descriptive Analytics Dashboard")

    col1, col2 = st.columns(2)



    # --------------------------------------------------
    # TIME IN RANGE
    # --------------------------------------------------
    with col1:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)

    s tir = ((df['glucose'] >= 70) & (df['glucose'] <= 180)).mean() * 100

    fig_tir = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = tir,
        title = {'text': "Time In Range (%)"},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "#00D4FF"},
            'steps': [
                {'range': [0, 50], 'color': '#7f1d1d'},
                {'range': [50, 70], 'color': '#78350f'},
                {'range': [70, 100], 'color': '#14532d'}
            ]
        }
    ))

    st.plotly_chart(fig_tir, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)


   

    # --------------------------------------------------
    # 24-HOUR GLUCOSE TREND
    # --------------------------------------------------

    fig_glucose = px.line(
        df,
        x='time',
        y='glucose',
        title='24-Hour Glucose Trend',
        template='plotly_dark'
    )

    fig_glucose.add_hline(y=70, line_dash='dash', line_color='red')
    fig_glucose.add_hline(y=180, line_dash='dash', line_color='orange')

    st.plotly_chart(fig_glucose, use_container_width=True)

    # --------------------------------------------------
    # HYPOGLYCEMIA ANALYSIS
    # --------------------------------------------------
    with col2:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)

    hypo = df[df['glucose'] < 70]

    fig_hypo = px.histogram(
        hypo,
        x='glucose',
        nbins=20,
        title='Hypoglycemic Frequency Distribution',
        template='plotly_dark'
    )

    st.plotly_chart(fig_hypo, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

   

    # --------------------------------------------------
    # HEART RATE VS ROC
    # --------------------------------------------------

    fig_hr = px.scatter(
        df,
        x='heart_rate',
        y='glucose_roc',
        color='glucose',
        size='steps',
        title='Heart Rate vs Glucose Rate of Change',
        template='plotly_dark',
        hover_data=['patient_id', 'glucose']
    )

    st.plotly_chart(fig_hr, use_container_width=True)

# ======================================================
# PREDICTIVE ANALYTICS
# ======================================================

elif analysis_type == "Predictive Analytics":

    st.subheader("🤖 Predictive Analytics Dashboard")

    # --------------------------------------------------
    # HYPOGLYCEMIA RISK SCORE
    # --------------------------------------------------

    df['risk_score'] = (
        abs(df['glucose_roc']) * 0.4 +
        abs(df['glucose_rolling_std_1h']) * 0.4 +
        abs(df['heart_rate']) * 0.2
    )

    fig_risk = px.line(
        df,
        x='time',
        y='risk_score',
        title='Predicted Hypoglycemia Risk Trend',
        template='plotly_dark'
    )

    st.plotly_chart(fig_risk, use_container_width=True)

    # --------------------------------------------------
    # HIGH VARIABILITY DAY PREDICTION
    # --------------------------------------------------

    fig_var = px.scatter(
        df,
        x='glucose_rolling_std_1h',
        y='glucose',
        color='steps',
        size='heart_rate',
        title='Glucose Variability Prediction',
        template='plotly_dark'
    )

    st.plotly_chart(fig_var, use_container_width=True)

    # --------------------------------------------------
    # MORNING GLUCOSE PREDICTION
    # --------------------------------------------------

    morning = df[df['hour'].between(5,10)]

    fig_morning = px.box(
        morning,
        x='hour',
        y='glucose',
        color='hour',
        title='Morning Glucose Pattern Analysis',
        template='plotly_dark'
    )

    st.plotly_chart(fig_morning, use_container_width=True)

# ======================================================
# PRESCRIPTIVE ANALYTICS
# ======================================================

elif analysis_type == "Prescriptive Analytics":

    st.subheader("🧠 Prescriptive Intervention Dashboard")

    # --------------------------------------------------
    # GLUCOSE VARIABILITY INTERVENTION
    # --------------------------------------------------

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
        title='Glucose Variability Risk Intervention',
        template='plotly_dark',
        hover_data=['patient_id', 'steps', 'carb_input']
    )

    fig_intervention.add_hline(
        y=30,
        line_dash='dash',
        line_color='red'
    )

    st.plotly_chart(fig_intervention, use_container_width=True)

    # --------------------------------------------------
    # ACTIVITY VS INSULIN
    # --------------------------------------------------

    fig_activity = px.scatter(
        df,
        x='calories',
        y='basal_rate',
        color='glucose',
        size='steps',
        trendline='lowess',
        title='Physical Activity vs Insulin Requirement',
        template='plotly_dark'
    )

    st.plotly_chart(fig_activity, use_container_width=True)

    # --------------------------------------------------
    # CARB TREATMENT HEATMAP
    # --------------------------------------------------

    hypo = df[df['glucose'] < 70].copy()

    hypo['Recovery_Status'] = np.where(
        hypo['glucose_roc'] > 3,
        'Rebound Hyperglycemia',
        'Safe Recovery'
    )

    hypo['carb_bin'] = pd.cut(
        hypo['carb_input'],
        bins=[0,5,10,15,20,30,50]
    ).astype(str)

    heat = hypo.groupby(
        ['carb_bin', 'Recovery_Status'],
        observed=False
    ).size().reset_index(name='count')

    fig_heat = px.density_heatmap(
        heat,
        x='carb_bin',
        y='Recovery_Status',
        z='count',
        text_auto=True,
        title='Optimal Carb Intake for Hypoglycemia Recovery',
        template='plotly_dark'
    )

    st.plotly_chart(fig_heat, use_container_width=True)

    # --------------------------------------------------
    # AI INTERVENTION ENGINE
    # --------------------------------------------------

    st.markdown("## 🚨 AI Intervention Recommendations")

    if df['glucose_rolling_std_1h'].mean() > 30:
        st.error("High glucose variability detected. Recommend insulin reassessment and activity intervention.")

    if df['glucose'].max() > 250:
        st.warning("Severe hyperglycemia risk detected. Increase glucose monitoring frequency.")

    if df['glucose'].min() < 60:
        st.info("Hypoglycemia intervention recommended. Monitor carb correction strategy.")

# ======================================================
# INSIGHT PANEL
# ======================================================

st.markdown("---")
st.subheader("📌 Clinical Insights")

st.markdown("""
<div class='insight-box'>
<b>Key Clinical Findings:</b><br><br>
• Increased glucose variability strongly predicts future glycemic instability.<br><br>
• Moderate physical activity improves insulin sensitivity and reduces glucose fluctuations.<br><br>
• High carbohydrate meals significantly increase post-meal glucose excursions.<br><br>
• Sleep duration between 7–8 hours is associated with improved Time-In-Range.<br><br>
• Early predictive alerts can reduce severe hypoglycemia risk through proactive intervention.
</div>
""", unsafe_allow_html=True)

# ======================================================
# FOOTER
# ======================================================

st.markdown("---")
st.caption("Developed for HUPA-UCM Diabetes Intelligence Analytics | PyCore Python Hackathon 2026")
