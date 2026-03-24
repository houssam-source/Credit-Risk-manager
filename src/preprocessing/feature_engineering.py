import pandas as pd
import numpy as np
import os
from pathlib import Path
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer

# Define the data directory
# Get the project root directory (two levels up from this file)
project_root = Path(__file__).parent.parent.parent

data_dir = project_root / 'home-credit-default-risk' / 'data'
processed_dir = data_dir / 'processed'

# Create processed directory if it doesn't exist
processed_dir.mkdir(exist_ok=True)

def load_and_explore_data():
    """
    Load multiple CSV files and categorize their features
    """
    # List of files to load
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
    
    # Load each dataset
    for file in files_to_load:
        file_path = data_dir / file
        if file_path.exists():
            print(f"Loading {file}...")
            df = pd.read_csv(file_path)
            datasets[file.replace('.csv', '')] = df
            print(f"{file}: Shape {df.shape}")
            print(f"{file}: Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB\n")
        else:
            print(f"File {file} not found!")
    
    return datasets

def categorize_features(df, dataset_name):
    """
    Categorize features in a DataFrame
    """
    print(f"\n--- Feature Analysis for {dataset_name} ---")
    print(f"Total features: {len(df.columns)}")
    
    # Identify different types of features
    categorical_features = []
    numerical_features = []
    binary_features = []
    datetime_features = []
    
    for col in df.columns:
        dtype = str(df[col].dtype)
        
        # Check if it's a binary feature (only 0s and 1s)
        unique_vals = df[col].dropna().unique()
        if len(unique_vals) <= 2 and set(unique_vals).issubset({0, 1, True, False}):
            binary_features.append(col)
        # Check if it's categorical (object type or low cardinality numeric)
        elif dtype == 'object':
            categorical_features.append(col)
        elif 'int' in dtype or 'float' in dtype:
            # Check cardinality for numeric features
            if df[col].nunique() < 20:  # Threshold for categorical-like numeric
                categorical_features.append(col)
            else:
                numerical_features.append(col)
        elif 'date' in dtype.lower() or 'time' in dtype.lower():
            datetime_features.append(col)
        else:
            numerical_features.append(col)
    
    print(f"Categorical features ({len(categorical_features)}): {categorical_features}")
    print(f"Numerical features ({len(numerical_features)}): {numerical_features[:10]}{'...' if len(numerical_features) > 10 else ''}")  # Show first 10
    print(f"Binary features ({len(binary_features)}): {binary_features}")
    print(f"Datetime features ({len(datetime_features)}): {datetime_features}")
    
    # Show basic statistics for numerical features
    if numerical_features:
        print("\nSample numerical features statistics:")
        sample_numerical = numerical_features[:min(5, len(numerical_features))]
        if sample_numerical:
            print(df[sample_numerical].describe())
    
    # Show sample values for categorical features
    if categorical_features:
        print("\nSample categorical features:")
        sample_categorical = categorical_features[:min(5, len(categorical_features))]
        for col in sample_categorical:
            print(f"  {col}: {df[col].unique()[:10]}{'...' if len(df[col].unique()) > 10 else ''}")
    
    return {
        'categorical': categorical_features,
        'numerical': numerical_features,
        'binary': binary_features,
        'datetime': datetime_features
    }

def normalize_numerical_features(df, numerical_features):
    """
    Normalize numerical features by calculating average and ratio, 
    then fill non-value rows with 0
    """
    df_processed = df.copy()
    
    for col in numerical_features:
        # Calculate mean for normalization
        col_mean = df_processed[col].mean()
        
        # Fill NaN values with 0
        df_processed[col] = df_processed[col].fillna(0)
        
        # Alternative approach: Normalize using mean and std
        col_std = df_processed[col].std()
        if col_std != 0:  # Avoid division by zero
            df_processed[f'{col}_normalized'] = (df_processed[col] - col_mean) / col_std
    
    return df_processed

def encode_categorical_features(df, categorical_features):
    """
    Apply one-hot encoding to categorical features
    """
    df_encoded = df.copy()
    
    for col in categorical_features:
        # Apply one-hot encoding
        dummies = pd.get_dummies(df_encoded[col], prefix=col)
        df_encoded = pd.concat([df_encoded, dummies], axis=1)
        # Drop the original categorical column
        df_encoded.drop(columns=[col], inplace=True)
    
    return df_encoded

def aggregate_by_id(df, group_col, agg_funcs=None):
    """
    Aggregate dataframe by a specific ID column
    """
    if agg_funcs is None:
        # Default aggregation functions
        agg_funcs = {
            'mean': ['mean'],
            'sum': ['sum'],
            'count': ['size'],
            'max': ['max'],
            'min': ['min'],
            'std': ['std']
        }
    
    # Get numerical columns for aggregation
    numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    # Remove the grouping column from numerical columns if present
    if group_col in numerical_cols:
        numerical_cols.remove(group_col)
    
    # Create aggregation dictionary
    agg_dict = {}
    for col in numerical_cols:
        agg_dict[col] = ['mean', 'sum', 'max', 'min', 'std']
    
    # Perform aggregation
    aggregated_df = df.groupby(group_col).agg(agg_dict).reset_index()
    
    # Flatten column names after aggregation
    flattened_columns = [group_col]
    for col in aggregated_df.columns[1:]:
        if isinstance(col, tuple):
            new_col_name = f"{col[0]}_{col[1]}"
            flattened_columns.append(new_col_name)
        else:
            flattened_columns.append(col)
    
    aggregated_df.columns = flattened_columns
    
    return aggregated_df

