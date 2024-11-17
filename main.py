import json, requests
from dotenv import dotenv_values

env = dotenv_values(".env")

path = 'repos/layout-list/data/'
base_url = 'http://127.0.0.1:8001/'
list_index_result = '_list.json'
benchmark = '_'
rank = 0

with open(path + list_index_result) as json_file:
    list = json.load(json_file)

for levelpath in list:
    print(levelpath)
    rank += 1
    
    with open(path + levelpath + '.json') as level_file:
        level = json.load(level_file)
    
        level['rank'] = rank
        newform = {
            'name': level['name'],
            'position': rank,
            'creators': level['creators'],
            'requirement': level['percentToQualify'],
            'verifier': level['verifier'],
            'publisher': level['author'],
            'video': level['verification']
        }
        
        print(newform)
        
        req = requests.post(
            base_url + 'api/v2/demons', 
            data=newform, 
            headers={
                'Authorization': 'Bearer ' + env['AUTH'],
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )
        
        print(req.content)