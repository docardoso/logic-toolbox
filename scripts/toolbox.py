from truths import Truths
import boolean
import random

bl = boolean.BooleanAlgebra()

def shorten(sentence):
    """
    Receives a logical sentence.
    Returns a list with each sub-item contained in a sentence. 
    Those items types are found in the boolean.py library.

    Example:
        >>> print(shorten((not a and b) or (a and b)))
        [Symbol('b'), Symbol('a'), NOT(Symbol('a')), AND(Symbol('a'), Symbol('b')), AND(NOT(Symbol('a')), Symbol('b')), OR(AND(NOT(Symbol('a')), Symbol('b')), AND(Symbol('a'), Symbol('b')))]
    """
    if type(sentence) == str:
        sentence = bl.parse(sentence)

    final = set()
    final.add(sentence)
    for i in sentence.args:
        final.add(i)
        if i.iscanonical:
            continue
        else:    
            final.update(shorten(i))
    return sorted(final, key=lambda x: len(x.__str__()))


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
        >>> print(x.table)
        [['b', 'a', '~a', 'a&b', '~a&b', '(~a&b)|(a&b)'], [0, 0, 1, 0, 0, 0], 
        [0, 1, 0, 0, 0, 0], [1, 0, 1, 0, 1, 1], [1, 1, 0, 1, 0, 1]]
    """
    if type(sentence) == str:
        sentence = shorten(sentence)

    x, y = [], []
    for i in sentence:
        if i.iscanonical:
            x.append(i.__str__())
        else:
            y.append(i.__str__())
    
    return Truths(x, y)

# Erros quando a sentença nunca é verdadeira
def DNF(sentence):
    """
    Receives either a sentence or the object returned by 'truthtable'.
    Returns the Disjunctive Normal Form of the provided sentence.

    Example:
        >>> DNF('(p and not q) or r')
        (~p&~q&r)|(~p&q&r)|(p&~q&~r)|(p&~q&r)|(p&q&r)

    -> If the sentence is always false the function will return False instead of another sentence
    """
    if type(sentence) == str:
        table = truthtable(sentence)
    else:
        table = sentence

    tablelist = table.table()
    parts = []
    
    for row in tablelist[1:]:
        if row[-1] == 1:
            temp = []

            for i in range(len(table.base)):
                if row[i] == 0:
                    temp.append('~'+tablelist[0][i])
                else:
                    temp.append(tablelist[0][i])
            
            part = '&'.join(temp)
            parts.append('(' + part + ')')
    try:
        dnf = bl.parse('|'.join(parts))
        return dnf

    except boolean.boolean.ParseError:
        return False

# Errors quando a sentença sempre é verdadeira
def CNF(sentence):
    """
    Receives either a sentence or the object returned by 'truthtable'.
    Returns the Conjunctive Normal Form of the provided sentence.

    Example:
        >>> CNF('(p and not q) or r')
        (r|q|p)&(r|~q|p)&(r|~q|~p)

    -> If the sentence is always true the function will return True instead of another sentence
    """
    if type(sentence) == str:
        table = truthtable(sentence)
    else:
        table = sentence


    tablelist = table.table()
    parts = []
    
    for row in tablelist[1:]:
        if row[-1] == 0:
            temp = []

            for i in range(len(table.base)):
                if row[i] == 1:
                    temp.append('~'+tablelist[0][i])
                else:
                    temp.append(tablelist[0][i])
            
            part = '|'.join(temp)
            parts.append('(' + part + ')')
    
    try:
        cnf = bl.parse('&'.join(parts))
        return cnf
    except boolean.boolean.ParseError:
        return True

def generate(nvars):
    alphabet = 'abcdefghijklmopqrstuvwxyz'
    chosen_ones = random.sample(alphabet, nvars)
    chosen_ones.extend(['~'+i for i in chosen_ones])
    
    sentence = ''
    for i in range(int((random.uniform(1, 5)))):
        sentence += '(' + random.choice(chosen_ones) + random.choice('|&') + random.choice(chosen_ones) + ')' + random.choice('|&')
    
    return(sentence[:-1])

class kmap(object):
    def __init__(self, sentence):
        self.map = self.gen_map(sentence)
        self.groups = self.gen_groups(self.map)

    def gen_map(self, sentence):
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
        patterns = [[3, 3], [3, 1], [1, 3], [3, 0], [0, 3], [-1, -1], [0, -1], [-1, 0]]
        pairs = set()

        for p in patterns:
            for n, x in enumerate(mapa):
                if p[0] < 0:
                    xi = p[0]
                    xf = 0
                else:
                    xi = 0
                    xf = p[0]

                for m, y in enumerate(x):
                    f = [[-1,0], [0,-1], [-1,-1], [0,3], [3,0], [1,3], [3,1], [3,3]]
                    if p[1] < 0:
                        yi = p[1]
                        yf = 0
                    else:
                        yi = 0
                        yf = p[1]

                    tmp = []
                    for i in range(xi, xf+1):
                        for j in range(yi, yf+1):
                            if n+i < len(mapa) and m+j < len(x) and mapa[n+i][m+j] == 1:
                                if n+i == -1:
                                    tmp.append((len(mapa)-1, m+j))
                                elif m+j == -1:
                                    tmp.append((n+i, len(x)-1))
                                elif n+i == -1 and m+j == -1:
                                    tmp.append((len(mapa)-1, len(y)-1))
                                else:
                                    tmp.append((n+i, m+j))
                                
                                continue

                            else:
                                f = 1
                                break

                        if f == 1:
                            break
                    if f == 1:              
                        continue
                    
                    tmp.sort()
                    pairs.add(tuple(tmp))

        return pairs

