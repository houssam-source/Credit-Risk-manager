import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

def app():
    st.title("📊 Model Performance")
    st.markdown("---")
    
    st.header("Model Comparison & Performance Metrics")
    
    # Sample model performance data
    models_data = {
        'Model': ['Random Forest', 'Gradient Boosting', 'Logistic Regression', 'XGBoost', 'LightGBM'],
        'Accuracy': [0.854, 0.862, 0.821, 0.871, 0.868],
        'Precision': [0.78, 0.79, 0.72, 0.81, 0.80],
        'Recall': [0.72, 0.74, 0.68, 0.76, 0.75],
        'F1-Score': [0.75, 0.76, 0.70, 0.78, 0.77],
        'AUC-ROC': [0.81, 0.83, 0.76, 0.85, 0.84],
        'Training_Time': [12.5, 18.3, 3.2, 15.7, 10.4]  # in minutes
    }
    
    df_models = pd.DataFrame(models_data)
    
    # Model comparison metrics
    st.subheader("Model Performance Comparison")
    
    # Create tabs for different metrics
    tab1, tab2, tab3, tab4 = st.tabs(["Accuracy & Precision", "Recall & F1-Score", "AUC-ROC", "Training Time"])
    
    with tab1:
        fig_metrics = go.Figure(data=[
            go.Bar(name='Accuracy', x=df_models['Model'], y=df_models['Accuracy']),
            go.Bar(name='Precision', x=df_models['Model'], y=df_models['Precision'])
        ])
        fig_metrics.update_layout(
            barmode='group',
            title='Model Accuracy and Precision Comparison',
            xaxis_title='Model',
            yaxis_title='Score',
            height=500
        )
        st.plotly_chart(fig_metrics, use_container_width=True)
    
    with tab2:
        fig_recall_f1 = go.Figure(data=[
            go.Bar(name='Recall', x=df_models['Model'], y=df_models['Recall']),
            go.Bar(name='F1-Score', x=df_models['Model'], y=df_models['F1-Score'])
        ])
        fig_recall_f1.update_layout(
            barmode='group',
            title='Model Recall and F1-Score Comparison',
            xaxis_title='Model',
            yaxis_title='Score',
            height=500
        )
        st.plotly_chart(fig_recall_f1, use_container_width=True)
    
    with tab3:
        fig_auc = px.bar(df_models, x='Model', y='AUC-ROC',
                         title='AUC-ROC Score Comparison',
                         color='Model',
                         color_discrete_sequence=px.colors.qualitative.Set3)
        fig_auc.update_layout(height=500)
        st.plotly_chart(fig_auc, use_container_width=True)
    
    with tab4:
        fig_time = px.bar(df_models, x='Model', y='Training_Time',
                          title='Training Time Comparison (minutes)',
                          color='Model',
                          color_discrete_sequence=px.colors.diverging.Tealrose)
        fig_time.update_layout(height=500)
        st.plotly_chart(fig_time, use_container_width=True)
    
    # Detailed metrics table
    st.subheader("Detailed Model Metrics")
    st.dataframe(df_models.style.format({
        'Accuracy': '{:.3f}',
        'Precision': '{:.3f}',
        'Recall': '{:.3f}',
        'F1-Score': '{:.3f}',
        'AUC-ROC': '{:.3f}',
        'Training_Time': '{:.1f} min'
    }), use_container_width=True)
    
    # Confusion matrix simulation
    st.subheader("Confusion Matrix Example (Random Forest)")
    
    # Create a sample confusion matrix
    cm_data = [[7850, 1250], [850, 2050]]  # [[TN, FP], [FN, TP]]
    cm_df = pd.DataFrame(cm_data, 
                         columns=['Predicted Negative', 'Predicted Positive'],
                         index=['Actual Negative', 'Actual Positive'])
    
    fig_cm = px.imshow(cm_df, 
                       text_auto=True,
                       color_continuous_scale='Blues',
                       title='Confusion Matrix - Random Forest Model')
    fig_cm.update_layout(height=400)
    st.plotly_chart(fig_cm, use_container_width=True)
    
    # ROC Curves
    st.subheader("ROC Curves Comparison")
    
    # Generate sample ROC curve data
    models = df_models['Model']
    fig_roc = go.Figure()
    
    for i, model in enumerate(models):
        # Generate sample ROC points
        fpr = np.linspace(0, 1, 100)
        # Create realistic TPR curves based on AUC scores
        auc = df_models[df_models['Model'] == model]['AUC-ROC'].values[0]
        # Simplified TPR calculation based on AUC
        tpr = fpr**(2-auc)  # Simplified approximation
        
        fig_roc.add_trace(go.Scatter(x=fpr, y=tpr, 
                                     mode='lines',
                                     name=f'{model} (AUC={auc:.3f})'))
    
    # Add diagonal line
    fig_roc.add_trace(go.Scatter(x=[0, 1], y=[0, 1], 
                                 mode='lines', 
                                 line=dict(dash='dash', color='gray'),
                                 name='Random Classifier'))
    
    fig_roc.update_layout(
        title='ROC Curves Comparison',
        xaxis_title='False Positive Rate',
        yaxis_title='True Positive Rate',
        height=500
    )
    st.plotly_chart(fig_roc, use_container_width=True)
    
    # Feature importance visualization
    st.subheader("Feature Importance (Top Features)")
    
    # Sample feature importance data
    feature_imp_data = {
        'Feature': ['EXT_SOURCE_3', 'EXT_SOURCE_2', 'EXT_SOURCE_1', 'DAYS_BIRTH', 
                   'AMT_INCOME_TOTAL', 'DAYS_EMPLOYED', 'AMT_CREDIT', 'DAYS_REGISTRATION'],
        'Importance': [0.18, 0.15, 0.12, 0.10, 0.09, 0.08, 0.07, 0.06]
    }
    df_features = pd.DataFrame(feature_imp_data)
    
    fig_feat_imp = px.bar(df_features, x='Importance', y='Feature',
                          orientation='h',
                          title='Top Feature Importances',
                          color='Feature',
                          color_discrete_sequence=px.colors.sequential.Viridis)
    fig_feat_imp.update_layout(height=500)
    st.plotly_chart(fig_feat_imp, use_container_width=True)
    
    # Model selection criteria
    st.subheader("Model Selection Criteria")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Best Models by Metric**:")
        best_accuracy = df_models.loc[df_models['Accuracy'].idxmax(), 'Model']
        best_precision = df_models.loc[df_models['Precision'].idxmax(), 'Model']
        best_recall = df_models.loc[df_models['Recall'].idxmax(), 'Model']
        best_f1 = df_models.loc[df_models['F1-Score'].idxmax(), 'Model']
        best_auc = df_models.loc[df_models['AUC-ROC'].idxmax(), 'Model']
        
        st.write(f"- Accuracy: {best_accuracy}")
        st.write(f"- Precision: {best_precision}")
        st.write(f"- Recall: {best_recall}")
        st.write(f"- F1-Score: {best_f1}")
        st.write(f"- AUC-ROC: {best_auc}")
    
    with col2:
        st.write("**Recommendation**:")
        # Simple weighted scoring (adjust weights as needed)
        weights = {'Accuracy': 0.25, 'Precision': 0.2, 'Recall': 0.2, 'F1-Score': 0.2, 'AUC-ROC': 0.15}
        
        df_models['Weighted_Score'] = (
            df_models['Accuracy'] * weights['Accuracy'] +
            df_models['Precision'] * weights['Precision'] +
            df_models['Recall'] * weights['Recall'] +
            df_models['F1-Score'] * weights['F1-Score'] +
            df_models['AUC-ROC'] * weights['AUC-ROC']
        )
        
        top_model = df_models.loc[df_models['Weighted_Score'].idxmax(), 'Model']
        st.write(f"**Top Recommended Model: {top_model}**")
        st.write(f"*Weighted Score: {df_models['Weighted_Score'].max():.3f}*")
        
        st.write("")
        st.write("**Use Cases**:")
        st.write("- XGBoost: Best overall performance")
        st.write("- LightGBM: Good balance of speed and accuracy")
        st.write("- Logistic Regression: Interpretable results")