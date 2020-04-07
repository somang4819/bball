import pymysql
import configparser
from config import HOST, PORT, USER, PASSWORD, DB, wtimeout
from common.Util.logger import Lamp_Logger

'''
CONFIG 를 만들어 넣는다
DB 정보 
smyucheck 여기 예외처리 모두 해야함

https://code.tutsplus.com/ko/tutorials/professional-error-handling-with-python--cms-25950
cursor.execute 의 param 에 대해서
https://pymysql.readthedocs.io/en/latest/modules/cursors.html

smyucheck 커넥터를 클래스로 만들수있음 생성자에서 커넥트 소멸자에서 클로스
'''
#smyucheck raise!! 
#https://www.programcreek.com/python/example/68898/pymysql.Error
def Connect(host=HOST, port=PORT, user=USER, password=PASSWORD, db=DB):
  try:
    db = pymysql.connect(host=host, port=port, user=user, password=password, db=db, write_timeout=wtimeout)
  except pymysql.Error as e:
    return e
  return db

#smyu200318
# db conn이 살아있는지 검사하고 끊음
'''
def dbConnectClose(conn):
  if conn is not None:
    conn.close()
  return None
'''
def dbConnectClose(conn):
  if conn is not None:
    try: 
      conn.close()
    except pymysql.Error as e:
#      return 'could not close connection error pymysql'
      return str(e)
  return 'connection closed successfully'

#smyucheck 예외처리
def dbCursorClose(cursor):
  if cursor is not None:
    try:
      cursor.close()
    except pymysql.Error as e:
      return str(e)
#      return 'could not close connection error pymysql {}: {}'.format(e.args[0], e.args[1])
  return 'db cursor closeed sucessfully'

#~smyu

#smyu 200318 return 조정
def selectsql(sql, conn, param):
  cursor = conn.cursor()
  cursor.execute(sql, param)
  fetchreslist=cursor.fetchall()

  dbCursorClose(cursor)
  return fetchreslist

#smyu
# ex반환 말고deledtedKeys 반환, ex는 위 함수에서 로깅
def deletewithgmkeylist(conn, table, keyColName, gmkeySet):
  delCnt=0
  deledtedKeys = [] 
  colname=list(keyColName.values())  

  try:
    cursor = conn.cursor()
  except pymysql.MySQLError as ex:
    return str(delCnt)+' rows deleted', ex

  for gmkey in gmkeySet:
    sql = 'DELETE FROM '+table+' WHERE '+colname[0]+'=\''+ gmkey +'\';'
    #print("sql")
    #print(sql)

    try:
      delres = cursor.execute(sql)
      #print (delres)
      delCnt += 1
      deledtedKeys.append(gmkey) 
    except Exception as ex:
      #print(ex)
      return str(delCnt)+' rows deleted', ex
    finally:
      conn.commit()
      dbCursorClose(cursor)

  return str(delCnt)+' rows deleted', deledtedKeys
#~smyu

def insertUpdatesql2(columns, table, key):
  insertsql = InsertSql(columns, table)
  updatesql = UpdateSql(columns, table, key)
  return insertsql, updatesql

#sql문 생성
def InsertSql(columns, table):

  placeholders = ', '.join(['%s'] * len(columns))
  columns = ', '.join(columns)

  return ''' INSERT INTO '''+table+''' (%s) VALUES (%s) ''' % (columns, placeholders)

#sql문 생성
def UpdateSql(columns, table, key):

  # 업데이트 컬럼
  update = '=%s ,'.join(columns)
  update += '=%s' # 마지막 컬럼 까지 추가

  pk = [k for k in key]
  pk = '=%s AND '.join(pk)
  pk += '=%s'  # 마지막 컬럼 까지 추가

  return ''' UPDATE '''+table+''' SET '''+ update +''' WHERE ''' + pk 


# def insertUpdatesql(columns, table):
#
#
#   # 업데이트 컬럼
#   update = '=%s ,'.join(columns)
#   update += '=%s' # 마지막 컬럼 까지 추가
#
#
#   columns = ', '.join(columns)
#
#   # 내용 찾아보고 뒷부분 고민
#   return ''' INSERT INTO '''+table+''' (%s) VALUES (%s) on duplicate key update %s ;''' % (columns, placeholders, update)
#


