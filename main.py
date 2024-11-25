import json, requests, time
from dotenv import dotenv_values

# get auth token
env = dotenv_values(".env")


# this should be the path to the level data in the TSL template
path = 'repos/layout-list/data/'

# your pointercrate clone
base_url = 'http://127.0.0.1:8001/'
list_index_result = '_list.json'
# levels with a name that starts with this will be skipped
benchmark = '_'
# first level in the list will be at pos 1
rank = 1

with open(path + list_index_result) as json_file:
    list = json.load(json_file)


for levelpath in list:
    print(levelpath)
    # if the lvl is a divider
    if levelpath.startswith(benchmark):
        print("Skipping...")
        continue
    
    try:
        # read this level's file
        with open(path + levelpath + '.json') as level_file:
            level = json.load(level_file)
            
            # if its a divider and the first check didn't work for some reason
            if level['id'] == 0:
                continue
        
            # format the level data into pointercrate's format
            newform = {
                'name': level['name'],
                'position': rank,
                'requirement': level['percentToQualify'],
                'verifier': level['verifier'],
                'level_id': level['id'],
                'video': level['verification'] 
            }
            
            # conditional fields have to be done like this i think THanks Pythoin
            if 'author' in level:
                newform['publisher'] = level['author']
                
            # overwrite creator with publisher if creators array is empty (this is how the layout list does it)
            newform['creators'] = [level['author']] if level['creators'] == [] else level['creators']
            
                
                
            # post request to your pointercrate server's api, sending the new format and your auth
            req = requests.post(
                base_url + 'api/v2/demons', 
                data=json.dumps(newform), 
                headers={
                    'Authorization': 'Bearer ' + env['AUTH'],
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )
            
            # avoid ratelimits
            time.sleep(1)
            
            # if the request did not result in a created demon
            if req.status_code != 201:
                f = open(f"errors/error demon rank {rank}.json", "a")
                f.write(req.text)
                f.write('\n\n')
                f.write(json.dumps(newform))
                f.close()
                continue
            else:   
                # link will look like: api/v2/demons/{id}
                link = req.headers['location']
                print(link)
                # extract the id from the link
                id = int([segment for segment in link.split('/') if segment][-1])
                
                # pointercrate stores records separately and connects them via demon id
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
                    
                    # if the enjoyment field exists and is not "?"
                    if 'enjoyment' in record:
                        if record['enjoyment'] != "?": # shut up
                            # if we're here, the enjoyment must look something like: "{num}" (in quotes)
                            if type(record['enjoyment']) == "string":
                                # if the enjoyment is a string for some reason (TANGIIII!!!!!) convert it to integer and add it to the format
                                recordform['enjoyment'] = int(record['enjoyment'])
                            else:
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
                    
                    
                    
                    # if the request did not result in 200 OK
                    if req.status_code != 200:
                        # the error could be because the player is spelt differently
                        # try to ask the server what the correct spelling should be
                        req2 = requests.get(
                            base_url + 'api/v1/players?name=' + record['user'],
                            headers={
                                'Authorization': 'Bearer ' + env['AUTH'],
                                'Content-Type': 'application/json',
                                'Accept': 'application/json'
                            }
                        )
                        
                        # load the response
                        playerinfo = json.loads(req2.content)
                        
                        # if the response returned a player
                        if (len(playerinfo) > 0):
                            # use the first returned player's name in the record form
                            recordform['player'] = playerinfo[0]['name']
                            
                            # resubmit the record with the corrected name
                            # dont even try to tell me this is trash bc idc
                            req = requests.post(
                                base_url + 'api/v1/records', 
                                data=json.dumps(recordform), 
                                headers={
                                    'Authorization': 'Bearer ' + env['AUTH'],
                                    'Content-Type': 'application/json',
                                    'Accept': 'application/json'
                                }
                            )
                            
                            # if the request still did not result in 200 OK
                            if req.status_code != 200:
                                f = open(f"errors/error demon {id} record {recordi}.json", "a")
                                f.write(req.text)
                                f.write('\n\n')
                                f.write(json.dumps(recordform))
                                f.close()
                                continue
                        
                    # avoid ratelimits
                    time.sleep(1)
                            
                    
        rank += 1
    except Exception as error:
        # what the hell
        print('error, skipping file...')
        f = open(f"errors/error file {levelpath}.json", "a")
        f.write(str(error))
        f.close()