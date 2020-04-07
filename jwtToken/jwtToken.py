from flask import request
import jwt

'''
18.12.11 patkjp
jwt 관련 함수 
jwt 토큰 설정해 놓지만 
내부에서만 움직이는 rest 이므로 
현재는 이슈가 없음
'''

secretKey = 'ai_data_discovery_crawler'
def jwtCert(function):
  def wrapperFunction(*args):

    # 받은 데이터 중에 토큰이 들어있는지 확인 합니다.
    if not 'token' in request.headers:
      return {
        'msg':'토큰이 없습니다.'
      }
    token = request.headers['token']
    if token == "test" :
      pass
    else:
      # 인증 과정
      try:
        payload = jwt.decode(token, secretKey, algorithms=['HS256'])
      except:
        return {
          'msg': '인증 실패'
        }
        # kwargs['payload'] = payload
    return function(*args)
  return wrapperFunction
