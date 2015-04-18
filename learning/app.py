from flask import Flask, request
import urllib2, httplib
import pickle, json
from pybrain.tools.shortcuts     import buildNetwork
app = Flask(__name__)

form = """
<html>
    <head>
    <title>Enter your lol username</title>
    <style>{style}</style>
    </head>
    <body>
        <form class='center' action="" method="GET">
            EUW username : <input type=text name=username></input>
        </form>
    </body>
<html>
"""

result = """
<html>
    <head>
    <style>{style}</style>
    <title>Current game for {name}</title>
    </head>
    <body>
    <a href="/">Change username</a> <a onclick='location.reload(true); return false;' href="#">Refresh</a>
    <div class='center'>You are going to <span class={result}>{result}</span> your game.</div>
    </body>
<html>
"""

error = """
<html>
    <head>
    <style>{style}</style>
    <title>{error}</title>
    </head>
    <body>
    <a href="/">Change username</a> <a href="#" onclick='location.reload(true); return false;'>Refresh</a>
    <div class='center'>{error}</div>
    </body>
<html>
"""

style = """
.center {
    position: fixed;
    top: calc(50vh - 0.5em);
    left: 0;
    width: 100%;
    height: 1em;
    text-align: center;
    font-size: 2em;
}
.win {
    color: #44ff44;
}
.loose {
    color: #ff4444;
}
"""

key = "INSERT KEY"

def getId(region, name):
    url = "https://euw.api.pvp.net/api/lol/{region}/v1.4/summoner/by-name/{summonerNames}?api_key={key}".format(region=region, summonerNames="".join(name.split(" ")), key=key)
    print("    -> get " + url)
    
    try: 
        data = json.loads(urllib2.urlopen(url).read())
    except urllib2.HTTPError, e:
        print(e)
        return None
    except urllib2.URLError, e:
        print(e)
        return None
    except httplib.HTTPException, e:
        print(e)
        return None
    return data.values()[0]['id']

def getCurrent(platformId, idd):
    url = "https://euw.api.pvp.net/observer-mode/rest/consumer/getSpectatorGameInfo/{platformId}/{summonerId}?api_key={key}".format(platformId=platformId, key=key, summonerId=idd)
    print("    -> get " + url)
    try: 
        data = json.loads(urllib2.urlopen(url).read())
    except urllib2.HTTPError, e:
        print(e)
        return None
    except urllib2.URLError, e:
        print(e)
        return None
    except httplib.HTTPException, e:
        print(e)
        return None
    return data

fileObject = open('network','r')
(fnn, labels) = pickle.load(fileObject)
fileObject.close()

REALINPUTS = [lambda data: float(data['gameStartTime'] % (3600 * 24))/(3600 * 24)]
INPUTS = REALINPUTS[:]
for i in range(10):
    def closure(x):
        INPUTS.append(lambda data:data['participants'][x]['championId'])
        INPUTS.append(lambda data:data['participants'][x]['spell1Id'])
        INPUTS.append(lambda data:data['participants'][x]['spell2Id'])
    closure(i)

def check(data, idd):
    inputs = []
    for inp in INPUTS:
        inputs.append(inp(data))
    inp = [0]*(len(REALINPUTS) + sum(map(lambda x: len(x), labels[len(REALINPUTS):])))
    for x in data['participants']:
        if x['summonerId'] == idd:
            team = x['teamId']
    i = 0
    for x in inputs:
        if i >= len(REALINPUTS):
            inp[labels[i][x]] = 1
        else:
            inp[i] = x
        i += 1
    output = fnn.activate(inp)
    team1win = output[0] > output[1]
    return team1win if 1 == team/100 else not team1win
    

@app.route("/", methods=['GET'])
def index():
    name = request.args.get('username', '')
    if name:
        idd = getId("euw", name)
        if not idd:
            return error.format(style=style, error="Unknown username")
        current = getCurrent("EUW1", idd)
        if not current:
            return error.format(style=style, error="No current match")
        win = check(current, idd)
        return result.format(style=style, name=name, result='win' if win else 'loose')
    else:
        return form.format(style=style)


if __name__ == "__main__":
    app.run(port=42042, host="0.0.0.0", debug=True)