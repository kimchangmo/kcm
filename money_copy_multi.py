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
#import pprint
import time
import pandas as pd
from datetime import datetime, timezone
from binance.spot import Spot as Client
from binance.client import Client as r_Client
import datetime as dt
#import win32api

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

all_coin.append('ETHUSDT')
all_coin.append('LTCUSDT')
all_coin.append('YFIIUSDT')
all_coin.append('MKRUSDT')
all_coin.append('BCHUSDT')

#총 몇개 돌릴건지 설정
coin_buy_index = 5
#분봉 +1
delay_time = 17
#구매가
#####1만원 시작######
#globals()['buy_money_{}'.format(0)] = 0.01 #ETHUSDT
#globals()['buy_money_{}'.format(1)] = 0.24 #LTCUSDT
#globals()['buy_money_{}'.format(2)] = 0.013 #YFIIUSDT
#globals()['buy_money_{}'.format(3)] = 0.014 #MKRUSDT
#globals()['buy_money_{}'.format(4)] = 0.082 #BCHUSDT
#####2만원 시작######
globals()['buy_money_{}'.format(0)] = 0.02 #ETHUSDT
globals()['buy_money_{}'.format(1)] = 0.48 #LTCUSDT
globals()['buy_money_{}'.format(2)] = 0.026 #YFIIUSDT
globals()['buy_money_{}'.format(3)] = 0.028 #MKRUSDT
globals()['buy_money_{}'.format(4)] = 0.164 #BCHUSDT
#배율
all_leverage = 4

#coin_one_buy = 'true'
#coin_one_sell = 'true'

for i in range(0, coin_buy_index):
    #코인별 롱/숏 보유상태
    globals()['count_buy_{}'.format(i)] = 'true'
    globals()['count_sell_{}'.format(i)] = 'true'
    globals()['coin_{}'.format(i)] = all_coin[i]
    #globals()['old_plus_buy_{}'.format(i)] = 0

