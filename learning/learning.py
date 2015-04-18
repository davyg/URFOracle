from __future__ import print_function

from pybrain.datasets            import ClassificationDataSet
from pybrain.utilities           import percentError
from pybrain.tools.shortcuts     import buildNetwork
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.structure.modules   import SoftmaxLayer
from pybrain.structure           import TanhLayer
from pybrain.tools.xml.networkwriter import NetworkWriter
from pybrain.tools.xml.networkreader import NetworkReader
import os
import json
import time
import pickle



REALINPUTS = [lambda data: float(data['matchCreation'] % (3600 * 24))/(3600 * 24)]
INPUTS = REALINPUTS[:]
for i in range(10):
    def closure(x):
        INPUTS.append(lambda data:data['participants'][x]['championId'])
        INPUTS.append(lambda data:data['participants'][x]['spell1Id'])
        INPUTS.append(lambda data:data['participants'][x]['spell2Id'])
    closure(i)

OUTPUTS = lambda data: data['teams'][0]['winner']

def getData(region, nbr):
    base = "../getMatch/" + region + "/"
    matchs = list(os.listdir(base))
    matchs = matchs[:nbr]
    datas = []
    i = 0
    for match in matchs:
        t = time.time()
        f = open(base + match, 'r')
        try:
            data = json.load(f)
        except ValueError:
            pass
        inputs = []
        for inp in INPUTS:
            inputs.append(inp(data))
        datas.append((inputs, OUTPUTS(data)))
        print("Parsing input : {:3}%".format((100 * i) / nbr), end="\r")
        i += 1
    return datas

BASE = 37000
FINALTEST = 1000

datas = getData('euw', BASE + FINALTEST)
print()

labels = []
sizeInputs = 0
for i in range(len(INPUTS)):
    labels.append({})

for d in datas:
    i = 0
    for x in d[0]:
        if i >= len(REALINPUTS) and not x in labels[i]:
            labels[i][x] = sizeInputs
            sizeInputs += 1
        i += 1
print("Labels extracted")

alldata = ClassificationDataSet(len(REALINPUTS) + sizeInputs, nb_classes=2, class_labels=['Team1','Team2'])

transformedData = []

for d in datas:
    inp = [0]*(len(REALINPUTS) + sizeInputs)
    i = 0
    for x in d[0]:
        if i >= len(REALINPUTS):
            inp[labels[i][x]] = 1
        else:
            inp[i] = x
        i += 1
    transformedData.append((inp, d[1]))
print("Data transformed")

for d in transformedData[:BASE]:
    alldata.addSample(d[0], 1 if d[1] else 0)
print("Dataset created")

test = transformedData[BASE:]

tstdata, trndata = alldata.splitWithProportion( 0.1 )

trndata._convertToOneOfMany( )
tstdata._convertToOneOfMany( )

fnn = buildNetwork( trndata.indim, 40, trndata.outdim, hiddenclass=TanhLayer, outclass=SoftmaxLayer )
trainer = BackpropTrainer(fnn, dataset=trndata, momentum=0.1, verbose=True, weightdecay=0.01)

trainer.trainUntilConvergence(maxEpochs=1000, verbose=True)

"""for i in range(100):
    trainer.trainEpochs(1)"""

trnresult = percentError( trainer.testOnClassData(),
                              trndata['class'] )
tstresult = percentError( trainer.testOnClassData(
       dataset=tstdata ), tstdata['class'] )
    
print("epoch: %4d" % trainer.totalepochs, \
      "  train error: %5.2f%%" % trnresult, \
      "  test error: %5.2f%%" % tstresult)
NetworkWriter.writeToFile(fnn, 'network.xml')

good = 0
for t in test:
    if (fnn.activate(t[0])[0] > fnn.activate(t[0])[1]) == t[1]:
        good += 1

print(float(good)/len(test))

fileObject = open('network', 'w')

pickle.dump((fnn, labels), fileObject)

fileObject.close()
