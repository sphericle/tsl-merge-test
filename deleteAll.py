import requests

from dotenv import dotenv_values

# get auth token
env = dotenv_values(".env")

i = 0

while True:
    i += 1
    req = requests.delete(f'http://127.0.0.1:8000/api/v2/demons/{i}', headers={
        'Authorization': "Bearer " + env['AUTH']
    })
    
    print(f"{i}: {req.status_code}")