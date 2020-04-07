# from pre.cleaning.cleaningPre import crawlerPre
from dataResult import CrawlerData
from flask import request, current_app

# from flask_restful import Resource
# from flask_restplus import api
from flask_restplus import Resource, Namespace, reqparse
from common.Util.logger import Lamp_Logger

# 토큰관리
from jwtToken.jwtToken import jwtCert

import time

from datetime import datetime, timedelta

#smyucheck 동기화는 실패해도 데이터 적재는 되도록 순서 조정
'''
18.11.14 parkjp
기본 크롤러 class
flask의 POST를 처리
child class의 함수를 불러내는 함수 main()

1. return 값으로 현재는 크롤링한 데이터를 반환하는데 수정 필요(18.11.14)
2. 여러개의 입력이 들어올때 독립적으로 잘 움직이는 확인해 보아야함[wsgi+Nginx](18.11.14)
3. 인증방식을 통해 rest에 접속할 수 있는 권한을 통제 하도록 만들어 주어야 함(18.11.26)
4. test key 는 test (19.01.18)

rest CRUD 구현
C(POST) : 구현 X
R(GET) : crawler 동작 
U(PUT) : 구현 X
D(DELETE) : 구현 X
'''
'''
19.03.10 koo
LAMP LOGGER INIT
'''

lamp_log = Lamp_Logger()

api = Namespace('crawler', description='데이터 수집')