def process_dataset(df, dataset_name, id_column=None):
    """
    Process a dataset: normalize numerical features, encode categorical features,
    and aggregate by ID if specified
    """
    print(f"\nProcessing {dataset_name} dataset...")
    
    # Categorize features
    feature_types = categorize_features(df, dataset_name)
    
    # Process numerical features
    if feature_types['numerical']:
        df = normalize_numerical_features(df, feature_types['numerical'])
        print(f"Normalized {len(feature_types['numerical'])} numerical features")
    
    # Process categorical features
    if feature_types['categorical']:
        df = encode_categorical_features(df, feature_types['categorical'])
        print(f"One-hot encoded {len(feature_types['categorical'])} categorical features")
    
    # If an ID column is specified, aggregate the data
    if id_column and id_column in df.columns:
        df_aggregated = aggregate_by_id(df, id_column)
        print(f"Aggregated data by {id_column}, resulting shape: {df_aggregated.shape}")
        return df_aggregated
    else:
        print(f"No aggregation performed for {dataset_name}, returning processed data with shape: {df.shape}")
        return df

def integrate_preprocessing_pipeline():
    """
    Integrate preprocessing pipeline with the training workflow
    """
    print("Starting preprocessing pipeline...")
    
    # Load datasets
    datasets = load_and_explore_data()
    
    # Define ID columns for each dataset that can be used for aggregation
    id_mapping = {
        'application_train': 'SK_ID_CURR',
        'application_test': 'SK_ID_CURR',
        'bureau': 'SK_ID_BUREAU',
        'bureau_balance': 'SK_ID_BUREAU',
        'POS_CASH_balance': 'SK_ID_PREV',
        'credit_card_balance': 'SK_ID_PREV',
        'installments_payments': 'SK_ID_PREV',
        'previous_application': 'SK_ID_PREV'
    }
    
    # Process each dataset
    processed_datasets = {}
    for dataset_name, df in datasets.items():
        id_col = id_mapping.get(dataset_name)
        processed_df = process_dataset(df, dataset_name, id_col)
        processed_datasets[dataset_name] = processed_df
        
        # Save processed dataset to the processed folder
        output_path = processed_dir / f"{dataset_name}_processed.csv"
        processed_df.to_csv(output_path, index=False)
        print(f"Saved processed {dataset_name} to {output_path}")
    
    # Special processing: Merge application data with bureau data
    if 'application_train' in processed_datasets and 'bureau' in processed_datasets:
        print(f"\nMerging application_train with bureau data...")
        
        # Merge application_train with bureau on SK_ID_CURR
        merged_df = pd.merge(
            processed_datasets['application_train'],
            processed_datasets['bureau'],
            left_on='SK_ID_CURR',
            right_on='SK_ID_CURR',
            how='left',
            suffixes=('', '_bureau')
        )
        
        # Save merged dataset
        merged_output_path = processed_dir / "application_train_with_bureau.csv"
        merged_df.to_csv(merged_output_path, index=False)
        print(f"Saved merged dataset to {merged_output_path}")
        print(f"Merged dataset shape: {merged_df.shape}")
        
        # Return the final processed training dataset for model training
        return merged_df
    
    # If merging didn't happen, return the processed application_train
    if 'application_train' in processed_datasets:
        return processed_datasets['application_train']
    
    return None

def prepare_features_for_training(df):
    """
    Prepare the final dataset for training by selecting appropriate features
    """
    print("\nPreparing features for training...")
    
    # Identify the target variable (assuming it's named 'TARGET')
    if 'TARGET' in df.columns:
        y = df['TARGET']
        X = df.drop(columns=['TARGET'])
    else:
        # If TARGET is not found, assume the last column might be the target
        # or handle appropriately based on your specific dataset
        print("Warning: TARGET column not found. Using the last column as target.")
        y = df.iloc[:, -1]  # Last column as target
        X = df.iloc[:, :-1]  # All other columns as features
    
    print(f"Features shape: {X.shape}")
    print(f"Target shape: {y.shape}")
    
    return X, y

# Example of how to use the preprocessing pipeline in your training workflow
def main():
    """
    Main function to run the preprocessing pipeline
    """
    print("Loading and processing datasets...")
    
    # Run the integrated preprocessing pipeline
    processed_train_data = integrate_preprocessing_pipeline()
    
    if processed_train_data is not None:
        # Prepare features for training
        X, y = prepare_features_for_training(processed_train_data)
        
        print(f"Final training dataset prepared:")
        print(f"X shape: {X.shape}")
        print(f"y shape: {y.shape}")
        
        # At this point, X and y are ready to be used in your model training
        # You can pass them to your model training function
        
        print(f"\nAll processed files saved to: {processed_dir}")
        print("Preprocessing pipeline completed successfully!")
        
        return X, y
    else:
        print("Error: Could not process the training data.")
        return None, None

if __name__ == "__main__":
    main()