'''
*** parkjp 2.27
특별한 값이 있으면 update 아니면 insert
'''
def insertUpdatesql(columns, table):

  placeholders = ', '.join(['%s'] * len(columns))
  # 업데이트 컬럼
  update = '=%s ,'.join(columns)
  update += '=%s' # 마지막 컬럼 까지 추가


  columns = ', '.join(columns)

  # 내용 찾아보고 뒷부분 고민
  return ''' INSERT INTO '''+table+''' (%s) VALUES (%s) on duplicate key update %s ;''' % (columns, placeholders, update)

def DataInsert(sql, param, columns, conn):
    '''
    exception 확인 해서 관련 내용 보완 해야 함
    '''
    try :
      p = []
      cursor = conn.cursor()

      for col in columns:
        if param[col] == 'True':
          p.append(True)
        elif param[col] == 'False':
          p.append(False)
        else:
          p.append(param[col])

      # 업데이트문 떄문에 2번 넣는다
      for col in columns:
        if param[col] == 'True':
          p.append(True)
        elif param[col] == 'False':
          p.append(False)
        else:
          p.append(param[col])

      for col in columns :
        p.append(param[col])
      # 에러 나는 것에 대한 로거를 찍는 부분
      # print (p)
      cursor.execute(sql, p)
    except Exception as ex:
      # 에러 나는 것에 대한 로거를 찍는 부분
      # 에러 나면 데이터 수집 종료를 선언하고 끝내야 한다
      raise ValueError
    finally:
      dbCursorClose(cursor)
'''
smyu 200319 가비지 코드 정리
def DataUpdate(sql, param, columns, conn):
  #exception 확인 해서 관련 내용 보완 해야 함
  try:
    p = []
    cursor = conn.cursor()

    for col in columns:
      if param[col] == 'True':
        p.append(True)
      elif param[col] == 'False':
        p.append(False)
      else:
        p.append(param[col])

    # 업데이트문 떄문에 2번 넣는다
    for col in columns:
      if param[col] == 'True':
        p.append(True)
      elif param[col] == 'False':
        p.append(False)
      else:
        p.append(param[col])

    for col in columns:
      p.append(param[col])
    # 에러 나는 것에 대한 로거를 찍는 부분
    # print(p)
    cursor.execute(sql, p)
  except Exception as ex:
    # 에러 나는 것에 대한 로거를 찍는 부분
    return ex
  finally:
    closeres = dbCursorClose(cursor)
'''
def DataInsertUpdate2(insertsql, updatesql, param, columns, conn, table, key, insertCnt, updateCnt):
  sql = ""
  '''
  exception 확인 해서 관련 내용 보완 해야 함
  '''
  try:
    p = []
    cursor = conn.cursor()
    for col in columns:
      if param[col] == 'True' : p.append(True)
      elif param[col] == 'False' : p.append(False)
      else : p.append(param[col])

    # 에러 나는 것에 대한 로거를 찍는 부분
    # 값이 없으면 insert

    if selectWithKey(conn, table, key, param) == 0:
      # print("insert")
      sql = insertsql
      insertCnt = insertCnt + 1
    else :
      # print("update")
      for k in key:
        p.append(param[key[k]])
      sql = updatesql
      updateCnt = updateCnt + 1

    # print (sql)
    # print (p)

    # 보완 #
    cursor.execute(sql, p)  
    return insertCnt, updateCnt, None
  except Exception as ex:
    # 에러 나는 것에 대한 로거를 찍는 부분
    # 보완해 주세요
    return None, None, ex
  finally:
    closeres = dbCursorClose(cursor)
  

