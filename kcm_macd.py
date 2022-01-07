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

#MACD
macd2 = 0
def MACD(tradePrice):
    global macd2
    exp5 = tradePrice.ewm(span=5, adjust=False).mean()
    #exp12 = tradePrice.ewm(span=12, adjust=False).mean()
    exp20 = tradePrice.ewm(span=20, adjust=False).mean()
    #exp26 = tradePrice.ewm(span=26, adjust=False).mean()
    #macd = exp12-exp26
    macd = exp5-exp20
    #macd2 = exp12-exp26
    macd2 = exp5-exp20
    #exp = macd.ewm(span=9, adjust=False).mean()
    exp = macd.ewm(span=5, adjust=False).mean()
    #exp12 = exp12.ewm(span=12, adjust=False).mean()
    exp5 = exp5.ewm(span=5, adjust=False).mean()
    return exp

acc_trade_price_24h = 0
def acc_trade_def(ticker):
    global acc_trade_price_24h
    #거래대금
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
#all_coin.remove('KRW-BTC')

#사용코인 목록
def change_coin_list():
    #거래량 + 코인가격으로 거르기
    p = 0
    global use_coin
    use_coin = []
    while p < len(all_coin) :
        try:
            acc_trade_def(all_coin[p])
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
            
            url = "https://api.upbit.com/v1/candles/minutes/15"
            querystring = {"market":"KRW-BTC","count":"500"}
            response = requests.request("GET", url, params=querystring)
            data = response.json()
            df = pd.DataFrame(data)
            df=df.iloc[::-1]
            macd = MACD(df['trade_price'])

            print("BTC red_rine:",macd2[0]) # 현재 빨강선
            
            #if True:
            #if start_time + datetime.timedelta(minutes=30) < now < end_time - datetime.timedelta(hours=1) and (macd2[0] > 0) and (macd2[1] > 0):
            #if (macd2[0] > 0) and (macd2[1] > 0):
            if start_time + datetime.timedelta(minutes=30) < now < end_time - datetime.timedelta(hours=1):
                url = "https://api.upbit.com/v1/candles/minutes/15"
                querystring = {"market":coin,"count":"500"}
                response = requests.request("GET", url, params=querystring)
                data = response.json()
                df = pd.DataFrame(data)
                df=df.iloc[::-1]
                macd = MACD(df['trade_price'])
                
                print("coin:", coin)
                #print(macd[1]) # 이전 노랑선(신호선)
                #print(macd2[1]) # 이전 빨강선
                print("red_rine:",macd2[0]) # 현재 빨강선
                print("yellow_rine:",macd[0]) # 현재 노랑선

                current_price = get_current_price(coin)
                
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
                
                #이전가 0 터치시 매수
                #if (macd2[2] < 0) and (macd2[1] > 0) and (macd2[0] > 0) and (macd2[1] > macd[1]) and (macd2[0] > macd[0]) and (current_price > 3000) and (count_all == 'true') and (upbit.get_balance(coin[4:]) == 0):
                #이전가 0 터치시 매수
                if (macd2[2] < 0) and (macd2[1] > 0) and (macd2[0] > 0) and (count_all == 'true') and (upbit.get_balance(coin[4:]) == 0):
                #골든크로스
                #if (macd2[2] < 0) and (macd2[2] < macd[2]) and (macd2[1] >= macd[1]) and (macd2[0] >= macd[0]) and (count_all == 'true') and (upbit.get_balance(coin[4:]) == 0):
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
                        url = "https://api.upbit.com/v1/candles/minutes/15"
                        querystring = {"market":globals()['buycoin_{}'.format(i)],"count":"500"}
                        response = requests.request("GET", url, params=querystring)
                        data = response.json()
                        df = pd.DataFrame(data)
                        df=df.iloc[::-1]
                        macd = MACD(df['trade_price'])
                    
                    #익절판매
                    if (globals()['count_{}'.format(i)] == 'false') and ((globals()['water_buy_price_{}'.format(i)] * 1.01) < (get_current_price(globals()['buycoin_{}'.format(i)]))) :
                        globals()['btc_{}'.format(i)] = upbit.get_balance(globals()['buycoin_{}'.format(i)][4:])
                        upbit.sell_market_order(globals()['buycoin_{}'.format(i)], globals()['btc_{}'.format(i)])
                        globals()['count_{}'.format(i)] = 'true'

                    #0역돌파판매
                    #if (globals()['count_{}'.format(i)] == 'false') and (macd2[2] > 0) and (macd2[1] < 0) and (macd2[0] < 0):
                    #    globals()['btc_{}'.format(i)] = upbit.get_balance(globals()['buycoin_{}'.format(i)][4:])
                    #    upbit.sell_market_order(globals()['buycoin_{}'.format(i)], globals()['btc_{}'.format(i)])
                    #    globals()['count_{}'.format(i)] = 'true'
                        
                    #익절판매(본전이상 + 데드크로스)
                    if (globals()['count_{}'.format(i)] == 'false') and (macd2[0] < macd[0]) and ((globals()['water_buy_price_{}'.format(i)] * 1.002) < (get_current_price(globals()['buycoin_{}'.format(i)]))):
                        globals()['btc_{}'.format(i)] = upbit.get_balance(globals()['buycoin_{}'.format(i)][4:])
                        upbit.sell_market_order(globals()['buycoin_{}'.format(i)], globals()['btc_{}'.format(i)])
                        globals()['count_{}'.format(i)] = 'true'
                        
                    #손절판매(본전 -1퍼 이상 + 0아래)
                    if (globals()['count_{}'.format(i)] == 'false') and (macd2[0] < 0) and ((globals()['water_buy_price_{}'.format(i)] * 0.99) > (get_current_price(globals()['buycoin_{}'.format(i)]))):
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
                        url = "https://api.upbit.com/v1/candles/minutes/15"
                        querystring = {"market":globals()['buycoin_{}'.format(i)],"count":"500"}
                        response = requests.request("GET", url, params=querystring)
                        data = response.json()
                        df = pd.DataFrame(data)
                        df=df.iloc[::-1]
                        macd = MACD(df['trade_price'])
                    
                    #약익절판매
                    if (globals()['count_{}'.format(i)] == 'false') and ((globals()['water_buy_price_{}'.format(i)] * 1.002) < (get_current_price(globals()['buycoin_{}'.format(i)]))) :
                        globals()['btc_{}'.format(i)] = upbit.get_balance(globals()['buycoin_{}'.format(i)][4:])
                        upbit.sell_market_order(globals()['buycoin_{}'.format(i)], globals()['btc_{}'.format(i)])
                        globals()['count_{}'.format(i)] = 'true'
                        
                    #0역돌파판매
                    #if (globals()['count_{}'.format(i)] == 'false') and (macd2[2] > 0) and (macd2[1] < 0) and (macd2[0] < 0):
                    #    globals()['btc_{}'.format(i)] = upbit.get_balance(globals()['buycoin_{}'.format(i)][4:])
                    #    upbit.sell_market_order(globals()['buycoin_{}'.format(i)], globals()['btc_{}'.format(i)])
                    #    globals()['count_{}'.format(i)] = 'true'
                        
                    #익절판매(본전이상 + 데드크로스)
                    #if (globals()['count_{}'.format(i)] == 'false') and ((globals()['water_buy_price_{}'.format(i)] * 1.001) < (get_current_price(globals()['buycoin_{}'.format(i)]))):
                    #    globals()['btc_{}'.format(i)] = upbit.get_balance(globals()['buycoin_{}'.format(i)][4:])
                    #    upbit.sell_market_order(globals()['buycoin_{}'.format(i)], globals()['btc_{}'.format(i)])
                    #    globals()['count_{}'.format(i)] = 'true'
                        
                    #손절판매(본전 -1퍼 이상 + 0아래)
                    if (globals()['count_{}'.format(i)] == 'false') and (macd2[0] < 0) and ((globals()['water_buy_price_{}'.format(i)] * 0.99) > (get_current_price(globals()['buycoin_{}'.format(i)]))):
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
