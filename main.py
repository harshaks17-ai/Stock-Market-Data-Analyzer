import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import yfinance as yf

# -------------------------------
# Create folders
# -------------------------------

folders = ["data", "images", "reports", "outputs"]

for folder in folders:
    os.makedirs(folder, exist_ok=True)

# -------------------------------
# User Inputs
# -------------------------------

ticker = input("Enter Stock Ticker Symbol: ").upper()
start_date = input("Enter Start Date (YYYY-MM-DD): ")
end_date = input("Enter End Date (YYYY-MM-DD): ")

# -------------------------------
# Fetch Stock Data
# -------------------------------

print("\nFetching stock data...")

try:
    df = yf.download(ticker, start=start_date, end=end_date)

    if df.empty:
        raise Exception("No data found.")

    csv_path = f"data/{ticker}_stock_data.csv"
    df.to_csv(csv_path)

    print(f"Data saved to {csv_path}")

except Exception as e:
    print("Error fetching data:", e)
    exit()

# -------------------------------
# Data Cleaning
# -------------------------------

print("\nCleaning data...")

df.dropna(inplace=True)

# -------------------------------
# Daily Returns
# -------------------------------

df['Daily Return'] = df['Close'].pct_change()

# -------------------------------
# Moving Averages
# -------------------------------

df['MA20'] = df['Close'].rolling(window=20).mean()
df['MA50'] = df['Close'].rolling(window=50).mean()

# -------------------------------
# Volatility
# -------------------------------

volatility = df['Daily Return'].std()

# -------------------------------
# Highest and Lowest Prices
# -------------------------------

highest_price = df['High'].max()
lowest_price = df['Low'].min()

# -------------------------------
# Summary Statistics
# -------------------------------

print("\n========== STOCK SUMMARY ==========")
print(f"Ticker: {ticker}")
print(f"Highest Price: {highest_price:.2f}")
print(f"Lowest Price: {lowest_price:.2f}")
print(f"Volatility: {volatility:.4f}")
print("===================================")

# -------------------------------
# Plot Closing Price
# -------------------------------

plt.figure(figsize=(12,6))
plt.plot(df['Close'], label='Closing Price')
plt.title(f'{ticker} Closing Price')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()

close_chart = f"images/{ticker}_closing_price.png"
plt.savefig(close_chart)
plt.close()

# -------------------------------
# Plot Moving Averages
# -------------------------------

plt.figure(figsize=(12,6))
plt.plot(df['Close'], label='Close Price')
plt.plot(df['MA20'], label='20-Day MA')
plt.plot(df['MA50'], label='50-Day MA')

plt.title(f'{ticker} Moving Averages')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()

ma_chart = f"images/{ticker}_moving_average.png"
plt.savefig(ma_chart)
plt.close()

# -------------------------------
# Return Distribution
# -------------------------------

plt.figure(figsize=(10,5))
sns.histplot(df['Daily Return'].dropna(), bins=50)

plt.title(f'{ticker} Daily Return Distribution')

return_chart = f"images/{ticker}_returns_distribution.png"
plt.savefig(return_chart)
plt.close()

# -------------------------------
# Generate Report
# -------------------------------

report_path = f"reports/{ticker}_report.txt"

with open(report_path, "w") as file:
    file.write("STOCK MARKET ANALYSIS REPORT\n")
    file.write("============================\n\n")

    file.write(f"Ticker: {ticker}\n")
    file.write(f"Highest Price: {highest_price:.2f}\n")
    file.write(f"Lowest Price: {lowest_price:.2f}\n")
    file.write(f"Volatility: {volatility:.4f}\n")

print(f"\nReport generated: {report_path}")

print("\nCharts saved successfully.")
print("Project execution completed.")