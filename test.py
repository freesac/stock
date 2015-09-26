import tushare as ts
ts.set_token('577c33e4d462eba6c110d77e39408eaa08f6e91c7e2cb4275fad192e374b1ddb')
print('this is only a test')
st = ts.Market()
df = st.MktEqud(tradeDate='20150925', field='ticker,secShortName,preClosePrice,openPrice,highestPrice,lowestPrice,closePrice,turnoverVol,turnoverRate')
df['ticker'] = df['ticker'].map(lambda x: str(x).zfill(6))
df1 = st.MktEqud(tradeDate='20150924', field='ticker,secShortName,preClosePrice,openPrice,highestPrice,lowestPrice,closePrice,turnoverVol,turnoverRate')
df1['ticker'] = df1['ticker'].map(lambda x: str(x).zfill(6))
good_stock = [0 for i in range(3000)]

i = 0
for index,row in df1.iterrows():
	preClosePrice = row['preClosePrice']
	closePrice = row['closePrice']
	if((closePrice/preClosePrice) >= 1.098):
		print(row['ticker'])
		good_stock[i] = row['ticker']
		i = i+1
		
def was_top(top_list, stockcode):
		for i in range(3000):
			if(stockcode == top_list[i]):
				return 1
		return 0
		
for index,row in df.iterrows():
	openPrice = row['openPrice']
	closePrice = row['closePrice']
	lowestPrice = row['lowestPrice']
	highestPrice = row['highestPrice']
	preClosePrice = row['preClosePrice']
	if(was_top(good_stock,row['ticker'])):
		if(row['openPrice'] == 0):
		 	continue
		if(row['openPrice']<=row['closePrice']):
			diff = (row['closePrice']-row['openPrice'])/row['openPrice']
			if(diff < 0.03):	
				if(((openPrice/lowestPrice) > 1.01)and ((highestPrice/closePrice)> 1.01)):
					print(row['ticker'],lowestPrice,openPrice,closePrice,highestPrice)
		else:
			diff = (row['openPrice']-row['closePrice'])/row['closePrice']	
			if(diff < 0.03):	
				if(((closePrice/lowestPrice) > 1.01)and ((highestPrice/openPrice)> 1.01)):
					print(row['ticker'],row['secShortName'],lowestPrice,openPrice,closePrice,highestPrice)
	
		
