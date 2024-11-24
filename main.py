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
    
    if levelpath.startswith(benchmark):
        continue
    with open(path + levelpath + '.json') as level_file:
        level = json.load(level_file)
        
        if level['id'] == 0:
            continue
    
        level['rank'] = rank
     
        newform = {
            'name': level['name'],
            'position': rank,
            'requirement': level['percentToQualify'],
            'verifier': level['verifier'],
            'level_id': level['id'],
            'video': level['verification'] 
        }
        
        # overwrite creator with publisher if creators array is empty (this is how the layout list does it)
        level['creators'] = [level['publisher']] if level['creators'] == [] else level['creators']
        
            
            
        
        req = requests.post(
            base_url + 'api/v2/demons', 
            data=json.dumps(newform), 
            headers={
                'Authorization': 'Bearer ' + env['AUTH'],
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )
        
        if req.status_code != 201:
            print(req.text)
            continue
        else:
            print('debug')        
            link = req.headers['location']
            id = link.split('/')[-1]
            
            
            
            for record in level['records']:
                recordform = {
                    'progress': record['percent'],
                    'player': record['user'],
                    'demon': 10,
                    'note': 'This record was automatically merged from the old TSL template.',
                    'video': record['link'],
                    'status': 'APPROVED'
                }
                
                if 'enjoyment' in record:
                    recordform['enjoyment'] = record['enjoyment']
                
                req = requests.post(
                    base_url + 'api/v1/records', 
                    data=json.dumps(recordform), 
                    headers={
                        'Authorization': 'Bearer ' + env['AUTH'],
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    }
                )
                
                if req.status_code != 200:
                    f = open(f"error demon", "a")
                    f.write(req.text)
                    f.close()
                    req.text
                    continue
                