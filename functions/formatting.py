def lvl_to_pc(level, rank):
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
    
    return newform

def record_to_pc(record, id):
    # format the record data into pointercrate's format
    recordform = {
        'progress': record['percent'],
        'player': record['user'],
        'demon': id,
        'video': record['link'],
        'status': 'APPROVED'
    }
    
    # if the enjoyment field exists and is not "?"
    if 'enjoyment' in record:
        if record['enjoyment'] != "?": # shut up
            # in case the enjoyment is a string for some reason (TANGIIII!!!!!) convert it to integer and add it to the format
            recordform['enjoyment'] = int(record['enjoyment'])
    
    return recordform


def writeError(name, txt):
    f = open(f"errors/{name}.json", "a")
    f.write(str(txt))
    f.close()
    
    return 201