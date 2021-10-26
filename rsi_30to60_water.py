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
oldrsi = 0
'''
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
'''
def rsiindex(symbol):
    global rsi
    global oldrsi
    url = "https://api.upbit.com/v1/candles/minutes/3"
    querystring = {"market":symbol,"count":"500"}
    response = requests.request("GET", url, params=querystring)
    data = response.json()
    df = pd.DataFrame(data)
    df=df.reindex(index=df.index[::-1]).reset_index()
    bit_mask = df['index'] > 0
    
    def rsi(ohlc: pd.DataFrame, period: int = 14):
        ohlc["trade_price"] = ohlc["trade_price"]
        delta = ohlc["trade_price"].diff()
        gains, declines = delta.copy(), delta.copy()
        gains[gains < 0] = 0
        declines[declines > 0] = 0

        _gain = gains.ewm(com=(period - 1), min_periods=period).mean()
        _loss = declines.abs().ewm(com=(period - 1), min_periods=period).mean()

        RS = _gain / _loss
        return pd.Series(100 - (100 / (1 + RS)), name="RSI")

    oldrsi = rsi(df[bit_mask], 14).iloc[-1]
    rsi = rsi(df, 14).iloc[-1]
    print(symbol)
    print('Upbit 3 minute oldRSI:', oldrsi)
    print('Upbit now RSI:', rsi)
    #print('')

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
all_coin = pyupbit.get_tickers('KRW')
all_coin.remove('KRW-MED')
all_coin.remove('KRW-CRE')

