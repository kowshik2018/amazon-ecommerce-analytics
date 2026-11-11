import sqlite3
import pandas as pd
from pathlib import Path


class SalesDatabase:
    def __init__(self, db_path='database/sales.db'):
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
    
    def connect(self):
        """Connect to database."""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        return self.conn
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def create_schema(self):
        """Create database schema."""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            DROP TABLE IF EXISTS fact_sales
        ''')
        
        cursor.execute('''
            CREATE TABLE fact_sales (
                sales_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                date DATE NOT NULL,
                status TEXT,
                fulfilment TEXT,
                sales_channel TEXT,
                ship_service_level TEXT,
                style TEXT,
                sku TEXT,
                category TEXT,
                size TEXT,
                asin TEXT,
                courier_status TEXT,
                qty INTEGER,
                currency TEXT,
                amount REAL,
                ship_city TEXT,
                ship_state TEXT,
                ship_postal_code REAL,
                ship_country TEXT,
                promotion_ids TEXT,
                b2b BOOLEAN,
                fulfilled_by TEXT
            )
        ''')
        
        cursor.execute('CREATE INDEX idx_order_id ON fact_sales(order_id)')
        cursor.execute('CREATE INDEX idx_date ON fact_sales(date)')
        cursor.execute('CREATE INDEX idx_status ON fact_sales(status)')
        cursor.execute('CREATE INDEX idx_category ON fact_sales(category)')
        cursor.execute('CREATE INDEX idx_fulfilment ON fact_sales(fulfilment)')
        cursor.execute('CREATE INDEX idx_ship_state ON fact_sales(ship_state)')
        cursor.execute('CREATE INDEX idx_b2b ON fact_sales(b2b)')
        
        self.conn.commit()
    
    def load_data(self, df):
        """Load cleaned data into database."""
        df.to_sql('fact_sales', self.conn, if_exists='append', index=False)
        self.conn.commit()
    
    def execute_query(self, query, params=None):
        """Execute SELECT query and return results."""
        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        columns = [description[0] for description in cursor.description]
        results = cursor.fetchall()
        return pd.DataFrame(results, columns=columns)
    
    def get_total_revenue(self, start_date=None, end_date=None, status_filter=None):
        """Get total revenue with optional filters."""
        query = 'SELECT COALESCE(SUM(amount), 0) as total_revenue FROM fact_sales WHERE 1=1'
        params = []
        
        if start_date:
            query += ' AND date >= ?'
            params.append(start_date)
        if end_date:
            query += ' AND date <= ?'
            params.append(end_date)
        if status_filter:
            query += ' AND status = ?'
            params.append(status_filter)
        
        result = self.execute_query(query, params)
        return result['total_revenue'].values[0]
    
    def get_total_orders(self, start_date=None, end_date=None):
        """Get total unique orders."""
        query = 'SELECT COUNT(DISTINCT order_id) as total_orders FROM fact_sales WHERE 1=1'
        params = []
        
        if start_date:
            query += ' AND date >= ?'
            params.append(start_date)
        if end_date:
            query += ' AND date <= ?'
            params.append(end_date)
        
        result = self.execute_query(query, params)
        return result['total_orders'].values[0]
    
    def get_total_units(self, start_date=None, end_date=None):
        """Get total units sold."""
        query = 'SELECT COALESCE(SUM(qty), 0) as total_units FROM fact_sales WHERE 1=1'
        params = []
        
        if start_date:
            query += ' AND date >= ?'
            params.append(start_date)
        if end_date:
            query += ' AND date <= ?'
            params.append(end_date)
        
        result = self.execute_query(query, params)
        return result['total_units'].values[0]
    
    def get_cancelled_orders_count(self):
        """Get count of cancelled orders."""
        query = "SELECT COUNT(DISTINCT order_id) as cancelled_count FROM fact_sales WHERE status = 'CANCELLED'"
        result = self.execute_query(query)
        return result['cancelled_count'].values[0]
    
    def get_revenue_by_category(self):
        """Get revenue breakdown by category."""
        query = '''
            SELECT category, COALESCE(SUM(amount), 0) as revenue, COUNT(DISTINCT order_id) as orders
            FROM fact_sales
            GROUP BY category
            ORDER BY revenue DESC
        '''
        return self.execute_query(query)
    
    def get_revenue_by_state(self):
        """Get revenue breakdown by state."""
        query = '''
            SELECT ship_state, COALESCE(SUM(amount), 0) as revenue, COUNT(DISTINCT order_id) as orders
            FROM fact_sales
            WHERE ship_state IS NOT NULL
            GROUP BY ship_state
            ORDER BY revenue DESC
        '''
        return self.execute_query(query)
    
    def get_top_products(self, limit=10):
        """Get top products by revenue."""
        query = '''
            SELECT sku, style, category, 
                   COALESCE(SUM(amount), 0) as revenue,
                   COALESCE(SUM(qty), 0) as units,
                   COUNT(DISTINCT order_id) as orders
            FROM fact_sales
            GROUP BY sku, style, category
            ORDER BY revenue DESC
            LIMIT ?
        '''
        return self.execute_query(query, [limit])
    
    def get_status_distribution(self):
        """Get order status distribution."""
        query = '''
            SELECT status, COUNT(DISTINCT order_id) as order_count, COALESCE(SUM(amount), 0) as revenue
            FROM fact_sales
            GROUP BY status
            ORDER BY order_count DESC
        '''
        return self.execute_query(query)
    
    def get_fulfilment_comparison(self):
        """Compare Amazon vs Merchant fulfilment."""
        query = '''
            SELECT fulfilment, 
                   COUNT(DISTINCT order_id) as orders,
                   COALESCE(SUM(amount), 0) as revenue,
                   COALESCE(SUM(qty), 0) as units
            FROM fact_sales
            GROUP BY fulfilment
        '''
        return self.execute_query(query)
    
    def get_b2b_analysis(self):
        """B2B vs B2C analysis."""
        query = '''
            SELECT b2b, 
                   COUNT(DISTINCT order_id) as orders,
                   COALESCE(SUM(amount), 0) as revenue,
                   COALESCE(AVG(amount), 0) as avg_order_value
            FROM fact_sales
            GROUP BY b2b
        '''
        return self.execute_query(query)
    
    def get_monthly_revenue(self):
        """Get monthly revenue trend."""
        query = '''
            SELECT DATE(date, 'start of month') as month,
                   COALESCE(SUM(amount), 0) as revenue,
                   COUNT(DISTINCT order_id) as orders
            FROM fact_sales
            GROUP BY DATE(date, 'start of month')
            ORDER BY month
        '''
        return self.execute_query(query)
    
    def get_daily_revenue(self):
        """Get daily revenue trend."""
        query = '''
            SELECT date,
                   COALESCE(SUM(amount), 0) as revenue,
                   COUNT(DISTINCT order_id) as orders
            FROM fact_sales
            GROUP BY date
            ORDER BY date
        '''
        return self.execute_query(query)
