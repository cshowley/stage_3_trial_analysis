import pandas as pd
import pandas_datareader.data as web
from datetime import datetime, timedelta


df = pd.read_excel('PDUFAdates.xlsx')

buyDate = 60
sellDate = 3

# Reformat dates so Python can read them
df.DATE = df.DATE.apply(lambda x: datetime.strptime(str(x), '%Y%m%d'))

# Will append data to this dictionary as it gets aggregated
di = {'ticker': [], '3 months': [], '1 week': [], 'percent change': [], 'SPY change': []}

# Iterate through each ticker
for i,ticker in enumerate(df.TICKER):
	print ticker
	ticker = str(ticker.strip())
	try:
		announceDate = df.DATE.iloc[i]
		# Temporary list that will append to dictionary if all values exist
		tmp = []
		# Ignore dates that haven't occurred yet
		if announceDate > datetime.now():
			print 'Planned announcement; skip for now'
			continue
		# Get 3 month old data
		tmp.append(web.DataReader(ticker, 'yahoo', datetime.strptime(datetime.strftime(announceDate - timedelta(days=buyDate), '%Y-%m-%d'), '%Y-%m-%d'), datetime.strptime(datetime.strftime(announceDate, '%Y-%m-%d'), '%Y-%m-%d'))['Adj Close'].iloc[0])
		# Get 1 week old data
		tmp.append(web.DataReader(ticker, 'yahoo', datetime.strptime(datetime.strftime(announceDate - timedelta(days=sellDate), '%Y-%m-%d'), '%Y-%m-%d'), datetime.strptime(datetime.strftime(announceDate, '%Y-%m-%d'), '%Y-%m-%d'))['Adj Close'].iloc[0])
		tmp.append(ticker)
		# Calculate percent change
		tmp.append((tmp[1] / tmp[0]) - 1)
		# Calculate change in S&P via SPY ETF
		tmp.append((web.DataReader('SPY','yahoo', datetime.strptime(datetime.strftime(announceDate - timedelta(days=sellDate), '%Y-%m-%d'), '%Y-%m-%d'), datetime.strptime(datetime.strftime(announceDate, '%Y-%m-%d'), '%Y-%m-%d'))['Adj Close'].iloc[0] / 
			web.DataReader('SPY','yahoo', datetime.strptime(datetime.strftime(announceDate - timedelta(days=buyDate), '%Y-%m-%d'), '%Y-%m-%d'), datetime.strptime(datetime.strftime(announceDate, '%Y-%m-%d'), '%Y-%m-%d'))['Adj Close'].iloc[0]) - 1)
		if len(tmp) == 5:
			di['3 months'].append(tmp[0])
			di['1 week'].append(tmp[1])
			di['ticker'].append(tmp[2])	
			di['percent change'].append(tmp[3])
			di['SPY change'].append(tmp[4])
	# For ticker data that python can't grab with pandas_datareader, escape it
	except:
		print 'No data available for %s' % ticker

# Write results to dataframe and save to csv
df = pd.DataFrame(di).sort_values('percent change', ascending=False)
df.to_csv('results.csv', index=None)
print 'Average change in SPY:', df['SPY change'].mean()
print 'Average change in co:', df['percent change'].mean()

