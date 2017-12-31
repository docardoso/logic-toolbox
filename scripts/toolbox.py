from truths import Truths
import boolean

bl = boolean.BooleanAlgebra()


def shorten(sentence):
    k = set()
    k.add(sentence)
    for i in sentence.args:
        k.add(i)
        if i.iscanonical:
            continue
        else:    
            k.update(shorten(i))
    return sorted(k, key=lambda x: len(x.__str__()))

# Assumes sentence will be the list returned by shorten
def truthtable(sentence):
    x, y = [], []
    for i in sentence:
        if i.iscanonical:
            x.append(i.__str__())
        else:
            y.append(i.__str__())
    
    return Truths(x, y)

# Receives the table returned by truthtable
def DNF(table):
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
    
    dnf = '|'.join(parts)
    
    return dnf
            