def DataInsertUpdate(sql, param, columns, conn):
  '''
  exception 확인 해서 관련 내용 보완 해야 함
  '''
  try:
    p = []
    cursor = conn.cursor()
    for col in columns:
      if param[col] == 'True' : p.append(True)
      elif param[col] == 'False' : p.append(False)
      else : p.append(param[col])

    # 업데이트문 떄문에 2번 넣는다
    for col in columns:
      if param[col] == 'True' : p.append(True)
      elif param[col] == 'False' : p.append(False)
      else : p.append(param[col])
    # 에러 나는 것에 대한 로거를 찍는 부분
    # print (sql)
    # print (p)
    cursor.execute(sql, p)
  except Exception as ex:
    # print (ex)
    return ex
  finally:
    closeres = dbCursorClose(cursor)
  

def InsertBatch(sql, params, columns, conn):
  for param in params :
    DataInsertUpdate(sql, param, columns, conn)
  # commit의 위치 확인
  conn.commit()

#smyu 200317 api 데이터 삭제 버그
#sql문을 만들자, 테이블에 있는 게임키들을 리스트로 가져옴
def selectFetchAllTableSQL(conn, table, gmkey, AmountOfDataToFetch):
  colname=list(gmkey.values())  

  sql = 'SELECT ' + colname[0] +' FROM '+table+' WHERE '+colname[0]+' LIKE \''+ AmountOfDataToFetch +'%\' '+';'
  
  try:
    keysInDB = selectFetchAllTable(conn, table, sql)
  except pymysql.MySQLError as ex:
    return '0 rows fetched ', ex
  finally:
    return str(len(keysInDB))+' rows fetched ', keysInDB

def selectFetchAllTable(conn, table, sql):
  #테이블에서 fetch 수행
  #smyucheck pymysql.에러 종류 조사해보자 
  try:
    curs=conn.cursor()
    curs.execute(sql)
    AllKeyInDBTable = curs.fetchall()  
  except pymysql.MySQLError as ex:
    return  ex
  finally:
    dbCursorClose(curs)
    return AllKeyInDBTable
#~smyu

'''
*** parkjp 3.5
idx가 있을 떄, 
특별한 값이 있으면 update 아니면 insert

select 로 한번 조회해옴
느려짐
'''

def selectWithKey(conn, table, key, param):
  p= []
  pk = []
  for k in key :
    pk.append(k)
    p.append(param[key[k]])
  pk = '=%s AND '.join(pk)
  pk += '=%s'  # 마지막 컬럼 까지 추가
  
  sql = 'SELECT * FROM '+table+' WHERE '+ pk +' ;'

  return len(selectsql(sql, conn, p))


def insertUpdatesql(columns, table):

  placeholders = ', '.join(['%s'] * len(columns))
  # 업데이트 컬럼
  update = '=%s , '.join(columns)
  update += '=%s' # 마지막 컬럼 까지 추가

  columns = ', '.join(columns)

  # 내용 찾아보고 뒷부분 고민
  return ''' INSERT INTO '''+table+''' (%s) VALUES (%s) on duplicate key update %s ;''' % (columns, placeholders, update)

'''
insert와 update sql 을 만든다
'''
def InsertUpdateBatch2(insertsql, updatesql, params, columns, conn, table, key):

  insertCnt = 0
  updateCnt = 0

  for param in params:
    try :
      insertCnt, updateCnt, error = DataInsertUpdate2(insertsql, updatesql, param, columns, conn, table, key, insertCnt, updateCnt)

      if error:
        return 'Error, 0 rows inserted ', 'Error, 0 row updated', error

    except Exception as ex:
      return 'Error, 0 rows inserted ', 'Error, 0 row updated', ex
      # 데이터를 commit 하지 않습니다.
  # commit의 위치 확인
  
  try:
    conn.commit()
  except Exception as ex:
    return 'Error, 0 rows inserted ', 'Error, 0 row updated', ex

  return str(insertCnt)+' rows inserted ', str(updateCnt)+' row updated', None

# if __name__ == "__main__":
#   conn = Connect()
#
#   if selectWithKey(conn) == 0 :
#     # 값이 없으면 insert
#     print("insert")
#     # DataInsert(sql, param, columns, conn)
#   else :
#     print("update")
#     DataUpdate(sql, param, columns, conn)
