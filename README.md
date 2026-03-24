# 💳 Credit Risk Management System

A comprehensive machine learning-powered credit risk assessment and management system with an interactive dashboard and RESTful API.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.25+-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 Overview

This project provides an end-to-end credit risk management solution that leverages multiple machine learning models (Random Forest, Gradient Boosting, and Neural Networks) to predict credit default probability. It includes both a production-ready API and an interactive Streamlit dashboard for business users.

## ✨ Features

### 🔮 Machine Learning Models
- **Ensemble Approach**: Combines predictions from 3 powerful models
  - Random Forest Classifier
  - Gradient Boosting Classifier
  - Neural Network (TensorFlow/Keras)
- **Majority Voting**: Intelligent ensemble prediction system
- **Confidence Scoring**: Model consensus and uncertainty quantification
- **Risk Factor Analysis**: Identifies key factors influencing predictions

### 🚀 FastAPI Backend
- **RESTful API**: Production-ready endpoints for predictions
- **Real-time Inference**: Single and batch prediction support
- **Security Features**:
  - API Key authentication
  - CORS protection
  - Request size limits
  - Security headers
- **Monitoring**: Inference logging for drift detection
- **Model Integrity**: SHA256 verification for model files
- **Health Checks**: Built-in endpoint monitoring

### 📊 Interactive Dashboard
- **Multi-page Interface**:
  - 🏠 Home: Overview and key metrics
  - 🔍 Data Exploration: Dataset analysis and statistics
  - 📊 Model Performance: Evaluation metrics and comparisons
  - 🔮 Predictions: Real-time credit risk assessment
  - 📈 Feature Analysis: Feature importance and insights
- **Visual Analytics**: Interactive charts using Plotly
- **User-Friendly**: No coding required for business users

## 🏗️ Architecture

```
┌─────────────────┐         ┌──────────────────┐
│   Streamlit     │◄───────►│   FastAPI Server │
│   Dashboard     │  HTTP   │   (ML Models)    │
│   (Port 8501)   │         │   (Port 8000)    │
└─────────────────┘         └──────────────────┘
                                     │
                              ┌──────▼──────┐
                              │Model Files  │
                              │.pkl, .h5    │
                              └─────────────┘
```

## 📁 Project Structure

```
credit-risk-management/
├── src/
│   ├── api/
│   │   └── server_model.py          # FastAPI server with ML endpoints
│   ├── dashboard/
│   │   ├── app.py                   # Main Streamlit application
│   │   ├── multipage.py             # Multi-page framework
│   │   └── pages/
│   │       ├── home.py              # Home page
│   │       ├── data_exploration.py  # Data exploration page
│   │       ├── model_performance.py # Model evaluation metrics
│   │       ├── predictions.py       # Live predictions interface
│   │       └── feature_analysis.py  # Feature importance analysis
│   ├── models/
│   │   ├── outputs/                 # Trained model artifacts
│   │   ├── evaluate_models.py       # Model evaluation scripts
│   │   └── train_models.py          # Model training scripts
│   ├── preprocessing/
│   │   ├── complete_preprocessing_pipeline.py
│   │   └── feature_engineering.py
│   └── monitoring/
│       └── drift_detection.py       # Model drift monitoring
├── data/
│   ├── raw/                         # Raw data (excluded from Git)
│   └── processed/                   # Processed data (excluded from Git)
├── .streamlit/
│   └── config.toml                  # Streamlit configuration
├── requirements.txt                 # Python dependencies
├── streamlit-requirements.txt       # Streamlit Cloud dependencies
└── DEPLOYMENT_GUIDE.md              # Detailed deployment instructions
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip package manager
- Git (for deployment)

### 1. Clone the Repository

```bash
git clone https://github.com/houssam-source/Credit-Risk-manager.git
cd credit-risk-management
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the API Server

```bash
# Start the FastAPI backend
python src/api/server_model.py
```

The API will be available at `http://127.0.0.1:8000`

**API Endpoints:**
- `GET /` - API information
- `GET /health` - Health check
- `GET /models/list` - List available models
- `POST /predict` - Single prediction
- `POST /predict/batch` - Batch predictions
- `GET /docs` - Interactive API documentation (dev only)

### 4. Run the Dashboard

Open a new terminal:

```bash
# Start the Streamlit dashboard
streamlit run src/dashboard/app.py
```

The dashboard will be available at `http://localhost:8501`

## 🎯 Usage Examples

### API Usage

#### Single Prediction

```python
import requests

url = "http://localhost:8000/predict"

application_data = {
    "AMT_INCOME_TOTAL": 250000,
    "AMT_CREDIT": 450000,
    "AMT_ANNUITY": 50000,
    "AMT_GOODS_PRICE": 400000,
    "REGION_POPULATION_RELATIVE": 0.5,
    "DAYS_BIRTH": -10000,
    "DAYS_EMPLOYED": -2000,
    "DAYS_REGISTRATION": -5000,
    "DAYS_ID_PUBLISH": -3000,
    "OWN_CAR_AGE": 5
}

response = requests.post(url, json=application_data)
result = response.json()

print(f"Prediction: {result['prediction']}")
print(f"Probability: {result['probability']:.2%}")
print(f"Confidence: {result['confidence']}")
```

