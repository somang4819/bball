'''
수동으로 스케줄러 실행
'''
import requests
import sys

def check(year, date):
  url = 'http://localhost:9000/crawler/iescoreinning'
  # 내부의 RESTful을 호출하는 로직
  headers = {
    'token': 'test',
    'detail': 'baseball',
    'season_id': year,
    'g_ds': date
  }

  r = requests.get(url, headers=headers)
  print (r.content)

if __name__ == "__main__":
  year = sys.argv[1]
  date = sys.argv[2]
  check(year, date)


