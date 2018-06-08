'''
 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
| One day this will be filled with relevant information, but that day isn't today|
 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

from truths import Truths
from copy import deepcopy
import boolean
import random

bl = boolean.BooleanAlgebra()

def sort_key_boolean_exp(boolean_exp):
    return len(boolean_exp), boolean_exp

def shorten(sentence):
    """
    Receives a logical sentence.
    Returns a list with each sub-item contained in a sentence.
    Those items types are found in the boolean.py library.

    Example:
        >>> print(shorten("(not a and b) or (a and b) or (c and d) or (d and c)"))
        ['a', 'b', 'c', 'd', '~a', 'a&b', 'c&d', 'd&c', '~a&b', '(~a&b)|(a&b)|(c&d)|(d&c)']
    """
    if type(sentence) == str:
        sentence = bl.parse(sentence)

    values = set()
    values.add(sentence)
    for i in sentence.args:
        values.add(i)
        if i.iscanonical:
            continue
        else:
            values.update(shorten(i))

    final = []
    values = map(str, values)
    for i in sorted(values, key=sort_key_boolean_exp):  # sort_al(values):
        if i not in final:
            final.append(i)

    return final

def truthtable(sentence):
    """
    Receives either a setence or an list returned by 'shorten'.

    Returns a Truth object which can be used to either get a list representation of truth table
    or a string representation.

    Example:
        >>> x = truthtable('(not a and b) or (a and b)')
        >>> print(x)
        +---+---+----+-----+------+--------------+
        | a | b | ~a | a&b | ~a&b | (~a&b)|(a&b) |
        +---+---+----+-----+------+--------------+
        | 0 | 0 | 1 |  0  |  0   |      0       |
        | 0 | 1 | 1 |  0  |  1   |      1       |
        | 1 | 0 | 0 |  0  |  0   |      0       |
        | 1 | 1 | 0 |  1  |  0   |      1       |
        +---+---+----+-----+------+--------------+
        >>> print(x.table())
        [['a', 'b', '~a', 'a&b', '~a&b', '(~a&b)|(a&b)'], [0, 0, 1, 0, 0, 0], [0, 1, 1, 0, 1, 1], [1, 0, 0, 0, 0, 0], [1, 1, 0, 1, 0, 1]]
    """
    if type(sentence) == str:
        sentence = shorten(sentence)

    x, y = [], []
    for i in sentence:
        if len(i) < 2:
            x.append(i.__str__())
        else:
            y.append(i.__str__())

    return Truths(x, y)

def DNF(sentence):
    """
    Receives either a sentence or the object returned by 'truthtable'.
    Returns the Disjunctive Normal Form of the provided sentence.

    Example:
        >>> DNF('(p and not q) or r')
        [(1, '~p&~q&r'), (3, '~p&q&r'), (4, 'p&~q&~r'), (5, 'p&~q&r'), (7, 'p&q&r')]
        >>> DNF('a and not a')
        []

    If the sentence is always false the function will return False instead of another sentence
    """
    if type(sentence) == str:
        table = truthtable(sentence)
    else:
        table = sentence

    tablelist = table.table()
    parts = []

    for n, row in enumerate(tablelist[1:]):
        if row[-1] == 1:
            temp = []

            for i in range(len(table.base)):
                if row[i] == 0:
                    temp.append('~'+tablelist[0][i])
                else:
                    temp.append(tablelist[0][i])

            part = '&'.join(temp)
            parts.append((n, part))

    try:
        return parts

    except boolean.boolean.ParseError:
        return False

def CNF(sentence):
    """
    Receives either a sentence or the object returned by 'truthtable'.
    Returns the Conjunctive Normal Form of the provided sentence.

    Example:
        >>> CNF('(p and not q) or r')
        [(0, 'p|q|r'), (2, 'p|~q|r'), (6, '~p|~q|r')]
        >>> CNF('not a or a')
        []

    If the sentence is always true the function will return True instead of another sentence
    """
    if type(sentence) == str:
        table = truthtable(sentence)
    else:
        table = sentence


    tablelist = table.table()
    parts = []

    for n, row in enumerate(tablelist[1:]):
        if row[-1] == 0:
            temp = []

            for i in range(len(table.base)):
                if row[i] == 1:
                    temp.append('~'+tablelist[0][i])
                else:
                    temp.append(tablelist[0][i])

            part = '|'.join(temp)
            parts.append((n, part))

    try:
        return parts

    except boolean.boolean.ParseError:
        return True

def generate(nvars, chosen_ones='', size=4, deeper=True):
    '''
    Generates a logical sentence.
    The 'nvars' argument limits the maximum number of variables that will be used.
    '''
    alphabet = 'abcdefghijklmopqrstuvwxyz'
    if chosen_ones == '':
        chosen_ones = random.sample(alphabet, nvars)
    
    if deeper:
        chosen_ones.extend(['~'+i for i in chosen_ones])
    paretheses = 0;

    print(chosen_ones)
    sentence = ''
    for i in range(random.randint(1, size)):
        if random.choice([True, False]) and deeper:
            chosen_ones.append(generate(nvars, chosen_ones, 3, False))           

        if random.choice([True, False]):
            sentence += '~'

        tmp = ''
        for j in range(random.randint(1, size)):
            tmp += random.choice(chosen_ones) + random.choice('|&')
                

        if tmp[-1] in '|&':
            sentence += '(' + tmp[:-1] + ')' + random.choice('|&')
        else:
            sentence += '(' + tmp + ')' + random.choice('|&')

    return(sentence[:-1])

class kmap(object):
    '''
    Creates a Karnaugh Map's object using the provided sentence or truth table.
    >>> kmp = kmap("(not c and not d) or (a and not b and not c) or (a and b and not d)")

    To get a list of lists representing the map, you can do
    >>> kmp.map
    [[0, 0, 0, 0], [1, 0, 0, 0], [1, 1, 1, 1], [0, 1, 0, 0]]

    To get a set with tuples representing each grouping made, you can do
    >>> kmp.groups
    {((2, 0), (1, 0)), ((2, 0), (2, 3), (2, 1), (2, 2)), ((3, 1), (2, 1))}

    '''
    def __init__(self, sentence):
        self.map = self.gen_map(sentence)
        self.groups = self.gen_groups(deepcopy(self.map))

    def gen_map(self, sentence):
        '''
        Returns a list of lists, where each position represents a position in a karnaugh map.
        '''
        if type(sentence) == str:
            table = truthtable(sentence).table()
        else:
            table = sentence.table()

        sols = []
        nvars = len([i for i in table[0] if len(i) < 2])

        for n, line in enumerate(table):
            if line[-1] == 1:
                tp = []

                for i in range(nvars):
                    tp.append(line[i])

                sols.append(tp)

        if nvars == 2:
            mapa = [[0,0],[0,0]]
            for s in sols:
                if s[0] == 1 and s[1] == 1:
                    mapa[0][0] = 1

                elif s[0] == 0 and s[1] == 1:
                    mapa[0][1] = 1

                elif s[0] == 1 and s[1] == 0:
                    mapa[1][0] = 1

                else:
                    mapa[1][1] = 1

            return mapa

        elif nvars == 3:
            mapa = [[0,0,0,0], [0,0,0,0]]

            for s in sols:
                if s[2] == 0:
                    if(s[0] == 1 and s[1] == 1):
                        mapa[1][0] = 1
                    elif(s[0] == 1 and s[1] == 0):
                        mapa[1][1] = 1
                    elif(s[0] == 0 and s[1] == 1):
                        mapa[1][3] = 1
                    else:
                        mapa[1][2] = 1

                else:
                    if(s[0] == 1 and s[1] == 1):
                        mapa[0][0] = 1
                    elif(s[0] == 1 and s[1] == 0):
                        mapa[0][1] = 1
                    elif(s[0] == 0 and s[1] == 1):
                        mapa[0][3] = 1
                    else:
                        mapa[0][2] = 1

            return mapa

        elif nvars == 4:
            mapa = [[0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0]]
            for s in sols:
                if s[2] == 1 and s[3] == 1:
                    if(s[0] == 1 and s[1] == 1):
                        mapa[0][0] = 1
                    elif(s[0] == 1 and s[1] == 0):
                        mapa[0][1] = 1
                    elif(s[0] == 0 and s[1] == 1):
                        mapa[0][3] = 1
                    else:
                        mapa[0][2] = 1

                elif s[2] == 1 and s[3] == 0:
                    if(s[0] == 1 and s[1] == 1):
                        mapa[1][0] = 1
                    elif(s[0] == 1 and s[1] == 0):
                        mapa[1][1] = 1
                    elif(s[0] == 0 and s[1] == 1):
                        mapa[1][3] = 1
                    else:
                        mapa[1][2] = 1

                elif s[2] == 0 and s[3] == 0:
                    if(s[0] == 1 and s[1] == 1):
                        mapa[2][0] = 1
                    elif(s[0] == 1 and s[1] == 0):
                        mapa[2][1] = 1
                    elif(s[0] == 0 and s[1] == 1):
                        mapa[2][3] = 1
                    else:
                        mapa[2][2] = 1

                else:
                    if(s[0] == 1 and s[1] == 1):
                        mapa[3][0] = 1
                    elif(s[0] == 1 and s[1] == 0):
                        mapa[3][1] = 1
                    elif(s[0] == 0 and s[1] == 1):
                        mapa[3][3] = 1
                    else:
                        mapa[3][2] = 1

            return mapa

        else:
            return []

    def gen_groups(self, mapa):
        '''
        Returns a set of tuples, where each tuple represents a possible grouping in the map.
        '''
        patterns = [[3, 3], [3, 1], [1, 3], [3, 0], [0, 3], [-1, -1], [0, -1], [-1, 0], [0, 0]]
        pairs = set()

        for p in patterns:

            cells = set() # Stores the coordinates of each cell that can be grouped by this kind of pattern
            while True:
                pgroups = set() # Where every valid group of this pattern will be stored before being selected for the final set (pairs).

                # Iterates over the X-axis of the map
                for n, x in enumerate(mapa):
                    if p[0] < 0:
                        xi = p[0]
                        xf = 0
                    else:
                        xi = 0
                        xf = p[0]

                    # Iterates over the Y-axis of the map
                    for m, y in enumerate(x):
                        f = 0
                        if p[1] < 0:
                            yi = p[1]
                            yf = 0
                        else:
                            yi = 0
                            yf = p[1]

                        cells_tmp = set() # Temporarily stores coordinates of each cell that may be used in groups of this pattern
                        group_tmp = [] # Temporarily stores coordinates of each cell that will be part of the final group
                        weight = 0 # Weight that will be attributed to the current group
                        anterior = deepcopy(mapa) # Safety measure in case this group isn't valid


                        for i in range(xi, xf+1):
                            for j in range(yi, yf+1):

                                # Evaluates a cell and adds them to the temporary cells_tmp and group_tmp
                                if n+i < len(mapa) and m+j < len(x) and (mapa[n+i][m+j] == 1 or mapa[n+i][m+j] == 2):
                                    if mapa[n+i][m+j] == 1: # Only cells unique to a group are important to its evaluation
                                        weight += 1

                                    if n+i == -1 and m+j != -1:
                                        cells_tmp.add((len(mapa)-1, m+j))
                                        group_tmp.append((len(mapa)-1, m+j))
                                    elif n+i != -1 and m+j == -1:
                                        cells_tmp.add((n+i, len(x)-1))
                                        group_tmp.append((n+i, len(x)-1))
                                    elif n+i == -1 and m+j == -1:
                                        cells_tmp.add((len(mapa)-1, len(x)-1))
                                        group_tmp.append((len(mapa)-1, len(x)-1))
                                    else:
                                        cells_tmp.add((n+i, m+j))
                                        group_tmp.append((n+i, m+j))

                                    continue

                                elif n+i < len(mapa) and m+j < len(x) and mapa[n+i][m+j] == 2:
                                    continue

                                else:
                                    mapa = deepcopy(anterior) # Activates the safety measure
                                    f = 1
                                    break

                            if f == 1:
                                break

                        if f == 1:
                            continue

                        if len(group_tmp) == 0:
                            continue

                        group_tmp.sort()
                        if group_tmp in list(pairs):
                            continue

                        if weight > 0: # Groups where there are no unique cells inside it are not useful.
                            cells.update(cells_tmp) # If a group is valid, its cells are going to be added to the pool of cells that can be grouped with this pattern
                            pgroups.add((tuple(group_tmp), weight)) # If the group is valid, then it's going to be added to the set of possible group choices



                if len(pgroups) == 0:
                    break


                pgroups = sorted(list(pgroups), key=lambda x: x[1], reverse=True)
                best = set(pgroups[0][0]) # Best group defined by weight
                pgroups.remove(pgroups[0])
                cells = cells-best # Removing the cells already grouped by the best group

                for tp in best:
                    mapa[tp[0]][tp[1]] = 2

                if len(cells) == 0:
                    pairs.add(tuple(best))
                    break




                pairs.add(tuple(best))
                pgroups = set(pgroups)

        return pairs


if __name__ == "__main__":
    import doctest
    doctest.testmod()
