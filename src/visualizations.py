import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def create_revenue_trend_chart(data, period='Daily'):
    """Create revenue trend line chart."""
    fig = px.line(
        data,
        x='date' if period == 'Daily' else 'month',
        y='revenue',
        title=f'{period} Revenue Trend',
        labels={'revenue': 'Revenue (INR)', 'date': 'Date', 'month': 'Month'},
        markers=True
    )
    fig.update_layout(
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    return fig


def create_category_revenue_chart(data):
    """Create category revenue bar chart."""
    fig = px.bar(
        data,
        x='category',
        y='revenue',
        title='Revenue by Category',
        labels={'revenue': 'Revenue (INR)', 'category': 'Category'},
        color='revenue',
        color_continuous_scale='Blues'
    )
    fig.update_layout(
        xaxis_tickangle=-45,
        template='plotly_white',
        height=400
    )
    return fig


def create_status_distribution_chart(data):
    """Create order status distribution chart."""
    fig = px.bar(
        data,
        x='status',
        y='order_count',
        title='Order Status Distribution',
        labels={'order_count': 'Orders', 'status': 'Status'},
        color='order_count',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(
        xaxis_tickangle=-45,
        template='plotly_white',
        height=400
    )
    return fig


def create_top_products_chart(data, limit=10):
    """Create top products revenue chart."""
    data_sorted = data.head(limit).sort_values('revenue')
    fig = go.Figure(data=[
        go.Bar(
            y=data_sorted['sku'],
            x=data_sorted['revenue'],
            orientation='h',
            marker=dict(color=data_sorted['revenue'], colorscale='Greens'),
            text=data_sorted['revenue'],
            textposition='auto'
        )
    ])
    fig.update_layout(
        title=f'Top {limit} Products by Revenue',
        xaxis_title='Revenue (INR)',
        yaxis_title='SKU',
        template='plotly_white',
        height=400,
        hovermode='y unified'
    )
    return fig


def create_state_revenue_chart(data, limit=15):
    """Create state revenue bar chart."""
    data_sorted = data.head(limit).sort_values('revenue')
    fig = go.Figure(data=[
        go.Bar(
            y=data_sorted['ship_state'],
            x=data_sorted['revenue'],
            orientation='h',
            marker=dict(color=data_sorted['revenue'], colorscale='Oranges'),
            text=data_sorted['revenue'],
            textposition='auto'
        )
    ])
    fig.update_layout(
        title=f'Top {limit} States by Revenue',
        xaxis_title='Revenue (INR)',
        yaxis_title='State',
        template='plotly_white',
        height=500,
        hovermode='y unified'
    )
    return fig


def create_fulfilment_comparison_chart(data):
    """Create fulfilment method comparison."""
    fig = px.bar(
        data,
        x='fulfilment',
        y=['orders', 'revenue'],
        title='Amazon vs Merchant Fulfilment Comparison',
        labels={'value': 'Count / Revenue (INR)', 'fulfilment': 'Fulfilment'},
        barmode='group'
    )
    fig.update_layout(
        template='plotly_white',
        height=400
    )
    return fig


def create_size_distribution_chart(data):
    """Create size distribution chart."""
    size_dist = data.groupby('size').agg({
        'qty': 'sum',
        'order_id': 'count'
    }).reset_index()
    size_dist.columns = ['size', 'units', 'orders']
    
    fig = px.bar(
        size_dist,
        x='size',
        y='units',
        title='Units Sold by Size',
        labels={'units': 'Units', 'size': 'Size'},
        color='units',
        color_continuous_scale='Purples'
    )
    fig.update_layout(
        template='plotly_white',
        height=400
    )
    return fig


def create_b2b_comparison_chart(data):
    """Create B2B vs B2C comparison."""
    fig = px.bar(
        data,
        x='b2b',
        y=['orders', 'revenue'],
        title='B2B vs B2C Comparison',
        labels={'value': 'Count / Revenue (INR)', 'b2b': 'Order Type'},
        barmode='group'
    )
    fig.update_xaxes(
        ticktext=['B2C', 'B2B'],
        tickvals=[False, True]
    )
    fig.update_layout(
        template='plotly_white',
        height=400
    )
    return fig


def create_shipping_method_chart(data):
    """Create shipping method distribution."""
    shipping_dist = data.groupby('ship_service_level').agg({
        'qty': 'sum',
        'amount': 'sum'
    }).reset_index()
    shipping_dist.columns = ['method', 'units', 'revenue']
    shipping_dist = shipping_dist.sort_values('revenue', ascending=False)
    
    fig = px.pie(
        shipping_dist,
        values='revenue',
        names='method',
        title='Revenue by Shipping Method'
    )
    fig.update_layout(
        height=400
    )
    return fig


def create_monthly_comparison_chart(data):
    """Create monthly orders vs revenue."""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=data['month'],
        y=data['orders'],
        name='Orders',
        yaxis='y'
    ))
    
    fig.add_trace(go.Scatter(
        x=data['month'],
        y=data['revenue'],
        name='Revenue',
        yaxis='y2',
        line=dict(color='red', width=3)
    ))
    
    fig.update_layout(
        title='Monthly Orders and Revenue Trend',
        xaxis_title='Month',
        yaxis_title='Orders',
        yaxis2=dict(title='Revenue (INR)', overlaying='y', side='right'),
        template='plotly_white',
        height=400,
        hovermode='x unified'
    )
    return fig
