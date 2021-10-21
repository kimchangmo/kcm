import time
import pyupbit
import datetime
import schedule
from fbprophet import Prophet
import requests
import pandas as pd
import webbrowser
import json

access = "GauxnmxqFhWqPmxPDgfrLxx4zNF2V66N5MZ1A3X8"
secret = "X5BYYzfckghA2IRbTG46caZw4xbdzxXcGoxquMtK"

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

predicted_close_price = 0
def predict_price(ticker):
    """Prophet으로 당일 종가 가격 예측"""
    global predicted_close_price
    df = pyupbit.get_ohlcv(ticker, interval="minute60")
    df = df.reset_index()
    df['ds'] = df['index']
    df['y'] = df['close']
    data = df[['ds','y']]
    model = Prophet()
    model.fit(data)
    future = model.make_future_dataframe(periods=24, freq='H')
    forecast = model.predict(future)

    closeDf = forecast[forecast['ds'] == forecast.iloc[-1]['ds'].replace(hour=9)]
    if len(closeDf) == 0:
        closeDf = forecast[forecast['ds'] == data.iloc[-1]['ds'].replace(hour=9)]
    closeValue = closeDf['yhat'].values[0]
    predicted_close_price = closeValue

rsi = 0
def rsiindex(symbol):
    global rsi
    url = "https://api.upbit.com/v1/candles/minutes/3"
    querystring = {"market":symbol,"count":"500"}
    response = requests.request("GET", url, params=querystring)
    data = response.json()
    df = pd.DataFrame(data)
    df=df.reindex(index=df.index[::-1]).reset_index()
    df['close']=df["trade_price"]
    
    def rsi(ohlc: pd.DataFrame, period: int = 14):
        ohlc["close"] = ohlc["close"]
        delta = ohlc["close"].diff()
        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0
        _gain = up.ewm(com=(period - 1), min_periods=period).mean()
        _loss = down.abs().ewm(com=(period - 1), min_periods=period).mean()
        RS = _gain / _loss
        return pd.Series(100 - (100 / (1 + RS)), name="RSI")

    rsi = rsi(df, 14).iloc[-1]
    #print(symbol)
    #print('Upbit 3 minute RSI:', rsi)
    #print('')

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
all_coin = pyupbit.get_tickers('KRW')
all_coin.remove('KRW-MED')
all_coin.remove('KRW-CRE')

rsi_list = [] #rsi 목록
#rsi_name = [] #상승예상코인명
#rsi_list_desc = []
#price_name = [] #상승예상코인명
#price_gap = [] #상승예상수치
#price_gap_desc = []

#1,2,3번코인 구매여부(true = 구매가능, false = 구매불가)
count1 = 'true'
count2 = 'true'
count3 = 'true'

#전체코인 rsi 정보 array 만들고 시작
"""
----------------------------------수정필요---------------------------------
k = 0
while k < len(all_coin) :
    try:
        data = {
            'coinName' : all_coin[n],
            'rsi' : rsiindex(all_coin[n])
        }
        
        global json_rsi_info = json.dumps(data)
        
    except Exception as e:
        print(e)
        time.sleep(1)
json_rsi_dict = json.loads(json_rsi_info)
----------------------------------수정필요---------------------------------
"""
k = 0
while k < len(all_coin) :
    try:
        print("find rsi ing...")
        rsiindex(all_coin[k])
        rsi_list.append(rsi)
        k = k+1
    except Exception as e:
        print(e)
        time.sleep(1)
