import pandas as pd

dataset = pd.read_csv("./Dataset/BMI.csv")
rangeDb = pd.read_csv("./Dataset/rangeValue.csv")
k = 5
tupleList = [x for x in range(0,500)]
rangeDict = {}
equivalenceClassDict = {}
for row in rangeDb.itertuples(index=True, name='Pandas'):
    rangeDict[getattr(row, "Index")] = getattr(row, "Value")
H = [2, 12, 22]
stopValue = [2, 12, 22, 28]
T = [i for i in rangeDict.keys() if i not in H]
T.remove(0)
equivalenceClassDict["2.12.22"] = tupleList

def MaxOfSmaller(values, n):
    return max(m for m in values if m < n)

def MinOfGreater(values, n):
    return min(m for m in values if m > n)

def EquivalenceClass(H, save = True):
    tempEquivalenceClassDict = equivalenceClassDict.copy()
    for v in H:
        key1 = key2 = ""
        if not any(str(v) in i.split(".") for i in equivalenceClassDict.keys()):
            for k in list(equivalenceClassDict.keys()):
                key1 = key2 = ""
                valueSplit = [int(n) for n in k.split(".")]
                valueSplit.sort()
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
                        tupleList = equivalenceClassDict[k]
                        if save:
                            del equivalenceClassDict[k]
                        else:
                            del tempEquivalenceClassDict[k]
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
                        if key1 != "":
                            columnIndex = stopValue.index(MinOfGreater(stopValue,v))
                            if maxSplit == 0:
                                maxSplit = 28
                            elif maxSplit > MinOfGreater(stopValue, v):
                                maxSplit = MinOfGreater(stopValue, v)
                            if save:
                                equivalenceClassDict[key1] = CreateRange(columnIndex, minSplit, v, tupleList)
                                equivalenceClassDict[key2] = CreateRange(columnIndex, v,maxSplit, tupleList)
                            else:
                                tempEquivalenceClassDict[key1] = CreateRange(columnIndex, minSplit, v, tupleList)
                                tempEquivalenceClassDict[key2] = CreateRange(columnIndex, v,maxSplit, tupleList)
    if not save:
        return tempEquivalenceClassDict

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
         tempList = H + [v]
         temp = EquivalenceClass(tempList, save=False)
         sizes = [len(v) for v in temp.values()]
         print(sizes)
         if all(size < k for size in sizes):
             print("Rimuoviamo " + str(v))
             T.remove(v)
     return T

def ComputeCost():
    cost = 0
    for item in equivalenceClassDict.values():
        if len(item) >= k:
            cost += (len(item))**2
        else:
            cost+= len(item) * len(tupleList)
    return cost

ComputeCost()
EquivalenceClass([2,12,15,22])
ComputeCost()
EquivalenceClass([2,5,12,15,22])
ComputeCost()
# EquivalenceClass([2,12,15,18,22])
# EquivalenceClass([2,12,15,18,22,25])
# EquivalenceClass([2,12,14,15,18,22,25,27])
# EquivalenceClass([2,5,12,15,22])
#PruneUselessValue(H,T)

