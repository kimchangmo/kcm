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

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

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
#predict_price("KRW-BTC")
#schedule.every().hour.do(lambda: predict_price("KRW-BTC"))

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
    url = "https://api.upbit.com/v1/candles/minutes/15"
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
        #ohlc["trade_price"] = ohlc["trade_price"]
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
    #print(symbol)
    #print('Upbit 20 minute oldRSI:', old_old_rsi)
    #print('Upbit 10 minute oldRSI:', oldrsi)
    #print('Upbit now RSI:', rsi)
    #print('')
    
#거래대금
acc_trade_price_24h = 0
res_json = 0
def acc_trade_price_24h(ticker):
    global acc_trade_price_24h
    global res_json
    url = "https://api.upbit.com/v1/ticker"
    querystring = {"markets":ticker}
    response = requests.request("GET", url, params=querystring)

    res_json = response.json()
    acc_trade_price_24h = res_json[0]['acc_trade_price_24h']

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
all_coin = pyupbit.get_tickers('KRW')
all_coin.remove('KRW-MED')
all_coin.remove('KRW-BTC')

# 자동매매 시작
#count1 = 'true'
#count2 = 'true'
#count3 = 'true'

#물타기 총가격
#old_plus_buy_0 = 0
#old_plus_buy_1 = 0
#old_plus_buy_2 = 0

#총 몇개 돌릴건지 설정
coin_buy_index = 6
#분봉 +1
delay_time = 17

for i in range(0, coin_buy_index):
    globals()['count_{}'.format(i)] = 'true'
    globals()['old_plus_buy_{}'.format(i)] = 0

