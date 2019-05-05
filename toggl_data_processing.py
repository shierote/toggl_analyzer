import requests
import pprint
import sys
from datetime import date
from datetime import datetime as dt
from datetime import timedelta as td
from statistics import mean
import os

API_TOKEN = os.environ["Toggl_API_TOKEN"]
W_ID = os.environ["Toggl_WORKSPACE_ID"]
MAIL = os.environ["MAIL"]
API_Endpoint = 'https://toggl.com/reports/api/v2/details'

class TogglData:
    def __init__(self, since_date=dt.now().strftime('%Y-%m-%d'), until_date=dt.now().strftime('%Y-%m-%d')):
        # 通信するメソッドとして切り出す
        headers = {'content-type': 'application/json'}
        today = date.today().isoformat()
        auth = requests.auth.HTTPBasicAuth(API_TOKEN, 'api_token')
        params = {'workspace_id': W_ID,
                  'user_agent': MAIL,
                  'since': since_date,
                  'until': until_date
                  }
        current = requests.get(API_Endpoint, auth=auth, headers=headers, params=params)
        current_json = current.json()
        # 通信するメソッドとして切り出す
        data = current_json['data']
        self.work_time = current_json['total_grand'] if current_json['total_grand'] else 0
        self.works  = []
        for i in range(len(data)):
            self.works.append(data[i])
        # 再帰にする
        if current_json['total_count'] > current_json['per_page']:
            params['page'] = 2
            current = requests.get(API_Endpoint, auth=auth, headers=headers, params=params)
            current_json = current.json()
            data = current_json['data']
            for i in range(len(data)):
                self.works.append(data[i])
        
    def print_work_time(self):
        print(self.work_time)
        return self.work_time

    def print_work_content(self):
        total_time = 0
        content_list = []
        for work in self.works:
            print(work['project'], end=' ')
            print(work['description'], end=' ')
            print(td(milliseconds=work['dur']))
            total_time += work['dur']
        print(td(milliseconds=total_time))

    def work_time_each_weekday(self, weeks, start_date_str):
         start_date = dt.strptime(start_date_str, '%Y-%m-%d')
         mon_data = [] 
         tue_data = []
         wed_data = []
         thu_data = []
         fri_data = []
         sat_data = []
         sun_data = []
         results = {}
         
         for i in range(weeks*7):
             target_date = start_date - td(days=i)
             target_date_weekday = target_date.weekday()
             target_date_str = target_date.strftime('%Y-%m-%d')
             print(target_date_str, end=":")
             if target_date_weekday == 0:
                 mon_data.append(TogglData(target_date_str, target_date_str).print_work_time())
             elif target_date_weekday == 1:
                 tue_data.append(TogglData(target_date_str, target_date_str).print_work_time())
             elif target_date_weekday == 2:
                 wed_data.append(TogglData(target_date_str, target_date_str).print_work_time())
             elif target_date_weekday == 3:
                 thu_data.append(TogglData(target_date_str, target_date_str).print_work_time())
             elif target_date_weekday == 4:
                 fri_data.append(TogglData(target_date_str, target_date_str).print_work_time())
             elif target_date_weekday == 5:
                 sat_data.append(TogglData(target_date_str, target_date_str).print_work_time())
             else:
                 sun_data.append(TogglData(target_date_str, target_date_str).print_work_time())
            
         print(mon_data)
         print(tue_data)
         print(wed_data)
         print(thu_data)
         print(fri_data)
         print(sat_data)
         print(sun_data)
         
         results['mon'] = mean(mon_data)
         results['tue'] = mean(tue_data)
         results['wed'] = mean(wed_data)
         results['thu'] = mean(thu_data)
         results['fri'] = mean(fri_data)
         results['sat'] = mean(sat_data)
         results['sun'] = mean(sun_data)
         return results


# for k, v in TogglData().work_time_each_weekday(int(sys.argv[1]), sys.argv[2]).items():
#     print(k)
#     print(td(milliseconds=v))
#     print("")

# print(TogglData(sys.argv[1], sys.argv[2]).print_work_content())

import numpy as np
import matplotlib.pyplot as plt

labels = []
data = []
for k, v in TogglData().work_time_each_weekday(int(sys.argv[1]), sys.argv[2]).items():
    labels.append(k)
    # data.append(td(milliseconds=v))
    data.append(round(v/3600000, 2))

labels.append("total")
data.append(round(mean(data)))

# 表示位置設定
x_width = 0.5
x_loc = np.array(range(len(data))) + x_width

plt.title("Average work hours per day")
plt.bar(x_loc, data, width=x_width)     # 棒グラフの設定
plt.xticks(x_loc, labels)               # x軸にラベル設定

for x, y in zip([i for i in range(len(labels))], data):
    plt.text(x+0.5, y, y, ha='center', va='bottom')

# 描画実行
plt.show()
