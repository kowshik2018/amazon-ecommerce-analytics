import pandas as pd
from datetime import datetime, timedelta


class FilterManager:
    def __init__(self, df):
        self.df = df
        try:
            self.available_statuses = sorted([s for s in df['status'].unique().tolist() if isinstance(s, str)])
            self.available_categories = sorted([c for c in df['category'].unique().tolist() if isinstance(c, str)])
            self.available_fulfilments = sorted([f for f in df['fulfilment'].unique().tolist() if isinstance(f, str)])
            self.available_states = sorted([s for s in df['ship_state'].unique() if s and isinstance(s, str)])
            self.available_cities = sorted([c for c in df['ship_city'].unique() if c and isinstance(c, str)])
            self.available_sizes = sorted([sz for sz in df['size'].unique().tolist() if isinstance(sz, str)])
            self.available_channels = sorted([ch for ch in df['sales_channel'].unique().tolist() if isinstance(ch, str)])
            self.min_date = pd.to_datetime(df['date']).min()
            self.max_date = pd.to_datetime(df['date']).max()
        except Exception as e:
            raise ValueError(f"Error initializing FilterManager: {str(e)}")
    
    def apply_filters(self, date_range=None, status=None, category=None, 
                     fulfilment=None, state=None, city=None, size=None, 
                     b2b=None, channel=None):
        """Apply multiple filters to dataframe."""
        filtered_df = self.df.copy()
        
        if date_range:
            start_date, end_date = date_range
            filtered_df = filtered_df[
                (filtered_df['date'] >= start_date) & 
                (filtered_df['date'] <= end_date)
            ]
        
        if status:
            if isinstance(status, str):
                status = [status]
            filtered_df = filtered_df[filtered_df['status'].isin(status)]
        
        if category:
            if isinstance(category, str):
                category = [category]
            filtered_df = filtered_df[filtered_df['category'].isin(category)]
        
        if fulfilment:
            if isinstance(fulfilment, str):
                fulfilment = [fulfilment]
            filtered_df = filtered_df[filtered_df['fulfilment'].isin(fulfilment)]
        
        if state:
            if isinstance(state, str):
                state = [state]
            filtered_df = filtered_df[filtered_df['ship_state'].isin(state)]
        
        if city:
            if isinstance(city, str):
                city = [city]
            filtered_df = filtered_df[filtered_df['ship_city'].isin(city)]
        
        if size:
            if isinstance(size, str):
                size = [size]
            filtered_df = filtered_df[filtered_df['size'].isin(size)]
        
        if b2b is not None:
            filtered_df = filtered_df[filtered_df['b2b'] == b2b]
        
        if channel:
            if isinstance(channel, str):
                channel = [channel]
            filtered_df = filtered_df[filtered_df['sales_channel'].isin(channel)]
        
        return filtered_df
    
    def get_filter_options(self):
        """Get all available filter options."""
        return {
            'date_range': (self.min_date.date(), self.max_date.date()),
            'statuses': self.available_statuses,
            'categories': self.available_categories,
            'fulfilments': self.available_fulfilments,
            'states': self.available_states,
            'cities': self.available_cities,
            'sizes': self.available_sizes,
            'channels': self.available_channels
        }
