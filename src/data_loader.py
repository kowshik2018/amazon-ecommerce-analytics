import pandas as pd
import numpy as np
import os
from pathlib import Path


def load_excel_data(file_path=None):
    """
    Load Excel/CSV data from file or find it in data/raw directory.
    
    Args:
        file_path: Optional path to CSV file
        
    Returns:
        DataFrame with raw data
    """
    if file_path is None:
        raw_dir = Path('data/raw')
        raw_dir.mkdir(parents=True, exist_ok=True)
        
        csv_files = list(raw_dir.glob('*.csv'))
        if csv_files:
            file_path = csv_files[0]
        else:
            raise FileNotFoundError(
                "No CSV file found in data/raw/. "
                "Please place your Amazon Sale Report CSV in data/raw/"
            )
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        df = pd.read_csv(file_path, low_memory=False)
        return df
    except Exception as e:
        raise ValueError(f"Error loading CSV file: {str(e)}")


def validate_columns(df, required_columns=None):
    """
    Validate that required columns exist in DataFrame.
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        
    Returns:
        Tuple (is_valid, missing_columns)
    """
    if required_columns is None:
        required_columns = [
            'Order ID', 'Date', 'Status', 'Fulfilment', 'Sales Channel ',
            'ship-service-level', 'Category', 'Size', 'Qty', 'Amount',
            'ship-city', 'ship-state', 'currency', 'B2B'
        ]
    
    missing = [col for col in required_columns if col not in df.columns]
    return len(missing) == 0, missing


def get_dataset_summary(df):
    """
    Get basic dataset summary.
    
    Returns:
        Dictionary with dataset info
    """
    return {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'unique_order_ids': df['Order ID'].nunique(),
        'date_range_start': df['Date'].min(),
        'date_range_end': df['Date'].max(),
        'columns': list(df.columns)
    }
