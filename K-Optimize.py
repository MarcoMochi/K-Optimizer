import pandas as pd

dataset = pd.read_csv("./Dataset/BMI.csv")
rangeDb = pd.read_csv("./Dataset/rangeValue.csv")
k = 5
tupleList = [x for x in range(0,500)]
rangeDict = {}
equivalenceClassDict = {}
tempEquivalenceClassDict = {}
for row in rangeDb.itertuples(index=True, name='Pandas'):
    rangeDict[getattr(row, "Index")] = getattr(row, "Value")
H = [2, 12, 22]
stopValue = [2, 12, 22, 28]
T = [i for i in rangeDict.keys() if i not in H]
equivalenceClassDict["2.12.22"] = tupleList

def MaxOfSmaller(values, n):
    return max(m for m in values if m < n)

def MinOfGreater(values, n):
    return min(m for m in values if m > n)

def EquivalenceClass(H, save = True):
    tempEquivalenceClassDict = equivalenceClassDict
    for v in H:
        key1 = key2 = ""
        if not any(str(v) in i.split(".") for i in equivalenceClassDict.keys()):
            for k in list(equivalenceClassDict.keys()):
                key1 = key2 = ""
                valueSplit = [int(n) for n in k.split(".")]
                if v < valueSplit[0]:
                    continue
                else:
                    minSplit = MaxOfSmaller(valueSplit,v)
                try:
                    maxSplit = valueSplit[valueSplit.index(minSplit)+1]
                except:
                    maxSplit = 0
                if minSplit >= MaxOfSmaller(stopValue, v):
                    secondStep = valueSplit[valueSplit.index(minSplit)-1]
                    if (secondStep < MaxOfSmaller(stopValue,v) and maxSplit <= MinOfGreater(stopValue, v)) or minSplit == stopValue[0]:
                        if save:
                            tupleList = equivalenceClassDict[k]
                            del equivalenceClassDict[k]
                        for m in valueSplit:
                            if m == minSplit:
                                key1 = key1 + str(m) + "."
                                key1 = key1 + str(v) + "."
                                key2 = key2 + str(v) + "."
                            elif m == maxSplit:
                                key2 = key2 + str(m) + "."
                                if m >= MinOfGreater(stopValue, v):
                                    key1 = key1 + str(m) + "."
                            else:
                                key1 = key1 + str(m) + "."
                                key2 = key2 + str(m) + "."
                        key1 = key1[:-1]
                        key2 = key2[:-1]
                        if key1 != "" and save:
                            columnIndex = stopValue.index(MinOfGreater(stopValue,v))
                            if maxSplit == 0:
                                maxSplit = 28
                            elif maxSplit > MinOfGreater(stopValue, v):
                                maxSplit = MinOfGreater(stopValue, v)
                            equivalenceClassDict[key1] = CreateRange(columnIndex, minSplit, v, tupleList)
                            equivalenceClassDict[key2] = CreateRange(columnIndex, v,maxSplit, tupleList)
                        elif not save:
                            tempEquivalenceClassDict[key1] = ""
                            tempEquivalenceClassDict[key2] = ""

def CreateRange(columnIndex, start, end, tupleList):
    tempList = []
    startRange = int(rangeDb.iloc[start-1, 1])
    if end in stopValue:
        for index in tupleList:
            checkValue = int(dataset.iloc[index, columnIndex])
            if checkValue >= startRange:
                tempList.append(index)
    else:
        endRange = int(rangeDb.iloc[end-1, 1])
        for index in tupleList:
            checkValue = int(dataset.iloc[index, columnIndex])
            if checkValue >= startRange and checkValue < endRange:
                tempList.append(index)
    return tempList

def PruneUselessValue(H, T):
     for v in T:
         tempList = H + v
         EquivalenceClass(H, save=False)
         sizes = [len(v) for v in tempEquivalenceClassDict.values()]
         if all(sizes < k):
             T.remove(v)

EquivalenceClass([2,12,15,22])
EquivalenceClass([2,12,15,18,22])
EquivalenceClass([2,12,15,18,22,25])
EquivalenceClass([2,12,14,15,18,22,25,27])
EquivalenceClass([2,5,12,15,22])

print(equivalenceClassDict)
for item in equivalenceClassDict:
    print(len(equivalenceClassDict[item]))
