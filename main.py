import json, requests

path = "repos/layout-list/data/"
list_index_result = "_list.json"
benchmark = "_"
rank = 0

with open(path + list_index_result) as json_file:
    list = json.load(json_file)

for levelpath in list:
    print(levelpath)
    rank += 1
    
    with open(path + levelpath + '.json') as level_file:
        level = json.load(level_file)
    
        level['rank'] = rank
        data = {
            'name': level.name,
            'position': rank,
            'requirement': level.percentToQualify,
            'verifier': level.verifier,
            'publisher': level.author,
            'creators': level.creators,
            'video': level.verification
        }
        
        print(data)
        
        requests.post('https://127.0.0.1/api/v2/demons/', data=data,)