print("rsi_list_length",len(rsi_list))
print("coin_length",len(all_coin))
# 자동매매 시작
while True:
    n = 0
    while n < len(all_coin) : #총 코인 갯수
        try:
            coin = all_coin[n]
            #predict_price(coin)

            now = datetime.datetime.now()
            start_time = get_start_time(coin)
            end_time = start_time + datetime.timedelta(days=1)

            if start_time + datetime.timedelta(seconds=600) < now < end_time - datetime.timedelta(seconds=60):
                print("ing... :",  coin)
                current_price = get_current_price(coin)
                #rsi 확인
                rsiindex(coin)
                print("old_rsi :",  rsi_list[n])
                print("now_rsi :",  rsi)
                if (30 > rsi_list[n]) and (30 < rsi) and (count1 == 'true' or count2 == 'true' or count3 == 'true') and (upbit.get_balance(coin[4:]) == 0):
                    if count1 == 'true':
                        upbit.buy_market_order(coin, 50000)
                        buycoin_0 = coin
                        buy_price_0 = current_price
                        print("buy coin 1:",  buycoin_0)
                        count1 = 'false'
                        time.sleep(5)
                    elif count2 == 'true':
                        upbit.buy_market_order(coin, 50000)
                        buycoin_1 = coin
                        buy_price_1 = current_price
                        print("buy coin 2:",  buycoin_1)
                        count2 = 'false'
                        time.sleep(5)
                    elif count3 == 'true':
                        upbit.buy_market_order(coin, 50000)
                        buycoin_2 = coin
                        buy_price_2 = current_price
                        print("buy coin 3:",  buycoin_2)
                        count3 = 'false'
                        time.sleep(5)
                        
                #1번구매코인 익절/손절
                if (count1 == 'false') :
                    rsiindex(buycoin_0)
                if (count1 == 'false') and (rsi > 50) :
                    btc_0 = upbit.get_balance(buycoin_0[4:])
                    upbit.sell_market_order(buycoin_0, btc_0)
                    count1 = 'true'
                #elif (count1 == 'false') :
                #    btc_0 = upbit.get_balance(buycoin_0[4:])
                #    upbit.sell_market_order(buycoin_0, btc_0)
                #    count1 = 'true'

                #2번구매코인 익절/손절
                if (count2 == 'false') :
                    rsiindex(buycoin_1)
                if (count2 == 'false') and (rsi > 50) :
                    btc_1 = upbit.get_balance(buycoin_1[4:])
                    upbit.sell_market_order(buycoin_1, btc_1)
                    count2 = 'true'
                #elif (count2 == 'false') :
                #    btc_1 = upbit.get_balance(buycoin_1[4:])
                #    upbit.sell_market_order(buycoin_1, btc_1)
                #    count2 = 'true'
                    
                #3번구매코인 익절/손절
                if (count3 == 'false') :
                    rsiindex(buycoin_2)
                if (count3 == 'false') and (rsi > 50) :
                    btc_2 = upbit.get_balance(buycoin_2[4:])
                    upbit.sell_market_order(buycoin_2, btc_2)
                    count3 = 'true'
                #elif (count3 == 'false') :
                #    btc_2 = upbit.get_balance(buycoin_2[4:])
                #    upbit.sell_market_order(buycoin_2, btc_2)
                #    count3 = 'true'

                #수동판매 대응
                if (count1 == 'false') and (upbit.get_balance(buycoin_0[4:]) == 0) :
                    count1 = 'true'
                if (count2 == 'false') and (upbit.get_balance(buycoin_1[4:]) == 0) :
                    count2 = 'true'
                if (count3 == 'false') and (upbit.get_balance(buycoin_2[4:]) == 0) :
                    count3 = 'true'

            else:
                print("only sell...")
                if (count1 == 'false') :
                    rsiindex(buycoin_0)
                if (count1 == 'false') and (rsi > 50) :
                    btc_0 = upbit.get_balance(buycoin_0[4:])
                    upbit.sell_market_order(buycoin_0, btc_0)
                    count1 = 'true'
                    
                if (count2 == 'false') :
                    rsiindex(buycoin_1)
                if (count2 == 'false') and (rsi > 50) :
                    btc_1 = upbit.get_balance(buycoin_1[4:])
                    upbit.sell_market_order(buycoin_1, btc_1)
                    count2 = 'true'
                    
                if (count3 == 'false') :
                    rsiindex(buycoin_2)
                if (count3 == 'false') and (rsi > 50) :
                    btc_2 = upbit.get_balance(buycoin_2[4:])
                    upbit.sell_market_order(buycoin_2, btc_2)
                    count3 = 'true'
            
            #rsi 정보 업데이트
            #print("what coin : ",  coin)
            #print("old_rsi : ", rsi_list[n])
            rsiindex(coin)
            rsi_list[n] = rsi
            #print("new_rsi : ", rsi_list[n])
            
            n = n+1
            time.sleep(1)
        except Exception as e:
            print(e)
            time.sleep(1)
""" 
price_gap_desc.sort(reverse=True) #내림차순 정렬
price_gap_index_0 = price_gap.index(price_gap_desc[0]) #1번 상승코인
price_gap_index_1 = price_gap.index(price_gap_desc[1]) #2번 상승코인
price_gap_index_2 = price_gap.index(price_gap_desc[2]) #3번 상승코인
print("price_gap_index_0", price_gap_index_0)
print("제일높은수치0 : " ,price_name[price_gap_index_0], " : ", price_gap_desc[0])
print("제일높은수치1 : " ,price_name[price_gap_index_1], " : ", price_gap_desc[1])
print("제일높은수치2 : " ,price_name[price_gap_index_2], " : ", price_gap_desc[2])
while True:
    try:
        rsiindex(price_name[price_gap_index_0])
        if rsi < 25 and price_gap_desc[0] > 1.05 :
            upbit.buy_market_order(price_name[price_gap_index_0], 10000)
            print("1번구매")
        rsiindex(price_name[price_gap_index_1])
        if rsi < 25 and price_gap_desc[1] > 1.05 :
            upbit.buy_market_order(price_name[price_gap_index_1], 10000)
            print("2번구매")
        rsiindex(price_name[price_gap_index_2])
        if rsi < 25 and price_gap_desc[2] > 1.05 :
            upbit.buy_market_order(price_name[price_gap_index_2], 10000)
            print("3번구매")
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
n = 0
while n < 112 : #총 코인 갯수
    try:
        coin = all_coin[n]
        now = datetime.datetime.now()
        start_time = get_start_time(coin)
        end_time = start_time + datetime.timedelta(days=1)
        print("진행중... :",  coin)
        rsiindex(coin)
        rsi_name.append(coin)
        rsi_list.append(rsi)
        rsi_list_desc.append(rsi)
        
        n = n+1
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
rsi_list_desc.sort() #오름차순 정렬
price_gap_index_0 = rsi_list.index(rsi_list_desc[0])
price_gap_index_1 = rsi_list.index(rsi_list_desc[1])
price_gap_index_2 = rsi_list.index(rsi_list_desc[2])
print("rsi_row_1 : " ,rsi_name[price_gap_index_0], " : ", rsi_list_desc[0])
print("rsi_row_2 : " ,rsi_name[price_gap_index_1], " : ", rsi_list_desc[1])
print("rsi_row_3 : " ,rsi_name[price_gap_index_2], " : ", rsi_list_desc[2])
"""
