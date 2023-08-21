import yfinance as yf
import pandas as pd
from datetime import date

def pull_yfin(full_data):
  sp500 = yf.download("^GSPC", start= '2019-1-1', end=str(date.today())) 
  idx = pd.date_range('2019-1-1', str(date.today()))
  sp500 = sp500.reindex(idx, fill_value=0)
  price_mem = -1
  vol_mem = -1
  for i in range(len(sp500['Adj Close'])):
    if sp500['Adj Close'][i] == 0:
      if i == 0:
        if sp500['Open'][i+1] == 0:
          price_mem = sp500['Open'][i+2]
          vol_mem = sp500['Volume'][i+2]
        else:
          price_mem = sp500['Open'][i+1]
          vol_mem = sp500['Volume'][i+1]
      sp500['Open'][i] = price_mem
      sp500['High'][i] = price_mem
      sp500['Low'][i] = price_mem
      sp500['Close'][i] = price_mem
      sp500['Adj Close'][i] = price_mem
      sp500['Volume'][i] = vol_mem
    else:
      vol_mem = sp500['Volume'][i]
      price_mem = sp500['Adj Close'][i]
  full_data.drop_duplicates(inplace=True, subset=['vin'])
  sp500 = pd.DataFrame(sp500)
  sp500 = sp500.groupby(sp500.index).first()
  full_data.reset_index()
  full_data = full_data.merge(sp500, left_on="Date", right_index=True, how="left")
  return full_data