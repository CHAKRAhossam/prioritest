#!/usr/bin/env python3
"""
Standalone script to generate detailed confusion matrix analysis for PRIORITEST models.
Focuses on comprehensive model performance metrics and analysis.

Features:
- Detailed confusion matrix with comprehensive metrics
- Model information extraction (type, hyperparameters)
- Support for multiple models with comparison
- Per-class detailed analysis
- Advanced metrics: Specificity, Sensitivity, ROC-AUC, etc.

Usage:
    python generate_confusion_matrix.py
    python generate_confusion_matrix.py --model-path /path/to/model.pkl --data-path /path/to/test.csv
    python generate_confusion_matrix.py --all-models  # Analyze all models in model directory
"""
import argparse
import sys
import os
import glob
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from confusion_matrix_analysis import (
    load_model_and_data,
    create_confusion_matrix_visualization,
    create_metrics_comparison_plot
)
import joblib
import numpy as np
from sklearn.metrics import (
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    matthews_corrcoef,
    cohen_kappa_score
)


def extract_model_info(model):
    """Extract detailed information about the model."""
    model_info = {
        'model_type': str(type(model).__name__),
        'model_module': str(type(model).__module__),
        'hyperparameters': {},
        'n_features': None,
        'n_classes': None
    }
    
    # Extract hyperparameters
    if hasattr(model, 'get_params'):
        try:
            params = model.get_params()
            # Filter out non-serializable parameters
            model_info['hyperparameters'] = {
                k: str(v) if not isinstance(v, (int, float, str, bool, type(None))) else v
                for k, v in params.items()
            }
        except:
            pass
    
    # Extract feature and class info
    if hasattr(model, 'n_features_in_'):
        model_info['n_features'] = int(model.n_features_in_)
    if hasattr(model, 'n_classes_'):
        model_info['n_classes'] = int(model.n_classes_)
    elif hasattr(model, 'classes_'):
        model_info['n_classes'] = len(model.classes_)
        model_info['classes'] = [int(c) for c in model.classes_]
    
    return model_info


def calculate_comprehensive_metrics(y_true, y_pred, y_pred_proba=None):
    """Calculate comprehensive classification metrics."""
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    total = cm.sum()
    
    # Basic metrics
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average='binary', zero_division=0)
    recall = recall_score(y_true, y_pred, average='binary', zero_division=0)
    f1 = f1_score(y_true, y_pred, average='binary', zero_division=0)
    
    # Advanced metrics
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0  # True Negative Rate
    sensitivity = recall  # True Positive Rate (same as recall)
    false_positive_rate = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    false_negative_rate = fn / (fn + tp) if (fn + tp) > 0 else 0.0
    
    # Additional metrics
    matthews_corr = matthews_corrcoef(y_true, y_pred)
    cohen_kappa = cohen_kappa_score(y_true, y_pred)
    
    # ROC-AUC if probabilities available
    roc_auc = None
    if y_pred_proba is not None:
        try:
            if len(y_pred_proba.shape) > 1 and y_pred_proba.shape[1] > 1:
                roc_auc = roc_auc_score(y_true, y_pred_proba[:, 1])
            else:
                roc_auc = roc_auc_score(y_true, y_pred_proba)
        except:
            pass
    
    # Per-class metrics
    precision_per_class = precision_score(y_true, y_pred, average=None, zero_division=0)
    recall_per_class = recall_score(y_true, y_pred, average=None, zero_division=0)
    f1_per_class = f1_score(y_true, y_pred, average=None, zero_division=0)
    
    metrics = {
        # Confusion matrix components
        'true_negative': int(tn),
        'false_positive': int(fp),
        'false_negative': int(fn),
        'true_positive': int(tp),
        'total_samples': int(total),
        
        # Overall metrics
        'accuracy': float(accuracy),
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(f1),
        
        # Advanced metrics
        'specificity': float(specificity),  # True Negative Rate
        'sensitivity': float(sensitivity),  # True Positive Rate
        'false_positive_rate': float(false_positive_rate),
        'false_negative_rate': float(false_negative_rate),
        'matthews_correlation_coefficient': float(matthews_corr),
        'cohen_kappa': float(cohen_kappa),
        
        # Per-class metrics
        'precision_per_class': [float(p) for p in precision_per_class],
        'recall_per_class': [float(r) for r in recall_per_class],
        'f1_per_class': [float(f) for f in f1_per_class],
        
        # Confusion matrix
        'confusion_matrix': cm.tolist(),
    }
    
    if roc_auc is not None:
        metrics['roc_auc'] = float(roc_auc)
    
    return metrics


