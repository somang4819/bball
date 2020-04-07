from crawler.CrawlerBase import CrawlerBase
from config import SECRET, BASEURL
from common.Util.logger import Lamp_Logger

try:
  import urlparse
except ImportError:
  import urllib.parse as urlparse

import json

import csv
import datetime
import requests
import base64
import hashlib
import hmac
'''
내용에 맞춰서 재활용 할 수 있는 소스 (API/ DB 에서 가져오는 것 둘다 할 수 있도록)

19.2.22 parkjp
야구 데이터 파일을 가져오는 로직 
'''
'''
19.03.10 koo
LAMP LOGGER INIT
'''

lamp_log = Lamp_Logger()

class scoreCrawler(CrawlerBase):

  def baseball(self):
    # 융기원 DB 정보 config로 정의 해서 넘기기
    self.table = 'KBO_SCORE'
    self.mapping = {'GMKEY': 'GMKEY',
                    'GDAY':'GDAY',
                    '1T': '1T',
                    '1B': '1B',
                    '2T': '2T',
                    '2B': '2B',
                    '3T': '3T',
                    '3B': '3B',
                    '4T': '4T',
                    '4B': '4B',
                    '5T': '5T',
                    '5B': '5B',
                    '6T': '6T',
                    '6B': '6B',
                    '7T': '7T',
                    '7B': '7B',
                    '8T': '8T',
                    '8B': '8B',
                    '9T': '9T',
                    '9B': '9B',
                    '10T': '10T',
                    '10B': '10B',
                    '11T': '11T',
                    '11B': '11B',
                    '12T': '12T',
                    '12B': '12B',
                    '13T': '13T',
                    '13B': '13B',
                    '14T': '14T',
                    '14B': '14B',
                    '15T': '15T',
                    '15B': '15B',
                    '16T': '16T',
                    '16B': '16B',
                    '17T': '17T',
                    '17B': '17B',
                    '18T': '18T',
                    '18B': '18B',
                    '19T': '19T',
                    '19B': '19B',
                    '20T': '20T',
                    '20B': '20B',
                    '21T': '21T',
                    '21B': '21B',
                    '22T': '22T',
                    '22B': '22B',
                    '23T': '23T',
                    '23B': '23B',
                    '24T': '24T',
                    '24B': '24B',
                    '25T': '25T',
                    '25B': '25B',
                    'TPOINT': 'TPOINT',
                    'BPOINT': 'BPOINT',
                    'THIT': 'THIT',
                    'BHIT': 'BHIT',
                    'TERR': 'TERR',
                    'BERR': 'BERR',
                    'TBBHP': 'TBBHP',
                    'BBBHP': 'BBBHP'
                    }

    self.key = {
      'GMKEY': 'GMKEY',
      'GDAY': 'GDAY'
    }

    # 스포츠 투아이 정보를 API로 가져오는 부분 검색 조건 확인/ 오늘 날짜와 하루 전날 데이터 업데이트
    # year = datetime.datetime.today().strftime("%Y")
    # g_ds = datetime.datetime.today().strftime("%Y%m%d")

    url = BASEURL + '/Record/SCORE?g_ds='+str(self.crawlerData.g_ds)

    # url = 'https://ktaijson.sports2i.com/Api/Record/SCORE?g_ds='+g_ds
    # get data
    # 이번 년도를 넣는다

    secret = SECRET
    #
    digest = hmac.new(secret, msg=str(url).encode('utf-8'), digestmod=hashlib.sha256).digest()
    signature = base64.b64encode(digest).decode()

    headers = {'baseKey': '8Bh3YiZsHnzQjhx9nK892w==',
               'hskey': signature,
               'apiKey': 'i3E8kEJIpAq9lSOHagdHZ19ZzB845htDBxZCpl5Le3k='
               }

    try:
      r = requests.get(url, headers=headers, timeout=120)

      if r.status_code == 200:
        data = r.json()
        # print(data)
        for d in data['LIST']:
          # print(d)
          DicElement = {}
          DicElement['GMKEY'] = d['GMKEY']
          DicElement['GDAY'] = d['GDAY']
          DicElement['1T'] = d['1T']
          DicElement['1B'] = d['1B']
          DicElement['2T'] = d['2T']
          DicElement['2B'] = d['2B']
          DicElement['3T'] = d['3T']
          DicElement['3B'] = d['3B']
          DicElement['4T'] = d['4T']
          DicElement['4B'] = d['4B']
          DicElement['5T'] = d['5T']
          DicElement['5B'] = d['5B']
          DicElement['6T'] = d['6T']
          DicElement['6B'] = d['6B']
          DicElement['7T'] = d['7T']
          DicElement['7B'] = d['7B']
          DicElement['8T'] = d['8T']
          DicElement['8B'] = d['8B']
          DicElement['9T'] = d['9T']
          DicElement['9B'] = d['9B']
          DicElement['10T'] = d['10T']
          DicElement['10B'] = d['10B']
          DicElement['11T'] = d['11T']
          DicElement['11B'] = d['11B']
          DicElement['12T'] = d['12T']
          DicElement['12B'] = d['12B']
          DicElement['13T'] = d['13T']
          DicElement['13B'] = d['13B']
          DicElement['14T'] = d['14T']
          DicElement['14B'] = d['14B']
          DicElement['15T'] = d['15T']
          DicElement['15B'] = d['15B']
          DicElement['16T'] = d['16T']
          DicElement['16B'] = d['16B']
          DicElement['17T'] = d['17T']
          DicElement['17B'] = d['17B']
          DicElement['18T'] = d['18T']
          DicElement['18B'] = d['18B']
          DicElement['19T'] = d['19T']
          DicElement['19B'] = d['19B']
          DicElement['20T'] = d['20T']
          DicElement['20B'] = d['20B']
          DicElement['21T'] = d['21T']
          DicElement['21B'] = d['21B']
          DicElement['22T'] = d['22T']
          DicElement['22B'] = d['22B']
          DicElement['23T'] = d['23T']
          DicElement['23B'] = d['23B']
          DicElement['24T'] = d['24T']
          DicElement['24B'] = d['24B']
          DicElement['25T'] = d['25T']
          DicElement['25B'] = d['25B']
          DicElement['TPOINT'] = d['TPOINT']
          DicElement['BPOINT'] = d['BPOINT']
          DicElement['THIT'] = d['THIT']
          DicElement['BHIT'] = d['BHIT']
          DicElement['TERR'] = d['TERR']
          DicElement['BERR'] = d['BERR']
          DicElement['TBBHP'] = d['TBBHP']
          DicElement['BBBHP'] = d['BBBHP']

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

