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
loss_limite = 0.009
gain_limite = 0.018
losted_times = 0


def init(api_key, api_secret_key, passphrase, instId2):
    global accountAPI, spotAPI, levelAPI, gouId, instId
    accountAPI = account.AccountAPI(api_key, api_secret_key, passphrase, False)
    spotAPI = spot.SpotAPI(api_key, api_secret_key, passphrase, False)
    levelAPI = lever.LeverAPI(api_key, api_secret_key, passphrase, False)
    instId = instId2
    levelAPI.set_leverage(instId, 3, 'cross', 'USDT')
    gouId = instId + '_' + datetime.datetime.now().replace(microsecond=0).isoformat("T").replace(':', '')
    record_to_file("gou_init\t" + instId + '\t' + str(loss_limite) + '~' + str(gain_limite))

def get_avail_currency(ccy = 'USDT'):
    result = accountAPI.get_currency(ccy)
    data2 = json.loads(json.dumps(result))
    return float(data2['data'][0]['details'][0]['availEq'])
    record_to_file("get_avail_currency\t" + instId + "\t" + str(current_price))

def get_coin_price():
    global current_price
    result = spotAPI.get_specific_ticker(instId)
    current_price = float(json.loads(json.dumps(result))['data'][0]['last'])
    current_change_rate = current_price / buy_price
    record_to_file("get_coin_price\t" + instId + "\t" + str(current_price) + '/' + str(buy_price) + "\t" + str(round((current_price / buy_price - 1) * 100, 3)) +'%')
    return current_price

def take_order(side):
    if side == 'buy':
        sz = get_avail_currency() * 0.6
    if side == 'sell':
        sz = get_avail_currency() / get_coin_price() * 0.6
    result = levelAPI.take_order(instId, 'cross', 'USDT', side, "market", sz)
    record_to_file("take_order\t" + instId + "\t" + side + "\t" + str(sz) + "\t" + json.dumps(result))

def get_position_price():
    global buy_price, deal_side, current_price
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
    record_to_file("get_position_price\t" + instId + "\t" + str(buy_price) + "\t" + deal_side)
    return buy_price

def close_position():
    result = levelAPI.close_position(instId, ccy = 'USDT')     # 市价全平
    record_to_file("close_position\t" + instId + "\t" + json.dumps(result))

def record_to_file(content):
    print(content)
    file_path = os.getcwd() + '/gou_record/' + gouId + '.txt'
    with open(file_path, 'a+') as f:
        f.write(str(datetime.datetime.now()) + "\t" + content + '\n')
        f.close()
    
def take():
    global buy_price, current_price, losted_times, loss_limite, gain_limite
    buy_price = get_position_price()
    if buy_price < 0:
        time.sleep(10)
        return
    
    # 获取当前价格
    current_price = get_coin_price()
    current_change_rate = current_price / buy_price
    if deal_side == 'buy':       #做多
        if current_change_rate < 1 - loss_limite:
            # 市价全平
            close_position()
            losted_times += 1
            record_to_file("losted_times\t" + str(losted_times))
            if losted_times > 2:
                time.sleep(1800)
            #市价卖出 做空
            take_order("sell")
            #获取最新买入价buy_price
            get_position_price()
        elif current_change_rate > 1 + gain_limite:
            # 市价全平
            close_position()
            losted_times = 0
            #市价买入 做多
            take_order("buy")
            #获取最新买入价buy_price
            get_position_price()
    else:       #做空
        if current_change_rate > 1 + loss_limite:
            # 市价全平
            close_position()
            losted_times += 1
            record_to_file("losted_times\t" + str(losted_times))
            if losted_times > 2:
                time.sleep(1800)
            #市价买入 做多
            take_order("buy")
            #获取最新买入价buy_price
            get_position_price()
        elif current_change_rate < 1 - gain_limite:
            # 市价全平
            close_position()
            losted_times = 0
            #市价卖出 做空
            take_order("sell")
            #获取最新买入价buy_price
            get_position_price()
