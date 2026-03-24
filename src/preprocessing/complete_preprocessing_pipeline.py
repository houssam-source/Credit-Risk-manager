"""
Complete Preprocessing Pipeline for Credit Risk Management
This script loads all CSV files, processes features, and creates a single consolidated dataset
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path
from sklearn.preprocessing import StandardScaler, LabelEncoder
import warnings
warnings.filterwarnings('ignore')

# Define directories
# Get the project root directory (two levels up from this file)
project_root = Path(__file__).parent.parent.parent

data_dir = project_root / 'home-credit-default-risk' / 'data'
processed_dir = data_dir / 'processed'
processed_dir.mkdir(exist_ok=True)

def load_all_datasets():
    """Load all available CSV files"""
    print("Loading all datasets...")
    
    files_to_load = [
        'application_train.csv',
        'application_test.csv', 
        'bureau.csv',
        'bureau_balance.csv',
        'POS_CASH_balance.csv',
        'credit_card_balance.csv',
        'installments_payments.csv',
        'previous_application.csv'
    ]
    
    datasets = {}
    
    for file in files_to_load:
        file_path = data_dir / file
        if file_path.exists():
            print(f"Loading {file}...")
            try:
                df = pd.read_csv(file_path)
                datasets[file.replace('.csv', '')] = df
                print(f"  ✓ Loaded {file}: Shape {df.shape}")
            except Exception as e:
                print(f"  ✗ Error loading {file}: {str(e)}")
        else:
            print(f"  ✗ File {file} not found!")
    
    return datasets

def preprocess_numerical_features(df, dataset_name):
    """Normalize numerical features and fill missing values with 0"""
    print(f"  Processing numerical features for {dataset_name}...")
    
    # Get numerical columns
    numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    # Remove ID columns from numerical processing
    id_columns = ['SK_ID_CURR', 'SK_ID_BUREAU', 'SK_ID_PREV']
    numerical_cols = [col for col in numerical_cols if col not in id_columns]
    
    processed_df = df.copy()
    
    for col in numerical_cols:
        # Fill NaN values with 0
        processed_df[col] = processed_df[col].fillna(0)
        
        # Normalize using mean and standard deviation
        col_mean = processed_df[col].mean()
        col_std = processed_df[col].std()
        
        if col_std != 0:  # Avoid division by zero
            processed_df[f'{col}_normalized'] = (processed_df[col] - col_mean) / col_std
        else:
            processed_df[f'{col}_normalized'] = 0
    
    print(f"    Processed {len(numerical_cols)} numerical features")
    return processed_df

def preprocess_categorical_features(df, dataset_name):
    """Apply one-hot encoding to categorical features"""
    print(f"  Processing categorical features for {dataset_name}...")
    
    # Get categorical columns
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    processed_df = df.copy()
    
    # Apply one-hot encoding
    if categorical_cols:
        processed_df = pd.get_dummies(processed_df, columns=categorical_cols, dummy_na=True)
        print(f"    One-hot encoded {len(categorical_cols)} categorical features")
    
    return processed_df

def aggregate_dataset(df, group_col, dataset_name):
    """Aggregate dataset by ID column"""
    print(f"  Aggregating {dataset_name} by {group_col}...")
    
    if group_col not in df.columns:
        print(f"    Warning: {group_col} not found in {dataset_name}")
        return df
    
    # Get numerical columns for aggregation
    numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    # Remove grouping column from aggregation
    if group_col in numerical_cols:
        numerical_cols.remove(group_col)
    
    # Define aggregation functions
    agg_dict = {}
    for col in numerical_cols:
        agg_dict[col] = ['mean', 'sum', 'count', 'max', 'min', 'std']
    
    # Perform aggregation
    try:
        aggregated_df = df.groupby(group_col).agg(agg_dict).reset_index()
        
        # Flatten column names
        flattened_columns = [group_col]
        for col_tuple in aggregated_df.columns[1:]:
            if isinstance(col_tuple, tuple):
                new_name = f"{col_tuple[0]}_{col_tuple[1]}"
                flattened_columns.append(new_name)
            else:
                flattened_columns.append(col_tuple)
        
        aggregated_df.columns = flattened_columns
        print(f"    Aggregated to shape: {aggregated_df.shape}")
        return aggregated_df
        
    except Exception as e:
        print(f"    Error during aggregation: {str(e)}")
        return df

def create_consolidated_dataset(datasets):
    """Create a single consolidated dataset with all processed features"""
    print("\nCreating consolidated dataset...")
    
    # Start with application_train as the base
    if 'application_train' not in datasets:
        raise ValueError("application_train.csv is required as base dataset")
    
    consolidated_df = datasets['application_train'].copy()
    print(f"Base dataset shape: {consolidated_df.shape}")
    
    # Process and merge each additional dataset
    merge_configs = [
        ('bureau', 'SK_ID_CURR', 'SK_ID_CURR'),
        ('bureau_balance', 'SK_ID_BUREAU', 'SK_ID_BUREAU'),
        ('previous_application', 'SK_ID_CURR', 'SK_ID_CURR'),
        ('POS_CASH_balance', 'SK_ID_PREV', 'SK_ID_PREV'),
        ('credit_card_balance', 'SK_ID_PREV', 'SK_ID_PREV'),
        ('installments_payments', 'SK_ID_PREV', 'SK_ID_PREV')
    ]
    
    for dataset_name, merge_key_base, merge_key_additional in merge_configs:
        if dataset_name in datasets:
            print(f"\nProcessing {dataset_name}...")
            
            # Get the additional dataset
            additional_df = datasets[dataset_name].copy()
            
            # Preprocess numerical features
            additional_df = preprocess_numerical_features(additional_df, dataset_name)
            
            # Preprocess categorical features
            additional_df = preprocess_categorical_features(additional_df, dataset_name)
            
            # Aggregate if needed
            if merge_key_additional in additional_df.columns:
                additional_df = aggregate_dataset(additional_df, merge_key_additional, dataset_name)
            
            # Merge with consolidated dataset
            if merge_key_base in consolidated_df.columns and merge_key_additional in additional_df.columns:
                consolidated_df = pd.merge(
                    consolidated_df,
                    additional_df,
                    left_on=merge_key_base,
                    right_on=merge_key_additional,
                    how='left',
                    suffixes=('', f'_{dataset_name}')
                )
                print(f"  Merged {dataset_name}. New shape: {consolidated_df.shape}")
            else:
                print(f"  Skipping merge for {dataset_name} - key columns not found")
        else:
            print(f"Skipping {dataset_name} - not loaded")
    
    return consolidated_df

def final_processing(consolidated_df):
    """Final processing steps for the consolidated dataset"""
    print("\nPerforming final processing...")
    
    # Handle any remaining categorical features
    categorical_cols = consolidated_df.select_dtypes(include=['object']).columns.tolist()
    if categorical_cols:
        print(f"Encoding remaining categorical features: {len(categorical_cols)}")
        consolidated_df = pd.get_dummies(consolidated_df, columns=categorical_cols, dummy_na=True)
    
    # Fill any remaining NaN values with 0
    numerical_cols = consolidated_df.select_dtypes(include=[np.number]).columns.tolist()
    for col in numerical_cols:
        if col != 'TARGET':  # Don't fill TARGET column
            consolidated_df[col] = consolidated_df[col].fillna(0)
    
    # Ensure all features are numerical
    consolidated_df = consolidated_df.select_dtypes(include=[np.number])
    
    print(f"Final dataset shape: {consolidated_df.shape}")
    print(f"Number of features: {len(consolidated_df.columns) - 1}")  # -1 for TARGET column
    
    return consolidated_df

def save_processed_datasets(datasets, consolidated_df):
    """Save all processed datasets"""
    print(f"\nSaving processed datasets to {processed_dir}...")
    
    # Save individual processed datasets
    for dataset_name, df in datasets.items():
        filename = f"{dataset_name}_processed.csv"
        filepath = processed_dir / filename
        df.to_csv(filepath, index=False)
        print(f"  Saved {filename}")
    
    # Save consolidated dataset
    consolidated_filepath = processed_dir / "consolidated_features.csv"
    consolidated_df.to_csv(consolidated_filepath, index=False)
    print(f"  Saved consolidated_features.csv")
    
    # Save feature summary
    feature_summary = {
        'total_rows': len(consolidated_df),
        'total_features': len(consolidated_df.columns) - 1,  # -1 for TARGET
        'target_distribution': consolidated_df['TARGET'].value_counts().to_dict() if 'TARGET' in consolidated_df.columns else 'N/A',
        'feature_list': list(consolidated_df.columns)
    }
    
    summary_filepath = processed_dir / "feature_summary.txt"
    with open(summary_filepath, 'w') as f:
        f.write("=== FEATURE SUMMARY ===\n")
        f.write(f"Total Rows: {feature_summary['total_rows']}\n")
        f.write(f"Total Features: {feature_summary['total_features']}\n")
        f.write(f"Target Distribution: {feature_summary['target_distribution']}\n")
        f.write("\nFeature List:\n")
        for i, feature in enumerate(feature_summary['feature_list'], 1):
            f.write(f"{i}. {feature}\n")
    
    print(f"  Saved feature_summary.txt")

def main():
    """Main execution function"""
    print("=" * 60)
    print("CREDIT RISK DATA PREPROCESSING PIPELINE")
    print("=" * 60)
    
    try:
        # Load all datasets
        datasets = load_all_datasets()
        
        if not datasets:
            print("No datasets loaded. Exiting.")
            return
        
        # Create consolidated dataset
        consolidated_df = create_consolidated_dataset(datasets)
        
        # Final processing
        consolidated_df = final_processing(consolidated_df)
        
        # Save all processed data
        save_processed_datasets(datasets, consolidated_df)
        
        print("\n" + "=" * 60)
        print("PREPROCESSING COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"All processed files saved to: {processed_dir}")
        print(f"Consolidated dataset ready for model training")
        
        return consolidated_df
        
    except Exception as e:
        print(f"\nError during preprocessing: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = main()