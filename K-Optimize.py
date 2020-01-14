import math

import pandas as pd

dataset = pd.read_csv("./Dataset/BMI.csv")
rangeDb = pd.read_csv("./Dataset/rangeValue.csv")
k = 5
sup = math.inf
iteration = 0
tupleList = [x for x in range(0,500)]
rangeDict = {}
for row in rangeDb.itertuples(index=True, name='Pandas'):
    rangeDict[getattr(row, "Index")] = getattr(row, "Value")
H = [0, 2, 12, 22]
stopValue = [0, 2, 12, 22, 28]
T = [i for i in rangeDict.keys() if i not in H]
T.remove(28)
bestCost = []
savedClass = {}

def MaxOfSmaller(values, n):
    """ Takes an array values and a value n, it gives the biggest number smaller than n """
    return max(m for m in values if m < n)
def MinOfGreater(values, n):
    """ Takes an array values and a value n, it gives the biggest number smaller than n """
    return min(m for m in values if m > n)

def EquivalenceClass(H, equivalenceClassDict, save = True):
    """ Takes a list of range value H, a dictionary with the eq. classes and a parameter to save or not.
        This function create the newly splitted classes
    """
    tempEquivalenceClassDict = equivalenceClassDict.copy()
    for v in H:
        key1 = key2 = ""
        if not any(str(v) in i.split(".") for i in tempEquivalenceClassDict.keys()): # check if a value is new for this H
           for k in list(tempEquivalenceClassDict.keys()):
                key1 = key2 = ""
                valueSplit = [int(n) for n in k.split(".")]
                valueSplit.sort()
                if v < valueSplit[0]:
                    continue
                else:
                    minSplit = MaxOfSmaller(valueSplit,v) # Get the first number smaller than v
                try:
                    maxSplit = valueSplit[valueSplit.index(minSplit)+1] # Get the first number bigger than v
                except:
                    maxSplit = 0
                if minSplit >= MaxOfSmaller(stopValue, v):
                    secondStep = valueSplit[valueSplit.index(minSplit)-1]
                    if secondStep < MaxOfSmaller(stopValue,v) or secondStep > minSplit: # Check if it split the class in two new class.
                        tupleList = tempEquivalenceClassDict[k]
                        if save:
                            del equivalenceClassDict[k]
                        else:
                            del tempEquivalenceClassDict[k]
                        for m in valueSplit:    # Create the name of the two new class
                            if m == minSplit:
                                key1 = key1 + str(m) + "."
                                key1 = key1 + str(v) + "."
                                key2 = key2 + str(v) + "."
                            elif m == maxSplit:
                                key2 = key2 + str(m) + "."
                                if m != 0 and m >= MinOfGreater(stopValue, v):
                                    key1 = key1 + str(m) + "."
                            else:
                                key1 = key1 + str(m) + "."
                                key2 = key2 + str(m) + "."
                        key1 = key1[:-1]
                        key2 = key2[:-1]
                        if key1 != "":
                            columnIndex = stopValue.index(MinOfGreater(stopValue,v)) - 1
                            if maxSplit == 0:
                                maxSplit = stopValue[-1]
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
    """ Takes a column index that is the number corresponding to the feature that it's splitting
        Start and End are the value range used to create the new eq class.
        tupleList is the array of tuples it has to check
        Return the tuples of this new class
    """
    tempList = []
    startRange = int(rangeDb.iloc[start, 1])
    if end in stopValue:
        for index in tupleList:
            checkValue = int(dataset.iloc[index, columnIndex])
            if checkValue >= startRange:
                tempList.append(index)
    else:
        endRange = int(rangeDb.iloc[end, 1])
        for index in tupleList:
            checkValue = int(dataset.iloc[index, columnIndex])
            if checkValue >= startRange and checkValue < endRange:
                tempList.append(index)
    return tempList

def PruneUselessValue(H, T, eCD):
    """ Delete all the values of T that create all eq. classes that are smaller than k """
    for v in T:
         tempList = H + [v]
         temp = EquivalenceClass(tempList, eCD, save=False)
         sizes = [len(v) for v in temp.values()]
         if all(size < k for size in sizes):
             print("Rimuoviamo " + str(v))
             T.remove(v)
    return T

def ComputeCost(equivalenceClassDict):
    """ Compute the cost given a dictionary of eq. classes"""
    cost = 0
    for item in equivalenceClassDict.values():
        if len(item) >= k:
            cost += (len(item))**2
        else:
            cost+= len(item) * len(tupleList)
    return cost

