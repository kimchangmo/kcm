import time
import pyupbit
import datetime
import schedule
from fbprophet import Prophet
import requests
import pandas as pd
import webbrowser
import numpy

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

#이평선 
now_ma20 = 0
now_ma60 = 0
old_ma20 = 0
old_ma60 = 0
def get_ma(ticker):
    global now_ma20
    global now_ma60
    global old_ma20
    global old_ma60
    url = "https://api.upbit.com/v1/candles/minutes/1"
    querystring = {"market":ticker,"count":"200"}
    response = requests.request("GET", url, params=querystring)
    data = response.json()
    df = pd.DataFrame(data)
    df=df['trade_price'].iloc[::-1]

    ma20 = df.rolling(window=20).mean()
    ma60 = df.rolling(window=60).mean()

    now_ma20 = round(ma20.iloc[-1],2)
    now_ma60 = round(ma60.iloc[-1],2)
    old_ma20 =  round(ma20.iloc[-2],2)
    old_ma60 =  round(ma60.iloc[-2],2)

#rsi, 볼밴 조회
rsi = 0
oldrsi = 0
old_old_rsi = 0
band_high = 0
band_low = 0
def rsiindex(symbol):
    global rsi
    global oldrsi
    global old_old_rsi
    global band_high
    global band_low
    url = "https://api.upbit.com/v1/candles/minutes/1"
    querystring = {"market":symbol,"count":"500"}
    response = requests.request("GET", url, params=querystring)
    data = response.json()
    df = pd.DataFrame(data)
    #여기서부터 볼밴 상/하단값 구하는법
    df_bol=df['trade_price'].iloc[::-1]
    unit=2
    band1=unit*numpy.std(df_bol[len(df_bol)-20:len(df_bol)])
    bb_center=numpy.mean(df_bol[len(df_bol)-20:len(df_bol)])
    band_high = bb_center+band1
    band_high = round(band_high,2)
    band_low = bb_center-band1
    band_low = round(band_low,2)
    #여기까지
    df=df.reindex(index=df.index[::-1]).reset_index()
    old = df['index'] > 0
    old_old = df['index'] > 1
    
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

    oldrsi = rsi(df[old], 14).iloc[-1]
    old_old_rsi = rsi(df[old_old], 14).iloc[-1]
    rsi = rsi(df, 14).iloc[-1]
    
# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
all_coin = pyupbit.get_tickers('KRW')
all_coin.remove('KRW-MED')
all_coin.remove('KRW-BTC')
all_coin.remove('KRW-XRP')
all_coin.remove('KRW-ETH')

#총 몇개 돌릴건지 설정
coin_buy_index = 6
#분봉 +1
delay_time = 1
#구매가
buy_money = 100000

for i in range(0, coin_buy_index):
    globals()['count_{}'.format(i)] = 'true'
    globals()['old_plus_buy_{}'.format(i)] = 0

