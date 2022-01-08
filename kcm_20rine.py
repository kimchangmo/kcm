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

old_ma20 = 0
def goldencross(symbol):
    global old_ma20
    url = "https://api.upbit.com/v1/candles/minutes/15"
    
    querystring = {"market":symbol,"count":"100"}
    
    response = requests.request("GET", url, params=querystring)
    
    data = response.json()
    
    df = pd.DataFrame(data)
    
    df=df['trade_price'].iloc[::-1]
        
    ma20 = df.rolling(window=20, min_periods=1).mean()
    ma60 = df.rolling(window=60, min_periods=1).mean()
    
    test1=ma20.iloc[-2]-ma60.iloc[-2]
    test2=ma20.iloc[-1]-ma60.iloc[-1]
    old_ma20 = round(ma20.iloc[-2],2)
    
    call='해당없음'
    
    if test1>0 and test2<0:
        call='데드크로스' 
        
    if test1<0 and test2>0:
        call='골든크로스'     
    
    print(symbol)
    print('old_rine 20: ', old_ma20)
    print('rine 20: ', round(ma20.iloc[-1],2))
   #print('이동평균선 60: ', round(ma60.iloc[-1],2))
   #print('골든크로스/데드크로스: ',call)
    print('')
    return round(ma20.iloc[-1],2)

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
all_coin = pyupbit.get_tickers('KRW')
all_coin.remove('KRW-MED')

#사용코인 목록
def change_coin_list():
    #거래량 + 코인가격으로 거르기
    p = 0
    global use_coin
    use_coin = []
    while p < len(all_coin) :
        try:
            current_price = get_current_price(all_coin[p])
            #if acc_trade_price_24h > 20000000000 and current_price > 3000:
            if current_price > 400:
                use_coin.append(all_coin[p])
            p = p+1
        except Exception as e:
            print(e)
            time.sleep(1)
    print(use_coin)
schedule.every(6).hours.do(change_coin_list)
change_coin_list()

#총 몇개 돌릴건지 설정
coin_buy_index = 5
#분봉 +1
delay_time = 16
#구매가
buy_money = 50000

for i in range(0, coin_buy_index):
    globals()['count_{}'.format(i)] = 'true'
    globals()['old_plus_buy_{}'.format(i)] = 0

