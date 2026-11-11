import pandas as pd


class InsightsGenerator:
    def __init__(self, kpi_calc, df):
        self.kpi = kpi_calc
        self.df = df
    
    def generate_all_insights(self):
        """Generate all business insights."""
        insights = []
        
        insights.append(self._revenue_insight())
        insights.append(self._orders_insight())
        insights.append(self._units_insight())
        insights.append(self._top_category_insight())
        insights.append(self._top_state_insight())
        insights.append(self._top_product_insight())
        insights.append(self._popular_size_insight())
        insights.append(self._cancellation_insight())
        insights.append(self._fulfilment_insight())
        insights.append(self._b2b_insight())
        
        return [i for i in insights if i is not None]
    
    def _revenue_insight(self):
        """Total revenue insight."""
        revenue = self.kpi.get_total_revenue()
        return {
            'title': 'Total Revenue Generated',
            'observation': f'INR {revenue:,.2f} total revenue',
            'interpretation': 'Overall sales performance across the period',
            'recommendation': 'Analyze revenue trends over time to identify growth patterns',
            'limitation': 'Does not account for product costs or profitability'
        }
    
    def _orders_insight(self):
        """Total orders insight."""
        orders = self.kpi.get_total_orders()
        avg_order_value = self.kpi.get_average_order_value()
        return {
            'title': 'Order Volume',
            'observation': f'{orders:,} unique orders with average value of INR {avg_order_value:,.2f}',
            'interpretation': 'Customer demand and transaction size patterns',
            'recommendation': 'Focus on increasing order frequency and value',
            'limitation': 'Average order value may be skewed by high-value outliers'
        }
    
    def _units_insight(self):
        """Total units insight."""
        units = self.kpi.get_total_units()
        return {
            'title': 'Units Sold',
            'observation': f'{units:,} total units sold',
            'interpretation': 'Volume of products moved to customers',
            'recommendation': 'Monitor inventory levels and reorder points',
            'limitation': 'Does not reflect actual inventory turnover rate'
        }
    
    def _top_category_insight(self):
        """Top performing category."""
        categories = self.kpi.get_category_performance()
        if len(categories) > 0:
            top_cat = categories.iloc[0]
            return {
                'title': 'Top Performing Category',
                'observation': f'{top_cat["category"]} generates INR {top_cat["revenue"]:,.2f} (top category)',
                'interpretation': 'Kurta and Set categories drive majority of revenue',
                'recommendation': 'Invest in inventory and marketing for top categories',
                'limitation': 'Category performance may vary seasonally'
            }
        return None
    
    def _top_state_insight(self):
        """Top performing state."""
        states = self.kpi.get_state_performance()
        if len(states) > 0:
            top_state = states.iloc[0]
            return {
                'title': 'Top Performing State',
                'observation': f'{top_state["ship_state"]} leads with INR {top_state["revenue"]:,.2f} revenue',
                'interpretation': 'Geographic concentration in metropolitan states',
                'recommendation': 'Expand logistics and inventory in high-performing states',
                'limitation': 'May reflect regional population density rather than market potential'
            }
        return None
    
    def _top_product_insight(self):
        """Top performing product."""
        products = self.kpi.get_top_products(limit=1)
        if len(products) > 0:
            top_prod = products.iloc[0]
            return {
                'title': 'Best Performing Product',
                'observation': f'SKU {top_prod["sku"]} ({top_prod["style"]}) generates INR {top_prod["revenue"]:,.2f}',
                'interpretation': 'Product-market fit for specific SKUs',
                'recommendation': 'Increase stock and promotion for high-performing SKUs',
                'limitation': 'Success may depend on temporary trends or promotions'
            }
        return None
    
    def _popular_size_insight(self):
        """Most popular size."""
        size_dist = self.df.groupby('size').agg({
            'qty': 'sum',
            'amount': 'sum'
        }).sort_values('qty', ascending=False)
        
        if len(size_dist) > 0:
            top_size = size_dist.index[0]
            top_qty = size_dist.iloc[0]['qty']
            return {
                'title': 'Most Popular Size',
                'observation': f'Size {top_size} accounts for {top_qty:,} units sold',
                'interpretation': 'Customer body type preferences',
                'recommendation': 'Ensure adequate inventory of popular sizes',
                'limitation': 'Size popularity may change with seasonal collections'
            }
        return None
    
    def _cancellation_insight(self):
        """Cancellation rate insight."""
        cancel_rate = self.kpi.get_cancellation_rate()
        return {
            'title': 'Order Cancellation Rate',
            'observation': f'{cancel_rate}% of orders were cancelled',
            'interpretation': 'Customer satisfaction and operational issues',
            'recommendation': f'Investigate cancellation reasons; target is typically <5%',
            'limitation': 'Dataset does not include cancellation reasons'
        }
    
    def _fulfilment_insight(self):
        """Fulfilment comparison insight."""
        fulfilment = self.kpi.get_fulfilment_comparison()
        if len(fulfilment) >= 2:
            amazon = fulfilment[fulfilment['fulfilment'] == 'AMAZON'].iloc[0] if len(fulfilment[fulfilment['fulfilment'] == 'AMAZON']) > 0 else None
            merchant = fulfilment[fulfilment['fulfilment'] == 'MERCHANT'].iloc[0] if len(fulfilment[fulfilment['fulfilment'] == 'MERCHANT']) > 0 else None
            
            if amazon is not None and merchant is not None:
                amazon_pct = (amazon['orders'] / (amazon['orders'] + merchant['orders'])) * 100
                return {
                    'title': 'Fulfilment Method Comparison',
                    'observation': f'Amazon fulfilment: {amazon_pct:.1f}%, Merchant: {100-amazon_pct:.1f}%',
                    'interpretation': 'Logistics strategy split between first-party and third-party',
                    'recommendation': 'Optimize cost and delivery speed between fulfilment methods',
                    'limitation': 'Does not include fulfillment cost or delivery time analysis'
                }
        return None
    
    def _b2b_insight(self):
        """B2B analysis insight."""
        b2b_data = self.kpi.get_b2b_analysis()
        if len(b2b_data) >= 2:
            b2b = b2b_data[b2b_data['b2b'] == True].iloc[0] if len(b2b_data[b2b_data['b2b'] == True]) > 0 else None
            b2c = b2b_data[b2b_data['b2b'] == False].iloc[0] if len(b2b_data[b2b_data['b2b'] == False]) > 0 else None
            
            if b2b is not None and b2c is not None:
                b2b_pct = (b2b['orders'] / (b2b['orders'] + b2c['orders'])) * 100
                return {
                    'title': 'B2B vs B2C Sales Mix',
                    'observation': f'B2B: {b2b_pct:.1f}% of orders, B2C: {100-b2b_pct:.1f}%',
                    'interpretation': 'Business model composition and revenue diversification',
                    'recommendation': 'Develop targeted strategies for each segment',
                    'limitation': 'B2B classification may not reflect actual business relationship'
                }
        return None
