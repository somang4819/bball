from flask import request
# from flask_restful import Resource
from flask_restplus import Resource, Namespace

import datetime
import jwt

'''
parkjp 18.12.11
rest CRUD 구현
C(POST) : 토큰관련 서비스 ...
R(GET) : 토큰관련 서비스 ...
U(PUT) : 토큰관련 서비스 ...
D(DELETE) : 토큰관련 서비스 ...
'''
secretKey = 'ai_data_discovery_crawler'

api = Namespace('register', description='관리')
auth_ip = ['localhost', '127.0.0.1']
class tokenRegister(Resource):

  def __init__(self, *args, **kwargs):
    logger = kwargs['logger']
    self.logger = logger
    self.api = api

  # 새로운 토큰 발급
  def post(self):

    # '''
    # header로 암호화된 id/ password 검증을 통해 token을 발급해야 한다
    # '''
    id = ''
    password = ''

    # request가 ip List에 존재할 경우에만 토큰을 준다

    if request.remote_addr in auth_ip :

      issuer = 'parkjp'

      subject = 'ai_data_discovery'
      # 토큰의 만료 날자
      date_time_obj = datetime.datetime
      exp_time = date_time_obj.timestamp(date_time_obj.utcnow() + datetime.timedelta(days=1))
      scope = ['crawler']

      payload = {
        'sub': subject,
        'iss': issuer,
        'exp': int(exp_time),
        'scope': scope,
        'aud' : request.remote_addr
      }

      token = jwt.encode(payload, secretKey, algorithm='HS256')

      return {
        'msg': '새로운 토큰이 생성 되었습니다.',
        'access_token': str(token)
      }

    else :
      return {
        'msg': '토큰 발급 조건을 확인 하세요'
      }