while True:
    n = 0
    schedule.run_pending()
    time.sleep(1)
    while n < len(use_coin) : #총 코인 갯수
        try:
            coin = use_coin[n]

            now = datetime.datetime.now()
            start_time = get_start_time(coin)
            end_time = start_time + datetime.timedelta(days=1)

            ma20 = goldencross("KRW-BTC")
            current_price = get_current_price("KRW-BTC")
            
            #if True:
            if start_time + datetime.timedelta(minutes=30) < now < end_time - datetime.timedelta(hours=1) and (current_price > ma20):
                ma20 = goldencross(coin)
                current_price = get_current_price(coin)

                old_price = pyupbit.get_ohlcv(ticker="KRW-BTC",interval="minute15",count=10)
                old_price=old_price['close'].iloc[::-1]
                old_price=old_price[1]
                
                print("coin:", coin)
                print("old_price:", old_price)
                print("current_price:", current_price)
                
                #모든 코인구매칸이 다찼는지 확인
                for i in range(0, coin_buy_index):
                    if (globals()['count_{}'.format(i)] == 'false'):
                        count_all = 'false'
                    else:
                        count_all = 'true'
                        break
                
                if (old_ma20 > old_price) and (ma20 < current_price) and (count_all == 'true') and (upbit.get_balance(coin[4:]) == 0):
                    for i in range(0, coin_buy_index):
                        if (globals()['count_{}'.format(i)] == 'true'):
                            globals()['buy_money_{}'.format(i)] = buy_money
                            krw = get_balance("KRW")
                            if krw > globals()['buy_money_{}'.format(i)]:
                                upbit.buy_market_order(coin, globals()['buy_money_{}'.format(i)])
                                globals()['buycoin_{}'.format(i)] = coin
                                globals()['buy_price_{}'.format(i)] = current_price
                                globals()['water_buy_price_{}'.format(i)] = current_price
                                print("buy:",  globals()['buycoin_{}'.format(i)])
                                globals()['count_{}'.format(i)] = 'false'
                                globals()['buytime_{}'.format(i)] = datetime.datetime.now() + datetime.timedelta(minutes=delay_time)
                                time.sleep(5)
                            break
                
                for i in range(0, coin_buy_index):
                    #macd 값 구하기
                    if (globals()['count_{}'.format(i)] == 'false') :
                        ma20 = goldencross(coin)
                        current_price = get_current_price(coin)

                        old_price = pyupbit.get_ohlcv(ticker="KRW-BTC",interval="minute15",count=10)
                        old_price=old_price['close'].iloc[::-1]
                        old_price=old_price[1]
                    
                    #익절판매
                    if (globals()['count_{}'.format(i)] == 'false') and ((globals()['water_buy_price_{}'.format(i)] * 1.01) < (get_current_price(globals()['buycoin_{}'.format(i)]))) :
                        globals()['btc_{}'.format(i)] = upbit.get_balance(globals()['buycoin_{}'.format(i)][4:])
                        upbit.sell_market_order(globals()['buycoin_{}'.format(i)], globals()['btc_{}'.format(i)])
                        globals()['count_{}'.format(i)] = 'true'
                        
                    #익절판매(본전이상 + 20평균아래)
                    if (globals()['count_{}'.format(i)] == 'false') and (ma20 > current_price) and ((globals()['water_buy_price_{}'.format(i)] * 1.002) < (get_current_price(globals()['buycoin_{}'.format(i)]))):
                        globals()['btc_{}'.format(i)] = upbit.get_balance(globals()['buycoin_{}'.format(i)][4:])
                        upbit.sell_market_order(globals()['buycoin_{}'.format(i)], globals()['btc_{}'.format(i)])
                        globals()['count_{}'.format(i)] = 'true'
                        
                    #손절판매(본전 -1퍼 이상 + 0아래)
                    if (globals()['count_{}'.format(i)] == 'false') and (ma20 > current_price) and ((globals()['water_buy_price_{}'.format(i)] * 0.99) > (get_current_price(globals()['buycoin_{}'.format(i)]))):
                        globals()['btc_{}'.format(i)] = upbit.get_balance(globals()['buycoin_{}'.format(i)][4:])
                        upbit.sell_market_order(globals()['buycoin_{}'.format(i)], globals()['btc_{}'.format(i)])
                        globals()['count_{}'.format(i)] = 'true'

                    #수동판매 대응
                    if (globals()['count_{}'.format(i)] == 'false') and (upbit.get_balance(globals()['buycoin_{}'.format(i)][4:]) == 0) :
                        globals()['count_{}'.format(i)] = 'true'

            else:
                for i in range(0, coin_buy_index):
                    #macd 값 구하기
                    if (globals()['count_{}'.format(i)] == 'false') :
                        ma20 = goldencross(coin)
                        current_price = get_current_price(coin)

                        old_price = pyupbit.get_ohlcv(ticker="KRW-BTC",interval="minute15",count=10)
                        old_price=old_price['close'].iloc[::-1]
                        old_price=old_price[1]
                    
                    #익절판매
                    if (globals()['count_{}'.format(i)] == 'false') and ((globals()['water_buy_price_{}'.format(i)] * 1.002) < (get_current_price(globals()['buycoin_{}'.format(i)]))) :
                        globals()['btc_{}'.format(i)] = upbit.get_balance(globals()['buycoin_{}'.format(i)][4:])
                        upbit.sell_market_order(globals()['buycoin_{}'.format(i)], globals()['btc_{}'.format(i)])
                        globals()['count_{}'.format(i)] = 'true'
                        
                    #익절판매(본전이상 + 20평균아래)
                    if (globals()['count_{}'.format(i)] == 'false') and (ma20 > current_price) and ((globals()['water_buy_price_{}'.format(i)] * 1.002) < (get_current_price(globals()['buycoin_{}'.format(i)]))):
                        globals()['btc_{}'.format(i)] = upbit.get_balance(globals()['buycoin_{}'.format(i)][4:])
                        upbit.sell_market_order(globals()['buycoin_{}'.format(i)], globals()['btc_{}'.format(i)])
                        globals()['count_{}'.format(i)] = 'true'
                        
                    #손절판매(본전 -1퍼 이상 + 0아래)
                    if (globals()['count_{}'.format(i)] == 'false') and (ma20 > current_price) and ((globals()['water_buy_price_{}'.format(i)] * 0.99) > (get_current_price(globals()['buycoin_{}'.format(i)]))):
                        globals()['btc_{}'.format(i)] = upbit.get_balance(globals()['buycoin_{}'.format(i)][4:])
                        upbit.sell_market_order(globals()['buycoin_{}'.format(i)], globals()['btc_{}'.format(i)])
                        globals()['count_{}'.format(i)] = 'true'

                    #수동판매 대응
                    if (globals()['count_{}'.format(i)] == 'false') and (upbit.get_balance(globals()['buycoin_{}'.format(i)][4:]) == 0) :
                        globals()['count_{}'.format(i)] = 'true'
            n = n+1
            time.sleep(1)
        except Exception as e:
            print(e)
            time.sleep(1)