while True:
    n = 0
    while n < len(all_coin) : #총 코인 갯수
        try:
            coin = all_coin[n]

            now = datetime.datetime.now()
            start_time = get_start_time(coin)
            end_time = start_time + datetime.timedelta(days=1)

            #if True:
            if start_time < now < end_time - datetime.timedelta(hours=1):
                #print("ing... :")
                current_price = get_current_price(coin)
                rsiindex(coin)
                
                #모든 코인구매칸이 다찼는지 확인
                for i in range(0, coin_buy_index):
                    if (globals()['count_{}'.format(i)] == 'false'):
                        count_all = 'false'
                    else:
                        count_all = 'true'
                        break

                #get_ma(coin)
                #print('코인: ', coin, current_price)
                #print(now_ma20)
                #print(now_ma60)
                #print(old_ma20)
                #print(old_ma60)
                
                #코인 전전가격 체크
                url = "https://api.upbit.com/v1/candles/minutes/1"
                querystring = {"market":coin,"count":"200"}
                response = requests.request("GET", url, params=querystring)
                data = response.json()
                df = pd.DataFrame(data)
                df=df['trade_price'].iloc[::-1]
                #print(coin, ":" , df)
                old_old_price = df[2]
                #print("old_old:" , old_old_price)
                
                #이평선 매수
                #if (old_ma20 < old_ma60) and (now_ma20 > now_ma60) and (current_price > 3000) and (count_all == 'true') and (upbit.get_balance(coin[4:]) == 0):
                #rsi 매수
                if (30 > old_old_rsi) and (30 <= oldrsi) and (count_all == 'true') and (upbit.get_balance(coin[4:]) == 0):
                    print("OK1")
                #test
                #if (current_price > 3000) and (count_all == 'true') and (upbit.get_balance(coin[4:]) == 0):
                    for i in range(0, coin_buy_index):
                        if (globals()['count_{}'.format(i)] == 'true'):
                            krw = get_balance("KRW")
                            if krw > buy_money:
                                upbit.buy_market_order(coin, buy_money)
                                globals()['buycoin_{}'.format(i)] = coin
                                globals()['buy_price_{}'.format(i)] = current_price
                                globals()['water_buy_price_{}'.format(i)] = current_price
                                print("buy:",  globals()['buycoin_{}'.format(i)])
                                globals()['count_{}'.format(i)] = 'false'
                                globals()['old_old_price_{}'.format(i)] = old_old_price
                                print("OK2")
                                time.sleep(5)
                            break
                
                for i in range(0, coin_buy_index):  
                    #if (globals()['count_{}'.format(i)] == 'false'):
                    #    get_ma(globals()['buycoin_{}'.format(i)])
                    #rsi 값 구하기
                    if (globals()['count_{}'.format(i)] == 'false') :
                        rsiindex(globals()['buycoin_{}'.format(i)])
                        
                        #코인 전전가격 체크
                        url = "https://api.upbit.com/v1/candles/minutes/1"
                        querystring = {"market":globals()['buycoin_{}'.format(i)],"count":"200"}
                        response = requests.request("GET", url, params=querystring)
                        data = response.json()
                        df = pd.DataFrame(data)
                        df=df['trade_price'].iloc[::-1]
                        #print(coin, ":" , df)
                        old_old_price = df[2]
                        #print("old_old:" , old_old_price)

                    #0.3퍼 판매
                    if (globals()['count_{}'.format(i)] == 'false') and ((globals()['water_buy_price_{}'.format(i)] * 1.003) < (get_current_price(globals()['buycoin_{}'.format(i)]))) :
                        globals()['btc_{}'.format(i)] = upbit.get_balance(globals()['buycoin_{}'.format(i)][4:])
                        #btc_0 = upbit.get_balance(buycoin_0[4:])
                        upbit.sell_market_order(globals()['buycoin_{}'.format(i)], globals()['btc_{}'.format(i)])
                        globals()['count_{}'.format(i)] = 'true'
                        #count1 = 'true'

                    #손절
                    if (globals()['count_{}'.format(i)] == 'false') and (globals()['old_old_price_{}'.format(i)] > get_current_price(globals()['buycoin_{}'.format(i)])):
                        globals()['btc_{}'.format(i)] = upbit.get_balance(globals()['buycoin_{}'.format(i)][4:])
                        #btc_0 = upbit.get_balance(buycoin_0[4:])
                        upbit.sell_market_order(globals()['buycoin_{}'.format(i)], globals()['btc_{}'.format(i)])
                        globals()['count_{}'.format(i)] = 'true'
                        #count1 = 'true'

                    #수동판매 대응
                    if (globals()['count_{}'.format(i)] == 'false') and (upbit.get_balance(globals()['buycoin_{}'.format(i)][4:]) == 0) :
                        globals()['count_{}'.format(i)] = 'true'

            else:
                for i in range(0, coin_buy_index):
                    #if (globals()['count_{}'.format(i)] == 'false'):
                    #    get_ma(globals()['buycoin_{}'.format(i)])
                    #rsi 값 구하기
                    if (globals()['count_{}'.format(i)] == 'false') :
                        rsiindex(globals()['buycoin_{}'.format(i)])

                    #0.3퍼 판매
                    if (globals()['count_{}'.format(i)] == 'false') and ((globals()['water_buy_price_{}'.format(i)] * 1.003) < (get_current_price(globals()['buycoin_{}'.format(i)]))) :
                        globals()['btc_{}'.format(i)] = upbit.get_balance(globals()['buycoin_{}'.format(i)][4:])
                        #btc_0 = upbit.get_balance(buycoin_0[4:])
                        upbit.sell_market_order(globals()['buycoin_{}'.format(i)], globals()['btc_{}'.format(i)])
                        globals()['count_{}'.format(i)] = 'true'
                        #count1 = 'true'

                    #손절
                    if (globals()['count_{}'.format(i)] == 'false') and (globals()['old_old_price_{}'.format(i)] > get_current_price(globals()['buycoin_{}'.format(i)])):
                        globals()['btc_{}'.format(i)] = upbit.get_balance(globals()['buycoin_{}'.format(i)][4:])
                        #btc_0 = upbit.get_balance(buycoin_0[4:])
                        upbit.sell_market_order(globals()['buycoin_{}'.format(i)], globals()['btc_{}'.format(i)])
                        globals()['count_{}'.format(i)] = 'true'
                        #count1 = 'true'

                    #수동판매 대응
                    if (globals()['count_{}'.format(i)] == 'false') and (upbit.get_balance(globals()['buycoin_{}'.format(i)][4:]) == 0) :
                        globals()['count_{}'.format(i)] = 'true'
            n = n+1
            time.sleep(1)
        except Exception as e:
            print(e)
            time.sleep(1)
