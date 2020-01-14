import math

import pandas as pd

dataset = pd.read_csv("./Dataset/BMI.csv")
rangeDb = pd.read_csv("./Dataset/rangeValue.csv")
k = 5
sup = math.inf
iteration = 0
tupleList = [x for x in range(0, 500)]
rangeDict = {}
for row in rangeDb.itertuples(index=True, name='Pandas'):
    rangeDict[getattr(row, "Index")] = getattr(row, "Value")
H = [0, 2, 12, 22]
stopValue = [0, 2, 12, 22, 28]
T = [i for i in rangeDict.keys() if i not in H]
T.remove(28)
bestCost = []
savedClass = {}


def max_of_smaller(values, n):
    """ Takes an array values and a value n, it gives the biggest number smaller than n """
    return max(m for m in values if m < n)


def min_of_greater(values, n):
    """ Takes an array values and a value n, it gives the biggest number smaller than n """
    return min(m for m in values if m > n)


def create_equivalence_class(h, equivalence_class, save=True):
    """ Takes a list of range value H, a dictionary with the eq. classes and a parameter to save or not.
        This function create the newly splitted classes
    """
    temp_equivalence_class = equivalence_class.copy()
    for v in h:
        if not any(str(v) in i.split(".") for i in temp_equivalence_class.keys()):  # check if a value is new for this H
            for k in list(temp_equivalence_class.keys()):
                key1 = key2 = ""
                value_split = [int(n) for n in k.split(".")]
                value_split.sort()

                # Check if the number insepcted will split the current eq. class
                if v < value_split[0]:
                    continue
                else:
                    min_split = max_of_smaller(value_split, v)  # Get the first number smaller than v
                try:
                    max_split = value_split[value_split.index(min_split) + 1]  # Get the first number bigger than v
                except:
                    max_split = 0
                if min_split >= max_of_smaller(stopValue, v):
                    second_step = value_split[value_split.index(min_split) - 1]
                    if second_step < max_of_smaller(stopValue, v) or second_step > min_split:

                        # Since it splits the class we delete the current eq class and create the two new classes
                        tuple_list = temp_equivalence_class[k]
                        if save:
                            del equivalence_class[k]
                        else:
                            del temp_equivalence_class[k]

                        # Create the name of the two new class
                        for m in value_split:
                            if m == min_split:
                                key1 = key1 + str(m) + "."
                                key1 = key1 + str(v) + "."
                                key2 = key2 + str(v) + "."
                            elif m == max_split:
                                key2 = key2 + str(m) + "."
                                if m != 0 and m >= min_of_greater(stopValue, v):
                                    key1 = key1 + str(m) + "."
                            else:
                                key1 = key1 + str(m) + "."
                                key2 = key2 + str(m) + "."
                        key1 = key1[:-1]
                        key2 = key2[:-1]
                        if key1 != "":
                            column_index = stopValue.index(min_of_greater(stopValue, v)) - 1
                            if max_split == 0:
                                max_split = stopValue[-1]
                            elif max_split > min_of_greater(stopValue, v):
                                max_split = min_of_greater(stopValue, v)
                            if save:
                                equivalence_class[key1] = create_range(column_index, min_split, v, tuple_list)
                                equivalence_class[key2] = create_range(column_index, v, max_split, tuple_list)
                            else:
                                temp_equivalence_class[key1] = create_range(column_index, min_split, v, tuple_list)
                                temp_equivalence_class[key2] = create_range(column_index, v, max_split, tuple_list)
    if not save:
        return temp_equivalence_class
    if save:
        return equivalence_class


def create_range(column, start, end, tuples):
    """ Takes a column index that is the number corresponding to the feature that it's splitting
        Start and End are the value range used to create the new eq class.
        tupleList is the array of tuples it has to check
        Return the tuples of this new class
    """
    temp_list = []
    start_range = int(rangeDb.iloc[start, 1])
    if end in stopValue:
        for index in tuples:
            check_value = int(dataset.iloc[index, column])
            if check_value >= start_range:
                temp_list.append(index)
    else:
        end_range = int(rangeDb.iloc[end, 1])
        for index in tuples:
            check_value = int(dataset.iloc[index, column])
            if check_value >= start_range and check_value < end_range:
                temp_list.append(index)
    return temp_list


def prune_useless_value(h, t, eCD):
    """ Delete all the values of T that create all eq. classes that are smaller than k """
    for v in t:
        tempList = h + [v]
        temp = create_equivalence_class(tempList, eCD, save=False)
        sizes = [len(v) for v in temp.values()]
        if all(size < k for size in sizes):
            print("Removing " + str(v))
            t.remove(v)
    return t


def compute_cost(equivalence_class):
    """ Compute the cost given a dictionary of eq. classes"""
    cost = 0
    for item in equivalence_class.values():
        if len(item) >= k:
            cost += (len(item)) ** 2
        else:
            cost += len(item) * len(tupleList)
    return cost


