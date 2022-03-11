#api키 : Xe70g6uznpnBznhPBKPUBfY5pB52kvH0o7aqFiJsYN6ZxKtyxONAsMgNhI0JVOv6
#비밀 키 : RMgRWgyHizGLqdF7P2wf8LeajnewCHMjMLLrDR5nL2651324ulQ0DotI6l5RqMJV

#참고 : 
#pip install ccxt @@@
#pip install binance-connector @@@
#pip install --upgrade pip @@@
#pip install python-binance @@@
#pip install binance-futures @@@
#시간설정 time.nist.gov 로 변경! @@@

#시계 자동 동기화 적용 할것!!!

#-----------테스트코드--------------------------------------------------------------------------
import ccxt 
import pprint
import time
import pandas as pd
from datetime import datetime, timezone
from binance.spot import Spot as Client
from binance.client import Client as r_Client
import datetime as dt
import win32api

#키
api_key = "Xe70g6uznpnBznhPBKPUBfY5pB52kvH0o7aqFiJsYN6ZxKtyxONAsMgNhI0JVOv6"
secret  = "RMgRWgyHizGLqdF7P2wf8LeajnewCHMjMLLrDR5nL2651324ulQ0DotI6l5RqMJV"

################################참고####################################
"""
# 최소 요청가능한 수량 (BTC 기준)
# df_exchange_info : 최소 요청가능한 수량 (BTC 기준) DataFrame
# 바이낸스에는 최소 거래량이 있어서 이 거래량보다 작은 양의 거래는 오류가 발생
exchange_info = client.get_exchange_info()['symbols']
df_exchange_info = pd.DataFrame.from_dict(exchange_info).set_index('symbol')
# 요청량
tickers = client.get_ticker()
df_Tickers = pd.DataFrame(tickers).set_index('symbol').astype(float)
length = df_exchange_info.loc[coin,['filters']]['filters'][0]['minPrice'].find('1') - 1
price = round(df_Tickers.loc[coin,'bidPrice'] * 1.0003, length)
stepSize = float(df_exchange_info.filters[coin][2]['stepSize'])
print(stepSize)



# 보유 포지션 조회
import ccxt 
import pprint


with open("../api.txt") as f:
    lines = f.readlines()
    api_key = lines[0].strip()
    secret  = lines[1].strip()

binance = ccxt.binance(config={
    'apiKey': api_key, 
    'secret': secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})

balance = binance.fetch_balance()
positions = balance['info']['positions']

for position in positions:
    if position["symbol"] == "BTCUSDT":
        pprint.pprint(position)
"""

#이건머지?
#console.info(await binance.futuresMultipleOrders(orders))
#유의사항 : leverage * coin balance (레버리지 X 코인의 양)이 적어도 usdt기준 5.0(달러) 이상이어야 한다.
#############################################################################

#
binance = ccxt.binance(config={
    'apiKey': api_key, 
    'secret': secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})

#선물코인조회
#markets = binance.load_markets()
#for m in markets:
#    print(m)

#선물잔고조회
balance = binance.fetch_balance(params={"type": "future"})
print('##################################Start############################################')
print('선물잔고 :', balance['USDT'])

#특정코인 현재가 조회
#btc = binance.fetch_ticker("BTC/USDT")
#print(btc)

def rsi(symbol):
    #특정코인 과거데이터 조회
    """
    btc = binance.fetch_ohlcv(
        symbol=symbol, 
        timeframe='1d', 
        since=None, 
        limit=10
        )
    df = pd.DataFrame(btc, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
    df.set_index('datetime', inplace=True)
    """

    client = Client(api_key, secret)

    klines = client.klines(symbol, '15m', limit=500)

    df = pd.DataFrame(data={
        'open_time': [datetime.fromtimestamp(x[0] / 1000, timezone.utc) for x in klines],
        'open': [float(x[1]) for x in klines],
        'high': [float(x[2]) for x in klines],
        'low': [float(x[3]) for x in klines],
        'close': [float(x[4]) for x in klines],
        'volume': [float(x[5]) for x in klines],
        'close_time': [datetime.fromtimestamp(x[6] / 1000, timezone.utc) for x in klines],
    })

    #rsi 구하는놈
    closedata = df["close"]
    delta = closedata.diff()
    ups, downs = delta.copy(), delta.copy()
    ups[ups < 0] = 0 
    downs[downs > 0] = 0
    period = 14 
    au = ups.ewm(com = period-1, min_periods = period).mean() 
    ad = downs.abs().ewm(com = period-1, min_periods = period).mean() 
    RS = au/ad 

    return pd.Series(100 - (100/(1 + RS)), name = "RSI")
    
