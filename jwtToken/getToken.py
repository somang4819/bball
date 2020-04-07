import jwt
import sys

secretKey = 'ai_data_discovery_crawler'
def gettoken(pw):
	subject = pw
	# 토큰의 만료 날자

	payload = {
		'password': subject
	}

	token = jwt.encode(payload, secretKey, algorithm='HS256')
	print(token)
	return token


if __name__ == "__main__":
	pw = sys.argv[1]
	token = gettoken(pw)

