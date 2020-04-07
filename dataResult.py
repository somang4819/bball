from common.DB.mysqlConnector import *
from common.Util.logger import Lamp_Logger

#smyucheck kwargs logger 불러오는 중/ 얘도 CrawlerBase 생성할 때 넘기는 인자를 받아야함.
from flask_restplus import Resource, Namespace, reqparse

import json
'''
18.11.14 parkjp
# 실질적으로 데이터 적재에 관한 설계
수집한 데이터를 적재 하는 class
데이터 기본정보 + 크롤링 데이터
1. data - 크롤링 결과 데이터
'''

'''
smyucheck 
여기서 로거 불러오는 부분 처리해서 db 핸들링 과정 로깅해야함.
'''
lamp_log = Lamp_Logger()

class CrawlerData(Resource):

  def __init__(self,  args, path):

    # 값이 제대로 안넘어 왔을때의 처리

    # 데이터 수집 카테고리 - 음악/ 영화/ 방송프로그램
    self.category = str(args.get('category')).lower()
    # 데이터 수집 채널 - 네이버/ 공공데이터 포털/ 지니/ 벅스 ...
    if args.get('channel') is not None :
      self.channel = str(args.get('channel')).lower()
    else : self.channel = str(path.split('/')[2]).lower()

    # 년도 id
    if args.get('season_id') is not None :
      self.season_id = str(args.get('season_id')).lower()
    else : pass

    # 경기 id
    if args.get('g_id') is not None :
      self.g_id = str(args.get('g_id')).lower()
    else : pass

    # 경기 일자
    if args.get('g_ds') is not None :
      self.g_ds = str(args.get('g_ds')).lower()
    else : pass

    # site에서의 detail/ 함수명
    if len(path.split('/')) > 3 : self.detail = str(path.split('/')[3])
    else :  self.detail = str(args.get('detail'))

    #json type 보내지는 다양한 옵션
    if args.get('option') is not None :
      # 값이 비어 있을 경우의 처리
      if len(args.get('option')) is 0:
        raise ValueError

      self.option = json.loads(json.dumps(str(args.get('option')))).encode('utf-8')
      print (self.option['params'])

    # 같은 함수내에서 분기점
    if args.get('type') is not None or args.get('type') != '' :
        self.type = str(args.get('type')).lower()

    # 데이터를 적제하는 값
    self.data = []
  
    #dheaderlist 는 스케쥴 정보를 크롤링 할 것
    self.keysInAPI = set()
    self.keysInDB = []
    self.keysInDBSet = set()
    self.KeysToDelete = set()

  # def defaultPrint(self):
  #   print ('=============== post header 에서 넘어온 값을 확인 합니다 ===============')
  #   print (self.category, '<===== category')
  #   print (self.channel, '<===== channel')
  #   print (self.type, '<===== type')
  #   print ('=================================================================')

  def printDic(self):
    for d in self.data:
      print(d)

  # 데이터 적재
  def dataInsert(self, table, mapping, key):
    params = []
    columns = list(mapping.keys())

    # 데이터를 맵핑해서 넣는다(매핑 코드 참조)
    
    '''
    smyu
    smyucheck-> 변수명 변경 필요
    1. params  
    여기서 부터 나오는 params 는 crawler channel 에서 사용하는 dicelement, data에 어펜드 했던 것들
    2. mapping
    mapping은 json 타입 필드명을 db 필드 명으로 맵핑 ! 
    mapping은 CrawlerBase 에 init 정의되어 있고 crawerchannel에서 값을 매김 CrawlerData에서만 사용 더이상 안씀 
    ~smyu
    '''

    for d in self.data:
      param = {}
      for k, v in mapping.items() :
        param[k] = d[v]
      params.append(param)    

    #테이블 컬럼에 맞는 sql문 생성
    insertsql, updatesql = insertUpdatesql2(columns, table, key)
    try:
      conn = Connect()
    except Exception as ex:
      lamp_log.printLoggerError(
        operation="{channel}_API".format(channel=str(self.channel)), 
        logType='NOTIFY',
        desc='{channel} DB connect error when Insert Update Batch'.format(channel=str(self.channel)),
        payload={'message': str(ex)}
      )      
    try:
      insertRes, updateRes, error = InsertUpdateBatch2(insertsql, updatesql, params, columns, conn, table, key)
    except Exception as ex:
      lamp_log.printLoggerError(
        operation="{channel}_API".format(channel=str(self.channel)), 
        logType='NOTIFY',
        desc='{channel} Insert Update Batch excute error'.format(channel=str(self.channel)),
        payload={'message': str(ex)}
      )  
    finally:   
      try:
        closeRes = dbConnectClose(conn)
      except Exception as ex:
        lamp_log.printLoggerError(
          operation="{channel}_API".format(channel=str(self.channel)), 
          logType='NOTIFY',
          desc='{channel} DB disconnect error when Insert Update Batch'.format(channel=str(self.channel)),
          payload={'message': str(ex)}
        )      

    #데이터 배치로 업데이트
    return insertRes, updateRes, error

  #smyu 더블헤더경기 스케줄 삭제
  #smyucheck fetchres 반환 말고 여기서 로그 찍고 리턴값조정
  def crawlerDataSync(self, table, mapping, key, AmountOfDataToSync):

    #검사에 쓸 set 초기화
    self.keysInDBSet.clear()
    self.keysInAPI.clear()
    self.KeysToDelete.clear()

    #프라이머리키의 컬럼 이름이 테이블마다 달라서 컬럼이름을 딕셔너리에서 가져옴
    keylist=list(key.values())
    
    #API에서 크롤링해온 데이터의 키 집합 모으기
    for d in self.data:
      self.keysInAPI.add(d[keylist[0]])
    #print("self.keysInAPI")
    #print(len(self.keysInAPI))
    #print(self.keysInAPI)

    #DB에서 sync 검사할 데이터의 키 집합 모으기
    try:
      conn = Connect()
    except Exception as ex:
      lamp_log.printLoggerError(
        operation="{channel}_API".format(channel=str(self.channel)), 
        logType='NOTIFY',
        desc='{channel} DB connect error when Sync data fetch'.format(channel=str(self.channel)),
        payload={'message': str(ex)}
      )
    try:
      fetchres, self.keysInDB= selectFetchAllTableSQL(conn, table, key, AmountOfDataToSync)
      lamp_log.printLoggerStandard(
        operation="{channel}_API".format(channel=self.channel), 
        logType='IN_MSG',
        desc=None,
        payload={
          'responseCode': 200,
          'message': '{channel} Synch data fetch SUCCESS'.format(channel=self.channel), 
          'count': fetchres
        }
      )
    except Exception as ex:
      lamp_log.printLoggerError(
        operation="{channel}_API".format(channel=str(self.channel)), 
        logType='NOTIFY',
        desc='{channel} Sync data fetch error'.format(channel=str(self.channel)),
        payload={'message': str(ex)+ ',' + fetchres}
      )
      return ex
    finally:
      try:
        closeres = dbConnectClose(conn)    
      except Exception as ex:
        lamp_log.printLoggerError(
          operation="{channel}_API".format(channel=str(self.channel)), 
          logType='NOTIFY',
          desc='{channel} DB disconnect error when Sync data fetch '.format(channel=str(self.channel)),
          payload={'message': str(ex)}
        )

    #fetch 결과로 받은 이중리스트 풀어서 set에 저장
    for sublist in self.keysInDB:
      for item in sublist:
        self.keysInDBSet.add(item)

    #print("self.keysInDB")
    #print(len(self.keysInDB))
    #print(self.keysInDBSet)

    #Sync검사 DB에는 있는데 API에는 없는 키를 검사
    self.KeysToDelete = self.keysInDBSet -self.keysInAPI

    #print("KeysToDelete")
    #print(len(self.KeysToDelete))
    #print(self.KeysToDelete)

    #smyucheck 동기화 할 데이터가 없을 때 delete 수행 없음
    if not self.KeysToDelete:
      return 'no data for synch, 0 rows deleted'

    try:
      conn = Connect()
    except Exception as ex:
      lamp_log.printLoggerError(
        operation="{channel}_API".format(channel=str(self.channel)), 
        logType='NOTIFY',
        desc='{channel} when Synch data delete, db connect error'.format(channel=str(self.channel)),
        payload={'message': str(ex)}
      )
    try:
      delres,deledtedKeys =deletewithgmkeylist(conn, table, key, self.KeysToDelete)
      #print(delres)
      #print(deledtedKeys) 
      lamp_log.printLoggerStandard(
        operation="{channel}_API".format(channel=self.channel), 
        logType='IN_MSG',
        desc=None,
        payload={
          'responseCode': 200,
          'message': '{channel} Synch data delete SUCCESS'.format(channel=self.channel), 
          'count': delres
        }
      )
    except Exception as ex:
      #print("deletewithgmkey ex")
      lamp_log.printLoggerError(
        operation="{channel}_API".format(channel=str(self.channel)), 
        logType='NOTIFY',
        desc='{channel} Synch data delete error '.format(channel=str(self.channel)),
        payload={'message': str(ex)}
      )
      return ex
    finally:
      try:
        closeres = dbConnectClose(conn)
      except Exception as ex:
        lamp_log.printLoggerError(
          operation="{channel}_API".format(channel=str(self.channel)), 
          logType='NOTIFY',
          desc='{channel} when Sync data delete, db disconnect error'.format(channel=str(self.channel)),
          payload={'message': str(ex)}
        )

    return delres
  #~smyu