while True:
    n = 0
    while n < len(all_coin) : #총 코인 갯수
        try:
            coin = all_coin[n]
            #인공지능
            #predict_price(coin)
            #df = pyupbit.get_ohlcv(coin)
            #open_price = df['open'].iloc[-1]

            now = datetime.datetime.now()
            start_time = get_start_time(coin)
            end_time = start_time + datetime.timedelta(days=1)

            #if True:
            if start_time + datetime.timedelta(minutes=30) < now < end_time - datetime.timedelta(hours=1):
                print("coin:", coin)
                current_price = get_current_price(coin)
                rsiindex(coin)
                
                #거래대금
                #url = "https://api.upbit.com/v1/ticker"
                #querystring = {"markets":coin}
                #response = requests.request("GET", url, params=querystring)
                #res_json = response.json()
                #acc_trade_price_24h = res_json[0]['acc_trade_price_24h']
                #print(coin,":", acc_trade_price_24h)
                
                #모든 코인구매칸이 다찼는지 확인
                for i in range(0, coin_buy_index):
                    if (globals()['count_{}'.format(i)] == 'false'):
                        count_all = 'false'
                    else:
                        count_all = 'true'
                        break
                
                #인공지능 적용 비교문
                #이전,이이전 비교문
                #if (30 > old_old_rsi) and (30 < oldrsi) and (predicted_close_price > open_price) and (acc_trade_price_24h > 100000000000) and (count_all == 'true') and (upbit.get_balance(coin[4:]) == 0):
                if (30 > old_old_rsi) and (30 < oldrsi) and (count_all == 'true') and (current_price > 100) and (upbit.get_balance(coin[4:]) == 0):
                    for i in range(0, coin_buy_index):
                        if (globals()['count_{}'.format(i)] == 'true'):
                            globals()['buy_money_{}'.format(i)] = 100000
                            #buy_money_{} = 100000
                            krw = get_balance("KRW")
                            if krw > globals()['buy_money_{}'.format(i)]:
                                upbit.buy_market_order(coin, globals()['buy_money_{}'.format(i)])
                                globals()['buycoin_{}'.format(i)] = coin
                                globals()['buy_price_{}'.format(i)] = current_price
                                globals()['water_buy_price_{}'.format(i)] = current_price
                                print("buy:",  globals()['buycoin_{}'.format(i)])
                                globals()['count_{}'.format(i)] = 'false'
                                #구매시간
                                globals()['buytime_{}'.format(i)] = datetime.datetime.now() + datetime.timedelta(minutes=delay_time)
                                globals()['overtime_{}'.format(i)] = datetime.datetime.now() + datetime.timedelta(hours=3)
                                time.sleep(5)
                            break
                
                for i in range(0, coin_buy_index):
                    #rsi 값 구하기
                    if (globals()['count_{}'.format(i)] == 'false') :
                        rsiindex(globals()['buycoin_{}'.format(i)])
                        
                    #3퍼 판매
                    if (globals()['count_{}'.format(i)] == 'false') and ((globals()['water_buy_price_{}'.format(i)] * 1.03) < (get_current_price(globals()['buycoin_{}'.format(i)]))) :
                        globals()['btc_{}'.format(i)] = upbit.get_balance(globals()['buycoin_{}'.format(i)][4:])
                        upbit.sell_market_order(globals()['buycoin_{}'.format(i)], globals()['btc_{}'.format(i)])
                        globals()['count_{}'.format(i)] = 'true'

                    #rsi70 역돌파시 본전매도
                    if (globals()['count_{}'.format(i)] == 'false') and (oldrsi < 70) and (70 < old_old_rsi) and ((globals()['water_buy_price_{}'.format(i)]) < (get_current_price(globals()['buycoin_{}'.format(i)]))) :
                        globals()['btc_{}'.format(i)] = upbit.get_balance(globals()['buycoin_{}'.format(i)][4:])
                        upbit.sell_market_order(globals()['buycoin_{}'.format(i)], globals()['btc_{}'.format(i)])
                        globals()['count_{}'.format(i)] = 'true'

                    #볼밴상단에 터치시 2퍼 판매
                    if (globals()['count_{}'.format(i)] == 'false') and ((get_current_price(globals()['buycoin_{}'.format(i)])) > band_high) and ((globals()['water_buy_price_{}'.format(i)] * 1.02) < (get_current_price(globals()['buycoin_{}'.format(i)]))) :
                        globals()['btc_{}'.format(i)] = upbit.get_balance(globals()['buycoin_{}'.format(i)][4:])
                        upbit.sell_market_order(globals()['buycoin_{}'.format(i)], globals()['btc_{}'.format(i)])
                        globals()['count_{}'.format(i)] = 'true'

                    #overtime 만큼 지나면 1퍼판매
                    if (globals()['count_{}'.format(i)] == 'false') and (now > globals()['overtime_{}'.format(i)]) and ((globals()['water_buy_price_{}'.format(i)] * 1.01) < (get_current_price(globals()['buycoin_{}'.format(i)]))) :
                        globals()['btc_{}'.format(i)] = upbit.get_balance(globals()['buycoin_{}'.format(i)][4:])
                        upbit.sell_market_order(globals()['buycoin_{}'.format(i)], globals()['btc_{}'.format(i)])
                        globals()['count_{}'.format(i)] = 'true'
                        
                    #40까지 물타고 -5퍼 손절
                    if (globals()['count_{}'.format(i)] == 'false') and ((globals()['water_buy_price_{}'.format(i)] * 0.95) > (get_current_price(globals()['buycoin_{}'.format(i)]))) and (globals()['buy_money_{}'.format(i)] == 400000) :
                        globals()['btc_{}'.format(i)] = upbit.get_balance(globals()['buycoin_{}'.format(i)][4:])
                        upbit.sell_market_order(globals()['buycoin_{}'.format(i)], globals()['btc_{}'.format(i)])
                        globals()['count_{}'.format(i)] = 'true'
                        
                    #수동판매 대응
                    if (globals()['count_{}'.format(i)] == 'false') and (upbit.get_balance(globals()['buycoin_{}'.format(i)][4:]) == 0) :
                        globals()['count_{}'.format(i)] = 'true'

                    #다시 돌파시 물타기 40만원까지만
                    if (globals()['count_{}'.format(i)] == 'false') and (globals()['buy_money_{}'.format(i)] < 800000) and (30 > old_old_rsi) and (30 < oldrsi) and (30 < rsi) and (now > globals()['buytime_{}'.format(i)]) and ((globals()['buy_price_{}'.format(i)] * 0.97) > (get_current_price(globals()['buycoin_{}'.format(i)]))):
                        krw = get_balance("KRW")
                        if krw > globals()['buy_money_{}'.format(i)]*2:
                            upbit.buy_market_order(globals()['buycoin_{}'.format(i)], globals()['buy_money_{}'.format(i)]*2)
                            #구매시간 갱신
                            globals()['buytime_{}'.format(i)] = datetime.datetime.now() + datetime.timedelta(minutes=delay_time)
                            #물타기가격 갱신(2배)
                            globals()['old_buy_money_{}'.format(i)] = globals()['buy_money_{}'.format(i)]
                            globals()['buy_money_{}'.format(i)] = globals()['buy_money_{}'.format(i)]*2
                            
                            if globals()['old_buy_money_{}'.format(i)] == 100000 :
                                globals()['old_plus_buy_{}'.format(i)] = globals()['old_buy_money_{}'.format(i)] + globals()['buy_money_{}'.format(i)]
                            else :
                                globals()['old_plus_buy_{}'.format(i)] = globals()['old_plus_buy_{}'.format(i)] + globals()['buy_money_{}'.format(i)]
                                
                            globals()['water_buy_price_{}'.format(i)] = globals()['old_plus_buy_{}'.format(i)]/upbit.get_balance(globals()['buycoin_{}'.format(i)][4:])
                            current_price = get_current_price(globals()['buycoin_{}'.format(i)])
                            globals()['buy_price_{}'.format(i)] = current_price
                            print("buycoin:",  globals()['buycoin_{}'.format(i)])
                            print("water_buy_price:",  globals()['water_buy_price_{}'.format(i)])
                            time.sleep(1)

            else:
                for i in range(0, coin_buy_index):
                    #rsi 값 구하기
                    if (globals()['count_{}'.format(i)] == 'false') :
                        rsiindex(globals()['buycoin_{}'.format(i)])
                        
                    #본전판매
                    if (globals()['count_{}'.format(i)] == 'false') and ((globals()['water_buy_price_{}'.format(i)] * 1.001) < (get_current_price(globals()['buycoin_{}'.format(i)]))) :
                        globals()['btc_{}'.format(i)] = upbit.get_balance(globals()['buycoin_{}'.format(i)][4:])
                        upbit.sell_market_order(globals()['buycoin_{}'.format(i)], globals()['btc_{}'.format(i)])
                        globals()['count_{}'.format(i)] = 'true'

                    #40까지 물타고 -5퍼 손절
                    if (globals()['count_{}'.format(i)] == 'false') and ((globals()['water_buy_price_{}'.format(i)] * 0.95) > (get_current_price(globals()['buycoin_{}'.format(i)]))) and (globals()['buy_money_{}'.format(i)] == 400000) :
                        globals()['btc_{}'.format(i)] = upbit.get_balance(globals()['buycoin_{}'.format(i)][4:])
                        upbit.sell_market_order(globals()['buycoin_{}'.format(i)], globals()['btc_{}'.format(i)])
                        globals()['count_{}'.format(i)] = 'true'
                        
                    #수동판매 대응
                    if (globals()['count_{}'.format(i)] == 'false') and (upbit.get_balance(globals()['buycoin_{}'.format(i)][4:]) == 0) :
                        globals()['count_{}'.format(i)] = 'true'
                        
                    #다시 돌파시 물타기 40만원까지만
                    if (globals()['count_{}'.format(i)] == 'false') and (globals()['buy_money_{}'.format(i)] < 800000) and (30 > old_old_rsi) and (30 < oldrsi) and (30 < rsi) and (now > globals()['buytime_{}'.format(i)]) and ((globals()['buy_price_{}'.format(i)] * 0.97) > (get_current_price(globals()['buycoin_{}'.format(i)]))):
                        krw = get_balance("KRW")
                        if krw > globals()['buy_money_{}'.format(i)]*2:
                            upbit.buy_market_order(globals()['buycoin_{}'.format(i)], globals()['buy_money_{}'.format(i)]*2)
                            #구매시간 갱신
                            globals()['buytime_{}'.format(i)] = datetime.datetime.now() + datetime.timedelta(minutes=delay_time)
                            #물타기가격 갱신(2배)
                            globals()['old_buy_money_{}'.format(i)] = globals()['buy_money_{}'.format(i)]
                            globals()['buy_money_{}'.format(i)] = globals()['buy_money_{}'.format(i)]*2
                            
                            if globals()['old_buy_money_{}'.format(i)] == 100000 :
                                globals()['old_plus_buy_{}'.format(i)] = globals()['old_buy_money_{}'.format(i)] + globals()['buy_money_{}'.format(i)]
                            else :
                                globals()['old_plus_buy_{}'.format(i)] = globals()['old_plus_buy_{}'.format(i)] + globals()['buy_money_{}'.format(i)]
                                
                            globals()['water_buy_price_{}'.format(i)] = globals()['old_plus_buy_{}'.format(i)]/upbit.get_balance(globals()['buycoin_{}'.format(i)][4:])
                            current_price = get_current_price(globals()['buycoin_{}'.format(i)])
                            globals()['buy_price_{}'.format(i)] = current_price
                            print("buycoin:",  globals()['buycoin_{}'.format(i)])
                            print("water_buy_price:",  globals()['water_buy_price_{}'.format(i)])
                            time.sleep(1)
            n = n+1
            time.sleep(1)
        except Exception as e:
            print(e)
            time.sleep(1)
