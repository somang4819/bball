from crawler.CrawlerBase import CrawlerBase
from config import SECRET, BASEURL, REQUEST_TIME_OUT, BASEKEY, APIKEY
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

'''
내용에 맞춰서 재활용 할 수 있는 소스 (API 가져와서 기초 데이터는 파일로 남기고 실시간 데이터만 넘긴다)

19.2.22 parkjp
야구 데이터 파일을 가져오는 로직 
'''
'''
19.03.10 koo
LAMP LOGGER INIT
'''

lamp_log = Lamp_Logger()

class battotalCrawler(CrawlerBase):

  def baseball(self):

    # 융기원 DB 정보 config로 정의 해서 넘기기 아래 정보대로 데이터 적재함
    self.table = 'KBO_BATTOTAL'
    self.mapping = {'PCODE': 'PCODE',
                    'GYEAR':'GYEAR',
                    'TEAM':'TEAM',
                    'T_ID': 'T_ID',
                    'HRA': 'HRA',
                    'HR': 'HR',
                    'RBI': 'RBI',
                    'SB': 'SB',
                    'OBP': 'OBP',
                    'SLG': 'SLG'
                    }
    self.key = {
      'PCODE': 'PCODE',
      'GYEAR': 'GYEAR',
    }

    # 스포츠 투아이 정보를 API로 가져오는 부분 검색 조건 확인
    # year = datetime.datetime.today().strftime("%Y")
    # # url = 'https://ktaijson.sports2i.com/Api/Record/BATTOTAL?season_id=2018'
    # url = 'https://ktaijson.sports2i.com/Api/Record/BATTOTAL?season_id=' + str(year)
    # get data
    # 이번 년도를 넣는다

    url = BASEURL + '/Record/BATTOTAL?season_id=' + str(self.crawlerData.season_id)

    secret = SECRET
    #
    digest = hmac.new(secret, msg=str(url).encode('utf-8'), digestmod=hashlib.sha256).digest()
    signature = base64.b64encode(digest).decode()

    headers = {'baseKey': BASEKEY,
               'hskey': signature,
               'apiKey': APIKEY
               }

    try:
      r = requests.get(url, headers=headers, timeout=REQUEST_TIME_OUT)
      if r.status_code == 200:
        data = r.json()

        for d in data['LIST']:
          DicElement = {}

          DicElement['PCODE'] = d['PCODE']
          DicElement['GYEAR'] = d['GYEAR']
          DicElement['TEAM'] = d['TEAM']
          DicElement['T_ID'] = d['T_ID']
          DicElement['HRA'] = d['HRA']
          DicElement['HR'] = d['HR']
          DicElement['RBI'] = d['RBI']
          DicElement['SB'] = d['SB']
          DicElement['OBP'] = d['OBP']
          DicElement['SLG'] = d['SLG']

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

    # 삭제 업데이트



