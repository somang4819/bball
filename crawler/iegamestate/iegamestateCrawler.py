from crawler.CrawlerBase import CrawlerBase
from config import SECRET, BASEURL

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
from common.Util.logger import Lamp_Logger

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
class iegamestateCrawler(CrawlerBase):

  def baseball(self):
    # 융기원 DB 정보 config로 정의 해서 넘기기 아래 정보대로 데이터 적재함
    self.table = 'KBO_IE_GAMESTATE'
    self.mapping = {'GAMEID': 'GAMEID',
                    'GYEAR': 'GYEAR',
                    'STATUS_ID': 'STATUS_ID',
                    'INN_NO': 'INN_NO',
                    'TB_SC': 'TB_SC',
                    'REG_DT': 'REG_DT'
                    }

    self.key = {
      'GAMEID': 'GAMEID'
    }

    # 스포츠 투아이 정보를 API로 가져오는 부분 검색 조건 확인
    # 오늘 경기 데이터만 가져오는 로직이 필요
    # 검증을 위해서 날짜와 연동이 변환가능 하도록

    
    # 스포츠투아이 API 에서 당일 게임 스케줄을 조회해서 gamekey 정보를 가져옴
    secret = SECRET
    
    url = BASEURL + '/Master/KBO_SCHEDULE?season_id='+str(self.crawlerData.season_id) +'&g_ds='+str(self.crawlerData.g_ds)

    #(테스트 200312) 스케쥴러 동작 테스트, API에 가서 테스트 게임아이디 가져옴. 
    #url = 'https://ktaijson.sports2i.com/Api/Master/KBO_SCHEDULE?season_id=2020&g_ds=20201215'

    digest = hmac.new(secret, msg=str(url).encode('utf-8'), digestmod=hashlib.sha256).digest()
    signature = base64.b64encode(digest).decode()

    headers = {'baseKey': '8Bh3YiZsHnzQjhx9nK892w==',
               'hskey': signature,
               'apiKey': 'i3E8kEJIpAq9lSOHagdHZ19ZzB845htDBxZCpl5Le3k='
               }

    try:
      r = requests.get(url, headers=headers, timeout=120)
      self.logger.info(' < ' + self.crawlerData.channel + ' : ' + self.crawlerData.detail + ' > ')
 
      #이 때 code 200이 에러 없이 get data 호출한 경우임
      if r.status_code == 200:
        data = r.json()
        sch = []
        crawSchedule = []
        for d in data['LIST']:
            schdic = {}
            sch.append(d['GMKEY'])
            schdic['GMKEY'] = d['GMKEY']
            schdic['GTIME'] = d['GTIME']
            crawSchedule.append(schdic)

      else:
        self.logger.info( 
          '< ' + self.crawlerData.channel + ' : ' + self.crawlerData.detail + ' > ' + '네트워크 상태/ 접속 URL 확인')
    except Exception as ex:
      self.logger.error('< ' + self.crawlerData.channel + ' : ' + self.crawlerData.detail + ' > ' + ex)

    # 오늘 날짜의 실시간 스케쥴 live 정보를 가져옵니다.
    for s in sch:
      url = BASEURL + '/Live/IE_GAMESTATE?season_id='+str(self.crawlerData.season_id) +'&g_id=' + str(s)

      # (테스트200311) 
      #url = 'https://ktaijson.sports2i.com/Api/Live/IE_GAMESTATE?season_id=2020'+'&g_id=' + str(s)
      # (테스트) 아직 2019 선수 데이터 없음
      #url = 'https://ktaijson.sports2i.com/Api/Live/IE_SCORERHEB?season_id='+str(year)+'&g_id=20180324HHWO0'
      #url = 'https://ktaijson.sports2i.com/Api/Live/IE_SCOREINNING?season_id=2018&g_id=20180324HHWO0'
      
      # get data
      # 이번 년도를 넣는다

      secret = SECRET
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
          for d in data['LIST']:
            DicElement = {}

            DicElement['GAMEID'] = d['GAMEID']
            DicElement['GYEAR'] = d['GYEAR']
            DicElement['STATUS_ID'] = d['STATUS_ID']
            DicElement['INN_NO'] = d['INN_NO']
            DicElement['TB_SC'] = d['TB_SC']
            DicElement['REG_DT'] = d['REG_DT']

            self.crawlerData.data.append(DicElement)
        else:
          lamp_log.printLoggerError(
            operation="{channel}_{detail}_API_Connection".format(channel=str(self.crawlerData.channel),
                                                                 detail=str(self.crawlerData.detail)),
            logType='NOTIFY',
            desc='네트워크 상태 / 접속 URL 확인 필요',
            payload={'message': 'url : ' + url}
          )
          self.logger.info(
            '< ' + self.crawlerData.channel + ' : ' + self.crawlerData.detail + ' > ' + '네트워크 상태/ 접속 URL 확인')
      except Exception as ex:
        lamp_log.printLoggerError(
          operation="{channel}_{detail}_API_Connection".format(channel=str(self.crawlerData.channel),
                                                               detail=str(self.crawlerData.detail)),
          logType='NOTIFY',
          desc='크롤링 에러',
          payload={'message': str(ex)}
        )
        self.logger.error('< ' + self.crawlerData.channel + ' : ' + self.crawlerData.detail + ' > ' + ex)

      #smyu 200317 API에서 사라진 데이터를 DB에서 삭제
      
      #2i API 의 키 생성 규칙을 이용해서 끌어올 데이터의 양을 정함
      #실시간 데이터는 당일에 해당하는 데이터만 sync 수행
      self.AmountOfDataToSync += self.crawlerData.g_ds

      #synchronize수행 
      super().BaseSynch()

      # 데이터 저장은 crawlerbase 소스에서 처리 확인\

