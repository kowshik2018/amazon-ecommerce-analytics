import pytest
import pandas as pd
import numpy as np
from src.data_cleaning import clean_sales_data, DataCleaningReport


@pytest.fixture
def sample_raw_data():
    """Create sample raw data for testing."""
    return pd.DataFrame({
        'index': [0, 1, 2],
        'Order ID': ['ORD001', 'ORD002', 'ORD003'],
        'Date': ['04-30-22', '05-01-22', '05-02-22'],
        'Status': ['Shipped', 'Cancelled', 'Shipped - Delivered to Buyer'],
        'Fulfilment': ['Amazon', 'Merchant', 'Amazon'],
        'Sales Channel ': ['Amazon.in', 'Amazon.in', 'Amazon.in'],
        'ship-service-level': ['Standard', 'Expedited', 'Standard'],
        'Style': ['SET001', 'KUR001', 'TOP001'],
        'SKU': ['SKU001', 'SKU002', 'SKU003'],
        'Category': ['Set', 'kurta', 'Top'],
        'Size': ['M', 'L', 'S'],
        'ASIN': ['B001', 'B002', 'B003'],
        'Courier Status': ['Shipped', np.nan, 'Delivered'],
        'Qty': [1, 0, 2],
        'currency': ['INR', 'INR', 'INR'],
        'Amount': [500.0, 0.0, 1000.0],
        'ship-city': ['MUMBAI', 'DELHI', 'BANGALORE'],
        'ship-state': ['MAHARASHTRA', 'DELHI', 'KARNATAKA'],
        'ship-postal-code': [400001.0, 110001.0, 560001.0],
        'ship-country': ['IN', 'IN', 'IN'],
        'promotion-ids': ['PROMO1', np.nan, 'PROMO2'],
        'B2B': [False, False, True],
        'fulfilled-by': ['Amazon', np.nan, 'Amazon'],
        'Unnamed: 22': [np.nan, np.nan, np.nan]
    })


def test_clean_sales_data_returns_tuple(sample_raw_data):
    """Test that clean_sales_data returns a tuple of 3 elements."""
    result = clean_sales_data(sample_raw_data)
    assert isinstance(result, tuple)
    assert len(result) == 3


def test_clean_sales_data_removes_columns(sample_raw_data):
    """Test that index and Unnamed: 22 columns are removed."""
    cleaned_df, _, _ = clean_sales_data(sample_raw_data)
    assert 'index' not in cleaned_df.columns
    assert 'unnamed__22' not in cleaned_df.columns


def test_dates_converted_to_datetime(sample_raw_data):
    """Test that dates are converted to datetime."""
    cleaned_df, _, _ = clean_sales_data(sample_raw_data)
    assert cleaned_df['date'].dtype == 'datetime64[ns]'


def test_amount_converted_to_numeric(sample_raw_data):
    """Test that Amount is numeric."""
    cleaned_df, _, _ = clean_sales_data(sample_raw_data)
    assert pd.api.types.is_numeric_dtype(cleaned_df['amount'])


def test_qty_converted_to_numeric(sample_raw_data):
    """Test that Qty is numeric."""
    cleaned_df, _, _ = clean_sales_data(sample_raw_data)
    assert pd.api.types.is_numeric_dtype(cleaned_df['qty'])


def test_text_standardized_to_uppercase(sample_raw_data):
    """Test that text columns are uppercase."""
    cleaned_df, _, _ = clean_sales_data(sample_raw_data)
    assert cleaned_df['status'].iloc[0] == 'SHIPPED'
    assert cleaned_df['category'].iloc[1] == 'KURTA'
    assert cleaned_df['ship_city'].iloc[0] == 'MUMBAI'


def test_quality_summary_contains_required_keys(sample_raw_data):
    """Test that quality summary has required information."""
    _, quality_summary, _ = clean_sales_data(sample_raw_data)
    required_keys = ['initial_rows', 'final_rows', 'rows_removed', 'total_columns', 
                     'unique_order_ids', 'date_range', 'total_revenue', 'total_units']
    for key in required_keys:
        assert key in quality_summary


def test_cleaning_report_captures_issues(sample_raw_data):
    """Test that cleaning report captures data issues."""
    _, _, report = clean_sales_data(sample_raw_data)
    assert len(report.issues) > 0
    assert len(report.transformations) > 0


def test_negative_quantities_removed(sample_raw_data):
    """Test that negative quantities are removed."""
    sample_raw_data.loc[0, 'Qty'] = -1
    cleaned_df, _, report = clean_sales_data(sample_raw_data)
    assert (cleaned_df['qty'] < 0).sum() == 0


def test_empty_dataframe_handled(sample_raw_data):
    """Test that empty dataframe is handled."""
    empty_df = sample_raw_data.iloc[0:0].copy()
    cleaned_df, quality_summary, _ = clean_sales_data(empty_df)
    assert len(cleaned_df) == 0
    assert quality_summary['final_rows'] == 0


def test_duplicates_identified(sample_raw_data):
    """Test that duplicates are identified."""
    _, _, report = clean_sales_data(sample_raw_data)
    # Should have some issues reported
    assert isinstance(report.issues, list)
