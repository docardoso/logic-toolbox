from truths import Truths
import boolean

bl = boolean.BooleanAlgebra()

def shorten(sentence):
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
    if type(sentence) == str:
        sentence = shorten(sentence)

    x, y = [], []
    for i in sentence:
        if i.iscanonical:
            x.append(i.__str__())
        else:
            y.append(i.__str__())
    
    return Truths(x, y)

# Receives the table returned by truthtable OR just a sentence
def DNF(sentence):
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