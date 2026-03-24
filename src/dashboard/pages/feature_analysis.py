import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

def app():
    st.title("📈 Feature Analysis")
    st.markdown("---")
    
    st.header("Feature Engineering & Analysis")
    
    # Load feature importance data
    st.subheader("Feature Importance Analysis")
    
    # Sample feature importance data (similar to what might be in feature_importances.csv)
    feature_data = {
        'Feature': [
            'EXT_SOURCE_3', 'EXT_SOURCE_2', 'EXT_SOURCE_1', 'DAYS_BIRTH', 
            'AMT_INCOME_TOTAL', 'DAYS_EMPLOYED', 'AMT_CREDIT', 'DAYS_REGISTRATION',
            'DAYS_ID_PUBLISH', 'OWN_CAR_AGE', 'CNT_FAM_MEMBERS', 'REGION_POPULATION_RELATIVE',
            'AMT_ANNUITY', 'DAYS_LAST_PHONE_CHANGE', 'FLAG_DOCUMENT_3', 'NEW_RATIO_DAYS_EMPLOYED_BIRTH',
            'NEW_RATIO_INCOME_CREDIT', 'NEW_RATIO_ANNUITY_CREDIT', 'OBS_30_CNT_SOCIAL_CIRCLE',
            'DEF_30_CNT_SOCIAL_CIRCLE', 'OBS_60_CNT_SOCIAL_CIRCLE', 'DEF_60_CNT_SOCIAL_CIRCLE',
            'DAYS_FIRST_DRAWING', 'DAYS_FIRST_DUE', 'DAYS_LAST_DUE_1ST_VERSION', 'DAYS_LAST_DUE',
            'DAYS_TERMINATION', 'FLAG_DOCUMENT_2', 'FLAG_DOCUMENT_4', 'FLAG_DOCUMENT_5',
            'FLAG_DOCUMENT_6', 'FLAG_DOCUMENT_7', 'FLAG_DOCUMENT_8', 'FLAG_DOCUMENT_9',
            'FLAG_DOCUMENT_10', 'FLAG_DOCUMENT_11', 'FLAG_DOCUMENT_12', 'FLAG_DOCUMENT_13',
            'FLAG_DOCUMENT_14', 'FLAG_DOCUMENT_15', 'FLAG_DOCUMENT_16', 'FLAG_DOCUMENT_17',
            'FLAG_DOCUMENT_18', 'FLAG_DOCUMENT_19', 'FLAG_DOCUMENT_20', 'FLAG_DOCUMENT_21'
        ],
        'Importance': [
            0.18, 0.15, 0.12, 0.10, 0.09, 0.08, 0.07, 0.06,
            0.05, 0.045, 0.042, 0.040, 0.038, 0.035, 0.032, 0.030,
            0.028, 0.025, 0.023, 0.022, 0.020, 0.018, 0.017, 0.016,
            0.015, 0.014, 0.013, 0.012, 0.011, 0.010, 0.009, 0.008,
            0.007, 0.006, 0.005, 0.004, 0.003, 0.002, 0.001, 0.001,
            0.001, 0.001, 0.001, 0.001, 0.001, 0.001
        ]
    }
    
    df_features = pd.DataFrame(feature_data)
    
    # Top features chart
    top_features = df_features.head(15)
    
    fig_top_features = px.bar(top_features, x='Importance', y='Feature',
                              orientation='h',
                              title='Top 15 Most Important Features',
                              color='Feature',
                              color_discrete_sequence=px.colors.sequential.Viridis)
    fig_top_features.update_layout(height=600)
    st.plotly_chart(fig_top_features, use_container_width=True)
    
    # Feature categories
    st.subheader("Feature Categories")
    
    # Group features by category
    feature_categories = {
        'Category': [
            'External Sources', 'Demographics', 'Financial', 'Documents', 
            'Social Circle', 'Application Info', 'Other'
        ],
        'Count': [3, 4, 5, 15, 4, 3, 16],
        'Total_Importance': [0.45, 0.25, 0.18, 0.08, 0.06, 0.05, 0.03]
    }
    
    df_categories = pd.DataFrame(feature_categories)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_cat_count = px.pie(df_categories, values='Count', names='Category',
                               title='Feature Distribution by Category')
        fig_cat_count.update_traces(textposition='inside', textinfo='percent+label')
        fig_cat_count.update_layout(height=400)
        st.plotly_chart(fig_cat_count, use_container_width=True)
    
    with col2:
        fig_cat_imp = px.bar(df_categories, x='Total_Importance', y='Category',
                             orientation='h',
                             title='Total Importance by Category',
                             color='Category',
                             color_discrete_sequence=px.colors.qualitative.Set2)
        fig_cat_imp.update_layout(height=400)
        st.plotly_chart(fig_cat_imp, use_container_width=True)
    
    # Feature correlation heatmap
    st.subheader("Feature Correlations")
    
    # Create a sample correlation matrix for top features
    top_feature_names = df_features.head(10)['Feature'].tolist()
    np.random.seed(42)
    
    # Generate a correlation matrix with some realistic correlations
    n_features = len(top_feature_names)
    corr_matrix = np.random.rand(n_features, n_features) * 0.5  # Random correlations scaled down
    corr_matrix = (corr_matrix + corr_matrix.T) / 2  # Make symmetric
    np.fill_diagonal(corr_matrix, 1.0)  # Diagonal is 1
    
    fig_corr = px.imshow(corr_matrix,
                         x=top_feature_names,
                         y=top_feature_names,
                         title='Correlation Heatmap of Top 10 Features',
                         color_continuous_scale='RdBu_r',
                         aspect="auto",
                         labels=dict(color="Correlation"))
    fig_corr.update_layout(height=600)
    st.plotly_chart(fig_corr, use_container_width=True)
    
    # Feature distributions
    st.subheader("Feature Distributions")
    
    # Create sample distribution data for important features
    sample_size = 1000
    np.random.seed(42)
    
    dist_data = {
        'EXT_SOURCE_3': np.random.beta(2, 5, sample_size),
        'EXT_SOURCE_2': np.random.beta(2.5, 4, sample_size),
        'EXT_SOURCE_1': np.random.beta(1.8, 4.5, sample_size),
        'DAYS_BIRTH': -np.random.randint(20*365, 70*365, sample_size),
        'AMT_INCOME_TOTAL': np.random.lognormal(mean=12.5, sigma=0.6, size=sample_size),
    }
    
    df_dist = pd.DataFrame(dist_data)
    df_dist['DAYS_BIRTH'] = df_dist['DAYS_BIRTH'] / 365  # Convert to years
    
    # Create histograms for top features
    feature_to_plot = st.selectbox(
        'Select feature to visualize distribution:',
        ['EXT_SOURCE_3', 'EXT_SOURCE_2', 'EXT_SOURCE_1', 'DAYS_BIRTH', 'AMT_INCOME_TOTAL']
    )
    
    if feature_to_plot == 'AMT_INCOME_TOTAL':
        fig_dist = px.histogram(df_dist, x=feature_to_plot, nbins=50,
                                title=f'Distribution of {feature_to_plot}',
                                labels={feature_to_plot: f'{feature_to_plot} ($)', 'count': 'Count'})
    else:
        fig_dist = px.histogram(df_dist, x=feature_to_plot, nbins=50,
                                title=f'Distribution of {feature_to_plot}',
                                labels={feature_to_plot: feature_to_plot, 'count': 'Count'})
    
    fig_dist.update_layout(height=500)
    st.plotly_chart(fig_dist, use_container_width=True)
    
    # Feature relationships
    st.subheader("Feature Relationships")
    
    # Select two features to compare
    col1, col2 = st.columns(2)
    
    with col1:
        x_feature = st.selectbox(
            'Select X-axis feature:',
            ['EXT_SOURCE_3', 'EXT_SOURCE_2', 'EXT_SOURCE_1', 'DAYS_BIRTH', 'AMT_INCOME_TOTAL'],
            index=0
        )
    
    with col2:
        y_feature = st.selectbox(
            'Select Y-axis feature:',
            ['EXT_SOURCE_3', 'EXT_SOURCE_2', 'EXT_SOURCE_1', 'DAYS_BIRTH', 'AMT_INCOME_TOTAL'],
            index=1
        )
    
    # Create scatter plot
    fig_scatter = px.scatter(df_dist, x=x_feature, y=y_feature,
                             title=f'Relationship between {x_feature} and {y_feature}',
                             opacity=0.6)
    fig_scatter.update_layout(height=500)
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Feature engineering insights
    st.subheader("Feature Engineering Insights")
    
    insights = [
        "• External sources (EXT_SOURCE_1, 2, 3) are the most predictive features",
        "• Age (DAYS_BIRTH) shows moderate correlation with default risk",
        "• Income and credit amount ratios are important indicators",
        "• Document flags may indicate completeness of application",
        "• Social circle defaults show correlation with target variable",
        "• Employment length affects repayment capability",
        "• Region population density has minor impact on risk"
    ]
    
    for insight in insights:
        st.write(insight)
    
    # Feature statistics
    st.subheader("Feature Statistics")
    
    # Create statistics for top features
    stats_data = {
        'Feature': top_features['Feature'],
        'Mean': np.round(np.random.uniform(0.1, 0.8, len(top_features)), 3),
        'Std': np.round(np.random.uniform(0.05, 0.3, len(top_features)), 3),
        'Min': np.round(np.random.uniform(0.0, 0.5, len(top_features)), 3),
        'Max': np.round(np.random.uniform(0.5, 1.0, len(top_features)), 3),
        'Missing_%': np.round(np.random.uniform(0.0, 25.0, len(top_features)), 2)
    }
    
    df_stats = pd.DataFrame(stats_data)
    
    st.dataframe(df_stats.style.format({
        'Mean': '{:.3f}',
        'Std': '{:.3f}',
        'Min': '{:.3f}',
        'Max': '{:.3f}',
        'Missing_%': '{:.2f}%'
    }), use_container_width=True)
    
    # Feature selection techniques
    st.subheader("Feature Selection Techniques")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Univariate Selection**")
        st.write("• Uses statistical tests to select features with highest correlation to target")
        st.write("• Fast computation, good baseline")
        st.write("• May miss interactions between features")
    
    with col2:
        st.write("**Recursive Feature Elimination**")
        st.write("• Iteratively removes least important features")
        st.write("• Considers feature interactions")
        st.write("• Computationally expensive")
    
    st.write("**Principal Component Analysis**")
    st.write("• Transforms features to uncorrelated components")
    st.write("• Reduces dimensionality")
    st.write("• Loses interpretability of original features")