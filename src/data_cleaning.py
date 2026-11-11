import pandas as pd
import numpy as np
from datetime import datetime


class DataCleaningReport:
    def __init__(self):
        self.issues = []
        self.transformations = []
        self.statistics = {}
    
    def add_issue(self, issue_type, count, description):
        self.issues.append({
            'type': issue_type,
            'count': count,
            'description': description
        })
    
    def add_transformation(self, action, details):
        self.transformations.append({
            'action': action,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
    
    def to_dict(self):
        return {
            'issues': self.issues,
            'transformations': self.transformations,
            'statistics': self.statistics
        }


def clean_column_names(df):
    """Clean and standardize column names."""
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.lower()
    df.columns = df.columns.str.replace(' ', '_')
    df.columns = df.columns.str.replace('-', '_')
    return df


def clean_dates(df):
    """Convert Date column to datetime format."""
    df['date'] = pd.to_datetime(df['date'], format='%m-%d-%y', errors='coerce')
    return df


def clean_amount_qty(df):
    """Convert Amount and Qty to numeric formats."""
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df['qty'] = pd.to_numeric(df['qty'], errors='coerce')
    return df


def standardize_text_columns(df):
    """Standardize text columns (capitalize consistently)."""
    text_cols = ['status', 'fulfilment', 'category', 'size', 'style']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].str.strip()
            df[col] = df[col].str.upper()
    
    df['ship_city'] = df['ship_city'].str.strip().str.upper()
    df['ship_state'] = df['ship_state'].str.strip().str.upper()
    df['ship_country'] = df['ship_country'].str.strip().str.upper()
    
    return df


def handle_missing_values(df, report):
    """Handle missing values appropriately."""
    initial_rows = len(df)
    
    df['courier_status'] = df['courier_status'].fillna('UNKNOWN')
    df['promotion_ids'] = df['promotion_ids'].fillna('NONE')
    df['fulfilled_by'] = df['fulfilled_by'].fillna('UNKNOWN')
    
    rows_with_missing_critical = df[
        (df['amount'].isnull()) | 
        (df['qty'].isnull()) |
        (df['order_id'].isnull()) |
        (df['date'].isnull())
    ]
    
    if len(rows_with_missing_critical) > 0:
        report.add_issue(
            'missing_critical_values',
            len(rows_with_missing_critical),
            'Rows with missing Order ID, Date, Amount, or Qty'
        )
        df = df.drop(rows_with_missing_critical.index)
    
    if df['currency'].isnull().sum() > 0:
        df['currency'] = df['currency'].fillna('INR')
    
    return df, report


def identify_duplicates(df, report):
    """Identify duplicate Order IDs and rows."""
    duplicate_order_ids = df[df.duplicated(subset=['order_id'], keep=False)].sort_values('order_id')
    duplicate_count = len(duplicate_order_ids)
    
    report.add_issue(
        'duplicate_order_ids',
        duplicate_count,
        f'Total rows with duplicate Order IDs: {duplicate_count}'
    )
    
    full_duplicates = df[df.duplicated(keep=False)]
    if len(full_duplicates) > 0:
        report.add_issue(
            'full_row_duplicates',
            len(full_duplicates),
            'Completely identical rows'
        )
        df = df.drop_duplicates()
    
    return df, duplicate_order_ids, report


def validate_data_ranges(df, report):
    """Validate data ranges and identify anomalies."""
    negative_qty = df[df['qty'] < 0]
    if len(negative_qty) > 0:
        report.add_issue(
            'negative_quantities',
            len(negative_qty),
            'Rows with negative quantities'
        )
        df = df[df['qty'] >= 0]
    
    zero_amount_cancelled = df[(df['amount'] == 0) & (~df['status'].str.contains('CANCELLED', na=False))]
    if len(zero_amount_cancelled) > 0:
        report.add_issue(
            'zero_amount_non_cancelled',
            len(zero_amount_cancelled),
            'Non-cancelled orders with zero amount'
        )
    
    return df, report


def clean_sales_data(df):
    """
    Complete data cleaning pipeline.
    
    Args:
        df: Raw DataFrame from load_excel_data
        
    Returns:
        Tuple of (cleaned_df, quality_summary, cleaning_report)
    """
    report = DataCleaningReport()
    initial_rows = len(df)
    
    df = clean_column_names(df)
    report.add_transformation('clean_column_names', 'Standardized column names')
    
    df = clean_dates(df)
    invalid_dates = df['date'].isnull().sum()
    if invalid_dates > 0:
        report.add_issue('invalid_dates', invalid_dates, 'Could not parse date format')
    report.add_transformation('clean_dates', f'Converted dates to datetime; {invalid_dates} invalid')
    
    df = clean_amount_qty(df)
    report.add_transformation('clean_amount_qty', 'Converted Amount and Qty to numeric')
    
    df = standardize_text_columns(df)
    report.add_transformation('standardize_text', 'Standardized text columns to UPPERCASE')
    
    df, report = handle_missing_values(df, report)
    
    df, duplicate_order_ids, report = identify_duplicates(df, report)
    
    df, report = validate_data_ranges(df, report)
    
    cols_to_drop = [col for col in df.columns if col in ['index', 'unnamed__22', 'unnamed: 22', 'unnamed:_22']]
    df = df.drop(columns=cols_to_drop, errors='ignore')
    report.add_transformation('drop_unused_columns', 'Removed index and Unnamed: 22 columns')
    
    rows_removed = initial_rows - len(df)
    quality_summary = {
        'initial_rows': initial_rows,
        'final_rows': len(df),
        'rows_removed': rows_removed,
        'total_columns': len(df.columns),
        'missing_values_summary': df.isnull().sum().to_dict(),
        'unique_order_ids': df['order_id'].nunique(),
        'date_range': f"{df['date'].min()} to {df['date'].max()}",
        'total_revenue': df['amount'].sum(),
        'total_units': df['qty'].sum()
    }
    
    report.statistics = quality_summary
    
    return df, quality_summary, report
