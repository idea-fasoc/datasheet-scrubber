from urllib.request import urlopen
import json
import sys
import pickle
 
myURL = "https://umich.box.com/s/8z3lsamqn3rn3yyxrtv636qe2chm5zvi"

try:
    with urlopen(myURL) as request:
        data = request.read().decode()
except Exception as e:
    print('Unable to request data from internet')
    sys.exit(1)
 
try:
    data = json.loads(data)
except Exception as e:
    print("Can't parse json string")
    sys.exit(1)
else:
    print('Finished loading json')
 
 
with open('digikey.pickle', 'wb') as fd:
    pickle.dump(data, fd)
 
with open('digikey.json', 'w') as fd:
    json.dump(data, fd)