#### Batch Predictions

```python
batch_url = "http://localhost:8000/predict/batch"

batch_data = {
    "applications": [application_data, application_data2, ...]
}

response = requests.post(batch_url, json=batch_data)
results = response.json()
```

### Dashboard Usage

1. Open your browser to `http://localhost:8501`
2. Navigate through different pages using the sidebar
3. Use the **Predictions** page for real-time credit risk assessment
4. Explore model performance and feature importance on respective pages

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# API Configuration
API_ENV=dev                    # dev | prod
API_HOST=127.0.0.1
API_PORT=8000
MAX_REQUEST_BYTES=262144       # 256KB

# Security (Optional)
API_KEY=your-secret-api-key

# CORS Configuration
API_ALLOWED_ORIGINS=http://localhost:8501,http://127.0.0.1:8501

# Model Integrity Verification (Optional)
SCALER_SHA256=abc123...
RANDOM_FOREST_SHA256=def456...
GRADIENT_BOOSTING_SHA256=ghi789...
NEURAL_NETWORK_SHA256=jkl012...

# Monitoring
INFERENCE_LOG_PATH=data/monitoring/inference_window.csv
INFERENCE_LOG_MAX_ROWS=10000
```

## 📊 Dataset

This project uses the [Home Credit Default Risk](https://www.kaggle.com/c/home-credit-default-risk) dataset from Kaggle, which contains:
- **Application data**: Client demographics and loan details
- **Bureau data**: Credit history from external sources
- **Previous applications**: Historical application data
- **Balance data**: Monthly snapshots of active loans
- **Payment data**: Installation payment records

**Note**: Large data files are excluded from the repository. Download from Kaggle if needed.

## 🧪 Model Performance

The ensemble model achieves:
- **Accuracy**: ~85% on validation set
- **AUC-ROC**: ~0.80
- **Precision**: Optimized for credit risk assessment
- **Recall**: Balanced for default detection

See the **Model Performance** page in the dashboard for detailed metrics.

## 🚢 Deployment

### Deploy to Streamlit Cloud

1. **Push to GitHub** (already done ✅)
   ```bash
   git remote add origin https://github.com/houssam-source/Credit-Risk-manager.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Visit https://share.streamlit.io
   - Click "New app"
   - Select repository: `houssam-source/Credit-Risk-manager`
   - Configure:
     - Branch: `main`
     - Main file: `src/dashboard/app.py`
     - Requirements: `streamlit-requirements.txt`
   - Click "Deploy!"

3. **Access Your App**:
   ```
   https://houssam-source-credit-risk-manager-app-xyz123.streamlit.app
   ```

### Docker Deployment

For containerized deployment, see `DEPLOYMENT_GUIDE.md`:

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access services
# API: http://localhost:8000
# Dashboard: http://localhost:8501
```

## 🔒 Security Features

- ✅ API Key authentication for protected endpoints
- ✅ CORS middleware with configurable origins
- ✅ Request size limits (DoS protection)
- ✅ Security headers (X-Frame-Options, X-Content-Type-Options, etc.)
- ✅ Model integrity verification via SHA256 hashes
- ✅ Input validation using Pydantic schemas
- ✅ Secure comparison for sensitive values

## 📈 Monitoring

The system includes built-in monitoring capabilities:

- **Inference Logging**: Records incoming prediction requests
- **Drift Detection**: Monitors data distribution changes
- **Rolling Window**: Maintains recent inference history
- **Automatic Pruning**: Keeps log size manageable

## 🛠️ Development

### Adding New Features

1. **New ML Model**:
   - Add training script in `src/models/`
   - Update `ModelManager` class in `server_model.py`
   - Retrain and save model to `src/models/outputs/`

2. **New Dashboard Page**:
   - Create page file in `src/dashboard/pages/`
   - Import and register in `app.py`

3. **New API Endpoint**:
   - Add route in `server_model.py`
   - Define request/response schemas
   - Update API documentation

### Running Tests

```bash
# Add your test files and run
pytest tests/
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- **Houssam** - [houssam-source](https://github.com/houssam-source)

## 🙏 Acknowledgments

- Home Credit Default Risk competition on Kaggle
- FastAPI and Streamlit communities
- scikit-learn and TensorFlow developers

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review API documentation at `/docs` endpoint

## 🗺️ Roadmap

- [ ] Real-time model retraining pipeline
- [ ] Enhanced drift detection alerts
- [ ] Additional ML models (XGBoost, LightGBM)
- [ ] SHAP integration for explainability
- [ ] User authentication for dashboard
- [ ] PostgreSQL database integration
- [ ] Automated CI/CD pipeline

---

<div align="center">

**Made with ❤️ by Houssam**

[Report Bug](https://github.com/houssam-source/Credit-Risk-manager/issues) · [Request Feature](https://github.com/houssam-source/Credit-Risk-manager/issues)

</div>
