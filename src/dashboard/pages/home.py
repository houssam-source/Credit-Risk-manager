import streamlit as st
import pandas as pd
import plotly.express as px
import os

def app():
    # Page configuration
    st.title("🏠 Credit Risk Management Dashboard - Home")
    st.markdown("---")
    
    # Welcome section
    st.header("Welcome to Credit Risk Management Dashboard")
    st.write("""
    This dashboard provides insights and analytics for credit risk assessment and management. 
    Navigate through different sections to explore data, model performance, predictions, and feature analysis.
    """)
    
    # Key metrics
    st.subheader("Key Metrics Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Total Applications", value="100,000+", delta="+12%")
    with col2:
        st.metric(label="Default Rate", value="18.2%", delta="-2.1%")
    with col3:
        st.metric(label="Model Accuracy", value="85.4%", delta="+3.2%")
    with col4:
        st.metric(label="Active Models", value="5", delta="+1")
    
    # Dataset information
    st.subheader("Dataset Information")
    st.write("""
    This dashboard uses the Home Credit Default Risk dataset which contains:
    - Client demographic and financial information
    - Previous loan application records
    - Credit bureau data
    - Payment history records
    """)
    
    # Sample data preview
    st.subheader("Sample Data Preview")
    sample_data = {
        'SK_ID_CURR': [274941, 274942, 274943, 274944, 274945],
        'TARGET': [0, 0, 0, 0, 1],
        'NAME_CONTRACT_TYPE': ['Cash loans', 'Cash loans', 'Revolving loans', 'Cash loans', 'Cash loans'],
        'AMT_INCOME_TOTAL': [202500.0, 299999.5, 216500.0, 195660.0, 180000.0],
        'AMT_CREDIT': [406597.5, 513531.0, 364500.0, 364500.0, 625840.5],
        'DAYS_BIRTH': [-17688, -15678, -18079, -19030, -19093],
        'EXT_SOURCE_3': [0.50625, 0.31250, 0.76250, 0.75000, 0.53750]
    }
    df_sample = pd.DataFrame(sample_data)
    st.dataframe(df_sample, use_container_width=True)
    
    # About the models
    st.subheader("About Our Models")
    st.write("""
    We use various machine learning models to predict credit default risk:
    - Random Forest Classifier
    - Gradient Boosting Classifier
    - Logistic Regression
    - XGBoost Classifier
    - LightGBM Classifier
    
    These models are trained on historical data to identify patterns that indicate higher probability of default.
    """)
    
    # Recent activity
    st.subheader("Recent Activity")
    recent_activity = [
        "✅ Model retraining completed successfully",
        "📊 New feature engineering pipeline deployed",
        "📈 Performance metrics updated",
        "🔍 Data quality checks passed"
    ]
    
    for activity in recent_activity:
        st.write(activity)