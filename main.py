import json, requests

path = 'repos/layout-list/data/'
list_index_result = '_list.json'
benchmark = '_'
rank = 0

initGet = requests.get('https://cscl.shuttleapp.rs/api/v2/demons/')
response = initGet.content
listdata = json.loads(response)
minLevel = listdata[0]
for minLevel in listdata:
    fullReq = requests.get(f'https://cscl.shuttleapp.rs/api/v2/demons/{minLevel['id']}')
    response2 = fullReq.content
    wtfpointercrate = json.loads(response2)
    level = wtfpointercrate['data']
    print(level['name'])
    
    creators = []
    records = []
    
    for creator in level['creators']:
        creators.append(creator['name'])
        
    for record in level['records']:
        recordBody = {
            'user': record['player']['name'],
            'link': record['video'],
            'percent': record['progress'],
            'hz': 240,
            'enjoyment': record['enjoyment']
        }
        records.append(recordBody)
        
    body = {
        'id': level['id'],
        'name': level['name'],
        'author': level['publisher']['name'], # python the goat!!!
        'creators': creators,
        'verifier': level['verifier'],
        'verification': level['video'],
        'percentToQualify': level['requirement'],
        'song': 'wip',
        'songLink': 'wip2',
        'difficulty': 1,
        'records': records
    }
    
    with open('repos/layout-list/data/' + body['name'] + '.json', 'w') as f:
        f.write(json.dumps(body))
        f.close()
        print('done')