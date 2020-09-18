import requests

url = 'http://127.0.0.1:5000/api/clubs'

obj = {
    "code":"abcd",
    "name":"Water Club",
    "description":"We drink water",
    "tags":["Undergraduate","Health","Graduate"]
}

res = requests.post(url, json=obj)
print(res)