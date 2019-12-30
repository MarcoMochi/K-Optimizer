import math

import pandas as pd

dataset = pd.read_csv("./Dataset/BMI.csv")
rangeDb = pd.read_csv("./Dataset/rangeValue.csv")
k = 5
iteration = 0
tupleList = [x for x in range(0,500)]
rangeDict = {}
for row in rangeDb.itertuples(index=True, name='Pandas'):
    rangeDict[getattr(row, "Index")] = getattr(row, "Value")
H = [2, 12, 22]
stopValue = [2, 12, 22, 28]
T = [i for i in rangeDict.keys() if i not in H]
T.remove(0)
T.remove(1)
visited = ([])


def MaxOfSmaller(values, n):
    return max(m for m in values if m < n)

def MinOfGreater(values, n):
    return min(m for m in values if m > n)

def EquivalenceClass(H, equivalenceClassDict, save = True):
    tempEquivalenceClassDict = equivalenceClassDict.copy()
    for v in H:
        key1 = key2 = ""
        if not any(str(v) in i.split(".") for i in tempEquivalenceClassDict.keys()):
            for k in list(tempEquivalenceClassDict.keys()):
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
                    if (secondStep < MaxOfSmaller(stopValue,v) and maxSplit <= MinOfGreater(stopValue, v)) or minSplit == stopValue[0] or secondStep > minSplit:
                        tupleList = tempEquivalenceClassDict[k]
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
    if save:
        return equivalenceClassDict

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

def PruneUselessValue(H, T, eCD):
     for v in T:
         tempList = H + [v]
         temp = EquivalenceClass(tempList, eCD, save=False)
         sizes = [len(v) for v in temp.values()]
         if all(size < k for size in sizes):
             print("Rimuoviamo " + str(v))
             T.remove(v)
     return T

def ComputeCost(equivalenceClassDict):
    cost = 0
    for item in equivalenceClassDict.values():
        if len(item) >= k:
            cost += (len(item))**2
        else:
            cost+= len(item) * len(tupleList)
    return cost

def ReorderTail(H, T, eCD):
    listClassModified = []
    for v in T:
        sumOfPower = 0
        classInduced = 0
        tempList = H + [v]
        temp = EquivalenceClass(tempList, eCD, save=False)
        for item in temp.values():
            classInduced += 1
            sumOfPower += len(item)**2
        listClassModified.append((v, classInduced - len(eCD), sumOfPower))
    listClassModified.sort(key=lambda tup:  tup[2], reverse=False)
    listClassModified.sort(key=lambda tup:  tup[1], reverse=True)
    listClassModified = list(map(lambda x: x[0], listClassModified))
    return listClassModified

def ComputeLBCost(H, T, eCD):
    temp = EquivalenceClass(H + T, eCD, save=False)
    tempH = EquivalenceClass(H, eCD, save=False)
    lbCost = 0
    sizeClass = 0
    for row in tupleList:
        for item in tempH.values():
            if row in item:
                sizeClass = len(item)
                break
        if sizeClass < k:
            lbCost += len(tupleList)
        else:
            for item1 in temp.values():
                if row in item1:
                    sizeClass = len(item1)
                    break
            lbCost += max(sizeClass, k)
    return lbCost

def Prune(H, T, c, eCD):
    global iteration
    print("Iterazione numero :" + str(iteration))
    iteration += 1

    if ComputeLBCost(H,T, eCD) >= c:
        return []
    Tnew = T.copy()
    for v in T:
        newH = H + [v]
        Tnew = T.copy()
        Tnew.remove(v)
        if ComputeLBCost(newH,Tnew, eCD) > c:
            T.remove(v)
    return T

def K_Optimize(H, T, c, eCD):
    T = PruneUselessValue(H, T, eCD)
    c = min(c, ComputeCost(eCD))
    T = Prune(H, T, c, eCD)
    T = ReorderTail(H, T, eCD)
    while T:
        v = T[0]
        newH = H + [v]
        newH.sort()
        if newH not in visited:
            visited.append(newH)
        else:
            print(str(newH) + "Giá visitato")
            continue
        T.remove(v)
        eCD = EquivalenceClass(newH, eCD)
        c = K_Optimize(newH, T, c, eCD.copy())
        T = Prune(H, T, c, eCD)
    print("best anonymization found!")
    print(str(H) + "with cost:" + str(c))
    return c

equivalenceClassDict = {}
equivalenceClassDict["2.12.22"] = tupleList
K_Optimize(H, T, math.inf, equivalenceClassDict.copy())
