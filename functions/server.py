from dotenv import dotenv_values
import requests, json

env = dotenv_values(".env")

def postLevel(data):
    # post request to your pointercrate server's api, sending the new format and your auth
    req = requests.post(
        env["BASE_URL"] + 'api/v2/demons', 
        data=json.dumps(data), 
        headers={
            'Authorization': 'Bearer ' + env['AUTH'],
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    )
    
    return req

def postRecord(data):
    req = requests.post(
        env["BASE_URL"] + 'api/v1/records', 
        data=json.dumps(data), 
        headers={
            'Authorization': 'Bearer ' + env['AUTH'],
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    )
    
    return req


def getUser(name):
    req = requests.get(
        env["BASE_URL"] + 'api/v1/players?name=' + name,
        headers={
            'Authorization': 'Bearer ' + env['AUTH'],
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    )
    
    return req

