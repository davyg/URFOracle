import urllib2
import os
import time
import datetime

def getReadableTime(s):
    t = datetime.datetime.fromtimestamp(s)
    fmt = "%Y-%m-%d %H:%M:%S"
    return t.strftime(fmt)

def get(region, start):
    key = "INSERT KEY"
    url = "https://euw.api.pvp.net/api/lol/{region}/v4.1/game/ids?beginDate={start}&api_key={key}".format(region=region, start=start, key=key)
    print("    -> get " + url)
    data = urllib2.urlopen(url).read()
    time.sleep(1)
    return data

def retrieve(region, start):
    print("try " + region + " " + str(start) + " (" + getReadableTime(start) + ")")
    pathname = region + "/" + str(start) + ".js"
    if not os.path.exists(region):
        os.mkdir(region)
    if os.path.exists(pathname):
        print("    -> already done")
        return
    print("    -> not done")
    try:
        data = get(region, start)
    except urllib2.HTTPError as e:
        print("    -> http error :" + str(e.read()))
        return
    f=open(pathname, 'w')
    f.write(data)
    f.close()
    print("    -> done")

def findAll():
    regions = ["euw"] #["br", "eune", "euw", "kr", "lan", "las", "na", "oce", "ru", "tr"]
    current = int(time.time() / 300) * 300 - 600
    start = current - 8 * 3600
    time.sleep(10)
    todo = start
    while todo <= current:
        for region in regions:
            retrieve(region, todo)
        todo += 300

def main():
    while True:
        findAll()
        time.sleep(300)

main()