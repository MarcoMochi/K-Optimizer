import pandas as pd

dataset = pd.read_csv("./Dataset/BMI.csv")
rangeDb = pd.read_csv("./Dataset/rangeValue.csv")
k = 5
rangeDict = {}
equivalenceClassDict = {}
for row in rangeDb.itertuples(index=True, name='Pandas'):
    rangeDict[getattr(row, "Index")] = getattr(row, "Value")
H = [2, 12, 22]
stopValue = [2, 12, 22, 28]
T = [i for i in rangeDict.keys() if i not in H]
equivalenceClassDict["2.12.22"] = ""

def MaxOfSmaller(values, n):
    return max(m for m in values if m < n)

def MinOfGreater(values, n):
    return min(m for m in values if m > n)

def EquivalenceClass(H, k):
    for v in H:
        key1 = key2 = ""
        if not any(str(v) in i.split(".") for i in equivalenceClassDict.keys()):
            for k in list(equivalenceClassDict.keys()):
                key1 = key2 = ""
                valueSplit = [int(n) for n in k.split(".")]
                minSplit = MaxOfSmaller(valueSplit,v)
                maxSplit = valueSplit[valueSplit.index(minSplit)+1]
                if maxSplit == MinOfGreater(stopValue, v):
                    maxSplit = maxSplit - 1
                if minSplit >= MaxOfSmaller(stopValue, v) and maxSplit < MinOfGreater(stopValue, v):
                    del equivalenceClassDict[k]
                    for m in valueSplit:
                        if m == minSplit:
                            key1 = key1 + str(m) + "."
                            key1 = key1 + str(v) + "."
                            key2 = key2 + str(v) + "."
                        elif m == maxSplit-1:
                            key2 = key2 + str(m) + "."
                        else:
                            key1 = key1 + str(m) + "."
                            key2 = key2 + str(m) + "."
                    key1 = key1[:-1]
                    key2 = key2[:-1]
        if key1 != "":
            equivalenceClassDict[key1] = ""
            equivalenceClassDict[key2] = ""


EquivalenceClass([2,12,15,22], 12)
print(equivalenceClassDict)
