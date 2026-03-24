import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

def app():
    st.title("🔍 Data Exploration")
    st.markdown("---")
    
    # Load real data if available, otherwise use simulated data
    st.header("Dataset Overview")
    
    # Attempt to load real data
    df = None
    
    # Get project root path
    import sys
    from pathlib import Path
    project_root = Path(__file__).parent.parent.parent
    processed_data_path = project_root / 'home-credit-default-risk' / 'data' / 'processed' / 'consolidated_features.csv'
    
    if processed_data_path.exists():
        try:
            df = pd.read_csv(processed_data_path)
            st.success(f"Loaded real data with {len(df):,} records and {len(df.columns)} features")
        except Exception as e:
            st.warning(f"Could not load real data: {str(e)}. Using simulated data instead.")
    
    # If real data not available or failed to load, use simulated data
    if df is None:
        sample_size = 1000  # Reduced for performance
        np.random.seed(42)
        
        # Generate sample data similar to Home Credit dataset
        data = {
            'SK_ID_CURR': range(100000, 100000 + sample_size),
            'TARGET': np.random.choice([0, 1], size=sample_size, p=[0.82, 0.18]),  # Approximate default rate
            'AMT_INCOME_TOTAL': np.random.lognormal(mean=12.5, sigma=0.6, size=sample_size),
            'AMT_CREDIT': np.random.lognormal(mean=11.8, sigma=0.5, size=sample_size),
            'DAYS_BIRTH': -np.random.randint(20*365, 70*365, size=sample_size),  # Age in days
            'DAYS_EMPLOYED': -np.random.randint(0, 40*365, size=sample_size),  # Days employed
            'EXT_SOURCE_1': np.random.beta(2, 5, size=sample_size),  # External score 1
            'EXT_SOURCE_2': np.random.beta(2, 5, size=sample_size),  # External score 2
            'EXT_SOURCE_3': np.random.beta(2, 5, size=sample_size),  # External score 3
            'NAME_CONTRACT_TYPE': np.random.choice(['Cash loans', 'Revolving loans'], 
                                              size=sample_size, p=[0.9, 0.1]),
            'CODE_GENDER': np.random.choice(['M', 'F'], size=sample_size, p=[0.6, 0.4]),
            'FLAG_OWN_CAR': np.random.choice(['N', 'Y'], size=sample_size, p=[0.7, 0.3]),
            'FLAG_OWN_REALTY': np.random.choice(['N', 'Y'], size=sample_size, p=[0.3, 0.7])
        }
        
        df = pd.DataFrame(data)
        st.info("Using simulated data for demonstration")
    
    # Display basic statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Total Records", value=f"{len(df):,}")
    with col2:
        default_rate = df['TARGET'].mean() * 100
        st.metric(label="Default Rate", value=f"{default_rate:.2f}%")
    with col3:
        avg_income = df['AMT_INCOME_TOTAL'].mean()
        st.metric(label="Avg Income", value=f"${avg_income:,.0f}")
    with col4:
        avg_credit = df['AMT_CREDIT'].mean()
        st.metric(label="Avg Credit", value=f"${avg_credit:,.0f}")
    
    # Distribution plots
    st.subheader("Distribution Plots")
    
    # Income distribution
    fig_income = px.histogram(df, x='AMT_INCOME_TOTAL', nbins=50, 
                              title='Distribution of Total Income',
                              labels={'AMT_INCOME_TOTAL': 'Total Income ($)', 'count': 'Count'})
    fig_income.update_layout(height=400)
    st.plotly_chart(fig_income, use_container_width=True)
    
    # Credit amount distribution
    fig_credit = px.histogram(df, x='AMT_CREDIT', nbins=50, 
                              title='Distribution of Credit Amount',
                              labels={'AMT_CREDIT': 'Credit Amount ($)', 'count': 'Count'})
    fig_credit.update_layout(height=400)
    st.plotly_chart(fig_credit, use_container_width=True)
    
    # Default rate by gender
    st.subheader("Default Rate Analysis")
    gender_default = df.groupby('CODE_GENDER')['TARGET'].agg(['count', 'sum', 'mean']).reset_index()
    gender_default.columns = ['Gender', 'Total', 'Defaults', 'Default_Rate']
    
    fig_gender = px.bar(gender_default, x='Gender', y='Default_Rate', 
                        title='Default Rate by Gender',
                        labels={'Default_Rate': 'Default Rate', 'Gender': 'Gender'},
                        color='Gender',
                        color_discrete_sequence=px.colors.qualitative.Set2)
    fig_gender.update_layout(height=400)
    st.plotly_chart(fig_gender, use_container_width=True)
    
    # Age vs Default rate
    st.subheader("Age vs Default Rate")
    df['AGE'] = -df['DAYS_BIRTH'] / 365  # Convert to years
    df['AGE_GROUP'] = pd.cut(df['AGE'], bins=[0, 25, 35, 45, 55, 100], 
                             labels=['<25', '25-35', '35-45', '45-55', '55+'])
    
    age_default = df.groupby('AGE_GROUP')['TARGET'].agg(['count', 'mean']).reset_index()
    age_default.columns = ['Age_Group', 'Count', 'Default_Rate']
    
    fig_age = px.bar(age_default, x='Age_Group', y='Default_Rate',
                     title='Default Rate by Age Group',
                     labels={'Default_Rate': 'Default Rate', 'Age_Group': 'Age Group'},
                     color='Age_Group',
                     color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_age.update_layout(height=400)
    st.plotly_chart(fig_age, use_container_width=True)
    
    # Correlation matrix
    st.subheader("Feature Correlations")
    numeric_cols = ['TARGET', 'AMT_INCOME_TOTAL', 'AMT_CREDIT', 'DAYS_BIRTH', 
                    'EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3']
    corr_matrix = df[numeric_cols].corr()
    
    fig_corr = px.imshow(corr_matrix, 
                         title='Correlation Matrix of Key Features',
                         color_continuous_scale='RdBu_r',
                         aspect="auto")
    fig_corr.update_layout(height=500)
    st.plotly_chart(fig_corr, use_container_width=True)
    
    # External scores distribution
    st.subheader("External Credit Scores Distribution")
    ext_scores = pd.melt(df, value_vars=['EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3'], 
                         var_name='Score_Type', value_name='Score_Value')
    
    fig_ext = px.box(ext_scores, x='Score_Type', y='Score_Value',
                     title='Distribution of External Credit Scores',
                     color='Score_Type',
                     color_discrete_sequence=px.colors.qualitative.Set3)
    fig_ext.update_layout(height=400)
    st.plotly_chart(fig_ext, use_container_width=True)
    
    # Data quality indicators
    st.subheader("Data Quality Indicators")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Missing Values Summary**")
        missing_data = df.isnull().sum()
        missing_percent = (missing_data / len(df)) * 100
        missing_df = pd.DataFrame({
            'Column': missing_data.index,
            'Missing Count': missing_data.values,
            'Percentage': missing_percent.values
        })
        missing_df = missing_df[missing_df['Missing Count'] > 0].sort_values('Percentage', ascending=False)
        
        if not missing_df.empty:
            st.dataframe(missing_df, height=300)
        else:
            st.info("No missing values found in the dataset.")
    
    with col2:
        st.write("**Unique Values Count**")
        unique_counts = df.nunique()
        unique_df = pd.DataFrame({
            'Column': unique_counts.index,
            'Unique_Count': unique_counts.values
        }).sort_values('Unique_Count', ascending=False)
        st.dataframe(unique_df, height=300)