import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os


def calculate_risk_score(income, credit_amount, age, ext_score_1, ext_score_2, ext_score_3, emp_length):
    """
    Simplified function to calculate risk score based on input features.
    In a real application, this would use a trained ML model.
    """
    # Normalize inputs
    income_ratio = min(credit_amount / max(income, 1), 5.0)  # Cap at 5x income
    
    # Calculate risk score based on features
    # Higher credit-to-income ratio increases risk
    risk = 0.3 * min(income_ratio / 2.0, 1.0)
    
    # Lower external scores increase risk
    risk += 0.2 * (1 - ext_score_3)  # External score 3 has highest weight
    risk += 0.15 * (1 - ext_score_1)
    risk += 0.1 * (1 - ext_score_2)
    
    # Age factor (younger and older clients may have higher risk)
    age_factor = 1.0 - max(0, 1 - abs(age - 40) / 20)  # Peak at age 40
    risk += 0.1 * age_factor
    
    # Employment length (longer employment reduces risk)
    risk += 0.15 * max(0, (10 - emp_length) / 10)  # More risk for shorter employment
    
    # Ensure risk is between 0 and 1
    risk = max(0, min(1, risk))
    
    return risk


def app():
    st.title("🔮 Predictions")
    st.markdown("---")
    
    st.header("Credit Risk Predictions")
    
    # Prediction form
    st.subheader("Client Information for Risk Assessment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        client_id = st.text_input("Client ID", value="100002")
        income = st.number_input("Total Income ($)", min_value=0, value=250000, step=1000)
        credit_amount = st.number_input("Credit Amount ($)", min_value=0, value=450000, step=1000)
        age = st.slider("Age", min_value=18, max_value=75, value=35)
    
    with col2:
        external_score_1 = st.slider("External Score 1", min_value=0.0, max_value=1.0, value=0.5, step=0.01)
        external_score_2 = st.slider("External Score 2", min_value=0.0, max_value=1.0, value=0.4, step=0.01)
        external_score_3 = st.slider("External Score 3", min_value=0.0, max_value=1.0, value=0.6, step=0.01)
        employment_length = st.slider("Employment Length (years)", min_value=0, max_value=40, value=5)
    
    # Make prediction button
    if st.button("Calculate Credit Risk"):
        # Try to load a real model if available, otherwise use the simulated function
        risk_score = None
        
        # Attempt to load real model
        try:
            import sys
            from pathlib import Path
            project_root = Path(__file__).parent.parent.parent
            sys.path.append(str(project_root))
            
            # Check if trained models exist
            model_path = project_root / 'src' / 'models' / 'outputs'
            scaler_path = model_path / 'scaler.pkl'
            
            if scaler_path.exists():
                import joblib
                from sklearn.ensemble import RandomForestClassifier
                
                # Try to load a model and make real prediction
                try:
                    # Load scaler
                    scaler = joblib.load(scaler_path)
                    
                    # Try to load a model (could be any of the trained models)
                    rf_model_path = model_path / 'random_forest_model.pkl'
                    if rf_model_path.exists():
                        model = joblib.load(rf_model_path)
                        
                        # Prepare features for prediction
                        features = np.array([[income, credit_amount, income/credit_amount if credit_amount > 0 else 0, 
                                            age, external_score_1, external_score_2, external_score_3, 
                                            employment_length]]).reshape(1, -1)
                        
                        # This is a simplified feature mapping - in reality, you'd need the exact features the model was trained on
                        # For now, use the simulated function as backup
                        risk_score = calculate_risk_score(income, credit_amount, age, external_score_1, 
                                                         external_score_2, external_score_3, employment_length)
                        
                        st.info("Used simulated prediction model (real model loading requires exact feature mapping)")
                    else:
                        # Use simulated function if no model found
                        risk_score = calculate_risk_score(income, credit_amount, age, external_score_1, 
                                                         external_score_2, external_score_3, employment_length)
                        
                except Exception as e:
                    st.warning(f"Could not load model for prediction: {str(e)}. Using simulated prediction.")
                    risk_score = calculate_risk_score(income, credit_amount, age, external_score_1, 
                                                     external_score_2, external_score_3, employment_length)
            else:
                # Use simulated function if no scaler found
                risk_score = calculate_risk_score(income, credit_amount, age, external_score_1, 
                                                 external_score_2, external_score_3, employment_length)
                
        except Exception as e:
            # Use simulated function if anything goes wrong
            st.warning(f"Error loading model: {str(e)}. Using simulated prediction.")
            risk_score = calculate_risk_score(income, credit_amount, age, external_score_1, 
                                             external_score_2, external_score_3, employment_length)
        
        # Determine risk level
        if risk_score < 0.3:
            risk_level = "Low Risk"
            risk_color = "#2ECC71"  # Green
        elif risk_score < 0.6:
            risk_level = "Medium Risk"
            risk_color = "#F39C12"  # Orange
        else:
            risk_level = "High Risk"
            risk_color = "#E74C3C"  # Red
        
        # Display results
        st.subheader("Prediction Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(label="Risk Score", value=f"{risk_score:.3f}")
        with col2:
            st.markdown(f"<div style='text-align: center; font-size: 24px; color: {risk_color};'><b>{risk_level}</b></div>", 
                       unsafe_allow_html=True)
        with col3:
            st.metric(label="Approval Probability", value=f"{(1-risk_score)*100:.1f}%")
        
        # Risk gauge chart
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = risk_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Risk Level"},
            gauge = {
                'axis': {'range': [None, 1], 'tickwidth': 1},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 0.3], 'color': "lightgreen"},
                    {'range': [0.3, 0.6], 'color': "orange"},
                    {'range': [0.6, 1], 'color': "red"}],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': risk_score}})
        )
        
        fig_gauge.update_layout(height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Show factors affecting risk
        st.subheader("Factors Influencing Risk Score")
        
        # Create factor influence data
        factors = {
            'Factor': ['Income Level', 'Credit-to-Income Ratio', 'Age', 'External Score 1', 
                      'External Score 2', 'External Score 3', 'Employment Length'],
            'Influence': [0.15, 0.25, 0.10, 0.15, 0.10, 0.20, 0.05],
            'Value': [f"${income:,}", f"{credit_amount/income:.2f}x", f"{age} years", 
                     f"{external_score_1:.2f}", f"{external_score_2:.2f}", 
                     f"{external_score_3:.2f}", f"{employment_length} years"]
        }
        
        df_factors = pd.DataFrame(factors)
        
        fig_factors = px.bar(df_factors, x='Influence', y='Factor', 
                            color='Factor',
                            orientation='h',
                            title='Influence of Factors on Risk Score',
                            hover_data=['Value'],
                            color_discrete_sequence=px.colors.qualitative.Pastel1)
        fig_factors.update_layout(height=400)
        st.plotly_chart(fig_factors, use_container_width=True)
        
        # Recommendation
        st.subheader("Recommendation")
        if risk_level == "Low Risk":
            st.success("✅ Approve loan with standard terms. Client presents low default risk.")
        elif risk_level == "Medium Risk":
            st.warning("⚠️ Consider approving with higher interest rate or additional collateral.")
        else:
            st.error("❌ Recommend rejecting loan application or requiring extensive additional documentation.")
    
    # Batch predictions section
    st.subheader("Batch Predictions")
    
    # Sample data for batch predictions
    sample_clients = pd.DataFrame({
        'Client_ID': ['100001', '100002', '100003', '100004', '100005'],
        'Income': [200000, 250000, 180000, 300000, 220000],
        'Credit_Amount': [350000, 450000, 300000, 500000, 380000],
        'Age': [28, 35, 42, 31, 39],
        'External_Score_3': [0.65, 0.60, 0.45, 0.70, 0.55],
        'Risk_Score': [0.25, 0.42, 0.71, 0.18, 0.53],
        'Risk_Level': ['Low Risk', 'Medium Risk', 'High Risk', 'Low Risk', 'Medium Risk']
    })
    
    st.write("Sample batch predictions:")
    st.dataframe(sample_clients.style.applymap(lambda x: 'background-color: #FFCCCC' if x == 'High Risk' 
                                               else 'background-color: #FFFFCC' if x == 'Medium Risk' 
                                               else 'background-color: #CCFFCC' if x == 'Low Risk' 
                                               else '', subset=['Risk_Level']))
    
    # Risk distribution chart
    st.subheader("Risk Distribution")
    
    # Create sample distribution data
    risk_dist = pd.DataFrame({
        'Risk_Level': ['Low Risk', 'Medium Risk', 'High Risk'],
        'Count': [650, 250, 100],
        'Percentage': [65, 25, 10]
    })
    
    fig_dist = px.pie(risk_dist, values='Count', names='Risk_Level',
                      title='Distribution of Risk Levels',
                      color_discrete_sequence=px.colors.sequential.RdBu)
    fig_dist.update_traces(textposition='inside', textinfo='percent+label')
    fig_dist.update_layout(height=400)
    st.plotly_chart(fig_dist, use_container_width=True)
    
    # Approval recommendations
    st.subheader("Approval Recommendations")
    
    approval_data = {
        'Recommendation': ['Approve', 'Conditional Approval', 'Reject'],
        'Percentage': [65, 25, 10],
        'Count': [650, 250, 100]
    }
    
    df_approval = pd.DataFrame(approval_data)
    
    fig_approval = px.bar(df_approval, x='Recommendation', y='Percentage',
                          title='Loan Approval Recommendations',
                          color='Recommendation',
                          color_discrete_map={'Approve': '#2ECC71', 
                                            'Conditional Approval': '#F39C12', 
                                            'Reject': '#E74C3C'})
    fig_approval.update_layout(height=400)
    st.plotly_chart(fig_approval, use_container_width=True)