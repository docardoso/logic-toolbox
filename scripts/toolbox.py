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

def DNF(sentence):
    """
    Receives either a sentence or the object returned by 'truthtable'.
    Returns the Disjunctive Normal Form of the provided sentence.

    Example:
        >>> DNF('(p and not q) or r')
        (~p&~q&r)|(~p&q&r)|(p&~q&~r)|(p&~q&r)|(p&q&r)
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
    
    dnf = bl.parse('|'.join(parts))
    
    return dnf

def CNF(sentence):
    """
    Receives either a sentence or the object returned by 'truthtable'.
    Returns the Conjunctive Normal Form of the provided sentence.

    Example:
        >>> CNF('(p and not q) or r')
        (r|q|p)&(r|~q|p)&(r|~q|~p)
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
    
    cnf = bl.parse('&'.join(parts))

    return cnf

def generate(nvars):
    alphabet = 'abcdefghijklmopqrstuvwxyz'
    chosen_ones = random.sample(alphabet, nvars)
    
    sentence = ''
    for i in range(int((random.random()*10)/2)):
        sentence += '(' + random.choice(chosen_ones) + random.choice('|&') + random.choice(chosen_ones) + ')' + random.choice('|&')
    
    return(sentence[:-1])
        




