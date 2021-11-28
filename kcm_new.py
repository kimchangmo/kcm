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
    url = "https://api.upbit.com/v1/candles/minutes/5"
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
#while True:
rsi_name = [] #상승예상코인명
rsi_list = [] #상승예상수치
rsi_list_desc = []

price_name = [] #상승예상코인명
price_gap = [] #상승예상수치
price_gap_desc = []
#price_gap_high = []
# 자동매매 시작
count = 0
count1 = 'true'
count2 = 'true'
count3 = 'true'

web1_1 = 'false'
web1_2 = 'false'
web1_3 = 'false'
web1_4 = 'false'
web1_5 = 'false'

web2_1 = 'false'
web2_2 = 'false'
web2_3 = 'false'
web2_4 = 'false'
web2_5 = 'false'

web3_1 = 'false'
web3_2 = 'false'
web3_3 = 'false'
web3_4 = 'false'
web3_5 = 'false'

#물타기 총가격
old_plus_buy_0 = 0
old_plus_buy_1 = 0
old_plus_buy_2 = 0

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

            if True:
            #if start_time + datetime.timedelta(seconds=600) < now < end_time - datetime.timedelta(seconds=60):
                print("ing... :")
                #target_price = get_target_price(coin, 0.5)
                current_price = get_current_price(coin)
                rsiindex(coin)
                #print('band_high:', band_high)
                #print('current_price:', current_price)
                
                #거래대금
                url = "https://api.upbit.com/v1/ticker"
                querystring = {"markets":coin}
                response = requests.request("GET", url, params=querystring)
                res_json = response.json()
                acc_trade_price_24h = res_json[0]['acc_trade_price_24h']
                #print(coin,":", acc_trade_price_24h)
                #인공지능 적용 비교문
                #이전,이이전 비교문
                #if (30 > old_old_rsi) and (30 < oldrsi) and (predicted_close_price > open_price) and (acc_trade_price_24h > 100000000000) and (count1 == 'true' or count2 == 'true' or count3 == 'true') and (upbit.get_balance(coin[4:]) == 0):
                if (30 > old_old_rsi) and (30 < oldrsi) and (acc_trade_price_24h > 100000000000) and (count1 == 'true' or count2 == 'true' or count3 == 'true') and (upbit.get_balance(coin[4:]) == 0):
                    if count1 == 'true':
                        buy_money_0 = 100000
                        krw = get_balance("KRW")
                        if krw > buy_money_0:
                            upbit.buy_market_order(coin, buy_money_0)
                            buycoin_0 = coin
                            buy_price_0 = current_price
                            water_buy_price_0 = current_price
                            print("buy 1:",  buycoin_0)
                            count1 = 'false'
                            price1_097 = 99999999999999
                            #구매시간
                            buytime1 = datetime.datetime.now() + datetime.timedelta(minutes=7)
                            overtime1 = datetime.datetime.now() + datetime.timedelta(hours=3)
                            water_persent_0 = 0.99
                            print("buytime 1:",  buytime1)
                            print("overtime 1:",  overtime1)
                            time.sleep(5)
                    elif count2 == 'true':
                        buy_money_1 = 100000
                        krw = get_balance("KRW")
                        if krw > buy_money_1:
                            upbit.buy_market_order(coin, buy_money_1)
                            buycoin_1 = coin
                            buy_price_1 = current_price
                            water_buy_price_1 = current_price
                            print("buy 2:",  buycoin_1)
                            count2 = 'false'
                            #구매시간
                            buytime2 = datetime.datetime.now() + datetime.timedelta(minutes=7)
                            overtime2 = datetime.datetime.now() + datetime.timedelta(hours=3)
                            price2_097 = 99999999999999
                            water_persent_1 = 0.99
                            print("buytime 2:",  buytime2)
                            print("overtime 2:",  overtime2)
                            time.sleep(5)
                    elif count3 == 'true':
                        buy_money_2 = 100000
                        krw = get_balance("KRW")
                        if krw > buy_money_2:
                            upbit.buy_market_order(coin, buy_money_2)
                            buycoin_2 = coin
                            buy_price_2 = current_price
                            water_buy_price_2 = current_price
                            print("buy 3:",  buycoin_2)
                            count3 = 'false'
                            #구매시간
                            buytime3 = datetime.datetime.now() + datetime.timedelta(minutes=7)
                            overtime3 = datetime.datetime.now() + datetime.timedelta(hours=3)
                            price3_097 = 99999999999999
                            water_persent_2 = 0.99
                            print("buytime 3:",  buytime3)
                            print("overtime 3:",  overtime3)
                            time.sleep(5)

                if (count1 == 'false') :
                    rsiindex(buycoin_0)
                if (count1 == 'false') and ((water_buy_price_0 * 1.05) < (get_current_price(buycoin_0))) :
                    btc_0 = upbit.get_balance(buycoin_0[4:])
                    upbit.sell_market_order(buycoin_0, btc_0)
                    count1 = 'true'
                    web1_1 = 'false'
                    web1_2 = 'false'
                    web1_3 = 'false'
                    web1_4 = 'false'
                    web1_5 = 'false'
                #elif (count1 == 'false') and (rsi < 70) and (70 < oldrsi) and ((water_buy_price_0) < (get_current_price(buycoin_0))) :
                if (count1 == 'false') and (oldrsi < 70) and (70 < old_old_rsi) and ((water_buy_price_0) < (get_current_price(buycoin_0))) :
                    btc_0 = upbit.get_balance(buycoin_0[4:])
                    upbit.sell_market_order(buycoin_0, btc_0)
                    count1 = 'true'
                    web1_1 = 'false'
                    web1_2 = 'false'
                    web1_3 = 'false'
                    web1_4 = 'false'
                    web1_5 = 'false'
                if (count1 == 'false') and ((get_current_price(buycoin_0)) > band_high) and ((water_buy_price_0 * 1.03) < (get_current_price(buycoin_0))) :
                    btc_0 = upbit.get_balance(buycoin_0[4:])
                    upbit.sell_market_order(buycoin_0, btc_0)
                    count1 = 'true'
                    web1_1 = 'false'
                    web1_2 = 'false'
                    web1_3 = 'false'
                    web1_4 = 'false'
                    web1_5 = 'false'
                if (count1 == 'false') and (now > overtime1) and ((water_buy_price_0 * 1.01) < (get_current_price(buycoin_0))) :
                    btc_0 = upbit.get_balance(buycoin_0[4:])
                    upbit.sell_market_order(buycoin_0, btc_0)
                    count1 = 'true'
                    web1_1 = 'false'
                    web1_2 = 'false'
                    web1_3 = 'false'
                    web1_4 = 'false'
                    web1_5 = 'false'
                #다시 돌파시 물타기
                if (count1 == 'false') and (30 > old_old_rsi) and (30 < oldrsi) and (30 < rsi) and (now > buytime1) and ((buy_price_0 * 0.98) > (get_current_price(buycoin_0))):
                    krw = get_balance("KRW")
                    if krw > buy_money_0*2:
                        upbit.buy_market_order(buycoin_0, buy_money_0*2)
                        #구매시간 갱신
                        buytime1 = datetime.datetime.now() + datetime.timedelta(minutes=7)
                        #물타기가격 갱신(2배)
                        old_buy_money_0 = buy_money_0
                        buy_money_0 = buy_money_0*2
                        if old_buy_money_0 == 100000 :
                            old_plus_buy_0 = old_buy_money_0 + buy_money_0
                        else :
                            old_plus_buy_0 = old_plus_buy_0 + buy_money_0
                        water_buy_price_0 = old_plus_buy_0/upbit.get_balance(buycoin_0[4:])
                        water_persent_0 = water_persent_0 - 0.01
                        current_price = get_current_price(buycoin_0)
                        buy_price_0 = current_price
                        print("buycoin_0:",  buycoin_0)
                        print("water_buy_price_0:",  water_buy_price_0)
                        time.sleep(1)

                if (count2 == 'false') :
                    rsiindex(buycoin_1)
                if (count2 == 'false') and ((water_buy_price_1 * 1.05) < (get_current_price(buycoin_1))) :
                    btc_1 = upbit.get_balance(buycoin_1[4:])
                    upbit.sell_market_order(buycoin_1, btc_1)
                    count2 = 'true'
                    web2_1 = 'false'
                    web2_2 = 'false'
                    web2_3 = 'false'
                    web2_4 = 'false'
                    web2_5 = 'false'
                #elif (count2 == 'false') and (rsi < 70) and (70 < oldrsi) and ((water_buy_price_1) < (get_current_price(buycoin_1))) :
                if (count2 == 'false') and (oldrsi < 70) and (70 < old_old_rsi) and ((water_buy_price_1) < (get_current_price(buycoin_1))) :
                    btc_1 = upbit.get_balance(buycoin_1[4:])
                    upbit.sell_market_order(buycoin_1, btc_1)
                    count2 = 'true'
                    web2_1 = 'false'
                    web2_2 = 'false'
                    web2_3 = 'false'
                    web2_4 = 'false'
                    web2_5 = 'false'
                if (count2 == 'false') and ((get_current_price(buycoin_1)) > band_high) and ((water_buy_price_1 * 1.03) < (get_current_price(buycoin_1))) :
                    btc_1 = upbit.get_balance(buycoin_1[4:])
                    upbit.sell_market_order(buycoin_1, btc_1)
                    count2 = 'true'
                    web2_1 = 'false'
                    web2_2 = 'false'
                    web2_3 = 'false'
                    web2_4 = 'false'
                    web2_5 = 'false'
                if (count2 == 'false') and (now > overtime2) and ((water_buy_price_1 * 1.01) < (get_current_price(buycoin_1))) :
                    btc_1 = upbit.get_balance(buycoin_1[4:])
                    upbit.sell_market_order(buycoin_1, btc_1)
                    count2 = 'true'
                    web2_1 = 'false'
                    web2_2 = 'false'
                    web2_3 = 'false'
                    web2_4 = 'false'
                    web2_5 = 'false'
                #다시 돌파시 물타기
                if (count2 == 'false') and (30 > old_old_rsi) and (30 < oldrsi) and (30 < rsi) and (now > buytime2) and ((buy_price_1 * 0.98) > (get_current_price(buycoin_1))):
                    krw = get_balance("KRW")
                    if krw > buy_money_1*2:
                        upbit.buy_market_order(buycoin_1, buy_money_1*2)
                        #구매시간 갱신
                        buytime2 = datetime.datetime.now() + datetime.timedelta(minutes=7)
                        #물타기가격 갱신(2배)
                        old_buy_money_1 = buy_money_1
                        buy_money_1 = buy_money_1*2
                        if old_buy_money_1 == 100000 :
                            old_plus_buy_1 = old_buy_money_1 + buy_money_1
                        else :
                            old_plus_buy_1 = old_plus_buy_1 + buy_money_1
                        water_buy_price_1 = old_plus_buy_1/upbit.get_balance(buycoin_1[4:])
                        water_persent_1 = water_persent_1 - 0.01
                        current_price = get_current_price(buycoin_1)
                        buy_price_1 = current_price
                        print("buycoin_1:",  buycoin_1)
                        print("water_buy_price_1:",  water_buy_price_1)
                        time.sleep(1)

                if (count3 == 'false') :
                    rsiindex(buycoin_2)
                if (count3 == 'false') and ((water_buy_price_2 * 1.05) < (get_current_price(buycoin_2))) :
                    btc_2 = upbit.get_balance(buycoin_2[4:])
                    upbit.sell_market_order(buycoin_2, btc_2)
                    count3 = 'true'
                    web3_1 = 'false'
                    web3_2 = 'false'
                    web3_3 = 'false'
                    web3_4 = 'false'
                    web3_5 = 'false'
                #elif (count3 == 'false') and (rsi < 70) and (70 < oldrsi) and ((water_buy_price_2) < (get_current_price(buycoin_2))) :
                if (count3 == 'false') and (oldrsi < 70) and (70 < old_old_rsi) and ((water_buy_price_2) < (get_current_price(buycoin_2))) :
                    btc_2 = upbit.get_balance(buycoin_2[4:])
                    upbit.sell_market_order(buycoin_2, btc_2)
                    count3 = 'true'
                    web3_1 = 'false'
                    web3_2 = 'false'
                    web3_3 = 'false'
                    web3_4 = 'false'
                    web3_5 = 'false'
                if (count3 == 'false') and ((get_current_price(buycoin_2)) > band_high) and ((water_buy_price_2 * 1.03) < (get_current_price(buycoin_2))) :
                    btc_2 = upbit.get_balance(buycoin_2[4:])
                    upbit.sell_market_order(buycoin_2, btc_2)
                    count3 = 'true'
                    web3_1 = 'false'
                    web3_2 = 'false'
                    web3_3 = 'false'
                    web3_4 = 'false'
                    web3_5 = 'false'
                if (count3 == 'false') and (now > overtime3) and ((water_buy_price_2 * 1.01) < (get_current_price(buycoin_2))) :
                    btc_2 = upbit.get_balance(buycoin_2[4:])
                    upbit.sell_market_order(buycoin_2, btc_2)
                    count3 = 'true'
                    web3_1 = 'false'
                    web3_2 = 'false'
                    web3_3 = 'false'
                    web3_4 = 'false'
                    web3_5 = 'false'
                #다시 돌파시 물타기
                if (count3 == 'false') and (30 > old_old_rsi) and (30 < oldrsi) and (30 < rsi) and (now > buytime3) and ((buy_price_2 * 0.98) > (get_current_price(buycoin_2))):
                    krw = get_balance("KRW")
                    if krw > buy_money_2*2:
                        upbit.buy_market_order(buycoin_2, buy_money_2*2)
                        #구매시간 갱신
                        buytime3 = datetime.datetime.now() + datetime.timedelta(minutes=7)
                        #물타기가격 갱신(2배)
                        old_buy_money_2 = buy_money_2
                        buy_money_2 = buy_money_2*2
                        if old_buy_money_2 == 100000 :
                            old_plus_buy_2 = old_buy_money_2 + buy_money_2
                        else :
                            old_plus_buy_2 = old_plus_buy_2 + buy_money_2
                        water_buy_price_2 = old_plus_buy_2/upbit.get_balance(buycoin_2[4:])
                        water_persent_2 = water_persent_2 - 0.01
                        current_price = get_current_price(buycoin_2)
                        buy_price_2 = current_price
                        print("buycoin_2:",  buycoin_2)
                        print("water_buy_price_2:",  water_buy_price_2)
                        time.sleep(1)

                #수동판매 대응
                if (count1 == 'false') and (upbit.get_balance(buycoin_0[4:]) == 0) :
                    count1 = 'true'
                    web1_1 = 'false'
                    web1_2 = 'false'
                    web1_3 = 'false'
                    web1_4 = 'false'
                    web1_5 = 'false'
                if (count2 == 'false') and (upbit.get_balance(buycoin_1[4:]) == 0) :
                    count2 = 'true'
                    web2_1 = 'false'
                    web2_2 = 'false'
                    web2_3 = 'false'
                    web2_4 = 'false'
                    web2_5 = 'false'
                if (count3 == 'false') and (upbit.get_balance(buycoin_2[4:]) == 0) :
                    count3 = 'true'
                    web3_1 = 'false'
                    web3_2 = 'false'
                    web3_3 = 'false'
                    web3_4 = 'false'
                    web3_5 = 'false'

            else:
                #수동판매 대응
                if (count1 == 'false') and (upbit.get_balance(buycoin_0[4:]) == 0) :
                    count1 = 'true'
                    web1_1 = 'false'
                    web1_2 = 'false'
                    web1_3 = 'false'
                    web1_4 = 'false'
                    web1_5 = 'false'
                if (count2 == 'false') and (upbit.get_balance(buycoin_1[4:]) == 0) :
                    count2 = 'true'
                    web2_1 = 'false'
                    web2_2 = 'false'
                    web2_3 = 'false'
                    web2_4 = 'false'
                    web2_5 = 'false'
                if (count3 == 'false') and (upbit.get_balance(buycoin_2[4:]) == 0) :
                    count3 = 'true'
                    web3_1 = 'false'
                    web3_2 = 'false'
                    web3_3 = 'false'
                    web3_4 = 'false'
                    web3_5 = 'false'
                
                #8:59~9:10 까지는 익절코드만 돌아감
                if (count1 == 'false') :
                    rsiindex(buycoin_0)
                if (count1 == 'false') and ((water_buy_price_0 * 1.015) < (get_current_price(buycoin_0))) :
                    btc_0 = upbit.get_balance(buycoin_0[4:])
                    upbit.sell_market_order(buycoin_0, btc_0)
                    count1 = 'true'
                    web1_1 = 'false'
                    web1_2 = 'false'
                    web1_3 = 'false'
                    web1_4 = 'false'
                    web1_5 = 'false'
                elif (count1 == 'false') and (rsi > 70) :
                    btc_0 = upbit.get_balance(buycoin_0[4:])
                    upbit.sell_market_order(buycoin_0, btc_0)
                    count1 = 'true'
                    web1_1 = 'false'
                    web1_2 = 'false'
                    web1_3 = 'false'
                    web1_4 = 'false'
                    web1_5 = 'false'
                elif (count1 == 'false') and ((get_current_price(buycoin_0)) > band_high) and ((water_buy_price_0 * 1.005) < (get_current_price(buycoin_0))) :
                    btc_0 = upbit.get_balance(buycoin_0[4:])
                    upbit.sell_market_order(buycoin_0, btc_0)
                    count1 = 'true'
                    web1_1 = 'false'
                    web1_2 = 'false'
                    web1_3 = 'false'
                    web1_4 = 'false'
                    web1_5 = 'false'
                    
                if (count2 == 'false') :
                    rsiindex(buycoin_1)
                if (count2 == 'false') and ((water_buy_price_1 * 1.015) < (get_current_price(buycoin_1))) :
                    btc_1 = upbit.get_balance(buycoin_1[4:])
                    upbit.sell_market_order(buycoin_1, btc_1)
                    count2 = 'true'
                    web2_1 = 'false'
                    web2_2 = 'false'
                    web2_3 = 'false'
                    web2_4 = 'false'
                    web2_5 = 'false'
                elif (count2 == 'false') and (rsi > 70) :
                    btc_1 = upbit.get_balance(buycoin_1[4:])
                    upbit.sell_market_order(buycoin_1, btc_1)
                    count2 = 'true'
                    web2_1 = 'false'
                    web2_2 = 'false'
                    web2_3 = 'false'
                    web2_4 = 'false'
                    web2_5 = 'false'
                elif (count2 == 'false') and ((get_current_price(buycoin_1)) > band_high) and ((water_buy_price_1 * 1.005) < (get_current_price(buycoin_1))) :
                    btc_1 = upbit.get_balance(buycoin_1[4:])
                    upbit.sell_market_order(buycoin_1, btc_1)
                    count2 = 'true'
                    web2_1 = 'false'
                    web2_2 = 'false'
                    web2_3 = 'false'
                    web2_4 = 'false'
                    web2_5 = 'false'
                    
                if (count3 == 'false') :
                    rsiindex(buycoin_2)
                if (count3 == 'false') and ((water_buy_price_2 * 1.015) < (get_current_price(buycoin_2))) :
                    btc_2 = upbit.get_balance(buycoin_2[4:])
                    upbit.sell_market_order(buycoin_2, btc_2)
                    count3 = 'true'
                    web3_1 = 'false'
                    web3_2 = 'false'
                    web3_3 = 'false'
                    web3_4 = 'false'
                    web3_5 = 'false'
                elif (count3 == 'false') and (rsi > 70) :
                    btc_2 = upbit.get_balance(buycoin_2[4:])
                    upbit.sell_market_order(buycoin_2, btc_2)
                    count3 = 'true'
                    web3_1 = 'false'
                    web3_2 = 'false'
                    web3_3 = 'false'
                    web3_4 = 'false'
                    web3_5 = 'false'
                elif (count3 == 'false') and ((get_current_price(buycoin_2)) > band_high) and ((water_buy_price_2 * 1.005) < (get_current_price(buycoin_2))) :
                    btc_2 = upbit.get_balance(buycoin_2[4:])
                    upbit.sell_market_order(buycoin_2, btc_2)
                    count3 = 'true'
                    web3_1 = 'false'
                    web3_2 = 'false'
                    web3_3 = 'false'
                    web3_4 = 'false'
                    web3_5 = 'false'
            
            n = n+1
            time.sleep(1)
        except Exception as e:
            print(e)
            time.sleep(1)
