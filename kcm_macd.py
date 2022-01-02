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
    exp12 = tradePrice.ewm(span=12, adjust=False).mean()
    exp26 = tradePrice.ewm(span=26, adjust=False).mean()
    macd = exp12-exp26
    macd2 = exp12-exp26
    exp = macd.ewm(span=9, adjust=False).mean()
    exp12 = exp12.ewm(span=12, adjust=False).mean()
    return exp

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
all_coin = pyupbit.get_tickers('KRW')
all_coin.remove('KRW-MED')
all_coin.remove('KRW-BTC')

#총 몇개 돌릴건지 설정
coin_buy_index = 6
#분봉 +1
delay_time = 16
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
            
            url = "https://api.upbit.com/v1/candles/minutes/15"
            querystring = {"market":coin,"count":"500"}
            response = requests.request("GET", url, params=querystring)
            data = response.json()
            df = pd.DataFrame(data)
            df=df.iloc[::-1]
            macd = MACD(df['trade_price'])

            if True:
            #if start_time < now < end_time - datetime.timedelta(hours=1):
                print("coin:", coin)
                #print(macd[1]) # 이전 노랑선(신호선)
                print(macd2[1]) # 이전 빨강선
                print(macd2[0]) # 현재 빨강선

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
                
                #이전,이이전 비교문
                if (macd2[1] < 0) and (macd2[0] > 0) and (macd2[0] > macd[0]) and (count_all == 'true') and (upbit.get_balance(coin[4:]) == 0):
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
                        
                    #판매
                    if (globals()['count_{}'.format(i)] == 'false') and (macd[1] > macd2[1]) :
                        globals()['btc_{}'.format(i)] = upbit.get_balance(globals()['buycoin_{}'.format(i)][4:])
                        upbit.sell_market_order(globals()['buycoin_{}'.format(i)], globals()['btc_{}'.format(i)])
                        globals()['count_{}'.format(i)] = 'true'

                    #수동판매 대응
                    if (globals()['count_{}'.format(i)] == 'false') and (upbit.get_balance(globals()['buycoin_{}'.format(i)][4:]) == 0) :
                        globals()['count_{}'.format(i)] = 'true'

            else:
                for i in range(0, coin_buy_index):
                    #rsi 값 구하기
                    if (globals()['count_{}'.format(i)] == 'false') :
                        rsiindex(globals()['buycoin_{}'.format(i)])
                        
                    #3퍼 판매
                    if (globals()['count_{}'.format(i)] == 'false') and ((globals()['water_buy_price_{}'.format(i)] * 1.03) < (get_current_price(globals()['buycoin_{}'.format(i)]))) :
                        globals()['btc_{}'.format(i)] = upbit.get_balance(globals()['buycoin_{}'.format(i)][4:])
                        #btc_0 = upbit.get_balance(buycoin_0[4:])
                        upbit.sell_market_order(globals()['buycoin_{}'.format(i)], globals()['btc_{}'.format(i)])
                        globals()['count_{}'.format(i)] = 'true'
                        #count1 = 'true'

                    #rsi70 역돌파시 본전매도
                    if (globals()['count_{}'.format(i)] == 'false') and (oldrsi < 70) and (70 < old_old_rsi) and ((globals()['water_buy_price_{}'.format(i)]) < (get_current_price(globals()['buycoin_{}'.format(i)]))) :
                        globals()['btc_{}'.format(i)] = upbit.get_balance(globals()['buycoin_{}'.format(i)][4:])
                        #btc_0 = upbit.get_balance(buycoin_0[4:])
                        upbit.sell_market_order(globals()['buycoin_{}'.format(i)], globals()['btc_{}'.format(i)])
                        globals()['count_{}'.format(i)] = 'true'
                        #count1 = 'true'

                    #볼밴상단에 터치시 2퍼 판매
                    if (globals()['count_{}'.format(i)] == 'false') and ((get_current_price(globals()['buycoin_{}'.format(i)])) > band_high) and ((globals()['water_buy_price_{}'.format(i)] * 1.02) < (get_current_price(globals()['buycoin_{}'.format(i)]))) :
                        globals()['btc_{}'.format(i)] = upbit.get_balance(globals()['buycoin_{}'.format(i)][4:])
                        #btc_0 = upbit.get_balance(buycoin_0[4:])
                        upbit.sell_market_order(globals()['buycoin_{}'.format(i)], globals()['btc_{}'.format(i)])
                        globals()['count_{}'.format(i)] = 'true'
                        #count1 = 'true'

                    #overtime 만큼 지나면 1퍼판매
                    if (globals()['count_{}'.format(i)] == 'false') and (now > globals()['overtime_{}'.format(i)]) and ((globals()['water_buy_price_{}'.format(i)] * 1.01) < (get_current_price(globals()['buycoin_{}'.format(i)]))) :
                        globals()['btc_{}'.format(i)] = upbit.get_balance(globals()['buycoin_{}'.format(i)][4:])
                        #btc_0 = upbit.get_balance(buycoin_0[4:])
                        upbit.sell_market_order(globals()['buycoin_{}'.format(i)], globals()['btc_{}'.format(i)])
                        globals()['count_{}'.format(i)] = 'true'
                        #count1 = 'true'

                    #150까지 매수시 본전매도
                    #if (globals()['count_{}'.format(i)] == 'false') and (globals()['buy_money_{}'.format(i)] == 800000) and ((globals()['water_buy_price_{}'.format(i)]) < (get_current_price(globals()['buycoin_{}'.format(i)]))) :
                    #    globals()['btc_{}'.format(i)] = upbit.get_balance(globals()['buycoin_{}'.format(i)][4:])
                    #    #btc_0 = upbit.get_balance(buycoin_0[4:])
                    #    upbit.sell_market_order(globals()['buycoin_{}'.format(i)], globals()['btc_{}'.format(i)])
                    #    globals()['count_{}'.format(i)] = 'true'
                    #    #count1 = 'true'
                        
                    #40까지 물타고 rsi70 역돌파시 손절
                    if (globals()['count_{}'.format(i)] == 'false') and (oldrsi < 70) and (70 < old_old_rsi) and (globals()['buy_money_{}'.format(i)] == 400000) :
                        globals()['btc_{}'.format(i)] = upbit.get_balance(globals()['buycoin_{}'.format(i)][4:])
                        #btc_0 = upbit.get_balance(buycoin_0[4:])
                        upbit.sell_market_order(globals()['buycoin_{}'.format(i)], globals()['btc_{}'.format(i)])
                        globals()['count_{}'.format(i)] = 'true'
                        #count1 = 'true'

                    #다시 돌파시 물타기 40만원까지만
                    if (globals()['count_{}'.format(i)] == 'false') and (globals()['buy_money_{}'.format(i)] < 800000) and (30 > old_old_rsi) and (30 < oldrsi) and (30 < rsi) and (now > globals()['buytime_{}'.format(i)]) and ((globals()['buy_price_{}'.format(i)] * 0.97) > (get_current_price(globals()['buycoin_{}'.format(i)]))):
                        krw = get_balance("KRW")
                        if krw > globals()['buy_money_{}'.format(i)]*2:
                            upbit.buy_market_order(globals()['buycoin_{}'.format(i)], globals()['buy_money_{}'.format(i)]*2)
                            #구매시간 갱신
                            globals()['buytime_{}'.format(i)] = datetime.datetime.now() + datetime.timedelta(minutes=delay_time)
                            #buytime1 = datetime.datetime.now() + datetime.timedelta(minutes=7)
                            #물타기가격 갱신(2배)
                            globals()['old_buy_money_{}'.format(i)] = globals()['buy_money_{}'.format(i)]
                            #old_buy_money_0 = buy_money_0
                            globals()['buy_money_{}'.format(i)] = globals()['buy_money_{}'.format(i)]*2
                            #buy_money_0 = buy_money_0*2
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

                    #수동판매 대응
                    if (globals()['count_{}'.format(i)] == 'false') and (upbit.get_balance(globals()['buycoin_{}'.format(i)][4:]) == 0) :
                        globals()['count_{}'.format(i)] = 'true'
            n = n+1
            time.sleep(1)
        except Exception as e:
            print(e)
            time.sleep(1)
