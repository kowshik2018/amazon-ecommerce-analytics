import pytest
import pandas as pd
import numpy as np
from src.database import SalesDatabase
from src.metrics import KPICalculator


@pytest.fixture
def sample_cleaned_data():
    """Create sample cleaned data."""
    return pd.DataFrame({
        'order_id': ['ORD001', 'ORD002', 'ORD003', 'ORD001'],
        'order_date': pd.to_datetime(['2022-04-30', '2022-05-01', '2022-05-02', '2022-05-03']),
        'status': ['SHIPPED', 'CANCELLED', 'SHIPPED - DELIVERED TO BUYER', 'SHIPPED'],
        'fulfilment': ['AMAZON', 'MERCHANT', 'AMAZON', 'AMAZON'],
        'sales_channel': ['AMAZON.IN', 'AMAZON.IN', 'AMAZON.IN', 'AMAZON.IN'],
        'ship_service_level': ['STANDARD', 'EXPEDITED', 'STANDARD', 'STANDARD'],
        'style': ['SET001', 'KUR001', 'TOP001', 'SET002'],
        'sku': ['SKU001', 'SKU002', 'SKU003', 'SKU004'],
        'category': ['SET', 'KURTA', 'TOP', 'SET'],
        'size': ['M', 'L', 'S', 'L'],
        'asin': ['B001', 'B002', 'B003', 'B004'],
        'courier_status': ['SHIPPED', 'UNKNOWN', 'DELIVERED', 'SHIPPED'],
        'qty': [1, 0, 2, 1],
        'currency': ['INR', 'INR', 'INR', 'INR'],
        'amount': [500.0, 0.0, 1000.0, 600.0],
        'ship_city': ['MUMBAI', 'DELHI', 'BANGALORE', 'MUMBAI'],
        'ship_state': ['MAHARASHTRA', 'DELHI', 'KARNATAKA', 'MAHARASHTRA'],
        'ship_postal_code': [400001.0, 110001.0, 560001.0, 400002.0],
        'ship_country': ['IN', 'IN', 'IN', 'IN'],
        'promotion_ids': ['PROMO1', 'NONE', 'PROMO2', 'NONE'],
        'b2b': [False, False, True, False],
        'fulfilled_by': ['AMAZON', 'UNKNOWN', 'AMAZON', 'AMAZON']
    })


@pytest.fixture
def db_with_data(sample_cleaned_data):
    """Create database with sample data."""
    db = SalesDatabase(':memory:')
    db.connect()
    db.create_schema()
    db.load_data(sample_cleaned_data)
    yield db
    db.close()


@pytest.fixture
def kpi_calculator(db_with_data):
    """Create KPI calculator with sample data."""
    return KPICalculator(db_with_data)


def test_total_revenue(kpi_calculator):
    """Test total revenue calculation."""
    revenue = kpi_calculator.get_total_revenue()
    expected = 500.0 + 0.0 + 1000.0 + 600.0
    assert revenue == expected


def test_total_orders(kpi_calculator):
    """Test total orders count."""
    orders = kpi_calculator.get_total_orders()
    assert orders == 3  # ORD001, ORD002, ORD003


def test_total_units(kpi_calculator):
    """Test total units calculation."""
    units = kpi_calculator.get_total_units()
    expected = 1 + 0 + 2 + 1
    assert units == expected


def test_average_order_value(kpi_calculator):
    """Test average order value calculation."""
    aov = kpi_calculator.get_average_order_value()
    total_revenue = 500.0 + 0.0 + 1000.0 + 600.0
    total_orders = 3
    expected = round(total_revenue / total_orders, 2)
    assert aov == expected


def test_cancellation_rate(kpi_calculator):
    """Test cancellation rate calculation."""
    rate = kpi_calculator.get_cancellation_rate()
    assert rate == round((1 / 3) * 100, 2)


def test_delivered_orders(kpi_calculator):
    """Test delivered orders count."""
    delivered = kpi_calculator.get_delivered_orders()
    assert delivered == 1


def test_fulfillment_percentage(kpi_calculator):
    """Test fulfillment percentage."""
    pct = kpi_calculator.get_fulfillment_percentage()
    assert pct == round((2 / 3) * 100, 2)


def test_category_performance(kpi_calculator):
    """Test category performance data."""
    categories = kpi_calculator.get_category_performance()
    assert len(categories) > 0
    assert 'category' in categories.columns
    assert 'revenue' in categories.columns


def test_state_performance(kpi_calculator):
    """Test state performance data."""
    states = kpi_calculator.get_state_performance()
    assert len(states) > 0
    assert 'ship_state' in states.columns
    assert 'revenue' in states.columns


def test_top_products(kpi_calculator):
    """Test top products query."""
    products = kpi_calculator.get_top_products(limit=2)
    assert len(products) <= 2
    assert 'sku' in products.columns
    assert 'revenue' in products.columns


def test_status_distribution(kpi_calculator):
    """Test status distribution."""
    status_dist = kpi_calculator.get_status_distribution()
    assert len(status_dist) > 0
    assert 'status' in status_dist.columns
    assert 'order_count' in status_dist.columns


def test_fulfillment_comparison(kpi_calculator):
    """Test fulfillment comparison."""
    fulfilment = kpi_calculator.get_fulfilment_comparison()
    assert len(fulfilment) > 0
    assert 'fulfilment' in fulfilment.columns


def test_b2b_analysis(kpi_calculator):
    """Test B2B analysis."""
    b2b = kpi_calculator.get_b2b_analysis()
    assert len(b2b) > 0
    assert 'b2b' in b2b.columns
    assert 'orders' in b2b.columns


def test_monthly_revenue_data(kpi_calculator):
    """Test monthly revenue data."""
    monthly = kpi_calculator.get_monthly_revenue_data()
    assert len(monthly) > 0
    assert 'month' in monthly.columns
    assert 'revenue' in monthly.columns


def test_daily_revenue_data(kpi_calculator):
    """Test daily revenue data."""
    daily = kpi_calculator.get_daily_revenue_data()
    assert len(daily) > 0
    assert 'date' in daily.columns
    assert 'revenue' in daily.columns


def test_all_kpis_returned(kpi_calculator):
    """Test that all KPIs are returned."""
    kpis = kpi_calculator.get_all_kpis()
    required_kpis = [
        'total_revenue', 'total_orders', 'total_units',
        'average_order_value', 'cancellation_rate',
        'delivered_orders', 'shipped_orders', 'fulfillment_percentage'
    ]
    for kpi in required_kpis:
        assert kpi in kpis
        assert kpis[kpi] is not None


def test_revenue_with_date_filter(db_with_data):
    """Test revenue calculation with date filter."""
    kpi = KPICalculator(db_with_data)
    start_date = '2022-05-02'
    end_date = '2022-05-03'
    revenue = kpi.get_total_revenue(start_date, end_date)
    assert revenue == 1000.0 + 600.0


def test_zero_division_handled(db_with_data):
    """Test that zero division is handled."""
    kpi = KPICalculator(db_with_data)
    start_date = '2025-01-01'
    end_date = '2025-12-31'
    aov = kpi.get_average_order_value(start_date, end_date)
    assert aov == 0
