@echo off
REM Amazon Sales Dashboard Launcher
REM This file runs the Streamlit dashboard

cd /d "C:\Users\Admin\Desktop\amazon-ecommerce-analytics"

echo ============================================================
echo AMAZON SALES DASHBOARD LAUNCHER
echo ============================================================
echo.
echo Installing dependencies...
pip install -q streamlit pandas numpy plotly sqlalchemy openpyxl

echo.
echo Starting dashboard...
echo Dashboard will open at: http://localhost:8501
echo Press Ctrl+C to stop
echo.

python -m streamlit run app.py

pause
