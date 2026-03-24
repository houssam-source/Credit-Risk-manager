import streamlit as st
from multipage import MultiPage
import pages.home as home
import pages.data_exploration as data_exploration
import pages.model_performance as model_performance
import pages.predictions as predictions
import pages.feature_analysis as feature_analysis

# Set page configuration
st.set_page_config(
    page_title="Credit Risk Management Dashboard",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Create multipage app instance
app = MultiPage()

# Add title to sidebar
st.sidebar.title("💳 Credit Risk Dashboard")

# Add pages to the app
app.add_page("🏠 Home", home.app)
app.add_page("🔍 Data Exploration", data_exploration.app)
app.add_page("📊 Model Performance", model_performance.app)
app.add_page("🔮 Predictions", predictions.app)
app.add_page("📈 Feature Analysis", feature_analysis.app)

# Run the app
app.run()
