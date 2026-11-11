import subprocess
import sys
import os

os.chdir(r'C:\Users\Admin\Desktop\amazon-ecommerce-analytics')

print("=" * 60)
print("AMAZON SALES DASHBOARD LAUNCHER")
print("=" * 60)

print("\nStarting Streamlit app...")
print("Dashboard will open at: http://localhost:8501")
print("\nPress Ctrl+C to stop the app\n")

try:
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
except KeyboardInterrupt:
    print("\n\nApp stopped.")
except Exception as e:
    print(f"Error: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure you're in the right folder")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Check if port 8501 is available")
