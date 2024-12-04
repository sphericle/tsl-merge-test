import requests

from dotenv import dotenv_values

# get auth token
env = dotenv_values(".env")

i = 0

while i < 100:
    i += 1
    print(i)
    req = requests.delete(f'http://127.0.0.1:8000/api/v1/players/{i}', headers={
        'Authorization': "Bearer " + env['AUTH']
    })
    print(req.status_code)