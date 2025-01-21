import requests, json

from dotenv import dotenv_values

# get auth token
env = dotenv_values(".env")

i = 0

preq = requests.get('http://127.0.0.1:8000/api/v2/demons', headers={
    'Authorization': "Bearer " + env['AUTH']
})

json = json.loads(preq.content)

if len(json) > 0:
    
    i = json[0]['id']

    while True:
        req = requests.delete(f'http://127.0.0.1:8000/api/v2/demons/{i}', headers={
            'Authorization': "Bearer " + env['AUTH']
        })
        i += 1

        print(f"{i}: {req.status_code}")