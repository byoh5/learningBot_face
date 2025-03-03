import requests
import jwt
# 2020080013002  러닝봇 class id
def login(id,pw,pid):
    key = 'secretjujuR'
    password = jwt.encode({'pass': pw}, key, algorithm='HS256')
    params = {'login_id': id, 'login_pass': password, 'class': pid}
    url_yes = 'http://runcoding.co.kr/auth_user/'
    r = requests.get(url_yes, params=params)
    return r.text

