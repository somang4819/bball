from common.SingletonInstance import SingletonType
from datetime import datetime
from config import SERVER_IP, SERVER_NAME, LOG_FILE_SIZE

import logging
import logging.handlers
import socket
import uuid
import json
'''
18.12.20 parkjp
서비스 별로 로거를 생성한다
singleton instance

config 값
service 별 formatter_str
service 별 log level
service 별 filesize 
'''

'''
19.03.06 koo
LAMP 규격 

  필수 적용 내용
  
  timestamp / 로그생성시간 / YYYY-MM-DD HH:MM:SS.sss
  service / 서비스코드 / 'PG059005'
  operation / 로그 생성한 오퍼레이션 명 / sche2in_API , in_API2out_API ++ 테이블 명 AND SYSTEM ON,OFF 로그
  transactionId / 생성 혹은 전달받은 트랜잭션 ID / 호스트명 + UUID ==> 날씨에서 timestamp를 사용함 쓰면 안됌
  logType / 로그의 목적,상황에 맞는 FLAG / 'IN_REQ', 'IN_RES' 등등
  host / 호스트명 / 호스트명
  
  response / 
    type=응답유형 / I, S, E
    desc=설명 
    code=상태코드 
    duration=시간

  선택 적용 내용
  
  payload / 자유로운 형태로 사용 => 에러 내용 저장 예정
  caller / 채널키 / AI_DATA_Baseball 형태로 적용 => 날씨와 차별점

'''

class LoggerAdapter(logging.LoggerAdapter):
  def __init__(self, logger):
    super(LoggerAdapter, self).__init__(logger, {})
    self.host = SERVER_NAME
    self.ip = SERVER_IP
    self.caller = 'AI_DATA_Baseball'
    self.service = 'PG059005'

  
  def process(self, msg, kwargs):
    extra = kwargs['extra']
    result = None
    #timestamp = datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    result = {
      'timestamp': timestamp,
      'host': {
        'name': self.host,
        'ip': self.ip
      },
      'caller': {
        'channel': self.caller
      },
      'service': self.service,
      'operation': extra['operation'],
      'transactionId': self.host + '_' + str(uuid.uuid4()),
      'logType': extra['logType'],
      'response': {
        'type': extra['resType'],
        'code': extra['code']
      }
    }

    if extra['payload'] is not None:
      result['payload'] = extra['payload']
    
    if extra['duration'] is not None:
      result['response']['duration'] = int(round(extra['duration'] * 1000))
    if extra['desc'] is not None:
      result['response']['desc'] = extra['desc']
    
    print(result)
    return  json.dumps(result, ensure_ascii=False), kwargs  

class Logger(object, metaclass=SingletonType):

  def __init__(self, services):
    self._logger = {}

    services.append('system')
    services.append('scheduler')

    for service in services :
      self._logger[service] = logging.getLogger(service)
      # config로 정의해야 될 부분
      self._logger[service].setLevel(logging.DEBUG)
      # 로그의 형식을 포매팅

      formatter = logging.Formatter(
        '[%(filename)s:%(module)s:%(lineno)d][%(asctime)s][service : %(name)s][%(levelname)s] - %(message)s'
      )

      streamHandler = logging.StreamHandler()
      streamHandler.setFormatter(formatter)

      # 두가지 모두를 표출하기 위한 핸들러 설정
      # fileHandler = logging.FileHandler('log/'+service+'.log')
      # fileHandler.setFormatter(formatter)

      # 로그 파일 처리(로테이팅)
      file_max_bytes = 1024 * 1024 * 100  # (100MB)
      if(LOG_FILE_SIZE):
        file_max_bytes = LOG_FILE_SIZE

      # backupCount는 갯수
      rotateFileHandler = logging.handlers.RotatingFileHandler(filename='log/baseball.log', maxBytes=file_max_bytes, backupCount=5)
      rotateFileHandler.setFormatter(formatter)
      # self._logger[service].addHandler(fileHandler)
      self._logger[service].addHandler(streamHandler)
      self._logger[service].addHandler(rotateFileHandler)
      
    services.remove('system')
    services.remove('scheduler')

  def getLogger(self, service):
    return self._logger[service]


class Lamp_Logger(object, metaclass=SingletonType):
  def __init__(self):
    self._logger = {}
    self._logger = logging.getLogger('lamp')
    # config로 정의해야 될 부분
    self._logger.setLevel(logging.DEBUG)
    # 로그의 형식을 포매팅

    # lampFileHandler = logging.FileHandler('/data/logadmin/baseball.log')
    # lampFileHandler = logging.FileHandler('log/lamp.log')
    # 로그 파일 처리(로테이팅)
    file_max_bytes = 1024 * 1024 * 100  # (100MB)
    if(LOG_FILE_SIZE):
      file_max_bytes = LOG_FILE_SIZE

    # backupCount는 갯수
    #rotateFileHandler = logging.handlers.RotatingFileHandler(filename='/data/logadmin/log/baseball_lamp.log', maxBytes=file_max_bytes, backupCount=5)
    rotateFileHandler = logging.handlers.RotatingFileHandler(filename='log/baseball_lamp.log', maxBytes=file_max_bytes, backupCount=5)

    # self._logger.addHandler(lampFileHandler)
    self._logger.addHandler(rotateFileHandler)
    self._logger = LoggerAdapter(self._logger)

  # print logger

  def printLoggerError(self, operation, logType, desc, duration=None, payload=None):
    resType = 'S'
    code = '999'
    self._logger.error(
      None, 
      extra={
        'operation':operation,
        'logType':logType, 
        'resType':resType, 
        'desc':desc, 
        'code':code, 
        'duration':duration, 
        'payload':payload
      }
    )

  def printLoggerStandard(self, operation, logType, desc=None, duration=None, payload=None):
    resType = 'I'
    code = '200'
    self._logger.info(
      None, 
      extra={
        'operation':operation,
        'logType':logType, 
        'resType':resType, 
        'desc':desc, 
        'code':code, 
        'duration':duration, 
        'payload':payload
      }
    )

