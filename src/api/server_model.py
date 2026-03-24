from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Any, Dict, List
import pandas as pd
import numpy as np
import joblib
import os
from pathlib import Path
import logging
import sys
import hashlib
import asyncio
import csv

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
from datetime import datetime
from contextlib import asynccontextmanager
import secrets

def _model_to_dict(m: Any) -> Dict[str, Any]:
    """Pydantic v1/v2 compatibility for request models."""
    if hasattr(m, "model_dump"):
        return m.model_dump()
    return m.dict()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables
model_manager = None

# --- Runtime environment flags ---
API_ENV = os.getenv("API_ENV", "dev").strip().lower()  # dev | prod
IS_PROD = API_ENV in {"prod", "production"}
MAX_REQUEST_BYTES = int(os.getenv("MAX_REQUEST_BYTES", str(256 * 1024)))  # 256KB default

# --- Simple API-key protection (easy security win) ---
# If API_KEY is set, protected endpoints require `X-API-Key: <API_KEY>`.
# If API_KEY is NOT set, the API runs in "open" mode (local/dev friendly).
API_KEY = os.getenv("API_KEY", "").strip()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def require_api_key(api_key: str | None = Depends(api_key_header)) -> None:
    if not API_KEY:
        return
    if not api_key or not secrets.compare_digest(api_key, API_KEY):
        raise HTTPException(status_code=401, detail="Unauthorized")

#
# --- Inference logging for drift monitoring (rolling window) ---
#
# This creates a "current" dataset for drift detection by recording incoming
# inference features. Treat these logs as sensitive.
#
INFERENCE_LOG_PATH = Path(
    os.getenv(
        "INFERENCE_LOG_PATH",
        str((project_root / "data" / "monitoring" / "inference_window.csv").resolve()),
    )
)
INFERENCE_LOG_MAX_ROWS = int(os.getenv("INFERENCE_LOG_MAX_ROWS", "10000"))
INFERENCE_LOG_PRUNE_EVERY = int(os.getenv("INFERENCE_LOG_PRUNE_EVERY", "200"))
_inference_log_lock = asyncio.Lock()
_inference_log_write_count = 0

def _utc_now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def _append_rows_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = path.exists()
    fieldnames = list(rows[0].keys())
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)

def _prune_csv_tail(path: Path, max_rows: int) -> None:
    if not path.exists():
        return
    try:
        df = pd.read_csv(path)
        if len(df) <= max_rows:
            return
        df.tail(max_rows).to_csv(path, index=False)
    except Exception as e:
        # Never break predictions because monitoring failed
        logger.warning(f"Failed to prune inference log: {e}")

async def log_inference_rows(rows: list[dict]) -> None:
    global _inference_log_write_count
    if not rows:
        return
    async with _inference_log_lock:
        try:
            _append_rows_csv(INFERENCE_LOG_PATH, rows)
            _inference_log_write_count += 1
            if _inference_log_write_count % max(INFERENCE_LOG_PRUNE_EVERY, 1) == 0:
                _prune_csv_tail(INFERENCE_LOG_PATH, INFERENCE_LOG_MAX_ROWS)
        except Exception as e:
            logger.warning(f"Failed to write inference log: {e}")

def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def _verify_file(path: Path, expected_sha256: str | None = None) -> None:
    # Ensure the file is inside the expected models directory (prevents path tricks)
    resolved = path.resolve()
    models_root = (project_root / "src" / "models" / "outputs").resolve()
    if models_root not in resolved.parents:
        raise RuntimeError(f"Refusing to load file outside models directory: {resolved}")

    if expected_sha256:
        actual = _sha256_file(resolved)
        if not secrets.compare_digest(actual.lower(), expected_sha256.lower()):
            raise RuntimeError(f"SHA256 mismatch for {resolved.name}")

