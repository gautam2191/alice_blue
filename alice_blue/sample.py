import logging
import datetime
import statistics
from time import sleep
from alice_blue import *

# Config
username = '478725'
password = 'India@2023'
app_id = 'c3STHKxMLWEjx6z'
api_secret = 'fpU12UrP6z4XjDy3K791EyehtO5bnUuZBJiGIObVpIyIYNYzlFHhSuymCK3X9X98l7dsGEhcfTgCbDJ9XWVJPuvqvi5Gurv0d4Nc'
twoFA = '1991'
EMA_CROSS_SCRIP = 'INFY'
logging.basicConfig(level=logging.DEBUG)        # Optional for getting debug messages.
# Config

ltp = 0
alice = None
def event_handler_quote_update(message):
    global ltp
    ltp = message['ltp']

def buy_signal(ins_scrip):
    global alice
    alice.place_order(transaction_type = TransactionType.Buy,
                         instrument = ins_scrip,
                         quantity = 1,
                         order_type = OrderType.Market,
                         product_type = ProductType.Intraday)

def sell_signal(ins_scrip):
    global alice
    alice.place_order(transaction_type = TransactionType.Sell,
                         instrument = ins_scrip,
                         quantity = 1,
                         order_type = OrderType.Market,
                         product_type = ProductType.Intraday)
    
def main():
    global alice
    global username
    global password
    global twoFA
    global app_id
    global api_secret
    global EMA_CROSS_SCRIP
    minute_close = []
    session_id = AliceBlue.login_and_get_sessionID( username    = username, 
                                                    password    = password, 
                                                    twoFA       = twoFA,
                                                    app_id      = app_id,
                                                    api_secret  = api_secret)
    alice = AliceBlue(username = "478725", session_id = session_id, master_contracts_to_download=['NSE'])
    
    print(alice.get_balance()) # get balance / margin limits
    print(alice.get_profile()) # get profile
    print(alice.get_daywise_positions()) # get daywise positions
    print(alice.get_netwise_positions()) # get netwise positions
    print(alice.get_holding_positions()) # get holding positions
    
    ins_scrip = alice.get_instrument_by_symbol('NSE', EMA_CROSS_SCRIP)
    
    alice.start_websocket(subscribe_callback=event_handler_quote_update)
    alice.subscribe(ins_scrip, LiveFeedType.TICK_DATA)
    
    current_signal = ''
    while True:
        if(datetime.datetime.now().second == 0):
            minute_close.append(ltp)
            if(len(minute_close) > 20):
                sma_5 = statistics.mean(minute_close[-5:])
                sma_20 = statistics.mean(minute_close[-20:])
                if(current_signal != 'buy'):
                    if(sma_5 > sma_20):
                        buy_signal(ins_scrip)
                        current_signal = 'buy'
                if(current_signal != 'sell'):
                    if(sma_5 < sma_20):
                        sell_signal(ins_scrip)
                        current_signal = 'sell'
            sleep(1)    # sleep for 1 seconds
        sleep(0.2)      # sleep for 200ms
    
if(__name__ == '__main__'):
    main()