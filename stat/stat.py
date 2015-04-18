import os
import json
import sys
import urllib2

class Data:
    def __init__(self, data):
        self.data = data
        self.id = data['id']
        self.nbr = 0
        self.win = 0

def getStatic(region, data):
    key = "c980286d-2e9c-41b5-bac5-6f6dd616eb9d"
    url = "https://global.api.pvp.net/api/lol/static-data/{region}/v1.2/{data}?api_key={key}".format(
        region=region, key=key, data=data)
    print("get " + data + " : " + url)
    data = urllib2.urlopen(url).read()
    data = json.loads(data)
    return data['data']

def processData(region, nbr, process):
    base = "../getMatch/" + region + "/"
    matchs = list(os.listdir(base))
    matchs = matchs[:nbr]
    datas = []
    i = 1
    for match in matchs:
        f = open(base + match, 'r')
        try:
            data = json.load(f)
        except ValueError:
            pass
        process(data)
        if i % (NBR/100):
            sys.stdout.write("\rParsing data : {:3}%".format((100 * i) / NBR))
            sys.stdout.flush()
        i += 1
    print("")
    return datas

NBR = 37000

champStats = {}
summStats = {}
champions = getStatic("euw", "champion")
summoners = getStatic("euw", "summoner-spell")

for x in champions:
    c = Data(champions[x])
    champStats[c.id] = c
    
for x in summoners:
    c = Data(summoners[x])
    summStats[c.id] = c

def process(data):
    winner = data['teams'][0]['teamId'] if data['teams'][0]['winner'] else data['teams'][1]['teamId']
    for p in data['participants']:
        todo = [
            (p['championId'], champStats, "champ"),
            (p['spell1Id'], summStats, "summ"),
            (p['spell2Id'], summStats, "summ")
            ]
        win = 1 if winner == p['teamId'] else 0
        for x in todo:
            if x[0] in x[1]:
                x[1][x[0]].nbr += 1
                x[1][x[0]].win += win
            else:
                print("unknown", x[2],":", x[0])

processData("euw", NBR, process)


for x in sorted(summStats.values(), key=lambda x: x.nbr):
    print("{name:15}: {win:3}% wins {nbr:3}% played".format(
        name = x.data['name'],
        win  = (100 * x.win) / x.nbr if x.nbr else 0,
        nbr  = (100 * x.nbr) / (NBR*10)
    ))

labels = []
data1 = []
data2 = []
for x in sorted(champStats.values(), key=lambda x: x.nbr):
    print("{name:15}: {win:3}% wins {nbr:3}% played".format(
        name = x.data['name'],
        win  = (100 * x.win) / x.nbr if x.nbr else 0,
        nbr  = (100 * x.nbr) / NBR
    ))
    labels.append('"' + x.data['name'] + '"')
    data1.append(str((100 * x.win) / x.nbr if x.nbr else 0))
    data2.append(str((100 * x.nbr) / NBR))

def win(data, team):
    val = {}
    for p in data['participants']:
        if not p['teamId'] in val:
            val[p['teamId']] = 0
        for x in [champStats[p['championId']], summStats[p['spell1Id']], summStats[p['spell2Id']]]:
            val[p['teamId']] += x.win / x.nbr
    
    return max(val, key=lambda x: val[x]) == team
TEST = 1000
good = 0
def test(data):
    global good
    if win(data, data['teams'][0]['teamId']) == data['teams'][0]['winner']:
        good += 1
processData("euw", TEST, test)

print(100 * good / TEST)

f = open("data.js", 'w')
f.write("""
var labels = [{0}];
var data1 = [{1}];
var data2 = [{2}];
""".format(",".join(labels[:]), ",".join(data1[:]), ",".join(data2[:])))
f.close()