while True:
    i = 0
    while i < len(all_coin) : #총 코인 갯수
        try:
            #coin = all_coin[n]
            now_rsi = float(rsi(globals()['coin_{}'.format(i)]).iloc[-1])
            old_rsi = float(rsi(globals()['coin_{}'.format(i)]).iloc[-2])
            old_old_rsi = float(rsi(globals()['coin_{}'.format(i)]).iloc[-3])

            now = dt.datetime.now()

            #코인 롱 구매
            if (globals()['count_buy_{}'.format(i)] == 'true') and (30 > old_old_rsi) and (30 < old_rsi) and (30 < now_rsi):
                #선물잔고조회
                balance = binance.fetch_balance(params={"type": "future"})
                
                if (globals()['buy_money_{}'.format(i)] < balance['USDT']['free']) :
                    print('코인(롱) :', globals()['coin_{}'.format(i)])
                    #코인 현재가
                    client = r_Client(api_key=api_key, api_secret=secret)
                    globals()['price_buy_{}'.format(i)] = client.futures_symbol_ticker(symbol=globals()['coin_{}'.format(i)])
                    globals()['water_buy_price_buy_{}'.format(i)] = globals()['price_buy_{}'.format(i)]['price']
                    #all_purchase_volume_buy_buy = globals()['price_buy_{}'.format(i)]['price']
                    globals()['last_current_price_buy_{}'.format(i)] = float(globals()['price_buy_{}'.format(i)]['price'])
                    print('코인(롱) 구매가:', globals()['water_buy_price_buy_{}'.format(i)])
                    print('')
                    #print('코인(롱) 물타기가:', float(globals()['water_buy_price_buy_{}'.format(i)]) * 0.98)
                    #print('코인(롱) 익절가:', float(globals()['water_buy_price_buy_{}'.format(i)]) * 1.02)

                    #구매시간
                    globals()['buytime_buy_{}'.format(i)] = dt.datetime.now() + dt.timedelta(minutes=delay_time)
                    globals()['buy_money_buy_{}'.format(i)] = globals()['buy_money_{}'.format(i)]
                    globals()['old_plus_buy_{}'.format(i)] = globals()['buy_money_{}'.format(i)]

                    #레버리지 설정
                    client.futures_change_leverage(symbol = globals()['coin_{}'.format(i)], leverage = all_leverage)
                    #구매
                    client.futures_create_order(
                        symbol=globals()['coin_{}'.format(i)], side='BUY',
                        positionSide = 'LONG', type='MARKET', quantity=globals()['buy_money_{}'.format(i)]
                    ) #0.05 = 5.34USDT
    
                    #print('구매(롱)')
                    globals()['count_buy_{}'.format(i)] = 'false'
                    time.sleep(1)    

            #코인 숏 구매
            if (globals()['count_sell_{}'.format(i)] == 'true') and (70 < old_old_rsi) and (70 > old_rsi) and (70 > now_rsi):
                #선물잔고조회
                balance = binance.fetch_balance(params={"type": "future"})
                if (globals()['buy_money_{}'.format(i)] < balance['USDT']['free']) :
                    print('코인(숏) :', globals()['coin_{}'.format(i)])
                    #코인 현재가
                    client = r_Client(api_key=api_key, api_secret=secret)          
                    globals()['price_sell_{}'.format(i)] = client.futures_symbol_ticker(symbol=globals()['coin_{}'.format(i)])
                    globals()['water_buy_price_sell_{}'.format(i)] = globals()['price_sell_{}'.format(i)]['price']
                    #all_purchase_volume_buy_sell = globals()['price_sell_{}'.format(i)]['price']
                    globals()['last_current_price_sell_{}'.format(i)] = globals()['price_sell_{}'.format(i)]['price']
                    print('코인(숏) 구매가:', globals()['water_buy_price_sell_{}'.format(i)])
                    print('')
                    #print('코인(숏) 물타기가:', float(globals()['water_buy_price_sell_{}'.format(i)]) * 1.02)
                    #print('코인(숏) 익절가:', float(globals()['water_buy_price_sell_{}'.format(i)]) * 0.98)

                    #구매시간
                    globals()['buytime_sell_{}'.format(i)] = dt.datetime.now() + dt.timedelta(minutes=delay_time)
                    globals()['buy_money_sell_{}'.format(i)] = globals()['buy_money_{}'.format(i)]
                    globals()['old_plus_sell_{}'.format(i)] =globals()['buy_money_{}'.format(i)]

                    #레버리지 설정
                    client.futures_change_leverage(symbol = globals()['coin_{}'.format(i)], leverage = all_leverage)
                    #구매
                    client.futures_create_order(
                        symbol=globals()['coin_{}'.format(i)], side='SELL',
                        positionSide = 'SHORT', type='MARKET', quantity=globals()['buy_money_{}'.format(i)]
                    )

                    #print('구매(숏)')
                    globals()['count_sell_{}'.format(i)] = 'false'
                    time.sleep(1)    



            #코인 현재가(롱)
            client = r_Client(api_key=api_key, api_secret=secret)
            globals()['current_price_buy_{}'.format(i)] = client.futures_symbol_ticker(symbol=globals()['coin_{}'.format(i)])
            globals()['current_price_buy_{}'.format(i)] = float(globals()['current_price_buy_{}'.format(i)]['price'])
            #print('현재가',globals()['current_price_buy_{}'.format(i)])
            #코인 현재가(숏)
            client = r_Client(api_key=api_key, api_secret=secret)
            globals()['current_price_sell_{}'.format(i)] = client.futures_symbol_ticker(symbol=globals()['coin_{}'.format(i)])
            globals()['current_price_sell_{}'.format(i)] = float(globals()['current_price_sell_{}'.format(i)]['price'])
            
            #2퍼 익절(롱)
            if (globals()['count_buy_{}'.format(i)] == 'false') and ((float(globals()['water_buy_price_buy_{}'.format(i)]) * 1.02) < globals()['current_price_buy_{}'.format(i)]) :
            #if (globals()['count_buy_{}'.format(i)] == 'false') :
                client.futures_create_order(
                    symbol=globals()['coin_{}'.format(i)], side='SELL',
                    positionSide = 'LONG', type='MARKET', quantity=globals()['old_plus_buy_{}'.format(i)]
                )
                print('코인(롱) :', globals()['coin_{}'.format(i)])
                print('익절(롱)')
                print('익절가:', globals()['current_price_buy_{}'.format(i)])
                print('')
                
                globals()['count_buy_{}'.format(i)] = 'true'
                time.sleep(1)    

            #2퍼 익절(숏)
            if (globals()['count_sell_{}'.format(i)] == 'false') and ((float(globals()['water_buy_price_sell_{}'.format(i)]) * 0.98) > globals()['current_price_sell_{}'.format(i)]) :
                client.futures_create_order(
                    symbol=globals()['coin_{}'.format(i)], side='BUY',
                    positionSide = 'SHORT', type='MARKET', quantity=globals()['old_plus_sell_{}'.format(i)]
                )
                print('코인(롱) :', globals()['coin_{}'.format(i)])
                print('익절(숏)')
                print('익절가:', globals()['current_price_sell_{}'.format(i)])
                print('')
                
                globals()['count_sell_{}'.format(i)] = 'true'
                time.sleep(1)    

            #물타기(롱)
            if (globals()['count_buy_{}'.format(i)] == 'false') and (30 > old_old_rsi) and (30 < old_rsi) and (30 < now_rsi) and (now > globals()['buytime_buy_{}'.format(i)]) and ((float(globals()['last_current_price_buy_{}'.format(i)]) * 0.97) > globals()['current_price_buy_{}'.format(i)]):
            #if (globals()['count_buy_{}'.format(i)] == 'false'):
                #선물잔고조회
                balance = binance.fetch_balance(params={"type": "future"})
                #balance = binance.fetch_balance()
                #print(balance['USDT']['used'])
                
                if (float(globals()['buy_money_buy_{}'.format(i)])*2 < balance['USDT']['free']) :
                    #레버리지 설정
                    client.futures_change_leverage(symbol = globals()['coin_{}'.format(i)], leverage = all_leverage)
                    #구매
                    client.futures_create_order(
                        symbol=globals()['coin_{}'.format(i)], side='BUY',
                        positionSide = 'LONG', type='MARKET', quantity=globals()['buy_money_buy_{}'.format(i)]*2
                    ) #0.05 = 5.34USDT

                    #구매시간 갱신
                    globals()['buytime_buy_{}'.format(i)] = dt.datetime.now() + dt.timedelta(minutes=delay_time)
                    #물타기가격 갱신(2배)
                    globals()['old_buy_money_buy_{}'.format(i)] = globals()['buy_money_buy_{}'.format(i)]
                    globals()['buy_money_buy_{}'.format(i)] = float(globals()['buy_money_buy_{}'.format(i)])*2
                    
                    globals()['current_price_buy_{}'.format(i)] = client.futures_symbol_ticker(symbol=globals()['coin_{}'.format(i)])
                    globals()['current_price_buy_{}'.format(i)] = float(globals()['current_price_buy_{}'.format(i)]['price'])
                    globals()['last_current_price_buy_{}'.format(i)] = globals()['current_price_buy_{}'.format(i)]
                    
                    #총 매수량 : all_purchase_volume_buy
                    if globals()['water_buy_price_buy_{}'.format(i)] == globals()['price_buy_{}'.format(i)]['price'] :
                        globals()['all_purchase_volume_buy_{}'.format(i)] = (float(globals()['water_buy_price_buy_{}'.format(i)]) * float(globals()['old_buy_money_buy_{}'.format(i)])) + (float(globals()['current_price_buy_{}'.format(i)]) * float(globals()['buy_money_buy_{}'.format(i)]))
                    else :
                        globals()['all_purchase_volume_buy_{}'.format(i)] = (float(globals()['water_buy_price_buy_{}'.format(i)]) * float(globals()['old_plus_buy_{}'.format(i)])) + (float(globals()['current_price_buy_{}'.format(i)]) * float(globals()['buy_money_buy_{}'.format(i)]))
                    
                    #총 비용 : globals()['old_plus_buy_{}'.format(i)]
                    if globals()['old_buy_money_buy_{}'.format(i)] == globals()['buy_money_{}'.format(i)] :
                        globals()['old_plus_buy_{}'.format(i)] = globals()['old_buy_money_buy_{}'.format(i)] + globals()['buy_money_buy_{}'.format(i)]
                    else :
                        globals()['old_plus_buy_{}'.format(i)] = globals()['old_plus_buy_{}'.format(i)] + globals()['buy_money_buy_{}'.format(i)]

                    #총 매수량
                    globals()['water_buy_price_buy_{}'.format(i)] = float(globals()['all_purchase_volume_buy_{}'.format(i)])/float(globals()['old_plus_buy_{}'.format(i)])
                    print('코인(롱) :', globals()['coin_{}'.format(i)])
                    print('old_old_rsi(롱)', old_old_rsi)
                    print('old_rsi(롱)', old_rsi)
                    print('물타기(롱)')
                    print('물탄평단(롱)', globals()['water_buy_price_buy_{}'.format(i)])
                    print('물탄익절가(롱)', float(globals()['water_buy_price_buy_{}'.format(i)])*1.02)
                    print('')

                    time.sleep(1)    

            #배율에따른 청산방지(롱)
            if (globals()['count_buy_{}'.format(i)] == 'false') and ((float(globals()['water_buy_price_buy_{}'.format(i)]) * 0.80) > globals()['current_price_buy_{}'.format(i)]):
            #if (globals()['count_buy_{}'.format(i)] == 'false'):
                #선물잔고조회
                balance = binance.fetch_balance(params={"type": "future"})
                #balance = binance.fetch_balance()
                #print(balance['USDT']['used'])
                
                if (globals()['buy_money_buy_{}'.format(i)]*2 < balance['USDT']['free']) :
                    #레버리지 설정
                    client.futures_change_leverage(symbol = globals()['coin_{}'.format(i)], leverage = all_leverage)
                    #구매
                    client.futures_create_order(
                        symbol=globals()['coin_{}'.format(i)], side='BUY',
                        positionSide = 'LONG', type='MARKET', quantity=globals()['buy_money_buy_{}'.format(i)]*2
                    ) #0.05 = 5.34USDT

                    #구매시간 갱신
                    globals()['buytime_buy_{}'.format(i)] = dt.datetime.now() + dt.timedelta(minutes=delay_time)
                    #물타기가격 갱신(2배)
                    globals()['old_buy_money_buy_{}'.format(i)] = globals()['buy_money_buy_{}'.format(i)]
                    globals()['buy_money_buy_{}'.format(i)] = globals()['buy_money_buy_{}'.format(i)]*2
                    
                    globals()['current_price_buy_{}'.format(i)] = client.futures_symbol_ticker(symbol=globals()['coin_{}'.format(i)])
                    globals()['current_price_buy_{}'.format(i)] = float(globals()['current_price_buy_{}'.format(i)]['price'])
                    globals()['last_current_price_buy_{}'.format(i)] = globals()['current_price_buy_{}'.format(i)]
                    
                    #총 매수량 : globals()['all_purchase_volume_buy_{}'.format(i)]
                    if globals()['water_buy_price_buy_{}'.format(i)] == globals()['price_buy_{}'.format(i)]['price'] :
                        globals()['all_purchase_volume_buy_{}'.format(i)] = (float(globals()['water_buy_price_buy_{}'.format(i)]) * float(globals()['old_buy_money_buy_{}'.format(i)])) + (float(globals()['current_price_buy_{}'.format(i)]) * float(globals()['buy_money_buy_{}'.format(i)]))
                    else :
                        globals()['all_purchase_volume_buy_{}'.format(i)] = (float(globals()['water_buy_price_buy_{}'.format(i)]) * float(globals()['old_plus_buy_{}'.format(i)])) + (float(globals()['current_price_buy_{}'.format(i)]) * float(globals()['buy_money_buy_{}'.format(i)]))
                    
                    #총 비용 : globals()['old_plus_buy_{}'.format(i)]
                    if globals()['old_buy_money_buy_{}'.format(i)] == globals()['buy_money_{}'.format(i)] :
                        globals()['old_plus_buy_{}'.format(i)] = globals()['old_buy_money_buy_{}'.format(i)] + globals()['buy_money_buy_{}'.format(i)]
                    else :
                        globals()['old_plus_buy_{}'.format(i)] = globals()['old_plus_buy_{}'.format(i)] + globals()['buy_money_buy_{}'.format(i)]

                    #총 매수량
                    globals()['water_buy_price_buy_{}'.format(i)] = float(globals()['all_purchase_volume_buy_{}'.format(i)])/float(globals()['old_plus_buy_{}'.format(i)])
                    #print('old_old_rsi(롱)', old_old_rsi)
                    #print('old_rsi(롱)', old_rsi)
                    print('코인(롱) :', globals()['coin_{}'.format(i)])
                    print('청산방지(롱)')
                    print('물탄평단(롱)', globals()['water_buy_price_buy_{}'.format(i)])
                    print('물탄익절가(롱)', float(globals()['water_buy_price_buy_{}'.format(i)])*1.02)
                    print('')

                    time.sleep(1) 

            #물타기(숏)
            if (globals()['count_sell_{}'.format(i)] == 'false') and (70 < old_old_rsi) and (70 > old_rsi) and (70 > now_rsi) and (now > globals()['buytime_sell_{}'.format(i)]) and ((float(globals()['last_current_price_sell_{}'.format(i)]) * 1.03) < globals()['current_price_sell_{}'.format(i)]):
                #선물잔고조회
                balance = binance.fetch_balance(params={"type": "future"})
                #balance = binance.fetch_balance()
                #print(balance['USDT']['used'])
                
                if (globals()['buy_money_sell_{}'.format(i)]*2 < balance['USDT']['free']) :
                    #레버리지 설정
                    client.futures_change_leverage(symbol = globals()['coin_{}'.format(i)], leverage = all_leverage)
                    #구매
                    #upbit.buy_market_order(globals()['buycoin_{}'.format(i)], globals()['buy_money_{}'.format(i)]*2)
                    client.futures_create_order(
                        symbol=globals()['coin_{}'.format(i)], side='SELL',
                        positionSide = 'SHORT', type='MARKET', quantity=globals()['buy_money_sell_{}'.format(i)]*2
                    ) #0.05 = 5.34USDT

                    #구매시간 갱신
                    globals()['buytime_sell_{}'.format(i)] = dt.datetime.now() + dt.timedelta(minutes=delay_time)
                    #물타기가격 갱신(2배)
                    globals()['old_buy_money_sell_{}'.format(i)] = globals()['buy_money_sell_{}'.format(i)]
                    globals()['buy_money_sell_{}'.format(i)] = globals()['buy_money_sell_{}'.format(i)]*2
                    
                    globals()['current_price_sell_{}'.format(i)] = client.futures_symbol_ticker(symbol=globals()['coin_{}'.format(i)])
                    globals()['current_price_sell_{}'.format(i)] = float(globals()['current_price_sell_{}'.format(i)]['price'])
                    globals()['last_current_price_sell_{}'.format(i)] = globals()['current_price_sell_{}'.format(i)]
                    
                    #총 매수량 : all_purchase_volume_sell
                    if globals()['water_buy_price_sell_{}'.format(i)] == globals()['price_sell_{}'.format(i)]['price'] :
                        globals()['all_purchase_volume_sell_{}'.format(i)] = (float(globals()['water_buy_price_sell_{}'.format(i)]) * float(globals()['old_buy_money_sell_{}'.format(i)])) + (float(globals()['current_price_sell_{}'.format(i)]) * float(globals()['buy_money_sell_{}'.format(i)]))
                    else :
                        globals()['all_purchase_volume_sell_{}'.format(i)] = (float(globals()['water_buy_price_sell_{}'.format(i)]) * float(globals()['old_plus_sell_{}'.format(i)])) + (float(globals()['current_price_sell_{}'.format(i)]) * float(globals()['buy_money_sell_{}'.format(i)]))
                    
                    #총 비용 : globals()['old_plus_sell_{}'.format(i)]
                    if globals()['old_buy_money_sell_{}'.format(i)] == globals()['buy_money_{}'.format(i)] :
                        globals()['old_plus_sell_{}'.format(i)] = globals()['old_buy_money_sell_{}'.format(i)] + globals()['buy_money_sell_{}'.format(i)]
                    else :
                        globals()['old_plus_sell_{}'.format(i)] = globals()['old_plus_sell_{}'.format(i)] + globals()['buy_money_sell_{}'.format(i)]

                    #총 매수량
                    globals()['water_buy_price_sell_{}'.format(i)] = float(globals()['all_purchase_volume_sell_{}'.format(i)])/float(globals()['old_plus_sell_{}'.format(i)])
                    print('코인(롱) :', globals()['coin_{}'.format(i)])
                    print('old_old_rsi(숏)', old_old_rsi)
                    print('old_rsi(숏)', old_rsi)
                    print('물타기(숏)')
                    print('물탄평단(숏)', globals()['water_buy_price_sell_{}'.format(i)])
                    print('물탄익절가(숏)', float(globals()['water_buy_price_sell_{}'.format(i)])*0.98)
                    print('')

                    time.sleep(1)    

            #배율에따른 청산방지(숏)
            if (globals()['count_sell_{}'.format(i)] == 'false') and ((float(globals()['water_buy_price_sell_{}'.format(i)]) * 1.20) < globals()['current_price_sell_{}'.format(i)]):
                #선물잔고조회
                balance = binance.fetch_balance(params={"type": "future"})
                #balance = binance.fetch_balance()
                #print(balance['USDT']['used'])
                
                if (globals()['buy_money_sell_{}'.format(i)]*2 < balance['USDT']['free']) :
                    #레버리지 설정
                    client.futures_change_leverage(symbol = globals()['coin_{}'.format(i)], leverage = all_leverage)
                    #구매
                    #upbit.buy_market_order(globals()['buycoin_{}'.format(i)], globals()['buy_money_{}'.format(i)]*2)
                    client.futures_create_order(
                        symbol=globals()['coin_{}'.format(i)], side='SELL',
                        positionSide = 'SHORT', type='MARKET', quantity=globals()['buy_money_sell_{}'.format(i)]*2
                    ) #0.05 = 5.34USDT

                    #구매시간 갱신
                    globals()['buytime_sell_{}'.format(i)] = dt.datetime.now() + dt.timedelta(minutes=delay_time)
                    #물타기가격 갱신(2배)
                    globals()['old_buy_money_sell_{}'.format(i)] = globals()['buy_money_sell_{}'.format(i)]
                    globals()['buy_money_sell_{}'.format(i)] = globals()['buy_money_sell_{}'.format(i)]*2
                    
                    globals()['current_price_sell_{}'.format(i)] = client.futures_symbol_ticker(symbol=globals()['coin_{}'.format(i)])
                    globals()['current_price_sell_{}'.format(i)] = float(globals()['current_price_sell_{}'.format(i)]['price'])
                    globals()['last_current_price_sell_{}'.format(i)] = globals()['current_price_sell_{}'.format(i)]
                    
                    #총 매수량 : globals()['all_purchase_volume_sell_{}'.format(i)]
                    if globals()['water_buy_price_sell_{}'.format(i)] == globals()['price_sell_{}'.format(i)]['price'] :
                        globals()['all_purchase_volume_sell_{}'.format(i)] = (float(globals()['water_buy_price_sell_{}'.format(i)]) * float(globals()['old_buy_money_sell_{}'.format(i)])) + (float(globals()['current_price_sell_{}'.format(i)]) * float(globals()['buy_money_sell_{}'.format(i)]))
                    else :
                        globals()['all_purchase_volume_sell_{}'.format(i)] = (float(globals()['water_buy_price_sell_{}'.format(i)]) * float(globals()['old_plus_sell_{}'.format(i)])) + (float(globals()['current_price_sell_{}'.format(i)]) * float(globals()['buy_money_sell_{}'.format(i)]))
                    
                    #총 비용 : globals()['old_plus_sell_{}'.format(i)]
                    if globals()['old_buy_money_sell_{}'.format(i)] == globals()['buy_money_{}'.format(i)] :
                        globals()['old_plus_sell_{}'.format(i)] = globals()['old_buy_money_sell_{}'.format(i)] + globals()['buy_money_sell_{}'.format(i)]
                    else :
                        globals()['old_plus_sell_{}'.format(i)] = globals()['old_plus_sell_{}'.format(i)] + globals()['buy_money_sell_{}'.format(i)]

                    #총 매수량
                    globals()['water_buy_price_sell_{}'.format(i)] = float(globals()['all_purchase_volume_sell_{}'.format(i)])/float(globals()['old_plus_sell_{}'.format(i)])
                    #print('old_old_rsi(숏)', old_old_rsi)
                    #print('old_rsi(숏)', old_rsi)
                    print('코인(롱) :', globals()['coin_{}'.format(i)])
                    print('청산방지(숏)')
                    print('물탄평단(숏)', globals()['water_buy_price_sell_{}'.format(i)])
                    print('물탄익절가(숏)', float(globals()['water_buy_price_sell_{}'.format(i)])*0.98)
                    print('')

                    time.sleep(1)    

            
            i = i+1
            time.sleep(2)
        except Exception as e:
            print(e)
            time.sleep(1)
