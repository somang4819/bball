from common.Util.logger import Logger, Lamp_Logger

from flask import Flask, g
# from flask_restful import Api
from flask_restplus import Api

from os.path import isfile
from config import config

import os
import sys
import importlib

sys.path.append(os.getcwd())
import importlib

app = Flask(__name__)

# config 업로드
app.config.from_object(config)
conf = app.config

api = Api(app, version='0.1', title='data crawling service', description='데이터 크롤링과 전처리')

# flask_restful
# api = Api(app)
# cNs = api.namespace('crawler', description = 'crawler services')

services = app.config['SERVICES']

# openServices = app.config['OPEN_SERVICES']
logger = Logger(services)

'''
19.03.10 koo
LAMP LOGGER INIT
'''

lamp_log = Lamp_Logger()

lamp_log.printLoggerStandard(
  operation='Server_Started', 
  logType='NOTIFY', 
  desc=None,
  duration=None
)

def loadMouduleFunction(moduleName, className):
  mod = importlib.import_module(moduleName)
  class_ = getattr(mod, className)
  # instance = class_()
  return mod, class_

def importService(service):

  crawlerPath = service+'/'
  try :
    for dir in os.listdir(crawlerPath):
      if isfile(crawlerPath+dir) is False and dir != '__pycache__':
        # 동적으로 전체 import
        channel = dir
        className = channel.lower() + service.capitalize()
        moduleName = service+'.' + channel + '.' + className
        mod, class_ = loadMouduleFunction(moduleName, className)

        # main 소스를 부른다
        # try/ catch 보완
        try :
          className = 'api'
          # flask plus namespace정의
          if service == "crawler" :
            moduleName = service +'.' + service.capitalize() + "base".capitalize()
          elif service == "register" :
            moduleName = service +'.' + channel +'.'+ channel.lower() + service.capitalize()

          # api.add_resource(class_, '/' + service + '/' + channel)
          nsMod, ns = loadMouduleFunction(moduleName, className)
          api.add_namespace(ns)
          ns.add_resource(class_, '/' + channel, resource_class_kwargs={'logger': logger.getLogger(service), 'service': service})

        except Exception as ex:
          lamp_log.printLoggerError(
            operation=str(channel) + 'Module_Loading', 
            logType='NOTIFY',
            desc='{channel} Module Loading Error'.format(channel=str(channel)),
            payload={'message': str(ex)}
          )

          log.error(ex)
          msg = 'error : 사이트 모듈 로딩 실패 ===>', 'channel : ' + str(channel)
          pass
        # print ('/' + service + '/' + channel)
  except Exception as ex:
    lamp_log.printLoggerError(
      operation='Module_Loading', 
      logType='NOTIFY',
      desc='Service Module Loading Error',
      payload={'message': str(ex)}
    )

    log.error(ex)
    pass

# log = logger.getLogger('system')
# log.info('=== service import ===')
# for service in services :
#   importService(service)

# log.info('=== service run ===')

# if __name__ == '__main__':
'''
18.11.14 parkjp
crawler 서비스를 flask에 올리기
crawler 에 있는 폴더 이름을 받아서
그 이름으로 flask REST URI 로 올린다

200302 smyu
사용자 인풋없이 모든 크롤러 서비스를 올리는데 왜 동적으로 올린지 모르겠다.

18.11.29
# try/ catch/ raise 에 관한 처리 고민
# token : jwtToken 이용 @jwtCert
'''
log = logger.getLogger('system')
log.info('=== service import ===')
lamp_log.printLoggerStandard(
  operation='Service_Import', 
  logType='NOTIFY',
  desc=None,
  duration=None
)
for service in services :
  importService(service)

log.info('=== service run ===')

# 시동 함수로 변경 ...

'''
19.3.3 parkjp 
스케쥴러에 로그를 부여하고 실행 합니다. 
나중에 분리하기 쉽도록 작성합니다.(web 과의 연결)
로그를 이용해서 
스케줄러 실패 x
스케줄러 처음 동작 0
스케줄러 시작 0
을 관리 할 수 있도록 합니다.
'''

if app.config['SHCEDULER'] == 'ON' :
  log.info('=== scheduler run ===')
  lamp_log.printLoggerStandard(
    operation='Scheduler_Init', 
    logType='NOTIFY', 
    desc=None,
    duration=None
  )
  from scheduler.crawler.crawlerScheduler import *
  from scheduler.crawler.config import TASK_CONFIG

  slog = logger.getLogger('scheduler')
  scheduler = Scheduler(slog)
  # 스케쥴러를 등록합니다. (config에 따라서)
  for k, v in TASK_CONFIG.items():
    scheduler.scheduler(k, **v)

# app.run(debug=False, host='0.0.0.0', port='1234')