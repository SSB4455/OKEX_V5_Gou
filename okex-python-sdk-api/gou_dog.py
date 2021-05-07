import okex.account_api as account
import okex.futures_api as future
import okex.lever_api as lever
import okex.spot_api as spot
import json
import os, time, datetime

gouId = datetime.datetime.now().replace(microsecond=0).isoformat("T").replace(':', '')
accountAPI = None
levelAPI = None
spotAPI = None
instId = 'DOGE-USDT'
buy_price = -1
current_price = None
deal_side = 'buy'
upl_ratio = 0
loss_limite = -0.012
gain_limite = 0.009
losted_times = 0
leverage = 3


def init(api_key, api_secret_key, passphrase, instId2):
    global accountAPI, spotAPI, levelAPI, gouId, instId, leverage, loss_limite, gain_limite
    accountAPI = account.AccountAPI(api_key, api_secret_key, passphrase, False)
    spotAPI = spot.SpotAPI(api_key, api_secret_key, passphrase, False)
    levelAPI = lever.LeverAPI(api_key, api_secret_key, passphrase, False)
    instId = instId2
    levelAPI.set_leverage(instId, leverage, 'cross', 'USDT')
    gouId = instId + '_' + datetime.datetime.now().replace(microsecond=0).isoformat("T").replace(':', '')
    loss_limite *= leverage
    gain_limite *= leverage
    record_to_file(f"gou_init\t{instId}\t{loss_limite:.3%}~{gain_limite:.3%}")

def get_avail_currency(ccy = 'USDT'):
    result = accountAPI.get_currency(ccy)
    data2 = json.loads(json.dumps(result))
    return float(data2['data'][0]['details'][0]['availEq'])
    record_to_file(f"get_avail_currency\t{instId}\t{current_price}")

def get_coin_price():
    global current_price
    result = spotAPI.get_specific_ticker(instId)
    current_price = float(json.loads(json.dumps(result))['data'][0]['last'])
    current_change_rate = current_price / buy_price
    record_to_file(f"get_coin_price\t{instId}\t{current_price}/{buy_price}\t{(current_price / buy_price)}")
    return current_price

def take_order(side):
    if side == 'buy':
        sz = get_avail_currency() * 0.3
    if side == 'sell':
        sz = get_avail_currency() / get_coin_price() * 0.3
    result = levelAPI.take_order(instId, 'cross', 'USDT', side, "market", sz)
    record_to_file(f"take_order\t{instId}\t{side}\t{sz}\t" + json.dumps(result))

def get_position_price():
    global buy_price, deal_side, current_price, upl_ratio
    buy_price = -1
    result = accountAPI.account_positions(instId)
    for position in json.loads(json.dumps(result))['data']:
        if position['instId'] == instId:
            buy_price = float(position['avgPx'])
            current_price = float(position['last'])
            upl_ratio = float(position['uplRatio'])
            if instId.startswith(str(position['posCcy'])):
                deal_side = 'buy'
            if instId.endswith(str(position['posCcy'])):
                deal_side = 'sell'
    record_to_file(f"get_position_price\t{instId}\t{current_price}/{buy_price}\t{deal_side}\t{upl_ratio:.3%}")
    return buy_price

def close_position():
    result = levelAPI.close_position(instId, ccy = 'USDT')     # 市价全平
    record_to_file(f"close_position\t{instId}\t" + json.dumps(result))

def record_to_file(content):
    print(f"{datetime.datetime.now().isoformat(' ', 'milliseconds')}\t{content}")
    file_path = os.getcwd() + '/gou_record/' + gouId + '.txt'
    with open(file_path, 'a+') as f:
        f.write(f"{datetime.datetime.now().isoformat(' ', 'milliseconds')}\t{content}\n")
        f.close()
    
def take():
    global buy_price, current_price, losted_times, loss_limite, gain_limite, upl_ratio
    get_position_price()
    if buy_price < 0:
        record_to_file("Can't_get_the_buy_price\t" + instId)
        time.sleep(10)
        return
    
    if upl_ratio < loss_limite:
        # 市价全平
        close_position()
        losted_times += 1
        record_to_file("losted_times\t" + str(losted_times))
        if losted_times > 2:
            time.sleep(1800)
        #转换买入方向
        take_order("sell" if deal_side == "buy" else "buy")
    elif upl_ratio > gain_limite:
        # 市价全平
        close_position()
        losted_times = 0
        #继续买入之前的方向
        take_order(deal_side)
