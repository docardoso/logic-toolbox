'''
 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
| One day this will be filled with relevant information, but that day isn't today|
 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
from boolean import NOT, OR, Symbol
from copy import deepcopy
from myalgebra import *

import itertools as it
import random

bl = MyAlgebra()
stash = {}

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

def make_table(expression):
    evaluations = [] # Where the final results are stored
    header = [bl.parse(i) for i in shorten(expression)] # Gets table headers
    exp_literals = sorted([i.__str__() for i in header if len(i.__str__()) <= 2 and type(i) != boolean.NOT]) # Gets expression literals

    n = len(exp_literals) # Number of literals in expression

    for value in it.product([1,0], repeat=n):
        tmp = [] # Temporary variable that store the evaluations
        subs_dict = {} # Stores the value a subexpression will assume in this case
        subs_dict_alt = {} # Same as the first one, but literals have already been replaced

        # Inserts the columns for each literal with the right values
        for i, v in zip(header[:n], value):
            literals = [j for j in i.literals if type(j) != boolean.NOT]
            exp_object = i.subs({i:bl.parse(str(v)) for new, old in zip(value, sorted(i.literals))}) # Magic-Vodoo
            tmp.append(int(exp_object.simplify().__str__()))

        # Evaluates the expression according to each literal value and inserts it in the correct place
        for i in header[n:]:
            original = i # Stores the original unmodified sub-expression

            # My own kind of boolean.Expression.subs
            ordered_subs_dict = sorted([(x.__str__(), str(y)) for x, y in subs_dict.items()], key=lambda v: len(v[0]), reverse=True)
            for item in ordered_subs_dict:
                if item[0] in i.__str__():
                    i = bl.parse(i.__str__().replace(item[0], item[1]))

            # Find the literals in the current sub-expression and stores them
            sub_literals = []
            sub_literals_str = []
            for ind, lit in enumerate(sorted([i.__str__() for i in header if len(i.__str__()) < 2])):
                for j, k in enumerate(str(i)):
                    if k == lit:
                        sub_literals.append(ind)
                        sub_literals_str.append(lit)

            
            special_values = list(value) # Stores the correct value for each literal
            special_values += [0 if i == 1 else 1 for i in special_values] # Creates the equivalent values for the NOT literals
            special_values = [special_values[i] for i in sub_literals] # Filters the values to only store what is needed

            sbs = {}
            for new, old in zip(special_values, sorted(sub_literals_str)):
                sbs[bl.parse(old)] = bl.parse(str(new))

            exp_object = i.subs(sbs) # Substitutes literals with 0's and 1's
            substituted_exp_object = exp_object
            
            # REMOVING ~(1) and ~(0) FROM SENTENCE
            subexp_str = exp_object.__str__()
            newexp = ""
            iterator = iter(range(len(subexp_str)))
            for index in iterator:
                if subexp_str[index] == '~' and (subexp_str[index+2] == '1' or subexp_str[index+2] == '0'):
                    if subexp_str[index+1:index+4] == '(1)':
                        newexp += '0'
                    else:
                        newexp += '1'
                    next(iterator)
                    next(iterator)
                    next(iterator)
                    
                else:
                    newexp += subexp_str[index]
            
            # END OF 'REMOVING ~(1) and ~(0)'

            # SIMPLIFYING BY PARTS (Another kind of boolean.Boolean.subs)
            ordered_subs_dict_alt = sorted([(x.__str__(), str(y)) for x, y in subs_dict_alt.items()], key=lambda v: len(v[0]), reverse=True)
            for k, v in ordered_subs_dict_alt:
                if k in newexp:
                    newexp = newexp.replace(k, v)
            # END OF 'SIMPLIFYING BY PARTS'

            exp_object = bl.parse(newexp).simplify()
                              
            if "~" in str(exp_object) and len(str(exp_object)) == 4:
                if str(exp_object)[2] == '1':
                    exp_object = bl.parse('0')
                else:
                    exp_object = bl.parse('1')
            
            subs_dict_alt[substituted_exp_object.__str__()] = exp_object
            
            subs_dict[original] = exp_object.simplify()
            tmp.append(int(exp_object.simplify().__str__()))
            
        evaluations.append(tmp)

    table = [[i.__str__() for i in header]] # Adds headers
    table.extend(reversed(evaluations)) # Adds the rest of the table

    return table

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
        tablelist = make_table(sentence)
    else:
        tablelist = sentence

    parts = []

    for n, row in enumerate(tablelist[1:]):
        if row[-1] == 1:
            temp = []

            for i in range(len([i for i in tablelist[0] if len(i) < 2])):
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
        tablelist = make_table(sentence)
    else:
        tablelist = sentence

    parts = []

    for n, row in enumerate(tablelist[1:]):
        if row[-1] == 0:
            temp = []

            for i in range(len([i for i in tablelist[0] if len(i) < 2])):
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
            table = make_table(sentence)
        else:
            table = sentence

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

def indc(expression):
    ans = remove_conjunctions(bl.cnf(convert_implication(bl.parse(expression))))
    return ans

def convert_implication(expression, new_args={}):
    if type(expression) == boolean.Symbol:
        return expression

    elif type(expression) == IMP:
        expression = OR(NOT(expression.args[0]), expression.args[1])

    
    # new_args = {}
    for arg in expression.args:
        if arg in new_args.keys():
            continue
        # print(arg, convert_implication(arg))
        new_args[arg] = convert_implication(arg, new_args)
    
    expression = expression.subs(new_args)

    return expression

def remove_conjunctions(expression):
    return str(expression).split('&')

def solve(clause, clause2):
    if type(clause) == str:
        bl.parse(clause)
    
    if type(clause2) == str:
        bl.parse(clause2)

    # E.g: a and b
    if (type(clause) == boolean.Symbol and type(clause2) == boolean.Symbol) or (type(clause) == NOT and type(clause2) == NOT):
        return None
    
    # E.g: a or b and a or b
    elif clause == clause2:
        return None

    # E.g: not a and a
    elif type(clause) == NOT and type(clause2) == boolean.Symbol:
        if clause.args[0] == clause2:
            return True

    # E.g: a and not a
    elif type(clause) == boolean.Symbol and type(clause2) == NOT:
        if clause2.args[0] == clause:
            return True
    
    # E.g: a and (not a or b)
    elif type(clause) == boolean.Symbol and type(clause2) == OR:
        tmp = [arg for arg in clause2.args if not (type(arg) == NOT and arg.args[0] == clause)]
        try:
            return OR(*tmp)    
        except TypeError:
            return tmp[0]

    # Eg: not a and (a or b)    
    elif type(clause) == NOT and type(clause2) == OR:
        tmp = [arg for arg in clause2.args if arg != clause.args[0]]
        try:
            return OR(*tmp)
        except TypeError:
            return tmp[0]

    # E.g: (not a or b) and a 
    elif type(clause) == OR and type(clause2) == boolean.Symbol:
        tmp = [arg for arg in clause.args if not (type(arg) == NOT and arg.args[0] == clause2)]
        try:
            return OR(*tmp)    
        except TypeError:
            return tmp[0]

    # Eg: (a or b) and not a
    elif type(clause) == OR and type(clause2) == NOT:
        tmp = [arg for arg in clause.args if arg != clause2.args[0]]
        try:
            return OR(*tmp)
        except TypeError:
            return tmp[0]
    
    else:
        vetted = set()
        excluded = set()
        for arg in clause.args:
            # tmp = False
            for arg2 in clause2.args:
                
                # E.g: not a and a
                if type(arg) == NOT and type(arg2) == boolean.Symbol:
                    if arg.args[0] == arg2:
                        excluded.add(arg)
                        excluded.add(arg2)
                        vetted.discard(arg)
                        vetted.discard(arg2)

                # E.g: a and not a
                elif type(arg) == boolean.Symbol and type(arg2) == NOT:
                    if arg == arg2.args[0]:
                        excluded.add(arg)
                        excluded.add(arg2)
                        vetted.discard(arg)
                        vetted.discard(arg2)

                if arg2 not in excluded:
                    vetted.add(arg2)
            
            if arg not in excluded:
                    vetted.add(arg)
        
        if len(vetted) == 1:
            try:
                return Symbol(*vetted)
            except TypeError:
                quit()
        elif len(vetted) == 0:
            return None
        else:
            return OR(*vetted)

def prove(expressions, answer):
    tree = dict()
    clauses = []
    for i in expressions + ["not({})".format(answer)]:
        for j in indc(i):
            if bl.parse(j) not in clauses:
                tree[str(bl.parse(j))] = (None, None)
                clauses.append(bl.parse(j))
    
    absurd = False
    l = 0
    history = set()    
    while not absurd:
        l += 1
        if l == 6:
            break

        for index, n in enumerate(clauses):
            for m in clauses:
                if ((n, m) not in history): #and ((m, n) not in history):
                    result = solve(n, m)

                history.add((n, m))        
                history.add((m, n))
                if result == None:
                    continue

                if str(result) not in tree:
                    tree[str(result)] = (str(n), str(m))
                
                if result == True:
                    queue = ['True']
                    tmp = set()
                    final = []
                    while queue:
                        current = queue.pop(0)
                        if (current, tree[current]) not in final:
                            final.append((current, tree[current]))

                        if current in tree:
                            for i in tree[str(current)]:
                                if i != None and i not in tmp:
                                    queue.append(i)
                                    tmp.add(i)
                    
                    return final

                else:
                    if result not in clauses:
                        clauses.append(result)

def dual_to_nand(exp):
    global stash
    
    if type(exp) == NOT:
        if type(exp.args[0]) == Symbol:
            return NOT(AND(exp.args[0], exp.args[0]))

        elif type(exp.args[0]) == AND:
            args = []
            for tmp in list(exp.args[0].args):
                if type(tmp) != Symbol:
                    if len(tmp.args) > 2:
                        args.append(sop_to_nand(tmp))
                    
                    else:
                        args.append(dual_to_nand(tmp))
                else:
                    args.append(tmp)
           
            return NOT(AND(*args))

        else:
            exp = exp.literalize()
            return pos_to_nand(exp)
            
    
    if type(exp) == Symbol:
        return exp

    if exp in stash:
        return stash[exp]

    a = exp.args[0]
    b = exp.args[1]
    if type(a) != Symbol:
        if a in stash:
            a = stash[a]
        else:
            a = dual_to_nand(a)
    
    if type(b) != Symbol:
        if b in stash:
            b = stash[b]
        else:
            b = dual_to_nand(b)


    if type(exp) == AND:
        stash[exp] = NOT(AND(NOT(AND(a, b)), NOT(AND(a, b))))
        return NOT(AND(NOT(AND(a, b)), NOT(AND(a, b))))
    
    elif type(exp) == OR:
        stash[exp] = NOT(AND(NOT(AND(a, a)), NOT(AND(b, b))))
        return NOT(AND(NOT(AND(a, a)), NOT(AND(b, b))))

def sop_to_nand(exp):
    if len(exp.args[0].args) > 2:
        if type(exp.args[0]) == AND:
            done = pos_to_nand(exp.args[0])
        else:
            done = sop_to_nand(exp.args[0])
    else:
        done = dual_to_nand(exp.args[0])

    for i in range(1, len(exp.args)):
        if len(exp.args[i].args) > 2:
            if type(exp.args[i]) == AND:
                current = pos_to_nand(exp.args[i])
            else:
                current = sop_to_nand(exp.args[i])
        else:
            current = dual_to_nand(exp.args[i])

        done = dual_to_nand(OR(done,current))

    return done

def pos_to_nand(exp):   
    if len(exp.args[0].args) > 2:
        if type(exp.args[0]) == AND:
            done = pos_to_nand(exp.args[0])
        else:
            done = sop_to_nand(exp.args[0])
    else:
        done = dual_to_nand(exp.args[0])

    for i in range(1, len(exp.args)):
        if len(exp.args[i].args) > 2:
            if type(exp.args[i]) == AND:
                current = pos_to_nand(exp.args[i])
            else:
                current = sop_to_nand(exp.args[i])
        else:
            current = dual_to_nand(exp.args[i])

        current = dual_to_nand(exp.args[i])
        done = dual_to_nand(AND(done,current))

    return done

if __name__ == "__main__":
    import doctest
    doctest.testmod()