def print_detailed_model_analysis(model_info, metrics, model_name):
    """Print comprehensive model analysis."""
    print("\n" + "="*80)
    print(f"DETAILED MODEL ANALYSIS - {model_name}")
    print("="*80)
    
    # Model Information
    print("\n[MODEL INFORMATION]")
    print(f"  Model Type:        {model_info['model_type']}")
    print(f"  Model Module:      {model_info['model_module']}")
    if model_info['n_features']:
        print(f"  Number of Features: {model_info['n_features']}")
    if model_info['n_classes']:
        print(f"  Number of Classes:  {model_info['n_classes']}")
    if 'classes' in model_info:
        print(f"  Classes:            {model_info['classes']}")
    
    if model_info['hyperparameters']:
        print("\n  Hyperparameters:")
        for key, value in sorted(model_info['hyperparameters'].items())[:10]:  # Show first 10
            print(f"    {key}: {value}")
        if len(model_info['hyperparameters']) > 10:
            print(f"    ... and {len(model_info['hyperparameters']) - 10} more")
    
    # Confusion Matrix Details
    print("\n[CONFUSION MATRIX DETAILS]")
    cm = np.array(metrics['confusion_matrix'])
    tn, fp, fn, tp = metrics['true_negative'], metrics['false_positive'], \
                     metrics['false_negative'], metrics['true_positive']
    
    print(f"\n  Confusion Matrix (Counts):")
    print(f"                    Predicted")
    print(f"                  No Risk    Risk")
    print(f"  True No Risk      {tn:6d}    {fp:6d}")
    print(f"       Risk         {fn:6d}    {tp:6d}")
    
    total = metrics['total_samples']
    print(f"\n  Confusion Matrix (Percentages):")
    print(f"                    Predicted")
    print(f"                  No Risk    Risk")
    print(f"  True No Risk      {tn/total*100:5.1f}%    {fp/total*100:5.1f}%")
    print(f"       Risk         {fn/total*100:5.1f}%    {tp/total*100:5.1f}%")
    
    # Performance Metrics
    print("\n[PERFORMANCE METRICS]")
    print(f"\n  Overall Metrics:")
    print(f"    Accuracy:  {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")
    print(f"    Precision: {metrics['precision']:.4f} ({metrics['precision']*100:.2f}%)")
    print(f"    Recall:    {metrics['recall']:.4f} ({metrics['recall']*100:.2f}%)")
    print(f"    F1 Score:  {metrics['f1_score']:.4f} ({metrics['f1_score']*100:.2f}%)")
    
    print(f"\n  Advanced Metrics:")
    print(f"    Specificity (TNR):     {metrics['specificity']:.4f} ({metrics['specificity']*100:.2f}%)")
    print(f"    Sensitivity (TPR):     {metrics['sensitivity']:.4f} ({metrics['sensitivity']*100:.2f}%)")
    print(f"    False Positive Rate:   {metrics['false_positive_rate']:.4f} ({metrics['false_positive_rate']*100:.2f}%)")
    print(f"    False Negative Rate:   {metrics['false_negative_rate']:.4f} ({metrics['false_negative_rate']*100:.2f}%)")
    print(f"    Matthews Correlation:  {metrics['matthews_correlation_coefficient']:.4f}")
    print(f"    Cohen's Kappa:         {metrics['cohen_kappa']:.4f}")
    if 'roc_auc' in metrics:
        print(f"    ROC-AUC Score:        {metrics['roc_auc']:.4f}")
    
    # Per-Class Metrics
    print(f"\n  Per-Class Metrics:")
    class_names = ['No Risk (0)', 'Risk (1)']
    for i, class_name in enumerate(class_names):
        if i < len(metrics['precision_per_class']):
            print(f"\n    {class_name}:")
            print(f"      Precision: {metrics['precision_per_class'][i]:.4f}")
            print(f"      Recall:    {metrics['recall_per_class'][i]:.4f}")
            print(f"      F1 Score:  {metrics['f1_per_class'][i]:.4f}")
    
    # Interpretation
    print("\n[INTERPRETATION]")
    print(f"  - Correct Predictions: {tn + tp} ({((tn + tp)/total)*100:.1f}%)")
    print(f"  - Incorrect Predictions: {fp + fn} ({((fp + fn)/total)*100:.1f}%)")
    if fp > fn:
        print(f"  - Model tends to over-predict Risk (more False Positives)")
    elif fn > fp:
        print(f"  - Model tends to under-predict Risk (more False Negatives)")
    else:
        print(f"  - Model has balanced error distribution")
    
    print("="*80)