def reorder_tail(h, t, eCD):
    """ Reorder the values inside of T according to the number of eq. classes splitted and the size of the new classes """
    list_class_modified = []
    for v in t:
        sum_of_power = 0
        class_induced = 0
        temp_list = h + [v]
        try:
            temp = savedClass[str(temp_list)]
        except:
            temp = create_equivalence_class(temp_list, eCD, save=False)
        for item in temp.values():
            class_induced += 1
            sum_of_power += len(item) ** 2
        list_class_modified.append((v, class_induced - len(eCD),
                                    sum_of_power))  # append a tuple with v, # of classes split and their dimension
    list_class_modified.sort(key=lambda tup: tup[2], reverse=False)  # Order by sumOfPower
    list_class_modified.sort(key=lambda tup: tup[1], reverse=True)  # Order by # of classes split
    list_class_modified = list(map(lambda x: x[0], list_class_modified))
    return list_class_modified


def compute_LB_cost(h, t, eCD):
    """ Compute the Lower Bound cost of a H node with a T tail"""
    temp_list = h + t
    temp_list.sort()
    h.sort()
    try:
        savedClass[str(temp_list)]
    except:
        temp = create_equivalence_class(h + t, eCD, save=False)
        savedClass[str(temp_list)] = temp.copy()
    try:
        savedClass[str(h)]
    except:
        temp_h = create_equivalence_class(h, eCD, save=False)
        savedClass[str(h)] = temp_h.copy()
    lb_cost = 0
    size_class = 0
    for temp_tuple in tupleList:
        for item in savedClass[str(h)].values():
            if temp_tuple in item:
                size_class = len(item)
                break
        if size_class < k:
            lb_cost += len(tupleList)
        else:
            for item1 in savedClass[str(temp_list)].values():
                if temp_tuple in item1:
                    size_class = len(item1)
                    break
            lb_cost += max(size_class, k)
    return lb_cost


def prune(h, t, c, eCD):
    """ Try to delete a node with H and T. if it can't it will try to delete values from T.
        After deleting a value from T it retry to delete H
    """
    if compute_LB_cost(h, t, eCD) > c:
        return []
    for v in t:
        h_new = h + [v]
        t_new = t.copy()
        t_new.remove(v)
        if compute_LB_cost(h_new, t_new, eCD) >= c:
            t.remove(v)
            if compute_LB_cost(h, t, eCD) >= c:
                return []
        else:
            if suppression(savedClass[str(h_new)]) > sup:
                t.remove(v)
    return t


def suppression(eCD):
    tot = sum([len(item) for item in eCD.values() if len(item) < k])
    return tot


def anonymize_dataset(eCD):
    anonymize_list = []
    for key in eCD.keys():
        key_split = [int(n) for n in key.split(".")]
        temp = []
        while key_split:
            a = key_split.pop(0)
            a_value = int(rangeDb.iloc[a, 1])
            try:
                if key_split[0] < min_of_greater(stopValue, a):
                    b = key_split.pop(0)
                    b_value = int(rangeDb.iloc[b, 1])
                    temp.append(str(a_value) + "-" + str(b_value))
                else:
                    temp.append(str(a_value) + "->")
            except:
                temp.append(str(a_value) + "->")
        for i in range(len(eCD[key])):
            anonymize_list.append(temp)

    anonymize_db = pd.DataFrame(anonymize_list, columns=['Gender', 'Height', 'Weight', 'Index'])
    return anonymize_db


def k_optimize(h, t, c, eCD):
    global iteration
    print("Iterazione numero :" + str(iteration))
    iteration += 1
    t = prune_useless_value(h, t, eCD)
    c = min(c, compute_cost(eCD))
    if c < bestCost[0][1]:
        bestCost.clear()
        bestCost.append((h, c, eCD.copy()))
        print("best anonymization found!")
        print(str(h) + "with cost:" + str(c) + " iteration:" + str(iteration))
    t = prune(h, t, c, eCD)
    t = reorder_tail(h, t, eCD)
    while t:
        v = t[0]
        newH = h + [v]
        newH.sort()
        t.remove(v)
        try:
            savedClass[str(newH)]
        except:
            savedClass[str(newH)] = create_equivalence_class(newH, savedClass[str(h)]).copy()
        c = k_optimize(newH, t, c, savedClass[str(newH)])
        t = prune(h, t, c, savedClass[str(newH)])
    return c


equivalence_class_dict = {"0.2.12.22": tupleList}
k = input("Inserisci il valore di k:\n")
k = int(k)
sup = input("Inserisci il numero massimo di soppressioni permesse, -1 per non avere limiti:\n")
sup = int(sup)
path = input("Inserisci il nome del file in cui vuoi stampare il risultato, 0 per non salvare il file:\n")
path = str(path)
check = 0
if sup == -1:
    sup = math.inf
bestCost.append((H, math.inf))
k_optimize(H, T, math.inf, equivalence_class_dict.copy())
final = anonymize_dataset(bestCost[0][2])
if path == "0":
    print(final)
else:
    final.to_csv(path_or_buf=("./" + str(path)))
