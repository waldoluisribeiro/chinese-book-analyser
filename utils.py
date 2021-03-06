# -*- coding: utf-8 -*-

# Copyright © 2021 Waldo Luis Ribeiro
# Released under the terms of the GNU General Public Licence, version 3
# <http://www.gnu.org/licenses/>

__license__ = 'GPL v3'
__author__ = 'Waldo Luis Ribeiro'


def index_of_first(lst, pred):
    for i, v in enumerate(lst):
        if pred(v):
            return i
    return -1

# def multisort(xs, specs):
#     for key, reverse in reversed(specs):
#         xs.sort(key=operator.attrgetter(key), reverse=reverse)
#     return xs
