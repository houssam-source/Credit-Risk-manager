import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, classification_report
from sklearn.model_selection import cross_val_score
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))


def evaluate_model_performance(model, X_test, y_test, model_name="Model"):
    """
    Comprehensive evaluation of model performance with detailed metrics and explanations.
    
    Args:
        model: Trained model object
        X_test: Test features
        y_test: True labels
        model_name: Name of the model for reporting
    
    Returns:
        Dictionary containing all evaluation metrics
    """
    print(f"\n{'='*60}")
    print(f"EVALUATING {model_name.upper()}")
    print(f"{'='*60}")
    
    # Make predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else None
    
    # Calculate metrics
    metrics = {}
    
    # 1. Accuracy - Overall correctness of the model
    # Formula: (TP + TN) / (TP + TN + FP + FN)
    # Interpretation: Percentage of correct predictions out of all predictions
    metrics['accuracy'] = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print("  Explanation: Proportion of correct predictions (both positive and negative cases)\n")
    
    # 2. Precision - Quality of positive predictions
    # Formula: TP / (TP + FP)
    # Interpretation: Of all positive predictions, how many were actually positive?
    metrics['precision'] = precision_score(y_test, y_pred)
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"  Explanation: Among all predicted defaults, {metrics['precision']*100:.2f}% were actual defaults\n")
    
    # 3. Recall (Sensitivity) - Coverage of actual positives
    # Formula: TP / (TP + FN)
    # Interpretation: Of all actual positive cases, how many were correctly identified?
    metrics['recall'] = recall_score(y_test, y_pred)
    print(f"Recall (Sensitivity): {metrics['recall']:.4f}")
    print(f"  Explanation: Among all actual defaults, {metrics['recall']*100:.2f}% were caught by the model\n")
    
    # 4. F1-Score - Harmonic mean of precision and recall
    # Formula: 2 * (precision * recall) / (precision + recall)
    # Interpretation: Balanced measure between precision and recall
    metrics['f1'] = f1_score(y_test, y_pred)
    print(f"F1-Score: {metrics['f1']:.4f}")
    print("  Explanation: Harmonic mean balancing precision and recall for overall performance\n")
    
    # 5. ROC-AUC - Area under the ROC curve
    # Interpretation: Probability that a randomly chosen positive instance is ranked higher 
    # than a randomly chosen negative instance
    if y_pred_proba is not None:
        metrics['roc_auc'] = roc_auc_score(y_test, y_pred_proba)
        print(f"ROC-AUC: {metrics['roc_auc']:.4f}")
        print("  Explanation: Ability to distinguish between classes (random=0.5, perfect=1.0)\n")
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    print("Confusion Matrix:")
    print(cm)
    print("  [[TN, FP], [FN, TP]] where TN=True Negatives, FP=False Positives, FN=False Negatives, TP=True Positives\n")
    
    # Detailed classification report
    print("Detailed Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['Non-Default', 'Default']))
    
    # Business-relevant metrics for credit risk
    print("\nBusiness Impact Metrics:")
    tn, fp, fn, tp = cm.ravel()
    
    # False Positive Rate - Percentage of non-defaulters incorrectly classified as defaulters
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    print(f"False Positive Rate: {fpr:.4f}")
    print(f"  Explanation: {fpr*100:.2f}% of non-defaulters would be incorrectly denied loans\n")
    
    # False Negative Rate - Percentage of defaulters incorrectly classified as non-defaulters
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0
    print(f"False Negative Rate: {fnr:.4f}")
    print(f"  Explanation: {fnr*100:.2f}% of defaulters would be incorrectly approved for loans\n")
    
    # Cost-sensitive analysis (hypothetical costs)
    cost_false_positive = fp * 1000  # Cost of denying a good customer
    cost_false_negative = fn * 10000  # Cost of approving a bad customer (higher penalty)
    total_cost = cost_false_positive + cost_false_negative
    print(f"Estimated Business Costs:")
    print(f"  Cost of False Positives: ${cost_false_positive:,} (denied good customers)")
    print(f"  Cost of False Negatives: ${cost_false_negative:,} (approved bad customers)")
    print(f"  Total Estimated Cost: ${total_cost:,}\n")
    
    return metrics


def plot_evaluation_metrics(model, X_test, y_test, model_name="Model"):
    """
    Create visualizations for model evaluation.
    """
    try:
        import matplotlib.pyplot as plt
        from sklearn.metrics import roc_curve, precision_recall_curve
        
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else None
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'Model Evaluation: {model_name}', fontsize=16)
        
        # 1. Confusion Matrix Heatmap
        cm = confusion_matrix(y_test, y_pred)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[0,0], 
                    xticklabels=['Non-Default', 'Default'], 
                    yticklabels=['Non-Default', 'Default'])
        axes[0,0].set_title('Confusion Matrix')
        axes[0,0].set_ylabel('True Label')
        axes[0,0].set_xlabel('Predicted Label')
        
        if y_pred_proba is not None:
            # 2. ROC Curve
            fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
            auc_score = roc_auc_score(y_test, y_pred_proba)
            axes[0,1].plot(fpr, tpr, label=f'ROC Curve (AUC = {auc_score:.4f})')
            axes[0,1].plot([0, 1], [0, 1], 'k--', label='Random Classifier')
            axes[0,1].set_xlabel('False Positive Rate')
            axes[0,1].set_ylabel('True Positive Rate')
            axes[0,1].set_title('ROC Curve')
            axes[0,1].legend()
            axes[0,1].grid(True)
            
            # 3. Precision-Recall Curve
            precision_vals, recall_vals, _ = precision_recall_curve(y_test, y_pred_proba)
            axes[1,0].plot(recall_vals, precision_vals, label='Precision-Recall Curve')
            axes[1,0].set_xlabel('Recall')
            axes[1,0].set_ylabel('Precision')
            axes[1,0].set_title('Precision-Recall Curve')
            axes[1,0].legend()
            axes[1,0].grid(True)
        
        # 4. Prediction Distribution
        axes[1,1].hist(y_pred_proba[y_test == 0], bins=50, alpha=0.5, label='Non-Default', density=True)
        axes[1,1].hist(y_pred_proba[y_test == 1], bins=50, alpha=0.5, label='Default', density=True)
        axes[1,1].set_xlabel('Predicted Probability')
        axes[1,1].set_ylabel('Density')
        axes[1,1].set_title('Distribution of Predicted Probabilities')
        axes[1,1].legend()
        axes[1,1].grid(True)
        
        plt.tight_layout()
        plt.show()
        
    except ImportError:
        print("Matplotlib not available for plotting")