all_coin = []

#all_coin.append('BTCUSDT')
all_coin.append('LTCUSDT')
#all_coin.append('ETHUSDT')
#all_coin.append('MKRUSDT')
#all_coin.append('EOSUSDT')

#총 몇개 돌릴건지 설정
coin_buy_index = 1
#분봉 +1
delay_time = 17
#구매가
buy_money = 0.24 #레버리지 3배면 넣고싶은 금액의 3배 넣어야함

coin_one_buy = 'true'
coin_one_sell = 'true'

for i in range(0, coin_buy_index):
    globals()['count_{}'.format(i)] = 'true'
    globals()['old_plus_buy_{}'.format(i)] = 0

while True:
    n = 0
    while n < len(all_coin) : #총 코인 갯수
        try:
            coin = all_coin[n]
            now_rsi = float(rsi(coin).iloc[-1])
            old_rsi = float(rsi(coin).iloc[-2])
            old_old_rsi = float(rsi(coin).iloc[-3])

            now = dt.datetime.now()
            #print(now)
            
            #모든 코인구매칸이 다찼는지 확인
            for i in range(0, coin_buy_index):
                if (globals()['count_{}'.format(i)] == 'false'):
                    count_all = 'false'
                else:
                    count_all = 'true'
                    break

            #코인 롱 구매
            if (coin_one_buy == 'true'):
                #선물잔고조회
                balance = binance.fetch_balance(params={"type": "future"})
                
                if (buy_money < balance['USDT']['free']) :
                    print('코인(롱) :', coin)
                    #코인 현재가
                    client = r_Client(api_key=api_key, api_secret=secret)
                    price_buy = client.futures_symbol_ticker(symbol=coin)
                    water_buy_price_buy = price_buy['price']
                    all_purchase_volume_buy_buy = price_buy['price']
                    last_current_price_buy = float(price_buy['price'])
                    print('코인(롱) 구매가:', water_buy_price_buy)
                    print('')
                    #print('코인(롱) 물타기가:', float(water_buy_price_buy) * 0.98)
                    #print('코인(롱) 익절가:', float(water_buy_price_buy) * 1.02)

                    #구매시간
                    buytime_buy = dt.datetime.now() + dt.timedelta(minutes=delay_time)
                    buy_money_buy = buy_money
                    old_plus_buy =buy_money

                    #레버리지 설정
                    client.futures_change_leverage(symbol = coin, leverage = 3)
                    #구매
                    client.futures_create_order(
                        symbol=coin, side='BUY',
                        positionSide = 'LONG', type='MARKET', quantity=buy_money
                    ) #0.05 = 5.34USDT
    
                    #print('구매(롱)')
                    coin_one_buy = 'false'
                    time.sleep(1)    

            #코인 숏 구매
            if (coin_one_sell == 'true'):
                #선물잔고조회
                balance = binance.fetch_balance(params={"type": "future"})
                if (buy_money < balance['USDT']['free']) :
                    print('코인(숏) :', coin)
                    #코인 현재가
                    client = r_Client(api_key=api_key, api_secret=secret)          
                    price_sell = client.futures_symbol_ticker(symbol=coin)
                    water_buy_price_sell = price_sell['price']
                    all_purchase_volume_buy_sell = price_sell['price']
                    last_current_price_sell = price_sell['price']
                    print('코인(숏) 구매가:', water_buy_price_sell)
                    print('')
                    #print('코인(숏) 물타기가:', float(water_buy_price_sell) * 1.02)
                    #print('코인(숏) 익절가:', float(water_buy_price_sell) * 0.98)

                    #구매시간
                    buytime_sell = dt.datetime.now() + dt.timedelta(minutes=delay_time)
                    buy_money_sell = buy_money
                    old_plus_sell =buy_money

                    #레버리지 설정
                    client.futures_change_leverage(symbol = coin, leverage = 3)
                    #구매
                    client.futures_create_order(
                        symbol=coin, side='SELL',
                        positionSide = 'SHORT', type='MARKET', quantity=buy_money
                    )

                    #print('구매(숏)')
                    coin_one_sell = 'false'
                    time.sleep(1)    



            #코인 현재가(롱)
            client = r_Client(api_key=api_key, api_secret=secret)
            current_price_buy = client.futures_symbol_ticker(symbol=coin)
            current_price_buy = float(current_price_buy['price'])
            #print('현재가',current_price_buy)
            #코인 현재가(숏)
            client = r_Client(api_key=api_key, api_secret=secret)
            current_price_sell = client.futures_symbol_ticker(symbol=coin)
            current_price_sell = float(current_price_sell['price'])
            
            #2퍼 익절(롱)
            if (coin_one_buy == 'false') and ((float(water_buy_price_buy) * 1.02) < current_price_buy) :
            #if (coin_one_buy == 'false') :
                #레버리지 설정
                #client.futures_change_leverage(symbol = coin, leverage = 3)
                #판매
                #client.futures_create_order(
                #    symbol=coin, side='SELL',
                #    positionSide = 'LONG', type='STOP_MARKET', stopPrice=(current_price_buy-1), closePosition = 'true'
                #) #0.05 = 5.34USDT

                client.futures_create_order(
                    symbol=coin, side='SELL',
                    positionSide = 'LONG', type='MARKET', quantity=old_plus_buy
                )

                print('익절(롱)')
                print('')
                
                coin_one_buy = 'true'
                time.sleep(1)    

            #2퍼 익절(숏)
            if (coin_one_sell == 'false') and ((float(water_buy_price_sell) * 0.98) > current_price_sell) :
                #레버리지 설정
                #client.futures_change_leverage(symbol = coin, leverage = 3)
                #판매
                client.futures_create_order(
                    symbol=coin, side='BUY',
                    positionSide = 'SHORT', type='MARKET', quantity=old_plus_sell
                )
                print('익절(숏)')
                print('')
                
                coin_one_sell = 'true'
                time.sleep(1)    

            #물타기(롱)
            if (coin_one_buy == 'false') and (30 > old_old_rsi) and (30 < old_rsi) and (30 < now_rsi) and (now > buytime_buy) and ((float(last_current_price_buy) * 0.97) > current_price_buy):
            #if (coin_one_buy == 'false'):
                #선물잔고조회
                balance = binance.fetch_balance(params={"type": "future"})
                #balance = binance.fetch_balance()
                #print(balance['USDT']['used'])
                
                if (float(buy_money_buy)*2 < balance['USDT']['free']) :
                    #레버리지 설정
                    client.futures_change_leverage(symbol = coin, leverage = 3)
                    #구매
                    client.futures_create_order(
                        symbol=coin, side='BUY',
                        positionSide = 'LONG', type='MARKET', quantity=buy_money_buy*2
                    ) #0.05 = 5.34USDT

                    #구매시간 갱신
                    buytime_buy = dt.datetime.now() + dt.timedelta(minutes=delay_time)
                    #물타기가격 갱신(2배)
                    old_buy_money_buy = buy_money_buy
                    buy_money_buy = float(buy_money_buy)*2
                    
                    current_price_buy = client.futures_symbol_ticker(symbol=coin)
                    current_price_buy = float(current_price_buy['price'])
                    last_current_price_buy = current_price_buy
                    
                    #총 매수량 : all_purchase_volume_buy
                    if water_buy_price_buy == price_buy['price'] :
                        all_purchase_volume_buy = (float(water_buy_price_buy) * float(old_buy_money_buy)) + (float(current_price_buy) * float(buy_money_buy))
                    else :
                        all_purchase_volume_buy = (float(water_buy_price_buy) * float(old_plus_buy)) + (float(current_price_buy) * float(buy_money_buy))
                    
                    #총 비용 : old_plus_buy
                    if old_buy_money_buy == buy_money :
                        old_plus_buy = old_buy_money_buy + buy_money_buy
                    else :
                        old_plus_buy = old_plus_buy + buy_money_buy

                    #총 매수량
                    water_buy_price_buy = float(all_purchase_volume_buy)/float(old_plus_buy)
                    print('old_old_rsi(롱)', old_old_rsi)
                    print('old_rsi(롱)', old_rsi)
                    print('물타기(롱)')
                    print('물탄평단(롱)', water_buy_price_buy)
                    print('물탄익절가(롱)', float(water_buy_price_buy)*1.02)
                    print('')

                    time.sleep(1)    

            #배율에따른 청산방지(롱)
            if (coin_one_buy == 'false') and ((float(water_buy_price_buy) * 0.72) > current_price_buy):
            #if (coin_one_buy == 'false'):
                #선물잔고조회
                balance = binance.fetch_balance(params={"type": "future"})
                #balance = binance.fetch_balance()
                #print(balance['USDT']['used'])
                
                if (buy_money_buy*2 < balance['USDT']['free']) :
                    #레버리지 설정
                    client.futures_change_leverage(symbol = coin, leverage = 3)
                    #구매
                    client.futures_create_order(
                        symbol=coin, side='BUY',
                        positionSide = 'LONG', type='MARKET', quantity=buy_money_buy*2
                    ) #0.05 = 5.34USDT

                    #구매시간 갱신
                    buytime_buy = dt.datetime.now() + dt.timedelta(minutes=delay_time)
                    #물타기가격 갱신(2배)
                    old_buy_money_buy = buy_money_buy
                    buy_money_buy = buy_money_buy*2
                    
                    current_price_buy = client.futures_symbol_ticker(symbol=coin)
                    current_price_buy = float(current_price_buy['price'])
                    last_current_price_buy = current_price_buy
                    
                    #총 매수량 : all_purchase_volume_buy
                    if water_buy_price_buy == price_buy['price'] :
                        all_purchase_volume_buy = (float(water_buy_price_buy) * float(old_buy_money_buy)) + (float(current_price_buy) * float(buy_money_buy))
                    else :
                        all_purchase_volume_buy = (float(water_buy_price_buy) * float(old_plus_buy)) + (float(current_price_buy) * float(buy_money_buy))
                    
                    #총 비용 : old_plus_buy
                    if old_buy_money_buy == buy_money :
                        old_plus_buy = old_buy_money_buy + buy_money_buy
                    else :
                        old_plus_buy = old_plus_buy + buy_money_buy

                    #총 매수량
                    water_buy_price_buy = float(all_purchase_volume_buy)/float(old_plus_buy)
                    #print('old_old_rsi(롱)', old_old_rsi)
                    #print('old_rsi(롱)', old_rsi)
                    print('청산방지(롱)')
                    print('물탄평단(롱)', water_buy_price_buy)
                    print('물탄익절가(롱)', float(water_buy_price_buy)*1.02)
                    print('')

                    time.sleep(1) 

            #물타기(숏)
            if (coin_one_sell == 'false') and (70 < old_old_rsi) and (70 > old_rsi) and (70 > now_rsi) and (now > buytime_sell) and ((float(last_current_price_sell) * 1.03) < current_price_sell):
                #선물잔고조회
                balance = binance.fetch_balance(params={"type": "future"})
                #balance = binance.fetch_balance()
                #print(balance['USDT']['used'])
                
                if (buy_money_sell*2 < balance['USDT']['free']) :
                    #레버리지 설정
                    client.futures_change_leverage(symbol = coin, leverage = 3)
                    #구매
                    #upbit.buy_market_order(globals()['buycoin_{}'.format(i)], globals()['buy_money_{}'.format(i)]*2)
                    client.futures_create_order(
                        symbol=coin, side='SELL',
                        positionSide = 'SHORT', type='MARKET', quantity=buy_money_sell*2
                    ) #0.05 = 5.34USDT

                    #구매시간 갱신
                    buytime_sell = dt.datetime.now() + dt.timedelta(minutes=delay_time)
                    #물타기가격 갱신(2배)
                    old_buy_money_sell = buy_money_sell
                    buy_money_sell = buy_money_sell*2
                    
                    current_price_sell = client.futures_symbol_ticker(symbol=coin)
                    current_price_sell = float(current_price_sell['price'])
                    last_current_price_sell = current_price_sell
                    
                    #총 매수량 : all_purchase_volume_sell
                    if water_buy_price_sell == price_sell['price'] :
                        all_purchase_volume_sell = (float(water_buy_price_sell) * float(old_buy_money_sell)) + (float(current_price_sell) * float(buy_money_sell))
                    else :
                        all_purchase_volume_sell = (float(water_buy_price_sell) * float(old_plus_sell)) + (float(current_price_sell) * float(buy_money_sell))
                    
                    #총 비용 : old_plus_sell
                    if old_buy_money_sell == buy_money :
                        old_plus_sell = old_buy_money_sell + buy_money_sell
                    else :
                        old_plus_sell = old_plus_sell + buy_money_sell

                    #총 매수량
                    water_buy_price_sell = float(all_purchase_volume_sell)/float(old_plus_sell)
                    print('old_old_rsi(숏)', old_old_rsi)
                    print('old_rsi(숏)', old_rsi)
                    print('물타기(숏)')
                    print('물탄평단(숏)', water_buy_price_sell)
                    print('물탄익절가(숏)', float(water_buy_price_sell)*0.98)
                    print('')

                    time.sleep(1)    

            #배율에따른 청산방지(숏)
            if (coin_one_sell == 'false') and ((float(water_buy_price_sell) * 1.28) < current_price_sell):
                #선물잔고조회
                balance = binance.fetch_balance(params={"type": "future"})
                #balance = binance.fetch_balance()
                #print(balance['USDT']['used'])
                
                if (buy_money_sell*2 < balance['USDT']['free']) :
                    #레버리지 설정
                    client.futures_change_leverage(symbol = coin, leverage = 3)
                    #구매
                    #upbit.buy_market_order(globals()['buycoin_{}'.format(i)], globals()['buy_money_{}'.format(i)]*2)
                    client.futures_create_order(
                        symbol=coin, side='SELL',
                        positionSide = 'SHORT', type='MARKET', quantity=buy_money_sell*2
                    ) #0.05 = 5.34USDT

                    #구매시간 갱신
                    buytime_sell = dt.datetime.now() + dt.timedelta(minutes=delay_time)
                    #물타기가격 갱신(2배)
                    old_buy_money_sell = buy_money_sell
                    buy_money_sell = buy_money_sell*2
                    
                    current_price_sell = client.futures_symbol_ticker(symbol=coin)
                    current_price_sell = float(current_price_sell['price'])
                    last_current_price_sell = current_price_sell
                    
                    #총 매수량 : all_purchase_volume_sell
                    if water_buy_price_sell == price_sell['price'] :
                        all_purchase_volume_sell = (float(water_buy_price_sell) * float(old_buy_money_sell)) + (float(current_price_sell) * float(buy_money_sell))
                    else :
                        all_purchase_volume_sell = (float(water_buy_price_sell) * float(old_plus_sell)) + (float(current_price_sell) * float(buy_money_sell))
                    
                    #총 비용 : old_plus_sell
                    if old_buy_money_sell == buy_money :
                        old_plus_sell = old_buy_money_sell + buy_money_sell
                    else :
                        old_plus_sell = old_plus_sell + buy_money_sell

                    #총 매수량
                    water_buy_price_sell = float(all_purchase_volume_sell)/float(old_plus_sell)
                    #print('old_old_rsi(숏)', old_old_rsi)
                    #print('old_rsi(숏)', old_rsi)
                    print('청산방지(숏)')
                    print('물탄평단(숏)', water_buy_price_sell)
                    print('물탄익절가(숏)', float(water_buy_price_sell)*0.98)
                    print('')

                    time.sleep(1)    

            
            n = n+1
            time.sleep(2)
        except Exception as e:
            print(e)
            time.sleep(1)
