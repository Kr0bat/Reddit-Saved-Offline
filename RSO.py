import requests
data = {'grant_type': 'password', 'username': 'USERNAME', 'password': 'PASSWORD'}
auth = requests.auth.HTTPBasicAuth('APPID', 'SECRET')
headers={'user-agent':'RSO.py by kr0bat'}
r = requests.post('https://www.reddit.com/api/v1/access_token', data=data, headers=headers, auth=auth)
d = r.json()
print(d)