def analyze_model(model_path, data_path, output_dir, model_name=None):
    """Analyze a single model and generate detailed confusion matrix."""
    # Load model and data
    model, X_test, y_test = load_model_and_data(model_path, data_path)
    
    # Extract model information
    model_info = extract_model_info(model)
    
    # Determine model name if not provided
    if model_name is None:
        model_type = model_info['model_type']
        if 'XGB' in model_type:
            model_name = f"PRIORITEST XGBoost Classifier"
        elif 'LGBM' in model_type or 'LightGBM' in model_type:
            model_name = f"PRIORITEST LightGBM Classifier"
        else:
            model_name = f"PRIORITEST {model_type} Classifier"
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Get prediction probabilities if available
    y_pred_proba = None
    if hasattr(model, 'predict_proba'):
        try:
            y_pred_proba = model.predict_proba(X_test)
        except:
            pass
    
    # Calculate comprehensive metrics
    metrics = calculate_comprehensive_metrics(y_test, y_pred, y_pred_proba)
    
    # Add model info to metrics
    metrics['model_info'] = model_info
    metrics['model_name'] = model_name
    
    # Create visualization
    create_confusion_matrix_visualization(
        y_test, 
        y_pred, 
        model_name=model_name,
        save_path=os.path.join(output_dir, f"confusion_matrix_{Path(model_path).stem}.png")
    )
    
    # Print detailed analysis
    print_detailed_model_analysis(model_info, metrics, model_name)
    
    return metrics, model_name


