import urllib2
import os
import time
import datetime
import json

def getReadableTime(s):
    t = datetime.datetime.fromtimestamp(s)
    fmt = "%Y-%m-%d %H:%M:%S"
    return t.strftime(fmt)

def get(region, matchId):
    key = "INSERT KEY"
    url = "https://euw.api.pvp.net/api/lol/{region}/v2.2/match/{matchId}?api_key={key}".format(matchId=matchId, region=region, key=key)
    print("    -> get " + url)
    data = urllib2.urlopen(url).read()
    return data

def retrieve(region, matchId):
    print("retrieve " + matchId + " from " + region)
    pathname = region + "/" + str(matchId) + ".js"
    if not os.path.exists(region):
        os.mkdir(region)
    if os.path.exists(pathname):
        print("    -> already done")
        return
    print("    -> not done")
    try:
        data = get(region, matchId)
    except urllib2.HTTPError as e:
        time.sleep(1)
        print("    -> http error :" + str(e.read()))
        return
    time.sleep(1)
    f=open(pathname, 'w')
    f.write(data)
    f.close()
    print("    -> done")

def findAll():
    base = "../getid/"
    regions = ["euw"] #["br", "eune", "euw", "kr", "lan", "las", "na", "oce", "ru", "tr"]
    
    for region in regions:
        newbase = base + region + "/"
        for path in os.listdir(newbase):
            f = open(newbase + path, 'r')
            data = []
            try:
                data = json.load(f)
            except ValueError:
                pass
            f.close()
            for x in data:
                retrieve(region, str(x))

def main():
    while True:
        findAll()
        time.sleep(600)

main()