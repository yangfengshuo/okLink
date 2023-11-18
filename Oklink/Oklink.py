import base64
import datetime
import json
import re
import time
from tqdm import tqdm
import js2py
import requests
import tracemalloc
from Database import DataBase
from logger import Logger


class Spider:
    # 实例化数据库类以及日志类
    def __init__(self):
        self.database = DataBase()
        self.logger = Logger()
        self.page = 1

    # 对ApiKey进行请求，获取API_KEY，并传入okLink.js进行加密，返回加密参数
    def __getApiKey(self):
        """
        非必要不做修改
        @return: ApiKey
        """
        context = js2py.EvalJs()
        with open('Oklink.js', 'r') as fp:
            js_code = fp.read()
        context.execute(js_code)
        get_api_key_js = requests.get(
            "https://static.oklink.com/cdn/assets/okfe/oklink-nav/vender/index.681aa2a6.js").text
        API_KEY = re.findall('this.API_KEY.*?=.*?"(.*?)".*?}', get_api_key_js)[0]
        l = 1111111111111
        X_Apikey = context.getApiKey(API_KEY, l)
        return base64.b64encode(X_Apikey.encode('utf-8')).decode('utf-8')

    # 携带加密数据对网站进行请求
    def request(self, url):
        response = requests.get(url,
                                headers={'X-Apikey': self.__getApiKey(),
                                         "Devid": "baa7a1e0-0976-4f36-86a9-78f0f2f63745",
                                         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                                         "Referer": "https://www.oklink.com/cn/btc/tx-list",
                                         }
                                )
        parse_data = response.json()
        status = True
        if parse_data.get('code') != 0 or \
                parse_data.get('msg') != "" or \
                parse_data.get('data') is None:
            status = False
        return status, response

    # 解析数据，返回列表嵌套
    def ParseData(self, response):
        data_list = response.json()['data']['hits']
        result = []
        for each in data_list:
            blockTime_ob = datetime.datetime.fromtimestamp(each['blocktime'])
            blockTime = blockTime_ob.strftime("%Y-%m-%d %H:%M:%S")
            item = [each['hash'], each['blockHeight'], each['blocktime'],
                    each['inputsCount'], each['outputsCount'], each['inputsValue']
                , each['fee'] * 0.000000001, blockTime]
            result.append(item)
        return result

    # 写入数据库
    def write(self, data):
        if len(data) == 0:
            return
        status = self.database.write_db(data)
        if status:
            self.logger.info(msg="入库")

    # 开始运行，如果出现错误打印至日志报告
    def run(self):
        for i in range(0, 10000, 100):
            url = f"https://www.oklink.com/api/explorer/v1/btc/transactionsNoRestrict?t={int(time.time())}&offset={i}&txType=&limit={i + 100}&curType="
            status, response = self.request(url)
            if status:  # 请求成功
                data = self.ParseData(response)
                if data:
                    self.write(data)


            else:
                self.logger.writer_logger('okLink.run', err=json.dumps(response))
            print("-" * 20, f"第{self.page}页采集完成", "-" * 20)
            self.page += 1
            time.sleep(5)


# TODO
if __name__ == '__main__':
    tracemalloc.start()
    spider = Spider()
    spider.run()
