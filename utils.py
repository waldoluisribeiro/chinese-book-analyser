# -*- coding: utf-8 -*-

def index_of_first(lst, pred):
    for i, v in enumerate(lst):
        if pred(v):
            return i
    return -1

# def multisort(xs, specs):
#     for key, reverse in reversed(specs):
#         xs.sort(key=operator.attrgetter(key), reverse=reverse)
#     return xs
