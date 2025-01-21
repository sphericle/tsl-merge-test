# todo: allow pointercrate to accept live videos and twitch clips
# fix medal thing its not working
# parse level id

import json, requests
from dotenv import dotenv_values
from functions.formatting import *
from functions.server import *

env = dotenv_values(".env")
# this should be the path to the level data in the TSL template
path = 'repos/layout-list/data/'
list_index_result = '_list.json'
# levels with a name that starts with this will be skipped
benchmark = '_'
# first level in the list will be at pos 1
rank = 1

with open(path + list_index_result) as json_file:
    list = json.load(json_file)
    
if rank > 6:
    exit()
    
for levelpath in list:
    req = None
    # if the lvl is a divider
    if levelpath.startswith(benchmark):
        continue
    try:
        # read this level's file
        with open(path + levelpath + '.json') as level_file:
            level = json.load(level_file)
            # if its a divider and the first check didn't work for some reason
            if level['id'] == 0 or level['id'] == "0":
                continue
            newform = lvl_to_pc(level, rank)
            # post request to your pointercrate server's api, sending the new format and your auth
            req = postLevel(newform)
            # if the request did not result in a created demon
            if req.status_code != 201:
                creatori = 0
                for creator in newform['creators']:
                    if creator == None:
                        writeError(f'creator error rank {rank}.json', json.dumps(newform))
                        continue
                    newuser = getUser(creator)
                    newform['creators'][creatori] = newuser
                    creatori += 1
                if newform['publisher'] != None:
                    newauth = getUser(newform['publisher'])
                    newform['publisher'] = newauth
                if newform['verifier'] != None:
                    newver = getUser(newform['verifier'])
                    newform['verifier'] = newver
                
                print("\n\n\n")
                print(newform)
                req = postLevel(newform)
                if req.status_code != 201:
                    writeError(f"error demon rank {rank}.json", req.text, json.dumps(newform))
                    continue
                else:
                    # link will look like: api/v2/demons/{id}
                    link = req.headers['location']
                    # extract the id from the link
                    id = int([segment for segment in link.split('/') if segment][-1])
                    # pointercrate stores records separately and connects them via demon id
                    recordi = 0
                    for record in level['records']:
                        recordi += 1
                        recordform = record_to_pc(record, id)
                        req = postRecord(recordform)
                        # if the request did not result in 200 OK
                        if req.status_code != 200:
                            # the error could be because the player is spelt differently
                            # try to ask the server what the correct spelling should be
                            newplayer = getUser(record['user'])
                            if newplayer is not None:
                                recordform['player'] = newplayer
                                # resubmit the record with the corrected name
                                req = postRecord(recordform)
                                # if the request still did not result in 200 OK
                                if req.status_code != 200:
                                    print('failed again, deleting video...')
                                    writeError(f"error video demon {id} record {recordi}.json", json.dumps(recordform), req.text)
                                    recordform['video'] = None
                                    req = postRecord(recordform)
                                    if req.status_code != 200:
                                        print('failed again, writing error...')
                                        writeError(f"error demon {id} record {recordi}.json", json.dumps(recordform), req.text)  
                            else:
                                writeError(f"error demon {id} record {recordi}.json", 'player not found', json.dumps(recordform))
        rank += 1
    except Exception as error:
        # what the hell
        print('error, skipping file...')
        writeError(f"error file {levelpath}", error)