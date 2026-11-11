import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

DATA_RAW_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw')
DATA_PROCESSED_PATH = os.path.join(PROJECT_ROOT, 'data', 'processed')
DATABASE_PATH = os.path.join(PROJECT_ROOT, 'database', 'sales.db')
SQL_SCHEMA_PATH = os.path.join(PROJECT_ROOT, 'sql', 'schema.sql')
SQL_QUERIES_PATH = os.path.join(PROJECT_ROOT, 'sql', 'business_queries.sql')

EXCEL_FILE_NAME = 'Amazon Sale Report.csv'
CLEANED_DATA_FILE = 'cleaned_sales_data.csv'

VALID_STATUSES = [
    'Shipped',
    'Shipped - Delivered to Buyer',
    'Cancelled',
    'Shipped - Returned to Seller',
    'Shipped - Picked Up',
    'Pending',
    'Pending - Waiting for Pick Up',
    'Shipped - Returning to Seller',
    'Shipped - Out for Delivery',
    'Shipped - Rejected by Buyer',
    'Shipping',
    'Shipped - Lost in Transit',
    'Shipped - Damaged'
]

VALID_FULFILMENTS = ['Amazon', 'Merchant']
VALID_CHANNELS = ['Amazon.in']
VALID_CURRENCIES = ['INR']

DELIVERED_STATUSES = ['Shipped - Delivered to Buyer']
CANCELLED_STATUSES = ['Cancelled']
SHIPPED_STATUSES = ['Shipped', 'Shipped - Delivered to Buyer', 'Shipped - Out for Delivery']
