from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor
from common.Util.logger import Lamp_Logger
# from scheduler.crawler.config import TASK_CONFIG
from datetime import timedelta


import requests
import datetime
import time
import pytz

'''
19.2.24 parkjp
내부 REST를 구성해 스케쥴러를 돌리는 로직

APScheduler(기본 구동 법)
Cron 방식으로 사용
Interval 방식으로 사용
'''

'''
19.03.10 koo
LAMP LOGGER INIT
'''

lamp_log = Lamp_Logger()

class Scheduler:
    def __init__(self, logger):
        executors = {
          'default': {'type': 'threadpool', 'max_workers': 20},
          'processpool': ProcessPoolExecutor(max_workers=8)
        }
        job_defaults = {
          'coalesce': False,
          'max_instances': 8
        }
        self.sched = BackgroundScheduler()
        self.sched.configure(executors=executors, job_defaults=job_defaults)
        self.sched.start()
        self.log = logger
        self.job_id = ''

    def __del__(self):
        self.shutdown()

    def shutdown(self):
        self.sched.shutdown()

    def kill_scheduler(self, job_id):
        try:
            self.sched.remove_job(job_id)
        except JobLookupError as err:
            lamp_log.printLoggerError(
                operation="Scheduler_Stop", 
                logType='NOTIFY',
                desc="Scheduler Stop Error",
                payload={'error': str(err)}
            )
            print("fail to stop Scheduler: {err}".format(err=err))
            return

    # 데이터를 적재해서 DB에 쌓는 스케쥴러를 실행 합니다.
    def task(self, type, name):
      self.log.info(str(type) + ' ' +str(name) + ' ' + '스케쥴을 실행 합니다')
      url = 'http://localhost:9000/crawler/' + name
      # 내부의 RESTful을 호출하는 로직

      # g_ds를 판단하는 로직
      # 오전 5시 이전에는 전날로 / 오후 5시에는 오늘로
      today = datetime.datetime.today()
      if int(today.strftime("%H")) > 5:
        g_ds = today.strftime("%Y%m%d")
      else:
        yes = today - timedelta(days=1)
        yes = yes.strftime("%Y%m%d")
        g_ds = yes
        
      start_time = time.time()

      headers = {
        'token': 'test',
        'detail': 'baseball',
        #'season_id': '2018',
        #'g_ds': '20180324'
        'season_id' : datetime.datetime.today().strftime("%Y"),
        'g_ds' : g_ds
      }
      r = requests.get(url, headers=headers, timeout=60)

      print(str(name) + " : --- %s seconds ---" % (time.time() - start_time))

    # 각각의 크론 정의를 할 필요가 있음
    def scheduler(self, name, **kwargs):
        self.log.info("{type} Scheduler Start".format(type=kwargs['type']))
        # 크론으로 실행할 경우와 주기적으로 실행할 경우로 나눈다(기초 데이터 업데이트와 주기 데이터 업데이트)
        # print (kwargs['type'], kwargs['interval'], kwargs['id'], name)

        if kwargs['type'] == 'interval':
            self.sched.add_job(self.task, kwargs['type'], seconds=kwargs['interval'], id=kwargs['id'], timezone=pytz.timezone('Asia/Seoul'), args=(kwargs['type'], name))
        elif kwargs['type'] == 'cron':
            # 크론에 대한 보다 상세한 정의로 만들어야 함
            # 없으로 None 으로 설정해도 되는지 ?
            self.sched.add_job(self.task, kwargs['type'],
                               # day_of_week=kwargs['option']['day_of_week'],
                               # hour=kwargs['option']['hour'],
                               # second=kwargs['option']['second'],
                               minute = kwargs['option']['minute'],
                               id=kwargs['id'],
                               timezone=pytz.timezone('Asia/Seoul'),
                               args=(kwargs['type'], name))


# while True:
#     time.sleep(1)

# if __name__ == '__main__':
#     # 스케쥴러 클래스를 로딩 합니다.
#

    # count = 0
    # while True:
    #   # time.sleep(1)
    #   count += 1
    # print ('??')
    # if count == 10:
    #   print ('???')
    #   scheduler.kill_scheduler("1")
    #
    # elif count == 30:
    #   scheduler.kill_scheduler("2")

    # scheduler.scheduler('cron', "1")
    # scheduler.scheduler('interval', "2")

    # count = 0
    # while True:
    #     '''
    #     count 제한할 경우 아래와 같이 사용
    #     '''
    #     print("Running main process")
    #     time.sleep(1)
    #     count += 1
    #     if count == 10:
    #         scheduler.kill_scheduler("1")
    #         print("Kill cron Scheduler")
    #     elif count == 15:
    #         scheduler.kill_scheduler("2")
    #         print("Kill interval Scheduler")