def main():
    parser = argparse.ArgumentParser(
        description='Generate detailed confusion matrix analysis for PRIORITEST ML models',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze default model
  python generate_confusion_matrix.py
  
  # Analyze specific model
  python generate_confusion_matrix.py --model-path /path/to/model.pkl
  
  # Analyze all models in model directory
  python generate_confusion_matrix.py --all-models
  
  # Custom paths
  python generate_confusion_matrix.py --model-path model.pkl --data-path test.csv --output-dir output/
        """
    )
    parser.add_argument(
        '--model-path',
        type=str,
        default=None,
        help='Path to trained model (.pkl file). If not specified, uses default model.pkl'
    )
    parser.add_argument(
        '--data-path',
        type=str,
        default=None,
        help='Path to test data CSV file'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default=None,
        help='Output directory for generated files'
    )
    parser.add_argument(
        '--model-name',
        type=str,
        default=None,
        help='Name of the model for visualization (auto-detected if not specified)'
    )
    parser.add_argument(
        '--all-models',
        action='store_true',
        help='Analyze all .pkl model files in the model directory'
    )
    
    args = parser.parse_args()
    
    # Set default paths
    model_dir = os.environ.get("MODEL_PATH", "/app/models")
    if args.data_path is None:
        data_path = os.path.join(
            os.environ.get("DATA_PATH", "/app/data"),
            "processed",
            "test.csv"
        )
    else:
        data_path = args.data_path
    
    if args.output_dir is None:
        output_dir = os.environ.get("OUTPUT_PATH", "/app/output")
    else:
        output_dir = args.output_dir
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if test data exists
    if not os.path.exists(data_path):
        print(f"ERROR: Test data not found at {data_path}")
        print("Please run S4 pipeline first or specify --data-path")
        return 1
    
    print("="*80)
    print("PRIORITEST - Detailed Confusion Matrix Analysis for Models")
    print("="*80)
    
    # Determine which models to analyze
    models_to_analyze = []
    
    if args.all_models:
        # Find all .pkl files in model directory (excluding feature_names.pkl)
        model_files = glob.glob(os.path.join(model_dir, "*.pkl"))
        model_files = [f for f in model_files if not f.endswith("feature_names.pkl")]
        if not model_files:
            print(f"ERROR: No model files found in {model_dir}")
            return 1
        models_to_analyze = [(f, None) for f in model_files]
    else:
        # Single model
        if args.model_path is None:
            model_path = os.path.join(model_dir, "model.pkl")
        else:
            model_path = args.model_path
        
        if not os.path.exists(model_path):
            print(f"ERROR: Model not found at {model_path}")
            print("Please train the model first or specify --model-path")
            return 1
        
        models_to_analyze = [(model_path, args.model_name)]
    
    # Analyze each model
    all_metrics = {}
    
    for i, (model_path, model_name) in enumerate(models_to_analyze, 1):
        print(f"\n{'='*80}")
        print(f"Analyzing Model {i}/{len(models_to_analyze)}: {Path(model_path).name}")
        print(f"{'='*80}")
        
        try:
            metrics, final_model_name = analyze_model(
                model_path, 
                data_path, 
                output_dir, 
                model_name
            )
            
            # Save individual metrics
            model_stem = Path(model_path).stem
            metrics_path = os.path.join(output_dir, f"confusion_matrix_metrics_{model_stem}.json")
            with open(metrics_path, 'w') as f:
                json.dump(metrics, f, indent=2)
            print(f"\n[OK] Metrics saved to: {metrics_path}")
            
            all_metrics[final_model_name] = metrics
            
        except Exception as e:
            print(f"\n[ERROR] Analyzing {model_path}: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    # If multiple models, create comparison
    if len(all_metrics) > 1:
        print("\n" + "="*80)
        print("MODEL COMPARISON")
        print("="*80)
        
        # Create comparison plot
        comparison_path = os.path.join(output_dir, "model_comparison.png")
        create_metrics_comparison_plot(all_metrics, save_path=comparison_path)
        print(f"\n[OK] Model comparison saved to: {comparison_path}")
        
        # Print comparison table
        print("\n[METRICS COMPARISON TABLE]")
        print(f"\n{'Model':<30} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'F1 Score':<12}")
        print("-" * 80)
        for model_name, metrics in all_metrics.items():
            print(f"{model_name[:28]:<30} {metrics['accuracy']:<12.4f} "
                  f"{metrics['precision']:<12.4f} {metrics['recall']:<12.4f} "
                  f"{metrics['f1_score']:<12.4f}")
        
        # Save comparison metrics
        comparison_metrics_path = os.path.join(output_dir, "model_comparison_metrics.json")
        with open(comparison_metrics_path, 'w') as f:
            json.dump(all_metrics, f, indent=2)
        print(f"\n[OK] Comparison metrics saved to: {comparison_metrics_path}")
    
    print("\n" + "="*80)
    print("[OK] Analysis complete! Files saved to:", output_dir)
    print("="*80)
    print("\nGenerated files:")
    for model_name in all_metrics.keys():
        model_stem = Path(model_name).stem if '/' in model_name else model_name.replace(' ', '_')
        print(f"  - confusion_matrix_{model_stem}.png (visualization)")
        print(f"  - confusion_matrix_metrics_{model_stem}.json (detailed metrics)")
    if len(all_metrics) > 1:
        print(f"  - model_comparison.png (comparison visualization)")
        print(f"  - model_comparison_metrics.json (comparison data)")
    print("="*80)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

