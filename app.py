import streamlit as st
import pandas as pd
from pathlib import Path
from src.data_loader import load_excel_data, validate_columns, get_dataset_summary
from src.data_cleaning import clean_sales_data
from src.database import SalesDatabase
from src.metrics import KPICalculator
from src.filters import FilterManager
from src.analysis import InsightsGenerator
from src.visualizations import *
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta


st.set_page_config(
    page_title="Amazon Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .kpi-value {
        font-size: 28px;
        font-weight: bold;
        color: #1f77b4;
    }
    .kpi-label {
        font-size: 14px;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_app():
    """Initialize app with data loading and processing."""
    try:
        raw_df = load_excel_data()
        
        is_valid, missing_cols = validate_columns(raw_df)
        if not is_valid:
            st.error(f"Missing required columns: {missing_cols}")
            st.stop()
        
        cleaned_df, quality_summary, cleaning_report = clean_sales_data(raw_df)
        
        db = SalesDatabase('database/sales.db')
        db.connect()
        db.create_schema()
        db.load_data(cleaned_df)
        db.close()
        
        kpi_calc = KPICalculator(db)
        filter_mgr = FilterManager(cleaned_df)
        insights_gen = InsightsGenerator(kpi_calc, cleaned_df)
        
        return cleaned_df, db, kpi_calc, filter_mgr, insights_gen, quality_summary, cleaning_report
    except Exception as e:
        st.error(f"Error initializing app: {str(e)}")
        st.stop()


cleaned_df, db, kpi_calc, filter_mgr, insights_gen, quality_summary, cleaning_report = initialize_app()

# Reconnect database for this thread
db.connect()


st.sidebar.title("Amazon Sales Analytics")
page = st.sidebar.radio(
    "Select Page",
    [
        "Executive Overview",
        "Sales Analysis",
        "Product Analysis",
        "Geographic Analysis",
        "Order & Fulfilment",
        "Business Analysis",
        "Data Quality",
        "SQL Explorer"
    ]
)

filter_options = filter_mgr.get_filter_options()

st.sidebar.header("Filters")
date_range = st.sidebar.date_input(
    "Date Range",
    value=(filter_options['date_range'][0], filter_options['date_range'][1]),
    min_value=filter_options['date_range'][0],
    max_value=filter_options['date_range'][1]
)

selected_status = st.sidebar.multiselect(
    "Order Status",
    filter_options['statuses'],
    default=filter_options['statuses']
)

selected_category = st.sidebar.multiselect(
    "Category",
    filter_options['categories'],
    default=filter_options['categories']
)

selected_fulfilment = st.sidebar.multiselect(
    "Fulfilment",
    filter_options['fulfilments'],
    default=filter_options['fulfilments']
)

selected_state = st.sidebar.multiselect(
    "State",
    filter_options['states'],
    default=filter_options['states'][:10]
)

selected_size = st.sidebar.multiselect(
    "Size",
    filter_options['sizes'],
    default=filter_options['sizes']
)

b2b_filter = st.sidebar.checkbox("B2B Orders Only")

filtered_df = filter_mgr.apply_filters(
    date_range=tuple(pd.to_datetime(date_range)),
    status=selected_status,
    category=selected_category,
    fulfilment=selected_fulfilment,
    state=selected_state,
    size=selected_size,
    b2b=b2b_filter if b2b_filter else None
)


if page == "Executive Overview":
    st.title("Executive Overview")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    kpis = kpi_calc.get_all_kpis()
    
    with col1:
        st.metric("Total Revenue", f"₹{kpis['total_revenue']:,.0f}")
    with col2:
        st.metric("Total Orders", f"{kpis['total_orders']:,}")
    with col3:
        st.metric("Total Units", f"{kpis['total_units']:,}")
    with col4:
        st.metric("Avg Order Value", f"₹{kpis['average_order_value']:,.0f}")
    with col5:
        st.metric("Cancellation Rate", f"{kpis['cancellation_rate']}%")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        monthly_data = kpi_calc.get_monthly_revenue_data()
        fig = create_revenue_trend_chart(monthly_data, period='Monthly')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        daily_data = kpi_calc.get_daily_revenue_data()
        fig = create_revenue_trend_chart(daily_data, period='Daily')
        st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        category_data = kpi_calc.get_category_performance()
        fig = create_category_revenue_chart(category_data)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        status_data = kpi_calc.get_status_distribution()
        fig = create_status_distribution_chart(status_data)
        st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        top_products = kpi_calc.get_top_products(limit=10)
        fig = create_top_products_chart(top_products, limit=10)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fulfilment_data = kpi_calc.get_fulfilment_comparison()
        fig = create_fulfilment_comparison_chart(fulfilment_data)
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    st.subheader("Executive Summary")
    insights = insights_gen.generate_all_insights()
    for insight in insights[:3]:
        st.info(f"**{insight['title']}**: {insight['observation']}")


elif page == "Sales Analysis":
    st.title("Sales Analysis")
    
    tab1, tab2, tab3 = st.tabs(["Revenue Trends", "Monthly Performance", "Category Analysis"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            monthly_data = kpi_calc.get_monthly_revenue_data()
            fig = px.line(monthly_data, x='month', y='revenue', title='Monthly Revenue', markers=True)
            fig.update_layout(template='plotly_white', height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            daily_data = kpi_calc.get_daily_revenue_data()
            fig = px.area(daily_data, x='date', y='revenue', title='Daily Revenue Trend')
            fig.update_layout(template='plotly_white', height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        monthly_data = kpi_calc.get_monthly_revenue_data()
        fig = create_monthly_comparison_chart(monthly_data)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        category_data = kpi_calc.get_category_performance()
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(category_data, values='revenue', names='category', title='Revenue Share by Category')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = create_category_revenue_chart(category_data)
            st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(category_data, use_container_width=True)


elif page == "Product Analysis":
    st.title("Product Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        top_by_revenue = kpi_calc.get_top_products(limit=15)
        fig = create_top_products_chart(top_by_revenue, limit=15)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        size_dist = cleaned_df.groupby('size').agg({'qty': 'sum'}).sort_values('qty', ascending=False)
        fig = px.bar(size_dist, title='Units by Size', labels={'qty': 'Units', 'size': 'Size'})
        fig.update_layout(template='plotly_white', height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Category Performance")
    category_data = kpi_calc.get_category_performance()
    st.dataframe(category_data, use_container_width=True)
    
    st.subheader("Top 20 Products")
    top_products = kpi_calc.get_top_products(limit=20)
    st.dataframe(top_products, use_container_width=True)


elif page == "Geographic Analysis":
    st.title("Geographic Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        state_data = kpi_calc.get_state_performance()
        fig = create_state_revenue_chart(state_data, limit=15)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        state_orders = state_data.sort_values('orders', ascending=False).head(15)
        fig = go.Figure(data=[
            go.Bar(
                y=state_orders['ship_state'],
                x=state_orders['orders'],
                orientation='h',
                marker=dict(color=state_orders['orders'], colorscale='Blues'),
                text=state_orders['orders'],
                textposition='auto'
            )
        ])
        fig.update_layout(
            title='Top 15 States by Orders',
            xaxis_title='Orders',
            yaxis_title='State',
            template='plotly_white',
            height=400,
            hovermode='y unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("State-wise Performance")
    st.dataframe(state_data, use_container_width=True)


elif page == "Order & Fulfilment":
    st.title("Order & Fulfilment Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        status_data = kpi_calc.get_status_distribution()
        fig = create_status_distribution_chart(status_data)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fulfilment_data = kpi_calc.get_fulfilment_comparison()
        fig = create_fulfilment_comparison_chart(fulfilment_data)
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Order Status Details")
    st.dataframe(kpi_calc.get_status_distribution(), use_container_width=True)
    
    st.subheader("Fulfilment Comparison")
    st.dataframe(kpi_calc.get_fulfilment_comparison(), use_container_width=True)


elif page == "Business Analysis":
    st.title("Business Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        b2b_data = kpi_calc.get_b2b_analysis()
        fig = create_b2b_comparison_chart(b2b_data)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        shipping_data = cleaned_df.groupby('ship_service_level').agg({
            'amount': 'sum'
        }).reset_index().sort_values('amount', ascending=False)
        fig = px.pie(shipping_data, values='amount', names='ship_service_level', 
                    title='Revenue by Shipping Method')
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("B2B Analysis")
    st.dataframe(kpi_calc.get_b2b_analysis(), use_container_width=True)


elif page == "Data Quality":
    st.title("Data Quality Report")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Rows", quality_summary['final_rows'])
    with col2:
        st.metric("Total Columns", quality_summary['total_columns'])
    with col3:
        st.metric("Unique Orders", quality_summary['unique_order_ids'])
    
    st.subheader("Missing Values")
    missing = quality_summary['missing_values_summary']
    missing_df = pd.DataFrame({
        'Column': missing.keys(),
        'Missing Count': missing.values()
    })
    missing_df = missing_df[missing_df['Missing Count'] > 0].sort_values('Missing Count', ascending=False)
    st.dataframe(missing_df, use_container_width=True)
    
    st.subheader("Data Issues Found")
    for issue in cleaning_report.issues:
        st.warning(f"{issue['type']}: {issue['count']} - {issue['description']}")


elif page == "SQL Explorer":
    st.title("SQL Query Explorer")
    
    query_type = st.selectbox(
        "Select Query",
        [
            "Total Revenue",
            "Category Revenue",
            "State Revenue",
            "Top Products",
            "Status Distribution",
            "Fulfilment Comparison",
            "B2B Analysis",
            "Monthly Revenue"
        ]
    )
    
    queries = {
        "Total Revenue": "SELECT COALESCE(SUM(amount), 0) as total_revenue FROM fact_sales",
        "Category Revenue": "SELECT category, COALESCE(SUM(amount), 0) as revenue FROM fact_sales GROUP BY category ORDER BY revenue DESC",
        "State Revenue": "SELECT ship_state, COALESCE(SUM(amount), 0) as revenue FROM fact_sales GROUP BY ship_state ORDER BY revenue DESC",
        "Top Products": "SELECT sku, COALESCE(SUM(amount), 0) as revenue FROM fact_sales GROUP BY sku ORDER BY revenue DESC LIMIT 10",
        "Status Distribution": "SELECT status, COUNT(*) as count FROM fact_sales GROUP BY status",
        "Fulfilment Comparison": "SELECT fulfilment, COUNT(*) as count FROM fact_sales GROUP BY fulfilment",
        "B2B Analysis": "SELECT b2b, COUNT(*) as count FROM fact_sales GROUP BY b2b",
        "Monthly Revenue": "SELECT DATE(order_date, 'start of month') as month, COALESCE(SUM(amount), 0) as revenue FROM fact_sales GROUP BY month ORDER BY month"
    }
    
    query = queries[query_type]
    
    st.code(query, language="sql")
    
    if st.button("Execute Query"):
        try:
            result = db.execute_query(query)
            st.dataframe(result, use_container_width=True)
            
            csv = result.to_csv(index=False)
            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name=f"query_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"Query error: {str(e)}")
