import gou_dog
import time

if __name__ == '__main__':

    api_key = ""
    secret_key = ""
    passphrase = ""

    instId = 'BTC-USDT'
    gou_dog.init(api_key, secret_key, passphrase, instId)

    while True:
        time.sleep(0.5)
        gou_dog.take()
