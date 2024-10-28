import os
import pandas as pd
import yfinance as yf
from django.shortcuts import render
from django.conf import settings
from datetime import datetime

def index(request):
    abovenifty50_final = []
    belownifty50_final = []
    error_message = None

    if request.method == 'POST':
        # Fetch Start Date and End Date from the form
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # Convert dates to datetime objects for filtering
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            error_message = "Invalid date format. Please enter dates in YYYY-MM-DD format."

        # Load stock list from Excel file
        stock_file_path = os.path.join(settings.MEDIA_ROOT, 'Stock Data.xlsx')
        stock_list = pd.read_excel(stock_file_path)
        stock_list['Company'] = stock_list['Company'].str.replace('.NS', '', regex=False)

        stock_data = pd.DataFrame()

        # Fetch historical data for each company within the given date range
        for stock_symbol in stock_list['Company']:
            try:
                data = yf.Ticker(stock_symbol + '.NS').history(start=start_date, end=end_date)['Close']
                if not data.empty:
                    stock_data[stock_symbol] = data
            except Exception as e:
                print(f"An error occurred for {stock_symbol}: {e}")

        # Fetch Nifty50 data
        nifty = yf.Ticker('^NSEI').history(start=start_date, end=end_date)['Close']
        df_nifty = pd.DataFrame(nifty)
        df_nifty.columns = ['Nifty50']
        stock_data.index = stock_data.index.tz_localize(None)
        df_nifty.index = df_nifty.index.tz_localize(None)

        # Combine stock data with Nifty50 data
        all_data = pd.concat([stock_data, df_nifty], axis=1)

        # Calculate percentage change from the first to last date
        first_day_data = all_data.iloc[0]
        last_day_data = all_data.iloc[-1]
        percentage_change = ((last_day_data - first_day_data) / first_day_data) * 100
        sorted_percentage_change = percentage_change.sort_values(ascending=False)
        df1 = pd.DataFrame(sorted_percentage_change, columns=["PercentageChange"])

        # Identify threshold for Nifty50 value
        nifty_value = df1.loc['Nifty50', "PercentageChange"]

        # Separate into Above and Below Nifty50 lists
        abovenifty50 = df1[df1["PercentageChange"] > nifty_value].reset_index()
        abovenifty50.rename(columns={'index': 'Company'}, inplace=True)
        abovenifty50_final = pd.merge(abovenifty50, stock_list, on='Company', how='left').to_dict(orient='records')

        belownifty50 = df1[df1["PercentageChange"] < nifty_value].reset_index()
        belownifty50.rename(columns={'index': 'Company'}, inplace=True)
        belownifty50_final = pd.merge(belownifty50, stock_list, on='Company', how='left').to_dict(orient='records')

    return render(request, 'myapp/index.html', {
        'abovenifty50_final': abovenifty50_final,
        'belownifty50_final': belownifty50_final,
        'error_message': error_message,
    })
