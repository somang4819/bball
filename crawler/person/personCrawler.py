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

class personCrawler(CrawlerBase):

  def baseball(self):
    # 융기원 DB 정보 config로 정의 해서 넘기기 아래 정보대로 데이터 적재함
    self.table = 'KBO_PERSON'
    self.mapping = {'PCODE': 'PCODE',
                    'NAME': 'NAME',
                    'TEAM': 'TEAM',
                    'T_ID': 'T_ID',
                    'POS': 'POS',
                    'POSITION': 'POSITION',
                    'BACKNUM': 'BACKNUM',
                    'CNAME': 'CNAME',
                    'BIRTH': 'BIRTH',
                    'HEIGHT': 'HEIGHT',
                    'WEIGHT': 'WEIGHT',
                    'CAREER': 'CAREER',
                    'HITTYPE': 'HITTYPE',
                    'INDATE': 'INDATE',
                    'PROMISE': 'PROMISE',
                    'MONEY': 'MONEY',
                    'CAREER2': 'CAREER2'
                    }

    self.key = {
      'PCODE': 'PCODE'
    }

    # 스포츠 투아이 정보를 API로 가져오는 부분 검색 조건 확인
    year = datetime.datetime.today().strftime("%Y")

    # 아직 2019 선수 데이터 없음
    # url = 'https://ktaijson.sports2i.com/Api/Master/PERSON?season_id=2018'
    # url = 'https://ktaijson.sports2i.com/Api/Master/PERSON?season_id='+str(year)
    url = BASEURL + '/Master/PERSON?season_id=' + str(self.crawlerData.season_id)
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
        # print (data)
        for d in data['LIST']:
          DicElement = {}
          DicElement['PCODE'] = d['PCODE']
          DicElement['TEAM'] = d['TEAM']
          DicElement['NAME'] = d['NAME']
          DicElement['T_ID'] = d['T_ID']
          DicElement['POS'] = d['POS']
          DicElement['POSITION'] = d['POSITION']
          DicElement['BACKNUM'] = d['BACKNUM']
          DicElement['CNAME'] = d['CNAME']
          DicElement['BIRTH'] = d['BIRTH']
          DicElement['HEIGHT'] = d['HEIGHT']
          DicElement['WEIGHT'] = d['WEIGHT']
          DicElement['CAREER'] = d['CAREER']
          DicElement['HITTYPE'] = d['HITTYPE']
          DicElement['INDATE'] = d['INDATE']
          DicElement['PROMISE'] = d['PROMISE']
          DicElement['MONEY'] = d['MONEY']
          DicElement['CAREER2'] = d['CAREER2']

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




