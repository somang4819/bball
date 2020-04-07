from crawler.CrawlerBase import CrawlerBase
from config import SECRET, BASEURL
from common.Util.logger import Lamp_Logger

try:
  import urlparse
except ImportError:
  import urllib.parse as urlparse

import csv
import datetime
import requests
import base64
import hashlib
import hmac

#from dateutil.relativedelta import relativedelta

'''
(venv) [baseball@localhost baseball]$ python3.6 -m pip install python-dateutil --upgrade
Collecting python-dateutil
  Using cached python_dateutil-2.8.1-py2.py3-none-any.whl (227 kB)
Requirement already satisfied, skipping upgrade: six>=1.5 in ./venv/lib/python3.6/site-packages (from python-dateutil) (1.14.0)
Installing collected packages: python-dateutil
Successfully installed python-dateutil-2.8.1
'''
'''
내용에 맞춰서 재활용 할 수 있는 소스 (API/ DB 에서 가져오는 것 둘다 할 수 있도록)

19.2.22 parkjp
야구 데이터 파일을 가져오는 로직 (MASTER DATA)
'''
'''
19.03.10 koo
LAMP LOGGER INIT
'''

lamp_log = Lamp_Logger()

class kboscheduleCrawler(CrawlerBase):

  def toCSV(self, data, mode):

    rootpath  = 'results/KBO_SCHEDULE'
    if mode == 'normal' : title = rootpath + '.csv'
    elif mode == 'save' :
      saveTime = datetime.datetime.today().strftime("%Y%m%d%%H%M%S")
      title = rootpath + saveTime + '.csv'

    with open(title, 'w', encoding='UTF8') as csv_file:
      writer = csv.writer(title, delimiter=',', lineterminator='\n')
      # writer.writerow(tcol)
      l = []
      # for d in data :
      #  l.append([i for i in data])
      writer.writerow(l)

  def baseball(self):
    # 융기원 DB 정보 config로 정의 해서 넘기기 아래 정보대로 데이터 적재함
    self.table = 'KBO_SCHEDULE'
    self.mapping = {'GMKEY': 'GMKEY',
                    'GAME_FLAG': 'GAME_FLAG',
                    'END_FLAG' : 'END_FLAG',
                    'GAMEDATE': 'GAMEDATE',
                    'GYEAR': 'GYEAR',
                    'GMONTH': 'GMONTH',
                    'GDAY': 'GDAY',
                    'GWEEK': 'GWEEK',
                    'HOME': 'HOME',
                    'HOME_KEY': 'HOME_KEY',
                    'VISIT': 'VISIT',
                    'VISIT_KEY': 'VISIT_KEY',
                    'STADIUM': 'STADIUM',
                    'STADIUM_KEY': 'STADIUM_KEY',
                    'DHEADER': 'DHEADER',
                    'HPCODE': 'HPCODE',
                    'VPCODE': 'VPCODE',
                    'GTIME': 'GTIME',
                    'HSCORE': 'HSCORE',
                    'VSCORE': 'VSCORE',
                    'CANCEL_FLAG': 'CANCEL_FLAG'
                    }

    self.key = {
      'GMKEY': 'GMKEY',
      'GAMEDATE': 'GAMEDATE',
    }

    # 스포츠 투아이 정보를 API로 가져오는 부분 검색 조건 확인
    year = datetime.datetime.today().strftime("%Y")
    # url = 'https://ktaijson.sports2i.com/Api/Master/KBO_SCHEDULE?season_id='+str(year)
    url = BASEURL + '/Master/KBO_SCHEDULE?season_id=' + self.crawlerData.season_id
    # get data
    # 이번 년도를 넣는다


    secret = SECRET
    #
    digest = hmac.new(secret, msg=str(url).encode('utf-8'), digestmod=hashlib.sha256).digest()
    signature = base64.b64encode(digest).decode()

    headers = {'baseKey' : '8Bh3YiZsHnzQjhx9nK892w==',
               'hskey':  signature,
               'apiKey':'i3E8kEJIpAq9lSOHagdHZ19ZzB845htDBxZCpl5Le3k='
               }

    try:
      r = requests.get(url, headers= headers, timeout=120)
      if r.status_code == 200:
        data = r.json()
        for d in data['LIST'] :
          DicElement = {}
          DicElement['GMKEY'] = d['GMKEY']
          DicElement['GAME_FLAG'] = d['GAME_FLAG']
          DicElement['END_FLAG'] = d['END_FLAG']
          DicElement['GAMEDATE'] = d['GAMEDATE']
          DicElement['GYEAR'] = d['GYEAR']
          DicElement['GMONTH'] = d['GMONTH']
          DicElement['GDAY'] = d['GDAY']
          DicElement['GWEEK'] = d['GWEEK']
          DicElement['HOME'] = d['HOME']
          DicElement['HOME_KEY'] = d['HOME_KEY']
          DicElement['VISIT'] = d['VISIT']
          DicElement['VISIT_KEY'] = d['VISIT_KEY']
          DicElement['STADIUM'] = d['STADIUM']
          DicElement['STADIUM_KEY'] = d['STADIUM_KEY']
          DicElement['DHEADER'] = d['DHEADER']
          DicElement['HPCODE'] = d['HPCODE']
          DicElement['VPCODE'] = d['VPCODE']
          DicElement['GTIME'] = d['GTIME']
          DicElement['HSCORE'] = d['HSCORE']
          DicElement['VSCORE'] = d['VSCORE']
          DicElement['CANCEL_FLAG'] = d['CANCEL_FLAG']
          
          self.crawlerData.data.append(DicElement)

      else:
        lamp_log.printLoggerError(
          operation="{channel}_{detail}_API_Connection".format(channel=str(self.crawlerData.channel), detail=str(self.crawlerData.detail)), 
          logType='NOTIFY',
          desc='네트워크 상태 / 접속 URL 확인 필요',
          payload={'message': 'url : ' + url}
        )
        self.logger.info(
          '< ' + self.crawlerData.channel + ' : ' + self.crawlerData.detail + ' > ' + '네트워크 상태/ 접속 URL 확인')
    except Exception as ex:
      lamp_log.printLoggerError(
        operation="{channel}_{detail}_API_Connection".format(channel=str(self.crawlerData.channel), detail=str(self.crawlerData.detail)), 
        logType='NOTIFY',
        desc='크롤링 에러',
        payload={'message': str(ex)}
      )
      self.logger.error('< ' + self.crawlerData.channel + ' : ' + self.crawlerData.detail + ' > ' + ex)

    # 데이터 저장은 공통 소스에서 처리 확인
    #smyu 200317 API에서 사라진 데이터를 DB에서 삭제

    #이번달 데이터 sync 
    #2i API 의 키 생성 규칙을 이용해서 DB에서 fetch할 데이터의 양을 정함
    self.AmountOfDataToSync += self.crawlerData.g_ds[:-2]

    #synchronize 수행
   
    super().BaseSynch()

    #다음달 데이터 sync
    #2i API 의 키 생성 규칙을 이용해서 DB에서 fetch할 데이터의 양을 정함
    #today = datetime.datetime.strptime(self.crawlerData.g_ds, "%Y%m%d").date()
    #nextmonth = today + relativedelta(months=1)
    #nextmonthstr=str(nextmonth).replace("-","")

    #print(nextmonthstr[:-2])
    #print(self.crawlerData.g_ds[:-2])