def cross_validate_model(model, X, y, cv=5):
    """
    Perform cross-validation to assess model stability.
    
    Args:
        model: Model to evaluate
        X: Features
        y: Labels
        cv: Number of cross-validation folds
    
    Returns:
        Dictionary with cross-validation scores
    """
    print(f"\nPerforming {cv}-Fold Cross-Validation...")
    
    # Different scoring metrics
    scoring_metrics = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']
    cv_results = {}
    
    for metric in scoring_metrics:
        scores = cross_val_score(model, X, y, cv=cv, scoring=metric)
        cv_results[metric] = {
            'scores': scores,
            'mean': scores.mean(),
            'std': scores.std()
        }
        print(f"{metric.capitalize()}: {scores.mean():.4f} (+/- {scores.std() * 2:.4f})")
    
    return cv_results


def compare_models(models_dict, X_test, y_test):
    """
    Compare multiple models side by side.
    
    Args:
        models_dict: Dictionary with model_name: model_object pairs
        X_test: Test features
        y_test: True labels
    
    Returns:
        DataFrame with comparison of metrics
    """
    comparison_results = []
    
    for model_name, model in models_dict.items():
        print(f"\nEvaluating {model_name}...")
        metrics = evaluate_model_performance(model, X_test, y_test, model_name)
        
        # Add model name to metrics
        metrics['model_name'] = model_name
        comparison_results.append(metrics)
    
    # Create comparison DataFrame
    comparison_df = pd.DataFrame(comparison_results)
    comparison_df.set_index('model_name', inplace=True)
    
    print(f"\n{'='*60}")
    print(f"MODEL COMPARISON SUMMARY")
    print(f"{'='*60}")
    print(comparison_df.round(4))
    
    return comparison_df


def main():
    """
    Main function to demonstrate model evaluation.
    This would typically be called after models are trained.
    """
    # Example usage (would need to load models and test data)
    print("Model Evaluation Module")
    print("This module provides comprehensive evaluation of credit risk models")
    print("Include this in your model training pipeline to evaluate performance")
    
    # Example of how to use:
    # model = joblib.load('path_to_model')
    # X_test, y_test = load_test_data()
    # evaluate_model_performance(model, X_test, y_test, "Random Forest")
    
    # Or for multiple models:
    # models = {
    #     'Random Forest': rf_model,
    #     'Gradient Boosting': gb_model,
    #     'Neural Network': nn_model
    # }
    # compare_models(models, X_test, y_test)

if __name__ == "__main__":
    main()