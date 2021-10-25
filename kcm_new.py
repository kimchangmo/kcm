import time
import pyupbit
import datetime
import schedule
from fbprophet import Prophet
import requests
import pandas as pd
import webbrowser

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
def rsiindex(symbol):
    global rsi
    url = "https://api.upbit.com/v1/candles/minutes/1"

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
    print(symbol)
    print('Upbit 3 minute RSI:', rsi)
    print('')

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
all_coin = pyupbit.get_tickers('KRW')
all_coin.remove('KRW-MED')
all_coin.remove('KRW-CRE')
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

while True:
    n = 0
    while n < len(all_coin) : #총 코인 갯수
        try:
            coin = all_coin[n]
            predict_price(coin)
            #schedule.every().hour.do(lambda: predict_price(coin))
            #schedule.run_pending()

            now = datetime.datetime.now()
            start_time = get_start_time(coin)
            end_time = start_time + datetime.timedelta(days=1)

            if start_time + datetime.timedelta(seconds=600) < now < end_time - datetime.timedelta(seconds=60):
                print("진행중... :",  coin)
                #target_price = get_target_price(coin, 0.5)
                current_price = get_current_price(coin)
                rsiindex(coin)
                if rsi < 30 and predicted_close_price/current_price > 1.05 and (count1 == 'true' or count2 == 'true' or count3 == 'true') and (upbit.get_balance(coin[4:]) == 0):
                    if count1 == 'true':
                        upbit.buy_market_order(coin, 50000)
                        buycoin_0 = coin
                        buy_price_0 = current_price
                        water_buy_price_0 = current_price
                        print("구매완료 코인 1:",  buycoin_0)
                        count1 = 'false'
                        buytime1 = datetime.datetime.now() + datetime.timedelta(minutes=10)
                        price1_097 = 99999999999999
                        time.sleep(5)
                    elif count2 == 'true':
                        upbit.buy_market_order(coin, 50000)
                        buycoin_1 = coin
                        buy_price_1 = current_price
                        water_buy_price_1 = current_price
                        print("구매완료 코인 2:",  buycoin_1)
                        count2 = 'false'
                        buytime2 = datetime.datetime.now() + datetime.timedelta(minutes=10)
                        price2_097 = 99999999999999
                        time.sleep(5)
                    elif count3 == 'true':
                        upbit.buy_market_order(coin, 50000)
                        buycoin_2 = coin
                        buy_price_2 = current_price
                        water_buy_price_2 = current_price
                        print("구매완료 코인 3:",  buycoin_2)
                        count3 = 'false'
                        buytime3 = datetime.datetime.now() + datetime.timedelta(minutes=10)
                        price3_097 = 99999999999999
                        time.sleep(5)

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
                #물타기
                #elif (count1 == 'false') and ((buy_price_0 * 0.995) > (get_current_price(buycoin_0))) and (web1_1 == 'false'):
                #    krw = get_balance("KRW")
                #    if krw > 40000:
                #        upbit.buy_market_order(buycoin_0, 40000)
                #        #water_current_price1_1 = get_current_price(buycoin_0)
                #        time.sleep(1)
                #        water_buy_price_0 = 60000/(upbit.get_balance(buycoin_0[4:]))
                #    web1_1 = 'true'
                #    time.sleep(1)
                elif (count1 == 'false') and ((buy_price_0 * 0.995) > (get_current_price(buycoin_0))) and (web1_2 == 'false'):
                    krw = get_balance("KRW")
                    if krw > 100000:
                        upbit.buy_market_order(buycoin_0, 100000) 
                        #water_current_price1_2 = get_current_price(buycoin_0)
                        time.sleep(1)
                        water_buy_price_0 = 150000/(upbit.get_balance(buycoin_0[4:]))
                        web1_2 = 'true'
                    time.sleep(1)
                elif (count1 == 'false') and ((buy_price_0 * 0.97) > (get_current_price(buycoin_0))) and (web1_3 == 'false') and (now > buytime1) and (web1_2 == 'true'):
                    krw = get_balance("KRW")
                    if krw > 200000:
                        upbit.buy_market_order(buycoin_0, 200000) 
                        #water_current_price1_3 = get_current_price(buycoin_0)
                        time.sleep(1)
                        water_buy_price_0 = 350000/(upbit.get_balance(buycoin_0[4:]))
                        web1_3 = 'true'
                        buytime1 = datetime.datetime.now() + datetime.timedelta(minutes=10)
                        price1_097 = get_current_price(buycoin_0)
                    time.sleep(1)
                #elif (count1 == 'false') and ((buy_price_0 * 0.94) > (get_current_price(buycoin_0))) and (web1_4 == 'false') and (now > buytime1):
                elif (count1 == 'false') and (web1_4 == 'false') and (now > buytime1) and ((price1_097 * 0.97) > (get_current_price(buycoin_0))) and (web1_3 == 'true'):
                    krw = get_balance("KRW")
                    if krw > 300000:
                        upbit.buy_market_order(buycoin_0, 300000) 
                        #water_current_price1_4 = get_current_price(buycoin_0)
                        time.sleep(1)
                        water_buy_price_0 = 650000/(upbit.get_balance(buycoin_0[4:]))
                        web1_4 = 'true'
                    time.sleep(1)
                #elif (count1 == 'false') and ((buy_price_0 * 0.94) > (get_current_price(buycoin_0))) and (web1_5 == 'false'):
                #    krw = get_balance("KRW")
                #    if krw > 140000:
                #        upbit.buy_market_order(buycoin_0, 140000) 
                #        #water_current_price1_5 = get_current_price(buycoin_0)
                #        time.sleep(1)
                #        water_buy_price_0 = 300000/(upbit.get_balance(buycoin_0[4:]))
                #    web1_5 = 'true'
                #물타기 종료
                #elif (count1 == 'false') and ((buy_price_0 * 0.90) > (get_current_price(buycoin_0))) :
                #    btc_0 = upbit.get_balance(buycoin_0[4:])
                #    upbit.sell_market_order(buycoin_0, btc_0)
                #    all_coin.remove(buycoin_0)
                #    count1 = 'true'
                #    web1_1 = 'false'
                #    web1_2 = 'false'
                #    web1_3 = 'false'
                #    web1_4 = 'false'
                #    web1_5 = 'false'
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
                #물타기
                #elif (count2 == 'false') and ((buy_price_1 * 0.995) > (get_current_price(buycoin_1))) and (web2_1 == 'false'):
                #    krw = get_balance("KRW")
                #    if krw > 40000:
                #        upbit.buy_market_order(buycoin_1, 40000)
                #        #water_current_price1_1 = get_current_price(buycoin_1)
                #        time.sleep(1)
                #        water_buy_price_1 = 60000/(upbit.get_balance(buycoin_1[4:]))
                #    web2_1 = 'true'
                #    time.sleep(1)
                elif (count2 == 'false') and ((buy_price_1 * 0.995) > (get_current_price(buycoin_1))) and (web2_2 == 'false'):
                    krw = get_balance("KRW")
                    if krw > 100000:
                        upbit.buy_market_order(buycoin_1, 100000) 
                        #water_current_price1_2 = get_current_price(buycoin_1)
                        time.sleep(1)
                        water_buy_price_1 = 150000/(upbit.get_balance(buycoin_1[4:]))
                        web2_2 = 'true'
                    time.sleep(1)
                elif (count2 == 'false') and ((buy_price_1 * 0.97) > (get_current_price(buycoin_1))) and (web2_3 == 'false') and (now > buytime2) and (web2_2 == 'true'):
                    krw = get_balance("KRW")
                    if krw > 200000:
                        upbit.buy_market_order(buycoin_1, 200000) 
                        #water_current_price1_3 = get_current_price(buycoin_1)
                        time.sleep(1)
                        water_buy_price_1 = 350000/(upbit.get_balance(buycoin_1[4:]))
                        web2_3 = 'true'
                        buytime2 = datetime.datetime.now() + datetime.timedelta(minutes=10)
                        price2_097 = get_current_price(buycoin_1)
                    time.sleep(1)
                #elif (count2 == 'false') and ((buy_price_1 * 0.94) > (get_current_price(buycoin_1))) and (web2_4 == 'false') and (now > buytime2):
                elif (count2 == 'false') and (web2_4 == 'false') and (now > buytime2) and ((price2_097 * 0.97) > (get_current_price(buycoin_1))) and (web2_3 == 'true'):
                    krw = get_balance("KRW")
                    if krw > 300000:
                        upbit.buy_market_order(buycoin_1, 300000) 
                        #water_current_price1_4 = get_current_price(buycoin_1)
                        time.sleep(1)
                        water_buy_price_1 = 650000/(upbit.get_balance(buycoin_1[4:]))
                        web2_4 = 'true'
                    time.sleep(1)
                #elif (count2 == 'false') and ((buy_price_1 * 0.94) > (get_current_price(buycoin_1))) and (web2_5 == 'false'):
                #    krw = get_balance("KRW")
                #    if krw > 140000:
                #        upbit.buy_market_order(buycoin_1, 140000) 
                #        #water_current_price1_5 = get_current_price(buycoin_1)
                #        time.sleep(1)
                #        water_buy_price_1 = 300000/(upbit.get_balance(buycoin_1[4:]))
                #    web2_5 = 'true'
                #물타기 종료
                #elif (count2 == 'false') and ((buy_price_1 * 0.90) > (get_current_price(buycoin_1))) :
                #    btc_1 = upbit.get_balance(buycoin_1[4:])
                #    upbit.sell_market_order(buycoin_1, btc_1)
                #    all_coin.remove(buycoin_1)
                #    count2 = 'true'
                #    web2_1 = 'false'
                #    web2_2 = 'false'
                #    web2_3 = 'false'
                #    web2_4 = 'false'
                #    web2_5 = 'false'
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
                #물타기
                #elif (count3 == 'false') and ((buy_price_2 * 0.995) > (get_current_price(buycoin_2))) and (web3_1 == 'false'):
                #    krw = get_balance("KRW")
                #    if krw > 40000:
                #        upbit.buy_market_order(buycoin_2, 40000)
                #        #water_current_price1_1 = get_current_price(buycoin_2)
                #        time.sleep(1)
                #        water_buy_price_2 = 60000/(upbit.get_balance(buycoin_2[4:]))
                #    web3_1 = 'true'
                #    time.sleep(1)
                elif (count3 == 'false') and ((buy_price_2 * 0.995) > (get_current_price(buycoin_2))) and (web3_2 == 'false'):
                    krw = get_balance("KRW")
                    if krw > 100000:
                        upbit.buy_market_order(buycoin_2, 100000) 
                        #water_current_price1_2 = get_current_price(buycoin_2)
                        time.sleep(1)
                        water_buy_price_2 = 150000/(upbit.get_balance(buycoin_2[4:]))
                        web3_2 = 'true'
                    time.sleep(1)
                elif (count3 == 'false') and ((buy_price_2 * 0.97) > (get_current_price(buycoin_2))) and (web3_3 == 'false') and (now > buytime3) and (web3_2 == 'true'):
                    krw = get_balance("KRW")
                    if krw > 200000:
                        upbit.buy_market_order(buycoin_2, 200000) 
                        #water_current_price1_3 = get_current_price(buycoin_2)
                        time.sleep(1)
                        water_buy_price_2 = 350000/(upbit.get_balance(buycoin_2[4:]))
                        web3_3 = 'true'
                        buytime3 = datetime.datetime.now() + datetime.timedelta(minutes=10)
                        price3_097 = get_current_price(buycoin_2)
                    time.sleep(1)
                #elif (count3 == 'false') and ((buy_price_2 * 0.94) > (get_current_price(buycoin_2))) and (web3_4 == 'false') and (now > buytime3):
                elif (count3 == 'false') and (web3_4 == 'false') and (now > buytime3) and ((price3_097 * 0.97) > (get_current_price(buycoin_2))) and (web3_3 == 'true'):
                    krw = get_balance("KRW")
                    if krw > 300000:
                        upbit.buy_market_order(buycoin_2, 300000) 
                        #water_current_price1_4 = get_current_price(buycoin_2)
                        time.sleep(1)
                        water_buy_price_2 = 650000/(upbit.get_balance(buycoin_2[4:]))
                        web3_4 = 'true'
                    time.sleep(1)
                #elif (count3 == 'false') and ((buy_price_2 * 0.94) > (get_current_price(buycoin_2))) and (web3_5 == 'false'):
                #    krw = get_balance("KRW")
                #    if krw > 140000:
                #        upbit.buy_market_order(buycoin_2, 140000) 
                #        #water_current_price1_5 = get_current_price(buycoin_2)
                #        time.sleep(1)
                #        water_buy_price_2 = 300000/(upbit.get_balance(buycoin_2[4:]))
                #    web3_5 = 'true'
                #물타기 종료
                #elif (count3 == 'false') and ((buy_price_2 * 0.90) > (get_current_price(buycoin_2))) :
                #    btc_2 = upbit.get_balance(buycoin_2[4:])
                #    upbit.sell_market_order(buycoin_2, btc_2)
                #    all_coin.remove(buycoin_2)
                #    count3 = 'true'
                #    web3_1 = 'false'
                #    web3_2 = 'false'
                #    web3_3 = 'false'
                #    web3_4 = 'false'
                #    web3_5 = 'false'

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
                #print("판매중...")
                #if (count1 == 'false') :
                #    btc0 = get_balance(buycoin_0[4:])
                #    upbit.sell_market_order(buycoin_0, btc0)
                #    count1 = 'true'
                #    web1_1 = 'false'
                #    web1_2 = 'false'
                #    web1_3 = 'false'
                #    web1_4 = 'false'
                #    web1_5 = 'false'
                #if (count2 == 'false') :
                #    btc1 = get_balance(buycoin_1[4:])
                #    upbit.sell_market_order(buycoin_1, btc1)
                #    count2 = 'true'
                #    web2_1 = 'false'
                #    web2_2 = 'false'
                #    web2_3 = 'false'
                #    web2_4 = 'false'
                #    web2_5 = 'false'
                #if (count3 == 'false') :
                #    btc2 = get_balance(buycoin_2[4:])
                #    upbit.sell_market_order(buycoin_2, btc2)
                #    count2 = 'true'
                #    web3_1 = 'false'
                #    web3_2 = 'false'
                #    web3_3 = 'false'
                #    web3_4 = 'false'
                #    web3_5 = 'false'

                #코인리스트 리셋(손해매도 코인 remove 대응)    
                #all_coin = pyupbit.get_tickers('KRW')
                #all_coin.remove('KRW-MED')
                #all_coin.remove('KRW-CRE')

                #price_name.append(coin)
                #price_gap.append(predicted_close_price/current_price)
                #price_gap_desc.append(predicted_close_price/current_price)
                #print("종가 : ", predicted_close_price, "예상가 : ", predicted_close_price_kcm, "현재가 : ", current_price) #kcm
                
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
            
            n = n+1
            time.sleep(1)
        except Exception as e:
            print(e)
            time.sleep(1)