class ModelManager:
    """Manages loading, caching, and using ML models for predictions"""
    
    def __init__(self):
        # Use an absolute path so running from different CWDs works.
        self.models_dir = (project_root / "src" / "models" / "outputs").resolve()
        self.scaler_path = self.models_dir / "scaler.pkl"
        
        # Model storage
        self.models: Dict[str, object] = {}
        self.scaler = None
        self.is_loaded = False
        
        # Expected feature names from training (you'll need to update this)
        self.expected_features = [
            'AMT_INCOME_TOTAL', 'AMT_CREDIT', 'AMT_ANNUITY', 'AMT_GOODS_PRICE',
            'REGION_POPULATION_RELATIVE', 'DAYS_BIRTH', 'DAYS_EMPLOYED',
            'DAYS_REGISTRATION', 'DAYS_ID_PUBLISH', 'OWN_CAR_AGE'
            # Add all 489 features from your consolidated dataset
        ]
    
    async def load_models(self):
        """Load all trained models and scaler"""
        logger.info("Loading models...")
        
        try:
            # Load scaler
            if self.scaler_path.exists():
                _verify_file(self.scaler_path, os.getenv("SCALER_SHA256"))
                self.scaler = joblib.load(self.scaler_path)
                logger.info("Scaler loaded successfully")
            else:
                raise FileNotFoundError(f"Scaler not found at {self.scaler_path}")
            
            # Load traditional ML models
            model_files = {
                'random_forest': 'random_forest_model.pkl',
                'gradient_boosting': 'gradient_boosting_model.pkl'
            }
            
            for model_name, filename in model_files.items():
                model_path = self.models_dir / filename
                if model_path.exists():
                    expected = None
                    if model_name == "random_forest":
                        expected = os.getenv("RANDOM_FOREST_SHA256")
                    elif model_name == "gradient_boosting":
                        expected = os.getenv("GRADIENT_BOOSTING_SHA256")
                    _verify_file(model_path, expected)
                    self.models[model_name] = joblib.load(model_path)
                    logger.info(f"{model_name} loaded successfully")
                else:
                    logger.warning(f"{model_name} not found at {model_path}")
            
            # Load neural network model
            nn_path = self.models_dir / 'neural_network_model.h5'
            if nn_path.exists():
                try:
                    _verify_file(nn_path, os.getenv("NEURAL_NETWORK_SHA256"))
                    # Optional dependency: only required if you have the NN model.
                    from tensorflow.keras.models import load_model  # type: ignore

                    self.models['neural_network'] = load_model(nn_path)
                    logger.info("Neural network loaded successfully")
                except Exception as e:
                    logger.warning(f"Neural network model present but failed to load: {e}")
            else:
                logger.warning(f"Neural network not found at {nn_path}")
            
            self.is_loaded = True
            logger.info(f"Successfully loaded {len(self.models)} models")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise
    
    def is_ready(self) -> bool:
        """Check if models are loaded and ready"""
        return self.is_loaded and len(self.models) > 0 and self.scaler is not None
    
    def get_loaded_models_count(self) -> int:
        """Get number of loaded models"""
        return len(self.models)
    
    def get_model_info(self) -> List[Dict]:
        """Get information about all loaded models"""
        info = []
        for name, model in self.models.items():
            model_info = {
                "name": name,
                "type": type(model).__name__,
                "loaded": True
            }
            info.append(model_info)
        return info
    
    async def predict_single(self, df: pd.DataFrame) -> Dict:
        """Make prediction for single application"""
        # Preprocess features
        processed_df = await self._preprocess_features(df)
        
        # Get predictions from all models
        predictions = {}
        probabilities = {}
        
        for model_name, model in self.models.items():
            pred, prob = await self._predict_with_model(model, model_name, processed_df)
            predictions[model_name] = pred
            probabilities[model_name] = prob
        
        # Ensemble prediction (majority vote)
        ensemble_pred = self._ensemble_prediction(predictions)
        ensemble_prob = np.mean(list(probabilities.values()))
        
        # Determine consensus
        consensus = self._determine_consensus(predictions)
        
        # Identify top risk factors (simplified)
        risk_factors = self._identify_risk_factors(processed_df.iloc[0], probabilities)
        
        return {
            "prediction": int(ensemble_pred),
            "probability": float(ensemble_prob),
            "confidence": self._calculate_confidence(probabilities),
            "model_consensus": consensus,
            "individual_predictions": {
                name: {
                    "prediction": int(pred),
                    "probability": float(probabilities[name])
                }
                for name, pred in predictions.items()
            },
            "risk_factors": risk_factors,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _preprocess_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess features for prediction"""
        processed_df = df.copy()
        
        # Add missing features with default values
        for feature in self.expected_features:
            if feature not in processed_df.columns:
                processed_df[feature] = 0.0
        
        # Select only expected features
        processed_df = processed_df[self.expected_features]
        
        # Handle missing values
        processed_df = processed_df.fillna(0.0)
        
        # Scale features
        if self.scaler:
            scaled_features = self.scaler.transform(processed_df)
            processed_df = pd.DataFrame(scaled_features, columns=self.expected_features)
        
        return processed_df
    
    async def _predict_with_model(self, model, model_name: str, df: pd.DataFrame):
        """Make prediction with specific model"""
        try:
            if model_name == 'neural_network':
                probability = model.predict(df, verbose=0).flatten()[0]
                prediction = int(probability > 0.5)
            else:
                probability = model.predict_proba(df)[:, 1][0]
                prediction = model.predict(df)[0]
            
            return prediction, probability
        except Exception as e:
            logger.error(f"Error predicting with {model_name}: {e}")
            raise
    
    def _ensemble_prediction(self, predictions: Dict) -> int:
        """Combine predictions using majority voting"""
        preds = list(predictions.values())
        return int(sum(preds) > len(preds) / 2)
    
    def _determine_consensus(self, predictions: Dict) -> str:
        """Determine level of agreement between models"""
        unique_preds = set(predictions.values())
        if len(unique_preds) == 1:
            return "unanimous"
        elif len(unique_preds) == 2:
            counts = [list(predictions.values()).count(pred) for pred in unique_preds]
            if max(counts) >= 2:
                return "majority"
            else:
                return "disagreement"
        else:
            return "disagreement"
    
    def _identify_risk_factors(self, features: pd.Series, probabilities: Dict) -> List[str]:
        """Identify top contributing risk factors (simplified)"""
        risk_indicators = []
        
        if features.get('AMT_CREDIT', 0) > 1000000:
            risk_indicators.append("High credit amount")
        
        if features.get('DAYS_EMPLOYED', 0) < -3650:
            risk_indicators.append("Long period unemployed")
        
        avg_probability = np.mean(list(probabilities.values()))
        if avg_probability > 0.7:
            risk_indicators.append("High overall risk score")
        
        return risk_indicators[:3]
    
    def _calculate_confidence(self, probabilities: Dict) -> str:
        """Calculate prediction confidence level"""
        std_dev = np.std(list(probabilities.values()))
        
        if std_dev < 0.1:
            return "high"
        elif std_dev < 0.2:
            return "medium"
        else:
            return "low"

# Pydantic data schemas
class CreditApplication(BaseModel):
    """Schema for credit application data"""
    AMT_INCOME_TOTAL: float = Field(..., ge=0, description="Total income")
    AMT_CREDIT: float = Field(..., ge=0, description="Credit amount")
    AMT_ANNUITY: float = Field(..., ge=0, description="Annuity amount")
    AMT_GOODS_PRICE: float = Field(..., ge=0, description="Goods price")
    REGION_POPULATION_RELATIVE: float = Field(..., ge=0, description="Region population relative")
    DAYS_BIRTH: int = Field(..., description="Days since birth (negative)")
    DAYS_EMPLOYED: int = Field(..., description="Days employed (can be negative)")
    DAYS_REGISTRATION: float = Field(..., description="Days since registration")
    DAYS_ID_PUBLISH: int = Field(..., description="Days since ID publish")
    OWN_CAR_AGE: float = Field(default=0, ge=0, description="Car age in years")

class IndividualPrediction(BaseModel):
    """Schema for individual model prediction"""
    prediction: int = Field(..., description="Binary prediction (0 or 1)")
    probability: float = Field(..., ge=0, le=1, description="Probability of default")

class PredictionResponse(BaseModel):
    """Schema for prediction response"""
    prediction: int = Field(..., description="Ensemble prediction (0 or 1)")
    probability: float = Field(..., ge=0, le=1, description="Average probability of default")
    confidence: str = Field(..., description="Confidence level (high/medium/low)")
    model_consensus: str = Field(..., description="Model agreement level")
    individual_predictions: Dict[str, IndividualPrediction] = Field(
        ..., description="Predictions from individual models"
    )
    risk_factors: List[str] = Field(..., description="Top risk factors identified")
    timestamp: str = Field(..., description="Timestamp of prediction")

class BatchPredictionRequest(BaseModel):
    """Schema for batch prediction request"""
    applications: List[CreditApplication] = Field(
        ..., min_length=1, max_length=1000, description="List of credit applications"
    )

class ModelInfo(BaseModel):
    """Schema for model information"""
    name: str = Field(..., description="Model name")
    type: str = Field(..., description="Model type")
    loaded: bool = Field(..., description="Whether model is loaded")

class HealthCheck(BaseModel):
    """Schema for health check response"""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Current timestamp")
    models_loaded: int = Field(..., description="Number of loaded models")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup/shutdown"""
    global model_manager
    
    # Startup
    logger.info("Starting Credit Risk API Server...")
    
    model_manager = ModelManager()
    try:
        await model_manager.load_models()
        logger.info("Models loaded successfully")
    except Exception as e:
        # Don't crash the API on startup; endpoints will return 503 until models are available.
        logger.error(f"Failed to load models on startup (API will run in degraded mode): {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Credit Risk API Server...")

# Create FastAPI app
app = FastAPI(
    title="Credit Risk Management API",
    description="API for predicting credit default risk using machine learning models",
    version="1.0.0",
    lifespan=lifespan,
    # Reduce attack surface in production (Swagger/OpenAPI enumeration)
    docs_url=None if IS_PROD else "/docs",
    redoc_url=None if IS_PROD else "/redoc",
    openapi_url=None if IS_PROD else "/openapi.json",
)

@app.middleware("http")
async def security_headers_and_limits(request: Request, call_next):
    # Basic request size limit (DoS protection). Works for requests with Content-Length.
    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            if int(content_length) > MAX_REQUEST_BYTES:
                raise HTTPException(status_code=413, detail="Request entity too large")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid Content-Length header")

    response: Response = await call_next(request)

    # Basic security headers
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("Cache-Control", "no-store")
    return response

# Configure CORS with restricted, configurable origins
_allowed_origins_env = os.getenv("API_ALLOWED_ORIGINS")
if _allowed_origins_env:
    ALLOWED_ORIGINS = [
        origin.strip()
        for origin in _allowed_origins_env.split(",")
        if origin.strip()
    ]
else:
    # Safe defaults for local development; override in production via API_ALLOWED_ORIGINS
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    # Using API key header (not cookies) so credentials aren't needed.
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.get("/health", response_model=HealthCheck)
async def health_check(_: None = Depends(require_api_key)):
    """Health check endpoint"""
    if not model_manager or not model_manager.is_ready():
        raise HTTPException(status_code=503, detail="Models not loaded")

    if IS_PROD:
        # Reduce recon info in prod
        return HealthCheck(status="healthy", timestamp=datetime.now(), models_loaded=0)

    return HealthCheck(
        status="healthy",
        timestamp=datetime.now(),
        models_loaded=model_manager.get_loaded_models_count(),
    )

@app.get("/models/list", response_model=List[ModelInfo])
async def list_models(_: None = Depends(require_api_key)):
    """List all available models"""
    if not model_manager:
        raise HTTPException(status_code=503, detail="Model manager not initialized")
    
    return model_manager.get_model_info()

@app.post("/predict", response_model=PredictionResponse)
async def predict_credit_risk(application: CreditApplication, _: None = Depends(require_api_key)):
    """Predict credit risk for a single application"""
    if not model_manager or not model_manager.is_ready():
        raise HTTPException(status_code=503, detail="Models not available")
    
    try:
        app_dict = _model_to_dict(application)
        await log_inference_rows([{"timestamp": _utc_now_iso(), **app_dict}])
        df = pd.DataFrame([app_dict])
        result = await model_manager.predict_single(df)
        return PredictionResponse(**result)
    except Exception as e:
        # Log full error server-side, but return a generic message to the client
        logger.exception("Prediction error during /predict")
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while generating the prediction.",
        )

@app.post("/predict/batch", response_model=List[PredictionResponse])
async def batch_predict(batch_request: BatchPredictionRequest, _: None = Depends(require_api_key)):
    """Predict credit risk for multiple applications"""
    if not model_manager or not model_manager.is_ready():
        raise HTTPException(status_code=503, detail="Models not available")
    
    try:
        rows = [_model_to_dict(app) for app in batch_request.applications]
        await log_inference_rows([{"timestamp": _utc_now_iso(), **r} for r in rows])
        df = pd.DataFrame(rows)
        results = []
        for i in range(len(df)):
            single_result = await model_manager.predict_single(df.iloc[[i]])
            results.append(single_result)
        return [PredictionResponse(**result) for result in results]
    except Exception as e:
        # Log full error server-side, but return a generic message to the client
        logger.exception("Batch prediction error during /predict/batch")
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while generating batch predictions.",
        )

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Credit Risk Management API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "health_check": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    # Bind to localhost by default; make host/port configurable via environment
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)