def ReorderTail(H, T, eCD):
    """ Reorder the values inside of T according to the number of eq. classes splitted and the size of the new classes """
    listClassModified = []
    for v in T:
        sumOfPower = 0
        classInduced = 0
        tempList = H + [v]
        try:
            temp = savedClass[str(tempList)]
        except:
            temp = EquivalenceClass(tempList, eCD, save=False)
        for item in temp.values():
            classInduced += 1
            sumOfPower += len(item)**2
        listClassModified.append((v, classInduced - len(eCD), sumOfPower)) # append a tuple with v, # of classes splitted and their dimension
    listClassModified.sort(key=lambda tup:  tup[2], reverse=False) # Order by sumOfPower
    listClassModified.sort(key=lambda tup:  tup[1], reverse=True)  # Order by # of classes splitted
    listClassModified = list(map(lambda x: x[0], listClassModified))
    return listClassModified

def ComputeLBCost(H, T, eCD):
    """ Compute the Lower Bound cost of a H node with a T tail"""
    tempList = H+T
    tempList.sort()
    H.sort()
    try:
        savedClass[str(tempList)]
    except:
        temp = EquivalenceClass(H + T, eCD, save=False)
        savedClass[str(tempList)] = temp.copy()
    try:
        savedClass[str(H)]
    except:
        tempH = EquivalenceClass(H, eCD, save=False)
        savedClass[str(H)] = tempH.copy()
    lbCost = 0
    sizeClass = 0
    for row in tupleList:
        for item in savedClass[str(H)].values():
            if row in item:
                sizeClass = len(item)
                break
        if sizeClass < k:
            lbCost += len(tupleList)
        else:
            for item1 in savedClass[str(tempList)].values():
                if row in item1:
                    sizeClass = len(item1)
                    break
            lbCost += max(sizeClass, k)
    return lbCost

def Prune(H, T, c, eCD):
    """ Try to delete a node with H and T. if it can't it will try to delete values from T.
        After deleting a value from T it retry to delete H
    """
    if check == 1 and ComputeLBCost(H,T, eCD) >= c:
        return []
    for v in T:
        newH = H + [v]
        Tnew = T.copy()
        Tnew.remove(v)
        if ComputeLBCost(newH,Tnew, eCD) >= c:
            T.remove(v)
            if ComputeLBCost(H, T, eCD) >= c:
                return []
        else:
            if Suppression(savedClass[str(newH)]) > sup:
                T.remove(v)

    return T

def Suppression(eCD):
    tot = 0
    tot = sum([len(item) for item in eCD.values() if len(item) < k])
    return tot

def AnonymizeDataset(eCD):
    final = []

    for key in eCD.keys():
        keySplit = [int(n) for n in key.split(".")]
        temp = []
        while keySplit:
            a = keySplit.pop(0)
            a_value = int(rangeDb.iloc[a, 1])
            try:
                keySplit[0]
                if keySplit[0] < MinOfGreater(stopValue, a):
                    b = keySplit.pop(0)
                    b_value = int(rangeDb.iloc[b, 1])
                    temp.append(str(a_value) + "-" + str(b_value))
                else:
                    temp.append(str(a_value) + "->")
            except:
                temp.append(str(a_value) + "->")
        for i in range(len(eCD[key])):
            final.append(temp)

    finalDb = pd.DataFrame(final, columns=['Gender', 'Height', 'Weight', 'Index'])
    return finalDb

def K_Optimize(H, T, c, eCD):
    global iteration
    print("Iterazione numero :" + str(iteration))
    iteration += 1
    T = PruneUselessValue(H, T, eCD)
    c = min(c, ComputeCost(eCD))
    if c < bestCost[0][1]:
        global check
        check = 1
        bestCost.clear()
        bestCost.append((H, c,  eCD.copy()))
        print("best anonymization found!")
        print(str(H) + "with cost:" + str(c) + " iteration:" + str(iteration))
    T = Prune(H, T, c, eCD)
    T = ReorderTail(H, T, eCD)
    while T:
        v = T[0]
        newH = H + [v]
        newH.sort()
        T.remove(v)
        try:
            savedClass[str(newH)]
        except:
            savedClass[str(newH)] = EquivalenceClass(newH, savedClass[str(H)]).copy()
        c = K_Optimize(newH, T, c, savedClass[str(newH)])
        T = Prune(H, T, c, savedClass[str(newH)])
    return c


equivalenceClassDict = {}
equivalenceClassDict["0.2.12.22"] = tupleList
k = input("Inserisci il valore di k:\n")
k = int(k)
sup = input("Inserisci il numero massimo di soppressioni permesse, -1 per non avere limiti:\n")
sup = int(sup)
seed = input("Inserisci un valore di seed, 0 per non inserirne:\n")
seed = int(seed)
path = input("Inserisci il nome del file in cui vuoi stampare il risultato, 0 per non salvare il file:\n")
path = str(path)
check = 0
if seed == 0:
    seed = math.inf
    check = 1
if sup == -1:
    sup = math.inf
bestCost.append((H, seed))
K_Optimize(H, T, seed, equivalenceClassDict.copy())
final = AnonymizeDataset(bestCost[0][2])
if path == "0":
    print(final)
else:
    final.to_csv(path_or_buf=("./" + str(path)))
