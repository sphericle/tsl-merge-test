import json, requests

path = 'repos/layout-list/data/'
list_index_result = '_list.json'
benchmark = '_'
rank = 0

def trimString(str):
    str = str.lower().replace(' ', '_')
    if str[0] == '_':
        str = str[1:]
    return str

paths = []
initGet = requests.get('https://cscl.shuttleapp.rs/api/v2/demons?limit=100')
response = initGet.content
listdata = json.loads(response)
minLevel = listdata[0]

with open('repos/layout-list/data/_list.json', 'r') as listfile:
    print('writing to _list...')
    list = json.load(listfile)
    for level in list:
        paths.append(level)
    
    
for minLevel in listdata:
    fullReq = requests.get(f'https://cscl.shuttleapp.rs/api/v2/demons/{minLevel['id']}')
    response2 = fullReq.content
    wtfpointercrate = json.loads(response2)
    level = wtfpointercrate['data']
    
    creators = []
    records = []
    
    for creator in level['creators']:
        creators.append(creator['name'])
        
    for record in level['records']:
        recordBody = {}
        if record['enjoyment'] != None:
            recordBody = {
                'user': record['player']['name'],
                'link': record['video'],
                'percent': record['progress'],
                'hz': 240,
                'enjoyment': record['enjoyment']
            }
        else:
            recordBody = {
                'user': record['player']['name'],
                'link': record['video'],
                'percent': record['progress'],
                'hz': 240
            }
        records.append(recordBody)
        
    body = {
        'id': level['level_id'],
        'name': level['name'],
        'author': level['publisher']['name'], # python the goat!!!
        'creators': creators,
        'verifier': level['verifier']['name'],
        'verification': level['video'],
        'percentToQualify': level['requirement'],
        'song': 'wip',
        'difficulty': 1,
        'records': records
    }
    
    path = trimString(body['name'])
    indexpos = level['position'] - 1
    print(indexpos)
    paths.insert(indexpos, path)
    
    with open('repos/layout-list/data/' + path + '.json', 'w') as f:
        f.write(json.dumps(body))
        f.close()
    print('done')
    
    
print(paths)

with open('repos/layout-list/data/_list.json', "w") as listfile2:
    listfile2.write(json.dumps(paths))
    
print('done!')