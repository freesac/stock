import tushare as ts
ts.set_token('577c33e4d462eba6c110d77e39408eaa08f6e91c7e2cb4275fad192e374b1ddb')
print('this is just only a test')
st = ts.Market()
df = st.MktEqud(tradeDate='20151009', field='ticker,secShortName,preClosePrice,openPrice,highestPrice,lowestPrice,closePrice,turnoverVol,turnoverRate')
df['ticker'] = df['ticker'].map(lambda x: str(x).zfill(6))
df1 = st.MktEqud(tradeDate='20151008', field='ticker,secShortName,preClosePrice,openPrice,highestPrice,lowestPrice,closePrice,turnoverVol,turnoverRate')
df1['ticker'] = df1['ticker'].map(lambda x: str(x).zfill(6))
good_stock = [0 for i in range(3000)]

def is_star(open_price, close_price, lowest_price,highest_price):
	is_star = 0
	if(open_price <= close_price):
		diff = (close_price - open_price)/open_price
		if(diff < 0.03):
			if(((open_price/lowest_price) > 1.01)and ((highest_price/close_price)> 1.01)):
				is_star = 1
	else:
		diff = (open_price - close_price)/close_price
		if(diff < 0.03):
			if(((close_price/lowest_price) > 1.01)and ((highest_price/open_price)> 1.01)):
				is_star = 1
	return is_star
		
i = 0
for index,row in df1.iterrows():
	openPrice = row['openPrice']
	closePrice = row['closePrice']
	lowestPrice = row['lowestPrice']
	highestPrice = row['highestPrice']
	if(row['openPrice'] == 0):
		 	continue
	if(is_star(openPrice,closePrice,lowestPrice,highestPrice)):
		print(row['ticker'])
		good_stock[i] = row['ticker']
		i = i+1
		
def was_star(top_list, stockcode):
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
	if(row['openPrice'] == 0):
		 	continue
	if(was_star(good_stock,row['ticker'])):
		if(is_star(openPrice,closePrice,lowestPrice,highestPrice)):
			print(row['ticker'],row['secShortName'],lowestPrice,openPrice,closePrice,highestPrice)