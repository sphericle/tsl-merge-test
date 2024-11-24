import json, requests, time
from dotenv import dotenv_values

env = dotenv_values(".env")

path = 'repos/layout-list/data/'
base_url = 'http://127.0.0.1:8001/'
list_index_result = '_list.json'
benchmark = '_'
rank = 1

with open(path + list_index_result) as json_file:
    list = json.load(json_file)

for levelpath in list:
    print(levelpath) + ".json"
    if levelpath.startswith(benchmark):
        print("Skipping...")
        continue
    
    try:
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
            
            if 'author' in level:
                newform['publisher'] = level['author']
                
            # overwrite creator with publisher if creators array is empty (this is how the layout list does it)
            newform['creators'] = [level['author']] if level['creators'] == [] else level['creators']
            
                
                
            
            req = requests.post(
                base_url + 'api/v2/demons', 
                data=json.dumps(newform), 
                headers={
                    'Authorization': 'Bearer ' + env['AUTH'],
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )
            
            time.sleep(1)
            
            if req.status_code != 201:
                f = open(f"errors/error demon rank {rank}.json", "a")
                f.write(req.text)
                f.close()
                continue
            else:   
                link = req.headers['location']
                print(link)
                id = int([segment for segment in link.split('/') if segment][-1])
                
                
                recordi = 0
                for record in level['records']:
                    recordi += 1
                    recordform = {
                        'progress': record['percent'],
                        'player': record['user'],
                        'demon': id,
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
                    
                    
                    time.sleep(1)
                    
                    if req.status_code != 200:
                        f = open(f"errors/error demon {id} record {recordi}.json", "a")
                        f.write(req.text)
                        f.close()
                        continue
        rank += 1
    except Exception as error:
        print('error, skipping file...')
        f = open(f"errors/error file {levelpath}.json", "a")
        f.write(error)
        f.close()