class CrawlerBase(Resource):

  def __init__(self, *args, **kwargs):
    logger = kwargs['logger']
    self.logger = logger
    self.api = api
    self.parser = reqparse.RequestParser()
    self.crawlerData = None
    
    #smyu 아래 세가지 정보는 clawer 채널에서 값이 매겨짐
    self.table = None
    self.mapping = []
    self.key = []
    
    #db sync에 사용할 변수
    self.AmountOfDataToSync = ""
  '''
  2018.11.27 parkjp
  detail 명으로 fucntion을 실행 시키는 함수
  '''

  def main(self):
    # 함수 명을 불러서 소환한다
    try :
      detail = self.crawlerData.detail
      self.logger.info('< ' + str(self.crawlerData.channel) + ' : ' + str(self.crawlerData.detail) + ' >' + ' 해당 채널의 서비스에 접속 ')
      getattr(self, detail)()
      self.logger.info('< ' + str(self.crawlerData.channel) + ' : ' + str(self.crawlerData.detail) + ' >' + ' 크롤링 종료')
    except Exception as ex:
      # msg = 'error : 해당 채널의 서비스가 없습니다.', 'detail : ' + self.crawlerData.detail
      # print(msg)
      lamp_log.printLoggerError(
        operation="{channel}_Service_Loading".format(channel=str(self.crawlerData.channel)), 
        logType='NOTIFY',
        desc='{channel} Service Loading Error'.format(channel=self.crawlerData.channel),
        payload={'message': str(ex)}
      )
      self.logger.error(str(ex))
      return self.crawlerData.data.append('< ' + str(self.crawlerData.channel) + ' : ' + str(self.crawlerData.detail) + ' >' + str(ex))

  parser = api.parser()
  parser.add_argument('token', type=str, help='인증을 위한 token 값(test값은 test)', location='headers', required=True)
  parser.add_argument('detail', type=str, help='실행 할 함수 명', location='headers')
  parser.add_argument('season_id', type=str, help='경기 년도', location='headers')
  parser.add_argument('g_ds', type=str, help='경기 날짜', location='headers')
  parser.add_argument('g_id', type=str, help='경기 id', location='headers')
  # parser.add_argument('option', type=str, help='옵션 명', location='headers')
  
  @api.doc(parser=parser)
  @jwtCert
  def get(self):

    try:
      # post 데이터 처리하는 부분
      self.crawlerData = CrawlerData(request.headers, request.path)
    except Exception as ex:
      lamp_log.printLoggerError(
        operation="{channel}_API".format(channel=str(self.crawlerData.channel)), 
        logType='NOTIFY',
        desc='{channel} API CALL Error'.format(channel=str(self.crawlerData.channel)),
        payload={'message': str(ex)}
      )
      self.logger.error('< ' + str(self.crawlerData.channel) + ' : ' + str(self.crawlerData.detail) + ' > ' + str(ex))

    # 함수를 실행해 주는 main()
    self.logger.info('< ' + str(self.crawlerData.channel) + ' : ' + str(self.crawlerData.detail) + ' >' + ' data crawler service')
    start_time = time.time()
    self.main()

    lamp_log.printLoggerStandard(
      operation="{channel}_API".format(channel=self.crawlerData.channel), 
      logType='IN_MSG',
      duration=time.time() - start_time,
      desc=None,
      payload={
        'responseCode': 200,
        'message': '{channel} API CALL SUCCESS'.format(channel=self.crawlerData.channel), 
        'count': len(self.crawlerData.data)
      }
    )

    self.logger.info(
      '< ' + str(self.crawlerData.channel) + ' : ' + str(self.crawlerData.detail) + ' >' + ' API Total rows: ' + str(len(self.crawlerData.data)))

    '''
    19.1.7 parkjp
    데이터 베이스 1차 적재
    데이터 확인을 위해 저장 모듈
    '''

    #200312 smyu
    #크롤링해온 데이터가 없을 때, 데이터 입력/업데이트 수행 없음
    #smyucheck None리턴 말고 대안을 찾자
    if not self.crawlerData.data:
      self.logger.info('< ' + str(self.crawlerData.channel) + ' : ' + str(self.crawlerData.detail) + ' >' + '입력할 크롤링 데이터 없음')
      lamp_log.printLoggerStandard(
        operation="{channel}_API".format(channel=self.crawlerData.channel), 
        logType='IN_MSG',
        duration=time.time() - start_time,
        desc=None,
        payload={
          'responseCode': 200,
          'message': '{channel} no data for insert/update'.format(channel=self.crawlerData.channel), 
          'count': len(self.crawlerData.data)
        }
      )
      return {'len': len(self.crawlerData.data), 'data' : self.crawlerData.data, 'result':' 0 rows Inserted'+" "+ ' 0 rows Updateed'} 
    # ~smyu

    try:        
      insertRes, updateRes, err = self.crawlerData.dataInsert(self.table, self.mapping, self.key)
      self.logger.info('< ' + str(self.crawlerData.channel) + ' : ' + str(self.crawlerData.detail) + ' >' + 'clawler data insert')

      if err is not None:
        self.logger.error(self.crawlerData.channel + " " + str(insertRes) +" "+ str(updateRes))

        lamp_log.printLoggerError(
          operation="{channel}_{detail}_Data_Insert/Update".format(channel=str(self.crawlerData.channel), detail=str(self.crawlerData.detail)), 
          logType='NOTIFY',
          duration=time.time() - start_time,
          desc='{channel} DATABASE Insert/Update Error, None Err'.format(channel=str(self.crawlerData.channel)),
          payload={'message': str(err)}
        )
        
      else:
        self.logger.info(self.crawlerData.channel + " " + str(insertRes) +" "+ str(updateRes))
        lamp_log.printLoggerStandard(
          operation="{channel}_{detail}_Data_Insert/Update".format(channel=str(self.crawlerData.channel), detail=str(self.crawlerData.detail)), 
          logType='IN_MSG',
          duration=time.time() - start_time,
          payload={
            'responseCode': 200,
            'message': '{channel} DB INSERT/UPDATE SUCCESS'.format(channel=str(self.crawlerData.channel)),
            'insert': str(insertRes).strip(),
            'update': str(updateRes).strip()
          }
        )

        # update / insert
        # try:
        #     # 수집한 결과를 적재합니다.
        #     if self.table is not None :
        #       self.crawlerData.dataInsert(self.table, self.mapping)
        #     else:
        #       self.logger.info('< ' + self.crawlerData.channel + ' : ' + self.crawlerData.detail + ' > 데이터 적재 하지 않고 넘어갑니다.' )
        # except Exception as ex:
        #      self.logger.error('< ' + self.crawlerData.channel + ' : ' + self.crawlerData.detail + ' > '+ex+' 데이터 적재 실패' )
        #
        #
        # return {'results':'ok'}

      return {'len': len(self.crawlerData.data), 'data' : self.crawlerData.data, 'result': str(insertRes) +" "+ str(updateRes) }
    except Exception as ex:
      self.logger.info('< ' + str(self.crawlerData.channel) + ' : ' + str(self.crawlerData.detail) + ' > ' + str(ex))

      lamp_log.printLoggerStandard(
        operation="{channel}_{detail}_Data_Insert/Update".format(channel=str(self.crawlerData.channel), detail=str(self.crawlerData.detail)), 
        logType='NOTIFY',
        duration=time.time() - start_time,
        desc='{channel} DATABASE Insert/Update Error'.format(channel=str(self.crawlerData.channel)),
        payload={'message': str(ex)}
      )

  #smyu
  def BaseSynch(self):
    #smyucheck 예외 클래스 상속 받아서 하나 만들어보자
    #https://brownbears.tistory.com/127
    '''
    if not self.AmountOfDataToSync
      return Error
    '''
    try:
      synchres = self.crawlerData.crawlerDataSync(self.table, self.mapping, self.key, self.AmountOfDataToSync) 
      lamp_log.printLoggerStandard(
            operation="{channel}_API".format(channel=self.crawlerData.channel), 
            logType='IN_MSG',
            desc=None,
            payload={
              'responseCode': 200,
              'message': '{channel} data Synchronize success'.format(channel=self.crawlerData.channel), 
              'count': synchres
            }
          )
      self.logger.info('< ' + str(self.crawlerData.channel) + ' : ' + str(self.crawlerData.detail) + ' > ' + synchres)
    except Exception as ex:
      self.logger.error('< ' + str(self.crawlerData.channel) + ' : ' + str(self.crawlerData.detail) + ' > ' + str(ex))
      lamp_log.printLoggerError(
        operation="{channel}_{detail}_Data_Synchronize".format(channel=str(self.crawlerData.channel), detail=str(self.crawlerData.detail)), 
        logType='NOTIFY',
        desc='{channel} DATABASE Synchronize Error'.format(channel=str(self.crawlerData.channel)),
        payload={'message': str(ex)}
      )
      return ex
    return synchres
  #~smyu
