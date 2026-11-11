import pandas as pd
from datetime import datetime, timedelta


class KPICalculator:
    def __init__(self, db):
        self.db = db
    
    def get_total_revenue(self, start_date=None, end_date=None):
        """Total Revenue: Sum of all order amounts."""
        return self.db.get_total_revenue(start_date, end_date)
    
    def get_total_orders(self, start_date=None, end_date=None):
        """Total Orders: Count of distinct Order IDs."""
        return self.db.get_total_orders(start_date, end_date)
    
    def get_total_units(self, start_date=None, end_date=None):
        """Total Units Sold: Sum of quantities."""
        return self.db.get_total_units(start_date, end_date)
    
    def get_average_order_value(self, start_date=None, end_date=None):
        """Average Order Value: Total Revenue / Total Orders."""
        total_revenue = self.get_total_revenue(start_date, end_date)
        total_orders = self.get_total_orders(start_date, end_date)
        
        if total_orders == 0:
            return 0
        return round(total_revenue / total_orders, 2)
    
    def get_cancellation_rate(self):
        """Cancellation Rate: (Cancelled Orders / Total Orders) * 100."""
        total_orders = self.get_total_orders()
        cancelled_orders = self.db.get_cancelled_orders_count()
        
        if total_orders == 0:
            return 0
        return round((cancelled_orders / total_orders) * 100, 2)
    
    def get_delivered_orders(self):
        """Count of orders with 'Shipped - Delivered to Buyer' status."""
        query = "SELECT COUNT(DISTINCT order_id) as delivered_count FROM fact_sales WHERE status = 'SHIPPED - DELIVERED TO BUYER'"
        result = self.db.execute_query(query)
        return result['delivered_count'].values[0] if len(result) > 0 else 0
    
    def get_shipped_orders(self):
        """Count of orders with 'Shipped' status."""
        query = "SELECT COUNT(DISTINCT order_id) as shipped_count FROM fact_sales WHERE status IN ('SHIPPED', 'SHIPPED - DELIVERED TO BUYER', 'SHIPPED - OUT FOR DELIVERY')"
        result = self.db.execute_query(query)
        return result['shipped_count'].values[0] if len(result) > 0 else 0
    
    def get_fulfillment_percentage(self):
        """Fulfilment Percentage: (Non-Cancelled Orders / Total Orders) * 100."""
        total_orders = self.get_total_orders()
        cancelled = self.db.get_cancelled_orders_count()
        fulfilled = total_orders - cancelled
        
        if total_orders == 0:
            return 0
        return round((fulfilled / total_orders) * 100, 2)
    
    def get_revenue_growth(self, current_period_start, current_period_end, previous_period_start, previous_period_end):
        """Revenue Growth: ((Current Revenue - Previous Revenue) / Previous Revenue) * 100."""
        current_revenue = self.get_total_revenue(current_period_start, current_period_end)
        previous_revenue = self.get_total_revenue(previous_period_start, previous_period_end)
        
        if previous_revenue == 0:
            return 0 if current_revenue == 0 else 100
        return round(((current_revenue - previous_revenue) / previous_revenue) * 100, 2)
    
    def get_monthly_revenue_data(self):
        """Get monthly revenue trend data."""
        return self.db.get_monthly_revenue()
    
    def get_daily_revenue_data(self):
        """Get daily revenue trend data."""
        return self.db.get_daily_revenue()
    
    def get_category_performance(self):
        """Get category-wise revenue and orders."""
        return self.db.get_revenue_by_category()
    
    def get_state_performance(self):
        """Get state-wise revenue and orders."""
        return self.db.get_revenue_by_state()
    
    def get_top_products(self, limit=10):
        """Get top N products by revenue."""
        return self.db.get_top_products(limit)
    
    def get_status_distribution(self):
        """Get order status breakdown."""
        return self.db.get_status_distribution()
    
    def get_fulfilment_comparison(self):
        """Compare fulfilment methods."""
        return self.db.get_fulfilment_comparison()
    
    def get_b2b_analysis(self):
        """Analyze B2B vs B2C orders."""
        return self.db.get_b2b_analysis()
    
    def get_all_kpis(self, start_date=None, end_date=None):
        """Get all main KPIs at once."""
        return {
            'total_revenue': self.get_total_revenue(start_date, end_date),
            'total_orders': self.get_total_orders(start_date, end_date),
            'total_units': self.get_total_units(start_date, end_date),
            'average_order_value': self.get_average_order_value(start_date, end_date),
            'cancellation_rate': self.get_cancellation_rate(),
            'delivered_orders': self.get_delivered_orders(),
            'shipped_orders': self.get_shipped_orders(),
            'fulfillment_percentage': self.get_fulfillment_percentage()
        }
