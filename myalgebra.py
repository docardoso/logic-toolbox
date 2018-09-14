from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

try:
    basestring  # Python 2
except NameError:
    basestring = str  # Python 3

import inspect


from boolean import BooleanAlgebra
from boolean import ParseError
from boolean import Symbol
from boolean import TOKEN_NOT
from boolean import TOKEN_AND
from boolean import TOKEN_OR
from boolean import TOKEN_TRUE
from boolean import TOKEN_FALSE
from boolean import TOKEN_SYMBOL
from boolean import TOKEN_LPAR
from boolean import TOKEN_RPAR
from boolean import boolean


TOKEN_IMP = 9
TRACE_PARSE = False

class MyAlgebra(BooleanAlgebra):
    def __init__(self, IMP_class=None):
        super().__init__()
        self.IMP = IMP_class or IMP      

    def tokenize(self, expr):
        if not isinstance(expr, basestring):
            raise TypeError('expr must be string but it is %s.' % type(expr))

        # mapping of lowercase token strings to a token type id for the standard
        # operators, parens and common true or false symbols, as used in the
        # default tokenizer implementation.
        TOKENS = {
            '>': TOKEN_IMP,# '->': TOKEN_IMP,
            '*': TOKEN_AND, '&': TOKEN_AND, 'and': TOKEN_AND,
            '+': TOKEN_OR, '|': TOKEN_OR, 'or': TOKEN_OR,
            '~': TOKEN_NOT, '!': TOKEN_NOT, 'not': TOKEN_NOT,
            '(': TOKEN_LPAR, ')': TOKEN_RPAR,
            '[': TOKEN_LPAR, ']': TOKEN_RPAR,
            'true': TOKEN_TRUE, '1': TOKEN_TRUE,
            'false': TOKEN_FALSE, '0': TOKEN_FALSE, 'none': TOKEN_FALSE
        }

        position = 0
        length = len(expr)

        while position < length:
            tok = expr[position]

            sym = tok.isalpha() or tok in ['_']
            if sym:
                position += 1
                while position < length:
                    char = expr[position]
                    if char.isalnum() or char in ('.', ':', '_'):
                        position += 1
                        tok += char
                    else:
                        break
                position -= 1

            try:
                yield TOKENS[tok.lower()], tok, position
            except KeyError:
                if sym:
                    yield TOKEN_SYMBOL, tok, position
                elif tok not in (' ', '\t', '\r', '\n'):
                    raise ParseError(token_string=tok, position=position,
                                     error_code=PARSE_UNKNOWN_TOKEN)

            position += 1

    def parse(self, expr, simplify=False):
        """
        Return a boolean expression parsed from `expr` either a unicode string
        or tokens iterable.

        Optionally simplify the expression if `simplify` is True.

        Raise ParseError on errors.

        If `expr` is a string, the standard `tokenizer` is used for tokenization
        and the algebra configured Symbol type is used to create Symbol
        instances from Symbol tokens.

        If `expr` is an iterable, it should contain 3-tuples of: (token,
        token_string, position). In this case, the `token` can be a Symbol
        instance or one of the TOKEN_* types.
        See the `tokenize()` method for detailed specification.
        """

        precedence = {self.NOT: 5, self.AND: 10, self.OR: 15, self.IMP: 20, TOKEN_LPAR: 25}

        if isinstance(expr, basestring):
            tokenized = self.tokenize(expr)
        else:
            tokenized = iter(expr)

        if TRACE_PARSE:
            tokenized = list(tokenized)
            print('tokens:')
            map(print, tokenized)
            tokenized = iter(tokenized)

        ast = [None, None]

        def is_sym(_t):
            return _t == TOKEN_SYMBOL or isinstance(_t, Symbol)

        prev = None
        for token, tokstr, position in tokenized:
            if TRACE_PARSE:
                print('\nprocessing token:', repr(token), repr(tokstr), repr(position))

            if prev:
                prev_token, _, _ = prev
                if is_sym(prev_token) and is_sym(token):
                    raise ParseError(token, tokstr, position, PARSE_INVALID_SYMBOL_SEQUENCE)

            if token == TOKEN_SYMBOL:
                ast.append(self.Symbol(tokstr))
                if TRACE_PARSE:
                    print(' ast: token == TOKEN_SYMBOL: append new symbol', repr(ast))

            elif isinstance(token, Symbol):
                ast.append(token)
                if TRACE_PARSE:
                    print(' ast: isinstance(token, Symbol): append existing symbol', repr(ast))

            elif token == TOKEN_TRUE:
                ast.append(self.TRUE)
                if TRACE_PARSE: print('ast4:', repr(ast))

            elif token == TOKEN_FALSE:
                ast.append(self.FALSE)
                if TRACE_PARSE: print('ast5:', repr(ast))

            elif token == TOKEN_NOT:
                ast = [ast, self.NOT]
                if TRACE_PARSE: print('ast6:', repr(ast))

            elif token == TOKEN_AND:
                ast = self._start_operation(ast, self.AND, precedence)
                if TRACE_PARSE: print(' ast: token == TOKEN_AND: start_operation', repr(ast))

            elif token == TOKEN_OR:
                ast = self._start_operation(ast, self.OR, precedence)
                if TRACE_PARSE: print(' ast: token == TOKEN_OR: start_operation', repr(ast))
            
            elif token == TOKEN_IMP:
                ast = self._start_operation(ast, self.IMP, precedence)
                if TRACE_PARSE: print(' ast: token == TOKEN_IMP: start_operation', repr(ast))

            elif token == TOKEN_LPAR:
                if prev:
                    ptoktype, _ptokstr, _pposition = prev
                    # Check that an opening parens is preceded by a function
                    # or an opening parens
                    if ptoktype not in (TOKEN_NOT, TOKEN_AND, TOKEN_OR, TOKEN_LPAR, TOKEN_IMP):
                        raise ParseError(token, tokstr, position, PARSE_INVALID_NESTING)
                ast = [ast, TOKEN_LPAR]

            elif token == TOKEN_RPAR:
                while True:
                    if ast[0] is None:
                        raise ParseError(token, tokstr, position, PARSE_UNBALANCED_CLOSING_PARENS)
                    if ast[1] is TOKEN_LPAR:
                        ast[0].append(ast[2])
                        if TRACE_PARSE: print('ast9:', repr(ast))
                        ast = ast[0]
                        if TRACE_PARSE: print('ast10:', repr(ast))
                        break

                    if isinstance(ast[1], int):
                        raise ParseError(token, tokstr, position, PARSE_UNBALANCED_CLOSING_PARENS)

                    # the parens are properly nested
                    # the top ast node should be a function subclass
                    if not (inspect.isclass(ast[1]) and issubclass(ast[1], boolean.Function)):
                        raise ParseError(token, tokstr, position, PARSE_INVALID_NESTING)

                    subex = ast[1](*ast[2:])
                    ast[0].append(subex)
                    if TRACE_PARSE: print('ast11:', repr(ast))
                    ast = ast[0]
                    if TRACE_PARSE: print('ast12:', repr(ast))
            else:
                raise ParseError(token, tokstr, position, PARSE_UNKNOWN_TOKEN)

            prev = (token, tokstr, position)

        try:
            while True:
                if ast[0] is None:
                    if ast[1] is None:
                        if len(ast) != 3:
                            raise ParseError(error_code=PARSE_INVALID_EXPRESSION)
                        parsed = ast[2]
                        if TRACE_PARSE: print('parsed1:', repr(parsed))
                    else:
                        parsed = ast[1](*ast[2:])
                        if TRACE_PARSE: print('parsed2:', repr(parsed))
                    break
                else:
                    subex = ast[1](*ast[2:])
                    ast[0].append(subex)
                    if TRACE_PARSE: print('ast13:', repr(ast))
                    ast = ast[0]
                    if TRACE_PARSE: print('ast14:', repr(ast))
        except TypeError:
            raise ParseError(error_code=PARSE_INVALID_EXPRESSION)

        if TRACE_PARSE: print('parsed3:', repr(parsed))
        if simplify:
            return parsed.simplify()
        return parsed

    def definition(self):
        """
        Return a tuple of this algebra defined elements and types as:
        (TRUE, FALSE, NOT, AND, OR, Symbol)
        """
        return self.TRUE, self.FALSE, self.NOT, self.AND, self.OR, self.Symbol, self.IMP

class IMP(boolean.DualBase):
    """
    Boolean IMP operation, taking 2 or more arguments

    It can also be created by using "->" between two boolean expressions.

    You can subclass to define alternative string representation.
    For example::
    >>> class IMP2(OR):
        def __init__(self, *args):
            super(OR2, self).__init__(*args)
            self.operator = 'IMP'
    """

    sort_order = 35

    def __init__(self, arg1, arg2, *args):
        super(IMP, self).__init__(arg1, arg2, *args)
        self.identity = self.FALSE
        self.annihilator = self.TRUE
        self.dual = self.AND
        self.operator = '>'

    def __eq__(self, other):
        try:
            if self.args == other.args:
                return True
            else:
                return False
        except AttributeError:
            return False
    
    def __hash__(self):
        return hash(self.args)

if __name__ == '__main__':
    bl = MyAlgebra()
    a = bl.parse('a and c > b and c')
    print(a)