#1,2,3번코인 구매여부(true = 구매가능, false = 구매불가)
count1 = 'true'
count2 = 'true'
count3 = 'true'
count4 = 'true'
count5 = 'true'
count6 = 'true'
count7 = 'true'
count8 = 'true'
count9 = 'true'
count10 = 'true'

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
                #print("ing... :",  coin)
                current_price = get_current_price(coin)
                #rsi 확인
                rsiindex(coin)
                if (30 > oldrsi) and (30 < rsi) and (count1 == 'true' or count2 == 'true' or count3 == 'true' or count4 == 'true' or count5 == 'true' or count6 == 'true' or count7 == 'true' or count8 == 'true' or count9 == 'true' or count10 == 'true') and (upbit.get_balance(coin[4:]) == 0):
                    if count1 == 'true':
                        krw = get_balance("KRW")
                        if krw > 50000:
                            upbit.buy_market_order(coin, 50000)
                            buycoin_0 = coin
                            buy_price_0 = current_price
                            print("buy coin 1:",  buycoin_0)
                            count1 = 'false'
                            #구매시간
                            buytime1 = datetime.datetime.now() + datetime.timedelta(minutes=4)
                            time.sleep(3)
                    elif count2 == 'true':
                        krw = get_balance("KRW")
                        if krw > 50000:
                            upbit.buy_market_order(coin, 50000)
                            buycoin_1 = coin
                            buy_price_1 = current_price
                            print("buy coin 2:",  buycoin_1)
                            count2 = 'false'
                            #구매시간
                            buytime2 = datetime.datetime.now() + datetime.timedelta(minutes=4)
                            time.sleep(3)
                    elif count3 == 'true':
                        krw = get_balance("KRW")
                        if krw > 50000:
                            upbit.buy_market_order(coin, 50000)
                            buycoin_2 = coin
                            buy_price_2 = current_price
                            print("buy coin 3:",  buycoin_2)
                            count3 = 'false'
                            #구매시간
                            buytime3 = datetime.datetime.now() + datetime.timedelta(minutes=4)
                            time.sleep(3)
                    elif count4 == 'true':
                        krw = get_balance("KRW")
                        if krw > 50000:
                            upbit.buy_market_order(coin, 50000)
                            buycoin_3 = coin
                            buy_price_3 = current_price
                            print("buy coin 4:",  buycoin_3)
                            count4 = 'false'
                            #구매시간
                            buytime4 = datetime.datetime.now() + datetime.timedelta(minutes=4)
                            time.sleep(3)
                    elif count5 == 'true':
                        krw = get_balance("KRW")
                        if krw > 50000:
                            upbit.buy_market_order(coin, 50000)
                            buycoin_4 = coin
                            buy_price_4 = current_price
                            print("buy coin 5:",  buycoin_4)
                            count5 = 'false'
                            #구매시간
                            buytime5 = datetime.datetime.now() + datetime.timedelta(minutes=4)
                            time.sleep(3)
                    elif count6 == 'true':
                        krw = get_balance("KRW")
                        if krw > 50000:
                            upbit.buy_market_order(coin, 50000)
                            buycoin_5 = coin
                            buy_price_5 = current_price
                            print("buy coin 6:",  buycoin_5)
                            count6 = 'false'
                            #구매시간
                            buytime6 = datetime.datetime.now() + datetime.timedelta(minutes=4)
                            time.sleep(3)
                    elif count7 == 'true':
                        krw = get_balance("KRW")
                        if krw > 50000:
                            upbit.buy_market_order(coin, 50000)
                            buycoin_6 = coin
                            buy_price_6 = current_price
                            print("buy coin 7:",  buycoin_6)
                            count7 = 'false'
                            #구매시간
                            buytime7 = datetime.datetime.now() + datetime.timedelta(minutes=4)
                            time.sleep(3)
                    elif count8 == 'true':
                        krw = get_balance("KRW")
                        if krw > 50000:
                            upbit.buy_market_order(coin, 50000)
                            buycoin_7 = coin
                            buy_price_7 = current_price
                            print("buy coin 8:",  buycoin_7)
                            count8 = 'false'
                            #구매시간
                            buytime8 = datetime.datetime.now() + datetime.timedelta(minutes=4)
                            time.sleep(3)
                    elif count9 == 'true':
                        krw = get_balance("KRW")
                        if krw > 50000:
                            upbit.buy_market_order(coin, 50000)
                            buycoin_8 = coin
                            buy_price_8 = current_price
                            print("buy coin 9:",  buycoin_8)
                            count9 = 'false'
                            #구매시간
                            buytime9 = datetime.datetime.now() + datetime.timedelta(minutes=4)
                            time.sleep(3)
                    elif count10 == 'true':
                        krw = get_balance("KRW")
                        if krw > 50000:
                            upbit.buy_market_order(coin, 50000)
                            buycoin_9 = coin
                            buy_price_9 = current_price
                            print("buy coin 10:",  buycoin_9)
                            count10 = 'false'
                            #구매시간
                            buytime10 = datetime.datetime.now() + datetime.timedelta(minutes=4)
                            time.sleep(3)
                        
                #1번구매코인 익절/손절
                if (count1 == 'false') :
                    rsiindex(buycoin_0)
                if (count1 == 'false') and (rsi > 60) :
                    btc_0 = upbit.get_balance(buycoin_0[4:])
                    upbit.sell_market_order(buycoin_0, btc_0)
                    count1 = 'true'
                #다시 돌파시 물타기
                elif (count1 == 'false') and (30 > oldrsi) and (30 < rsi) and (now > buytime1):
                    krw = get_balance("KRW")
                    if krw > 50000:
                        upbit.buy_market_order(buycoin_0, 50000)
                        #구매시간 갱신
                        buytime1 = datetime.datetime.now() + datetime.timedelta(minutes=4)
                        time.sleep(1)
                        
                #2번구매코인 익절/손절
                if (count2 == 'false') :
                    rsiindex(buycoin_1)
                if (count2 == 'false') and (rsi > 60) :
                    btc_1 = upbit.get_balance(buycoin_1[4:])
                    upbit.sell_market_order(buycoin_1, btc_1)
                    count2 = 'true'
                #다시 돌파시 물타기
                elif (count2 == 'false') and (30 > oldrsi) and (30 < rsi) and (now > buytime2):
                    krw = get_balance("KRW")
                    if krw > 50000:
                        upbit.buy_market_order(buycoin_1, 50000)
                        #구매시간 갱신
                        buytime2 = datetime.datetime.now() + datetime.timedelta(minutes=4)
                        time.sleep(1)
                    
                #3번구매코인 익절/손절
                if (count3 == 'false') :
                    rsiindex(buycoin_2)
                if (count3 == 'false') and (rsi > 60) :
                    btc_2 = upbit.get_balance(buycoin_2[4:])
                    upbit.sell_market_order(buycoin_2, btc_2)
                    count3 = 'true'
                #다시 돌파시 물타기
                elif (count3 == 'false') and (30 > oldrsi) and (30 < rsi) and (now > buytime3):
                    krw = get_balance("KRW")
                    if krw > 50000:
                        upbit.buy_market_order(buycoin_2, 50000)
                        #구매시간 갱신
                        buytime3 = datetime.datetime.now() + datetime.timedelta(minutes=4)
                        time.sleep(1)
                    
                #4번구매코인 익절/손절
                if (count4 == 'false') :
                    rsiindex(buycoin_3)
                if (count4 == 'false') and (rsi > 60) :
                    btc_3 = upbit.get_balance(buycoin_3[4:])
                    upbit.sell_market_order(buycoin_3, btc_3)
                    count4 = 'true'
                #다시 돌파시 물타기
                elif (count4 == 'false') and (30 > oldrsi) and (30 < rsi) and (now > buytime4):
                    krw = get_balance("KRW")
                    if krw > 50000:
                        upbit.buy_market_order(buycoin_3, 50000)
                        #구매시간 갱신
                        buytime4 = datetime.datetime.now() + datetime.timedelta(minutes=4)
                        time.sleep(1)
                        
                #5번구매코인 익절/손절
                if (count5 == 'false') :
                    rsiindex(buycoin_4)
                if (count5 == 'false') and (rsi > 60) :
                    btc_4 = upbit.get_balance(buycoin_4[4:])
                    upbit.sell_market_order(buycoin_4, btc_4)
                    count5 = 'true'
                #다시 돌파시 물타기
                elif (count5 == 'false') and (30 > oldrsi) and (30 < rsi) and (now > buytime5):
                    krw = get_balance("KRW")
                    if krw > 50000:
                        upbit.buy_market_order(buycoin_4, 50000)
                        #구매시간 갱신
                        buytime5 = datetime.datetime.now() + datetime.timedelta(minutes=4)
                        time.sleep(1)
                        
                #6번구매코인 익절/손절
                if (count6 == 'false') :
                    rsiindex(buycoin_5)
                if (count6 == 'false') and (rsi > 60) :
                    btc_5 = upbit.get_balance(buycoin_5[4:])
                    upbit.sell_market_order(buycoin_5, btc_5)
                    count6 = 'true'
                #다시 돌파시 물타기
                elif (count6 == 'false') and (30 > oldrsi) and (30 < rsi) and (now > buytime6):
                    krw = get_balance("KRW")
                    if krw > 50000:
                        upbit.buy_market_order(buycoin_5, 50000)
                        #구매시간 갱신
                        buytime6 = datetime.datetime.now() + datetime.timedelta(minutes=4)
                        time.sleep(1)
                        
                #7번구매코인 익절/손절
                if (count7 == 'false') :
                    rsiindex(buycoin_6)
                if (count7 == 'false') and (rsi > 60) :
                    btc_6 = upbit.get_balance(buycoin_6[4:])
                    upbit.sell_market_order(buycoin_6, btc_6)
                    count7 = 'true'
                #다시 돌파시 물타기
                elif (count7 == 'false') and (30 > oldrsi) and (30 < rsi) and (now > buytime7):
                    krw = get_balance("KRW")
                    if krw > 50000:
                        upbit.buy_market_order(buycoin_6, 50000)
                        #구매시간 갱신
                        buytime7 = datetime.datetime.now() + datetime.timedelta(minutes=4)
                        time.sleep(1)
                        
                #8번구매코인 익절/손절
                if (count8 == 'false') :
                    rsiindex(buycoin_7)
                if (count8 == 'false') and (rsi > 60) :
                    btc_7 = upbit.get_balance(buycoin_7[4:])
                    upbit.sell_market_order(buycoin_7, btc_7)
                    count8 = 'true'
                #다시 돌파시 물타기
                elif (count8 == 'false') and (30 > oldrsi) and (30 < rsi) and (now > buytime8):
                    krw = get_balance("KRW")
                    if krw > 50000:
                        upbit.buy_market_order(buycoin_7, 50000)
                        #구매시간 갱신
                        buytime8 = datetime.datetime.now() + datetime.timedelta(minutes=4)
                        time.sleep(1)
                        
                #9번구매코인 익절/손절
                if (count9 == 'false') :
                    rsiindex(buycoin_8)
                if (count9 == 'false') and (rsi > 60) :
                    btc_8 = upbit.get_balance(buycoin_8[4:])
                    upbit.sell_market_order(buycoin_8, btc_8)
                    count9 = 'true'
                #다시 돌파시 물타기
                elif (count9 == 'false') and (30 > oldrsi) and (30 < rsi) and (now > buytime9):
                    krw = get_balance("KRW")
                    if krw > 50000:
                        upbit.buy_market_order(buycoin_8, 50000)
                        #구매시간 갱신
                        buytime9 = datetime.datetime.now() + datetime.timedelta(minutes=4)
                        time.sleep(1)
                        
                #10번구매코인 익절/손절
                if (count10 == 'false') :
                    rsiindex(buycoin_9)
                if (count10 == 'false') and (rsi > 60) :
                    btc_9 = upbit.get_balance(buycoin_9[4:])
                    upbit.sell_market_order(buycoin_9, btc_9)
                    count10 = 'true'
                #다시 돌파시 물타기
                elif (count10 == 'false') and (30 > oldrsi) and (30 < rsi) and (now > buytime10):
                    krw = get_balance("KRW")
                    if krw > 50000:
                        upbit.buy_market_order(buycoin_9, 50000)
                        #구매시간 갱신
                        buytime10 = datetime.datetime.now() + datetime.timedelta(minutes=4)
                        time.sleep(1)

                #수동판매 대응
                if (count1 == 'false') and (upbit.get_balance(buycoin_0[4:]) == 0) :
                    count1 = 'true'
                if (count2 == 'false') and (upbit.get_balance(buycoin_1[4:]) == 0) :
                    count2 = 'true'
                if (count3 == 'false') and (upbit.get_balance(buycoin_2[4:]) == 0) :
                    count3 = 'true'

            else:
                #1번구매코인 익절/손절
                if (count1 == 'false') :
                    rsiindex(buycoin_0)
                if (count1 == 'false') and (rsi > 60) :
                    btc_0 = upbit.get_balance(buycoin_0[4:])
                    upbit.sell_market_order(buycoin_0, btc_0)
                    count1 = 'true'
                #다시 돌파시 물타기
                elif (count1 == 'false') and (30 > oldrsi) and (30 < rsi) and (now > buytime1):
                    krw = get_balance("KRW")
                    if krw > 50000:
                        upbit.buy_market_order(buycoin_0, 50000)
                        #구매시간 갱신
                        buytime1 = datetime.datetime.now() + datetime.timedelta(minutes=4)
                        time.sleep(1)
                        
                #2번구매코인 익절/손절
                if (count2 == 'false') :
                    rsiindex(buycoin_1)
                if (count2 == 'false') and (rsi > 60) :
                    btc_1 = upbit.get_balance(buycoin_1[4:])
                    upbit.sell_market_order(buycoin_1, btc_1)
                    count2 = 'true'
                #다시 돌파시 물타기
                elif (count2 == 'false') and (30 > oldrsi) and (30 < rsi) and (now > buytime2):
                    krw = get_balance("KRW")
                    if krw > 50000:
                        upbit.buy_market_order(buycoin_1, 50000)
                        #구매시간 갱신
                        buytime2 = datetime.datetime.now() + datetime.timedelta(minutes=4)
                        time.sleep(1)
                    
                #3번구매코인 익절/손절
                if (count3 == 'false') :
                    rsiindex(buycoin_2)
                if (count3 == 'false') and (rsi > 60) :
                    btc_2 = upbit.get_balance(buycoin_2[4:])
                    upbit.sell_market_order(buycoin_2, btc_2)
                    count3 = 'true'
                #다시 돌파시 물타기
                elif (count3 == 'false') and (30 > oldrsi) and (30 < rsi) and (now > buytime3):
                    krw = get_balance("KRW")
                    if krw > 50000:
                        upbit.buy_market_order(buycoin_2, 50000)
                        #구매시간 갱신
                        buytime3 = datetime.datetime.now() + datetime.timedelta(minutes=4)
                        time.sleep(1)
                    
                #4번구매코인 익절/손절
                if (count4 == 'false') :
                    rsiindex(buycoin_3)
                if (count4 == 'false') and (rsi > 60) :
                    btc_3 = upbit.get_balance(buycoin_3[4:])
                    upbit.sell_market_order(buycoin_3, btc_3)
                    count4 = 'true'
                #다시 돌파시 물타기
                elif (count4 == 'false') and (30 > oldrsi) and (30 < rsi) and (now > buytime4):
                    krw = get_balance("KRW")
                    if krw > 50000:
                        upbit.buy_market_order(buycoin_3, 50000)
                        #구매시간 갱신
                        buytime4 = datetime.datetime.now() + datetime.timedelta(minutes=4)
                        time.sleep(1)
                        
                #5번구매코인 익절/손절
                if (count5 == 'false') :
                    rsiindex(buycoin_4)
                if (count5 == 'false') and (rsi > 60) :
                    btc_4 = upbit.get_balance(buycoin_4[4:])
                    upbit.sell_market_order(buycoin_4, btc_4)
                    count5 = 'true'
                #다시 돌파시 물타기
                elif (count5 == 'false') and (30 > oldrsi) and (30 < rsi) and (now > buytime5):
                    krw = get_balance("KRW")
                    if krw > 50000:
                        upbit.buy_market_order(buycoin_4, 50000)
                        #구매시간 갱신
                        buytime5 = datetime.datetime.now() + datetime.timedelta(minutes=4)
                        time.sleep(1)
                        
                #6번구매코인 익절/손절
                if (count6 == 'false') :
                    rsiindex(buycoin_5)
                if (count6 == 'false') and (rsi > 60) :
                    btc_5 = upbit.get_balance(buycoin_5[4:])
                    upbit.sell_market_order(buycoin_5, btc_5)
                    count6 = 'true'
                #다시 돌파시 물타기
                elif (count6 == 'false') and (30 > oldrsi) and (30 < rsi) and (now > buytime6):
                    krw = get_balance("KRW")
                    if krw > 50000:
                        upbit.buy_market_order(buycoin_5, 50000)
                        #구매시간 갱신
                        buytime6 = datetime.datetime.now() + datetime.timedelta(minutes=4)
                        time.sleep(1)
                        
                #7번구매코인 익절/손절
                if (count7 == 'false') :
                    rsiindex(buycoin_6)
                if (count7 == 'false') and (rsi > 60) :
                    btc_6 = upbit.get_balance(buycoin_6[4:])
                    upbit.sell_market_order(buycoin_6, btc_6)
                    count7 = 'true'
                #다시 돌파시 물타기
                elif (count7 == 'false') and (30 > oldrsi) and (30 < rsi) and (now > buytime7):
                    krw = get_balance("KRW")
                    if krw > 50000:
                        upbit.buy_market_order(buycoin_6, 50000)
                        #구매시간 갱신
                        buytime7 = datetime.datetime.now() + datetime.timedelta(minutes=4)
                        time.sleep(1)
                        
                #8번구매코인 익절/손절
                if (count8 == 'false') :
                    rsiindex(buycoin_7)
                if (count8 == 'false') and (rsi > 60) :
                    btc_7 = upbit.get_balance(buycoin_7[4:])
                    upbit.sell_market_order(buycoin_7, btc_7)
                    count8 = 'true'
                #다시 돌파시 물타기
                elif (count8 == 'false') and (30 > oldrsi) and (30 < rsi) and (now > buytime8):
                    krw = get_balance("KRW")
                    if krw > 50000:
                        upbit.buy_market_order(buycoin_7, 50000)
                        #구매시간 갱신
                        buytime8 = datetime.datetime.now() + datetime.timedelta(minutes=4)
                        time.sleep(1)
                        
                #9번구매코인 익절/손절
                if (count9 == 'false') :
                    rsiindex(buycoin_8)
                if (count9 == 'false') and (rsi > 60) :
                    btc_8 = upbit.get_balance(buycoin_8[4:])
                    upbit.sell_market_order(buycoin_8, btc_8)
                    count9 = 'true'
                #다시 돌파시 물타기
                elif (count9 == 'false') and (30 > oldrsi) and (30 < rsi) and (now > buytime9):
                    krw = get_balance("KRW")
                    if krw > 50000:
                        upbit.buy_market_order(buycoin_8, 50000)
                        #구매시간 갱신
                        buytime9 = datetime.datetime.now() + datetime.timedelta(minutes=4)
                        time.sleep(1)
                        
                #10번구매코인 익절/손절
                if (count10 == 'false') :
                    rsiindex(buycoin_9)
                if (count10 == 'false') and (rsi > 60) :
                    btc_9 = upbit.get_balance(buycoin_9[4:])
                    upbit.sell_market_order(buycoin_9, btc_9)
                    count10 = 'true'
                #다시 돌파시 물타기
                elif (count10 == 'false') and (30 > oldrsi) and (30 < rsi) and (now > buytime10):
                    krw = get_balance("KRW")
                    if krw > 50000:
                        upbit.buy_market_order(buycoin_9, 50000)
                        #구매시간 갱신
                        buytime10 = datetime.datetime.now() + datetime.timedelta(minutes=4)
                        time.sleep(1)
            
            n = n+1
            time.sleep(1)
        except Exception as e:
            print(e)
            time.sleep(1)
