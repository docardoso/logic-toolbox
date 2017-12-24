from truths import Truths
import boolean

bl = boolean.BooleanAlgebra()


def shorten(sentence):
    k = set()
    for i in sentence.args:
        k.add(i)
        if i.iscanonical:
            continue
        else:    
            k.update(shorten(i))
    return k

# Assumes sentence will be the set returned by shorten
def truthtable(sentence):
    x, y = [], []
    for i in sentence:
        if i.iscanonical:
            x.append(i.__str__())
        else:
            y.append(i.__str__())
    
    return Truths(x, y)
        
