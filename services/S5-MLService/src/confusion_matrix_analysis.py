"""
Generate detailed confusion matrix analysis for PRIORITEST ML models.
Creates professional visualizations suitable for reports.
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    confusion_matrix, 
    classification_report,
    accuracy_score, 
    precision_score, 
    recall_score, 
    f1_score,
    roc_auc_score
)
import joblib
from pathlib import Path
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set style for professional plots
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


def load_model_and_data(model_path: str, test_data_path: str):
    """Load trained model and test data."""
    logger.info(f"Loading model from {model_path}")
    model = joblib.load(model_path)
    
    logger.info(f"Loading test data from {test_data_path}")
    test_df = pd.read_csv(test_data_path)
    
    # Prepare features (same logic as train_model.py)
    cols_to_drop = []
    for col in test_df.columns:
        if test_df[col].dtype == 'object':
            cols_to_drop.append(col)
        elif col in ['commit_sha', 'repository_id', 'file_path', 'commit_date', 
                     'test_class', 'class_name', 'repository', 'test_name',
                     'commit_id', 'id']:
            cols_to_drop.append(col)
    
    test_df = test_df.drop(columns=[c for c in cols_to_drop if c in test_df.columns], errors='ignore')
    
    # Get target
    if 'target' in test_df.columns:
        X_test = test_df.drop(columns=['target'])
        y_test = test_df['target']
    elif 'failed' in test_df.columns:
        X_test = test_df.drop(columns=['failed'])
        y_test = test_df['failed']
    else:
        X_test = test_df.iloc[:, :-1]
        y_test = test_df.iloc[:, -1]
    
    # Ensure numeric only
    X_test = X_test.select_dtypes(include=[np.number])
    
    logger.info(f"Test data shape: {X_test.shape}, Target distribution: {y_test.value_counts().to_dict()}")
    
    return model, X_test, y_test


def create_confusion_matrix_visualization(
    y_true, 
    y_pred, 
    model_name: str = "PRIORITEST ML Model",
    save_path: str = None,
    figsize: tuple = (14, 6)
):
    """
    Create a detailed confusion matrix visualization similar to the examples.
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        model_name: Name of the model for title
        save_path: Path to save the figure
        figsize: Figure size (width, height)
    """
    # Calculate confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    
    # Calculate metrics
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average='binary', zero_division=0)
    recall = recall_score(y_true, y_pred, average='binary', zero_division=0)
    f1 = f1_score(y_true, y_pred, average='binary', zero_division=0)
    
    # Calculate advanced metrics
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    total = cm.sum()
    
    # Calculate percentages for normalized matrix
    cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    cm_normalized = np.nan_to_num(cm_normalized) * 100  # Convert to percentage
    
    # Create figure with subplots - larger to accommodate metrics
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    
    # Labels for binary classification
    labels = ['No Risk (0)', 'Risk (1)']
    
    # Plot 1: Confusion Matrix with Counts (similar to examples)
    sns.heatmap(
        cm, 
        annot=True, 
        fmt='d', 
        cmap='RdYlGn_r',  # Red-Yellow-Green reversed (red for high, green for low)
        xticklabels=labels,
        yticklabels=labels,
        ax=axes[0],
        cbar_kws={'label': 'Number of Classes'},
        linewidths=0.5,
        linecolor='gray'
    )
    axes[0].set_title(
        f'Confusion Matrix - {model_name}\n(0=No Risk, 1=Risk)', 
        fontsize=14, 
        fontweight='bold',
        pad=20
    )
    axes[0].set_ylabel('True Label', fontsize=12, fontweight='bold')
    axes[0].set_xlabel('Predicted Label', fontsize=12, fontweight='bold')
    
    # Add detailed annotations below the matrix with metrics
    axes[0].text(0.5, -0.12, f'True Negative (TN): {tn} | False Positive (FP): {fp}', 
                 ha='center', transform=axes[0].transAxes, fontsize=9, 
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    axes[0].text(0.5, -0.20, f'False Negative (FN): {fn} | True Positive (TP): {tp}', 
                 ha='center', transform=axes[0].transAxes, fontsize=9,
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    # Add key metrics
    metrics_text = (f'Accuracy: {accuracy:.3f} | Precision: {precision:.3f} | '
                   f'Recall: {recall:.3f} | F1: {f1:.3f} | Specificity: {specificity:.3f}')
    axes[0].text(0.5, -0.30, metrics_text,
                 ha='center', transform=axes[0].transAxes, fontsize=9,
                 bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.6))
    
    # Plot 2: Normalized Confusion Matrix (Percentages)
    sns.heatmap(
        cm_normalized,
        annot=True,
        fmt='.1f',
        cmap='RdYlGn_r',
        xticklabels=labels,
        yticklabels=labels,
        ax=axes[1],
        cbar_kws={'label': 'Percentage (%)'},
        linewidths=0.5,
        linecolor='gray'
    )
    axes[1].set_title(
        f'Normalized Confusion Matrix - {model_name}\n(Percentage Distribution)', 
        fontsize=14, 
        fontweight='bold',
        pad=20
    )
    axes[1].set_ylabel('True Label', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('Predicted Label', fontsize=12, fontweight='bold')
    
    # Add percentage annotations
    axes[1].text(0.5, -0.12, f'TN: {tn/total*100:.1f}% | FP: {fp/total*100:.1f}%', 
                 ha='center', transform=axes[1].transAxes, fontsize=9,
                 bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
    axes[1].text(0.5, -0.20, f'FN: {fn/total*100:.1f}% | TP: {tp/total*100:.1f}%', 
                 ha='center', transform=axes[1].transAxes, fontsize=9,
                 bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
    # Add error rates
    error_rate = (fp + fn) / total * 100
    axes[1].text(0.5, -0.30, f'Error Rate: {error_rate:.1f}% | Correct: {(tn+tp)/total*100:.1f}%',
                 ha='center', transform=axes[1].transAxes, fontsize=9,
                 bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.6))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        logger.info(f"Confusion matrix saved to: {save_path}")
    
    plt.close()
    
    # Print detailed metrics
    print("\n" + "="*70)
    print(f"{model_name} - Classification Performance Metrics")
    print("="*70)
    print(f"\nOverall Metrics:")
    print(f"  Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"  Precision: {precision:.4f} ({precision*100:.2f}%)")
    print(f"  Recall:    {recall:.4f} ({recall*100:.2f}%)")
    print(f"  F1 Score:  {f1:.4f} ({f1*100:.2f}%)")
    
    print(f"\nConfusion Matrix (Counts):")
    print(f"                Predicted")
    print(f"              No Risk  Risk")
    print(f"True No Risk    {tn:4d}    {fp:4d}")
    print(f"     Risk       {fn:4d}    {tp:4d}")
    
    print(f"\nConfusion Matrix (Percentages):")
    print(f"                Predicted")
    print(f"              No Risk  Risk")
    print(f"True No Risk  {tn/total*100:5.1f}%  {fp/total*100:5.1f}%")
    print(f"     Risk      {fn/total*100:5.1f}%  {tp/total*100:5.1f}%")
    
    print("\n" + "="*70)
    print("Detailed Classification Report:")
    print("="*70)
    print(classification_report(y_true, y_pred, 
                                target_names=['No Risk (0)', 'Risk (1)'],
                                digits=4))
    
    return {
        'confusion_matrix': cm.tolist(),
        'confusion_matrix_normalized': cm_normalized.tolist(),
        'accuracy': float(accuracy),
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(f1),
        'true_negative': int(tn),
        'false_positive': int(fp),
        'false_negative': int(fn),
        'true_positive': int(tp),
        'total_samples': int(total)
    }


def create_metrics_comparison_plot(models_metrics: dict, save_path: str = None):
    """
    Create a bar chart comparing metrics across different models.
    
    Args:
        models_metrics: Dictionary with model names as keys and metrics dict as values
        save_path: Path to save the figure
    """
    if not models_metrics:
        logger.warning("No metrics provided for comparison")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Model Performance Comparison - PRIORITEST', 
                 fontsize=16, fontweight='bold', y=1.02)
    
    model_names = list(models_metrics.keys())
    metrics_to_plot = ['accuracy', 'precision', 'recall', 'f1_score']
    metric_labels = ['Accuracy', 'Precision', 'Recall', 'F1 Score']
    
    for idx, (metric, label) in enumerate(zip(metrics_to_plot, metric_labels)):
        ax = axes[idx // 2, idx % 2]
        values = [models_metrics[m][metric] for m in model_names]
        
        bars = ax.bar(model_names, values, color=sns.color_palette("husl", len(model_names)))
        ax.set_ylabel(label, fontsize=12, fontweight='bold')
        ax.set_title(f'{label} Comparison', fontsize=12, fontweight='bold')
        ax.set_ylim([0, 1.1])
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.4f}',
                   ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        logger.info(f"Metrics comparison saved to: {save_path}")
    
    plt.close()


def main():
    """Main function to generate confusion matrix analysis."""
    # Paths
    data_path = os.environ.get("DATA_PATH", "/app/data")
    model_dir = os.environ.get("MODEL_PATH", "/app/models")
    output_dir = os.environ.get("OUTPUT_PATH", "/app/output")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    model_path = os.path.join(model_dir, "model.pkl")
    test_data_path = os.path.join(data_path, "processed", "test.csv")
    
    # Check if files exist
    if not os.path.exists(model_path):
        logger.error(f"Model not found at {model_path}")
        logger.info("Please train the model first using train_model.py")
        return
    
    if not os.path.exists(test_data_path):
        logger.error(f"Test data not found at {test_data_path}")
        logger.info("Please run S4 pipeline first to generate test data")
        return
    
    print("="*70)
    print("PRIORITEST - Confusion Matrix Analysis")
    print("="*70)
    
    # Load model and data
    print("\n[1/4] Loading model and test data...")
    model, X_test, y_test = load_model_and_data(model_path, test_data_path)
    
    # Make predictions
    print("\n[2/4] Making predictions...")
    y_pred = model.predict(X_test)
    
    # Determine model name
    model_type = "XGBoost" if "XGB" in str(type(model)) else "LightGBM"
    model_name = f"PRIORITEST {model_type} Classifier"
    
    # Create confusion matrix
    print("\n[3/4] Generating confusion matrix visualization...")
    metrics = create_confusion_matrix_visualization(
        y_test, 
        y_pred, 
        model_name=model_name,
        save_path=os.path.join(output_dir, "confusion_matrix.png")
    )
    
    # Save metrics to JSON
    print("\n[4/4] Saving metrics to JSON...")
    metrics_path = os.path.join(output_dir, "confusion_matrix_metrics.json")
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to: {metrics_path}")
    
    print("\n" + "="*70)
    print("Analysis complete! Files saved to:", output_dir)
    print("="*70)
    print("\nGenerated files:")
    print(f"  - confusion_matrix.png (visualization)")
    print(f"  - confusion_matrix_metrics.json (detailed metrics)")
    print("="*70)


if __name__ == "__main__":
    main()

