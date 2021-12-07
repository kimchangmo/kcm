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

"""시작 시간 조회"""
def get_start_time(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

"""잔고 조회"""
def get_balance(ticker):
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

"""현재가 조회"""
def get_current_price(ticker):
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

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

# 구매된 코인
count1 = 'true'
count2 = 'true'
count3 = 'true'

while True:
    n = 0
    while n < len(all_coin) : #총 코인 갯수
        try:
            coin = all_coin[n]

            now = datetime.datetime.now()
            start_time = get_start_time(coin)
            end_time = start_time + datetime.timedelta(days=1)

            url = "https://api.upbit.com/v1/candles/minutes/5"
            querystring = {"market":coin,"count":"200"}
            response = requests.request("GET", url, params=querystring)
            data = response.json()
            df = pd.DataFrame(data)
            df=df.iloc[::-1]
            macd = MACD(df['trade_price'])

            if True:
            #if start_time < now < end_time - datetime.timedelta(seconds=600):
                print("ing... :", coin)
                print(macd[1]) # 이전 노랑선(신호선)
                print(macd2[1]) # 이전 빨강선
                
                current_price = get_current_price(coin)

                if (macd[2] >= macd2[2]) and (macd[1] < macd2[1]) and (count1 == 'true' or count2 == 'true' or count3 == 'true') and (upbit.get_balance(coin[4:]) == 0):
                    if count1 == 'true':
                        buy_money_0 = 20000
                        krw = get_balance("KRW")
                        if krw > buy_money_0:
                            upbit.buy_market_order(coin, buy_money_0)
                            buycoin_0 = coin
                            buy_price_0 = current_price
                            print("buy 1:",  buycoin_0)
                            count1 = 'false'
                            buytime1 = datetime.datetime.now() + datetime.timedelta(minutes=7)
                            time.sleep(5)
                    elif count2 == 'true':
                        buy_money_1 = 20000
                        krw = get_balance("KRW")
                        if krw > buy_money_1:
                            upbit.buy_market_order(coin, buy_money_1)
                            buycoin_1 = coin
                            buy_price_1 = current_price
                            print("buy 2:",  buycoin_1)
                            count2 = 'false'
                            buytime2 = datetime.datetime.now() + datetime.timedelta(minutes=7)
                            time.sleep(5)
                    elif count3 == 'true':
                        buy_money_2 = 20000
                        krw = get_balance("KRW")
                        if krw > buy_money_2:
                            upbit.buy_market_order(coin, buy_money_2)
                            buycoin_2 = coin
                            buy_price_2 = current_price
                            print("buy 3:",  buycoin_2)
                            count3 = 'false'
                            buytime3 = datetime.datetime.now() + datetime.timedelta(minutes=7)
                            time.sleep(5)

##################################1 buy_coin######################################################################################
                if (count1 == 'false') :
                    url = "https://api.upbit.com/v1/candles/minutes/5"
                    querystring = {"market":buycoin_0,"count":"200"}
                    response = requests.request("GET", url, params=querystring)
                    data = response.json()
                    df = pd.DataFrame(data)
                    df=df.iloc[::-1]
                    macd = MACD(df['trade_price'])
                if (count1 == 'false') and ((buy_price_0 * 1.03) < (get_current_price(buycoin_0))) :
                    btc_0 = upbit.get_balance(buycoin_0[4:])
                    upbit.sell_market_order(buycoin_0, btc_0)
                    count1 = 'true'
                if (count1 == 'false') and (now > buytime1) and (macd[1] > macd2[1]) :
                    btc_0 = upbit.get_balance(buycoin_0[4:])
                    upbit.sell_market_order(buycoin_0, btc_0)
                    count1 = 'true'

##################################2 buy_coin######################################################################################
                if (count2 == 'false') :
                    url = "https://api.upbit.com/v1/candles/minutes/5"
                    querystring = {"market":buycoin_1,"count":"200"}
                    response = requests.request("GET", url, params=querystring)
                    data = response.json()
                    df = pd.DataFrame(data)
                    df=df.iloc[::-1]
                    macd = MACD(df['trade_price'])
                if (count2 == 'false') and ((buy_price_1 * 1.03) < (get_current_price(buycoin_1))) :
                    btc_1 = upbit.get_balance(buycoin_1[4:])
                    upbit.sell_market_order(buycoin_1, btc_1)
                    count2 = 'true'
                if (count2 == 'false') and (now > buytime2) and (macd[1] > macd2[1]) :
                    btc_1 = upbit.get_balance(buycoin_1[4:])
                    upbit.sell_market_order(buycoin_1, btc_1)
                    count2 = 'true'

##################################3 buy_coin######################################################################################
                if (count3 == 'false') :
                    url = "https://api.upbit.com/v1/candles/minutes/5"
                    querystring = {"market":buycoin_2,"count":"200"}
                    response = requests.request("GET", url, params=querystring)
                    data = response.json()
                    df = pd.DataFrame(data)
                    df=df.iloc[::-1]
                    macd = MACD(df['trade_price'])
                if (count3 == 'false') and ((buy_price_2 * 1.03) < (get_current_price(buycoin_2))) :
                    btc_2 = upbit.get_balance(buycoin_2[4:])
                    upbit.sell_market_order(buycoin_2, btc_2)
                    count3 = 'true'
                if (count3 == 'false') and (now > buytime3) and (macd[1] > macd2[1]) :
                    btc_2 = upbit.get_balance(buycoin_2[4:])
                    upbit.sell_market_order(buycoin_2, btc_2)
                    count3 = 'true'

                #수동판매 대응
                if (count1 == 'false') and (upbit.get_balance(buycoin_0[4:]) == 0) :
                    count1 = 'true'
                if (count2 == 'false') and (upbit.get_balance(buycoin_1[4:]) == 0) :
                    count2 = 'true'
                if (count3 == 'false') and (upbit.get_balance(buycoin_2[4:]) == 0) :
                    count3 = 'true'

            else:
                #수동판매 대응
                if (count1 == 'false') and (upbit.get_balance(buycoin_0[4:]) == 0) :
                    count1 = 'true'
                if (count2 == 'false') and (upbit.get_balance(buycoin_1[4:]) == 0) :
                    count2 = 'true'
                if (count3 == 'false') and (upbit.get_balance(buycoin_2[4:]) == 0) :
                    count3 = 'true'

            n = n+1
            time.sleep(1)
        except Exception as e:
            print(e)
            time.sleep(1)
