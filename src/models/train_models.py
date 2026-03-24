"""
Credit Risk Model Training Script
Loads processed data, splits into train/validation sets (80%/20%), and trains models
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras import layers, models
import os
import joblib
from pathlib import Path
import sys

# Set random seed for reproducibility
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
tf.random.set_seed(RANDOM_SEED)

# Define paths
# Get the project root directory (two levels up from this file)
project_root = Path(__file__).parent.parent.parent

data_dir = project_root / 'home-credit-default-risk' / 'data'
processed_dir = data_dir / 'processed'
models_dir = Path(__file__).parent / 'outputs'
models_dir.mkdir(exist_ok=True)

def load_processed_data():
    """Load the consolidated processed dataset"""
    print("Loading processed data...")
    
    consolidated_file = processed_dir / 'consolidated_features.csv'
    
    if not consolidated_file.exists():
        raise FileNotFoundError(f"Consolidated features file not found: {consolidated_file}")
    
    df = pd.read_csv(consolidated_file)
    print(f"Loaded dataset with shape: {df.shape}")
    
    return df

def prepare_features_and_target(df):
    """Separate features and target variable"""
    print("Preparing features and target...")
    
    # Assuming 'TARGET' is the target column (1 = default, 0 = no default)
    if 'TARGET' not in df.columns:
        raise ValueError("TARGET column not found in dataset")
    
    # Separate features and target
    y = df['TARGET']
    X = df.drop(columns=['TARGET'])
    
    print(f"Features shape: {X.shape}")
    print(f"Target shape: {y.shape}")
    print(f"Target distribution:")
    print(y.value_counts())
    print(f"Default rate: {y.mean():.4f}")
    
    return X, y

def split_data(X, y, test_size=0.2):
    """
    Split data into train and test sets
    Uses 80% for training, 20% for validation
    """
    print("Splitting data...")
    
    # Split data: 80% for training, 20% for validation
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=test_size, random_state=RANDOM_SEED, stratify=y
    )
    
    print(f"Training set: {X_train.shape[0]} samples ({X_train.shape[0]/len(X)*100:.1f}%)")
    print(f"Validation set: {X_val.shape[0]} samples ({X_val.shape[0]/len(X)*100:.1f}%)")
    
    return X_train, X_val, y_train, y_val

def scale_features(X_train, X_val):
    """Scale numerical features using StandardScaler"""
    print("Scaling features...")
    
    scaler = StandardScaler()
    
    # Fit on training data and transform validation set
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    
    # Convert back to DataFrames with original column names
    X_train_scaled = pd.DataFrame(X_train_scaled, columns=X_train.columns, index=X_train.index)
    X_val_scaled = pd.DataFrame(X_val_scaled, columns=X_val.columns, index=X_val.index)
    
    print("Features scaled successfully")
    
    return X_train_scaled, X_val_scaled, scaler

def train_random_forest(X_train, y_train, X_val, y_val):
    """Train Random Forest classifier"""
    print("Training Random Forest...")
    
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=RANDOM_SEED,
        n_jobs=-1
    )
    
    rf_model.fit(X_train, y_train)
    
    # Predictions
    y_pred_train = rf_model.predict(X_train)
    y_pred_val = rf_model.predict(X_val)
    y_pred_proba_val = rf_model.predict_proba(X_val)[:, 1]
    
    # Metrics
    train_accuracy = accuracy_score(y_train, y_pred_train)
    val_accuracy = accuracy_score(y_val, y_pred_val)
    val_precision = precision_score(y_val, y_pred_val)
    val_recall = recall_score(y_val, y_pred_val)
    val_f1 = f1_score(y_val, y_pred_val)
    val_auc = roc_auc_score(y_val, y_pred_proba_val)
    
    print(f"Random Forest Results:")
    print(f"  Training Accuracy: {train_accuracy:.4f}")
    print(f"  Validation Accuracy: {val_accuracy:.4f}")
    print(f"  Validation Precision: {val_precision:.4f}")
    print(f"  Validation Recall: {val_recall:.4f}")
    print(f"  Validation F1-Score: {val_f1:.4f}")
    print(f"  Validation AUC: {val_auc:.4f}")
    
    return rf_model, {
        'train_accuracy': train_accuracy,
        'val_accuracy': val_accuracy,
        'val_precision': val_precision,
        'val_recall': val_recall,
        'val_f1': val_f1,
        'val_auc': val_auc
    }

def train_gradient_boosting(X_train, y_train, X_val, y_val):
    """Train Gradient Boosting classifier"""
    print("Training Gradient Boosting...")
    
    gb_model = GradientBoostingClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        random_state=RANDOM_SEED
    )
    
    gb_model.fit(X_train, y_train)
    
    # Predictions
    y_pred_train = gb_model.predict(X_train)
    y_pred_val = gb_model.predict(X_val)
    y_pred_proba_val = gb_model.predict_proba(X_val)[:, 1]
    
    # Metrics
    train_accuracy = accuracy_score(y_train, y_pred_train)
    val_accuracy = accuracy_score(y_val, y_pred_val)
    val_precision = precision_score(y_val, y_pred_val)
    val_recall = recall_score(y_val, y_pred_val)
    val_f1 = f1_score(y_val, y_pred_val)
    val_auc = roc_auc_score(y_val, y_pred_proba_val)
    
    print(f"Gradient Boosting Results:")
    print(f"  Training Accuracy: {train_accuracy:.4f}")
    print(f"  Validation Accuracy: {val_accuracy:.4f}")
    print(f"  Validation Precision: {val_precision:.4f}")
    print(f"  Validation Recall: {val_recall:.4f}")
    print(f"  Validation F1-Score: {val_f1:.4f}")
    print(f"  Validation AUC: {val_auc:.4f}")
    
    return gb_model, {
        'train_accuracy': train_accuracy,
        'val_accuracy': val_accuracy,
        'val_precision': val_precision,
        'val_recall': val_recall,
        'val_f1': val_f1,
        'val_auc': val_auc
    }

def create_neural_network(input_dim):
    """Create and compile neural network model"""
    model = models.Sequential([
        layers.Dense(128, activation='relu', input_shape=(input_dim,)),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        layers.Dense(64, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        layers.Dense(32, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.2),
        layers.Dense(1, activation='sigmoid')
    ])
    
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy', 'precision', 'recall']
    )
    
    return model

def train_neural_network(X_train, y_train, X_val, y_val):
    """Train Neural Network classifier"""
    print("Training Neural Network...")
    
    # Create model
    nn_model = create_neural_network(X_train.shape[1])
    
    # Callbacks
    early_stopping = tf.keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True
    )
    
    reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.2,
        patience=5,
        min_lr=0.0001
    )
    
    # Train model
    history = nn_model.fit(
        X_train, y_train,
        epochs=50,
        batch_size=1024,
        validation_data=(X_val, y_val),
        callbacks=[early_stopping, reduce_lr],
        verbose=1
    )
    
    # Predictions
    y_pred_train = (nn_model.predict(X_train) > 0.5).astype(int)
    y_pred_val = (nn_model.predict(X_val) > 0.5).astype(int)
    y_pred_proba_val = nn_model.predict(X_val)
    
    # Metrics
    train_accuracy = accuracy_score(y_train, y_pred_train)
    val_accuracy = accuracy_score(y_val, y_pred_val)
    val_precision = precision_score(y_val, y_pred_val)
    val_recall = recall_score(y_val, y_pred_val)
    val_f1 = f1_score(y_val, y_pred_val)
    val_auc = roc_auc_score(y_val, y_pred_proba_val)
    
    print(f"Neural Network Results:")
    print(f"  Training Accuracy: {train_accuracy:.4f}")
    print(f"  Validation Accuracy: {val_accuracy:.4f}")
    print(f"  Validation Precision: {val_precision:.4f}")
    print(f"  Validation Recall: {val_recall:.4f}")
    print(f"  Validation F1-Score: {val_f1:.4f}")
    print(f"  Validation AUC: {val_auc:.4f}")
    
    return nn_model, {
        'train_accuracy': train_accuracy,
        'val_accuracy': val_accuracy,
        'val_precision': val_precision,
        'val_recall': val_recall,
        'val_f1': val_f1,
        'val_auc': val_auc,
        'history': history
    }

def evaluate_model(model, model_type, X_val, y_val):
    """Evaluate model on validation set"""
    print(f"\nEvaluation on Validation Set ({model_type}):")
    
    if model_type == 'neural_network':
        y_pred = (model.predict(X_val) > 0.5).astype(int)
        y_pred_proba = model.predict(X_val)
    else:
        y_pred = model.predict(X_val)
        y_pred_proba = model.predict_proba(X_val)[:, 1]
    
    accuracy = accuracy_score(y_val, y_pred)
    precision = precision_score(y_val, y_pred)
    recall = recall_score(y_val, y_pred)
    f1 = f1_score(y_val, y_pred)
    auc = roc_auc_score(y_val, y_pred_proba)
    
    print(f"  Validation Accuracy: {accuracy:.4f}")
    print(f"  Validation Precision: {precision:.4f}")
    print(f"  Validation Recall: {recall:.4f}")
    print(f"  Validation F1-Score: {f1:.4f}")
    print(f"  Validation AUC: {auc:.4f}")
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'auc': auc
    }

def save_model_and_results(model, model_type, results, scaler=None):
    """Save trained model and results"""
    print(f"Saving {model_type} model and results...")
    
    # Save model
    if model_type == 'neural_network':
        model_path = models_dir / f'{model_type}_model.h5'
        model.save(model_path)
    else:
        model_path = models_dir / f'{model_type}_model.pkl'
        joblib.dump(model, model_path)
    
    # Save scaler if provided
    if scaler is not None:
        scaler_path = models_dir / 'scaler.pkl'
        joblib.dump(scaler, scaler_path)
    
    # Save results
    results_path = models_dir / f'{model_type}_results.txt'
    with open(results_path, 'w') as f:
        f.write(f"=== {model_type.upper()} MODEL RESULTS ===\n\n")
        for key, value in results.items():
            if key != 'history':
                f.write(f"{key}: {value:.4f}\n")
    
    print(f"Model saved to: {model_path}")
    if scaler is not None:
        print(f"Scaler saved to: {scaler_path}")
    print(f"Results saved to: {results_path}")

def main():
    """Main training pipeline"""
    print("=" * 60)
    print("CREDIT RISK MODEL TRAINING PIPELINE")
    print("=" * 60)
    
    try:
        # Load data
        df = load_processed_data()
        
        # Prepare features and target
        X, y = prepare_features_and_target(df)
        
        # Split data (80% train, 20% validation)
        X_train, X_val, y_train, y_val = split_data(X, y)
        
        # Scale features
        X_train_scaled, X_val_scaled, scaler = scale_features(X_train, X_val)
        
        # Train models
        print("\n" + "=" * 40)
        print("TRAINING MODELS")
        print("=" * 40)
        
        # Random Forest
        rf_model, rf_results = train_random_forest(X_train_scaled, y_train, X_val_scaled, y_val)
        save_model_and_results(rf_model, 'random_forest', rf_results, scaler)
        
        # Gradient Boosting
        gb_model, gb_results = train_gradient_boosting(X_train_scaled, y_train, X_val_scaled, y_val)
        save_model_and_results(gb_model, 'gradient_boosting', gb_results, scaler)
        
        # Neural Network
        nn_model, nn_results = train_neural_network(X_train_scaled, y_train, X_val_scaled, y_val)
        save_model_and_results(nn_model, 'neural_network', nn_results, scaler)
        
        # Evaluation on validation set
        print("\n" + "=" * 40)
        print("VALIDATION SET EVALUATION")
        print("=" * 40)
        
        evaluate_model(rf_model, 'Random Forest', X_val_scaled, y_val)
        evaluate_model(gb_model, 'Gradient Boosting', X_val_scaled, y_val)
        evaluate_model(nn_model, 'Neural Network', X_val_scaled, y_val)
        
        print("\n" + "=" * 60)
        print("TRAINING COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"Models and results saved to: {models_dir}")
        
    except Exception as e:
        print(f"Error during training: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()