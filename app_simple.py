import streamlit as st
import sys
sys.path.insert(0, '.')

st.set_page_config(page_title="Amazon Sales Dashboard", layout="wide")

st.title("Amazon India E-Commerce Sales Dashboard")

try:
    st.write("Loading data...")
    from src.data_loader import load_excel_data
    from src.data_cleaning import clean_sales_data
    from src.database import SalesDatabase
    from src.metrics import KPICalculator
    
    raw_df = load_excel_data()
    st.write(f"✓ Data loaded: {len(raw_df)} rows")
    
    cleaned_df, quality_summary, _ = clean_sales_data(raw_df)
    st.write(f"✓ Data cleaned: {len(cleaned_df)} rows")
    
    db = SalesDatabase('database/sales.db')
    db.connect()
    db.create_schema()
    db.load_data(cleaned_df)
    st.write("✓ Database created")
    
    kpi_calc = KPICalculator(db)
    kpis = kpi_calc.get_all_kpis()
    
    st.divider()
    st.subheader("Key Metrics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
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
    
    st.success("Dashboard loaded successfully!")
    db.close()
    
except Exception as e:
    st.error(f"Error: {str(e)}")
    import traceback
    st.write(traceback.format_exc())
