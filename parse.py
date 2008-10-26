#!/usr/bin/env python

import getopt, sys
try:
    import psyco
    psyco.full()
except ImportError:
    pass

START_RULE = 'ROOT'

class EarleyParser:
    def __init__(self, grammar):
        self._grammar = grammar
        self._state = {}
    def _add_rule(column, rule):
        self._state[column] = self._state.get(column, []) + [rule]

    def _scan(self): # I need args
        pass

    def _predict(self): # I need args
        pass

    def _complete(self): # I need args
        pass

    def parse(self, tokens):
        grammar = self._grammar
        is_nonterminal = grammar.is_nonterminal
        is_terminal = grammar.is_terminal
        
        tok_len = len(tokens)
        self._add_rule(0, (2, self._grammar.start()))
        for i in xrange(tok_len):
            for dot_rule in self._state[i]:
                dot_pos = dot_rule[0]
                rule = dot_rule[1]
                try:
                    dotsym = rule[dot_pos]
                except IndexError:
                    dotsym = None
                    
                if is_terminal(dotsym):
                    # scan
                    pass
                elif is_nonterminal(dotsym):
                    #predict
                    pass
                elif dotsym == None:
                    # complete
                    pass
                

class Grammar:
    def __init__(self, file):
        self.grammar = {}
        self._make_grammar(file)

        self.is_terminal = lambda symbol: len(self.grammar[symbol]) == 1
        self.is_nonterminal = lambda symbol: len(self.grammar[symbol]) != 1
        
    def _parse_rule(self, line):
        line = line.split('#')[0].split()
        if not len(line) or '#' in line[0]:
            return
        weight, symbol, expansion = float(line[0]), line[1], line[2:]
        self.grammar[symbol] = self.grammar.get(symbol, []) + [(weight, symbol, expansion)]
        
    def _make_grammar(self, file):
        [self._parse_rule(line) for line in open(file, 'r').readlines()]

    def get(self, rule):
        return grammar.get(rule, None)

    def start(self):
        return grammar['ROOT']

    def __str__(self):
        output = ""
        for lhs in self.grammar.keys():
            fmtstring = ""
            rhs = self.grammar[lhs]
            l = len(rhs)
            for i in xrange(l):
                fmtstring += "%s" % ' '.join(rhs[i][2])
                if i != l - 1:
                    fmtstring += " | "
            output += "%s -> %s\n" % (lhs, fmtstring)
        return output


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "t")
    except getopt.GetoptError, err:
        print str(err)
        sys.exit(2)
    trace = False # Set whether to trace output using "#" comments
    for o, a in opts:
        if o == '-t':
            trace = true
    if len(args) != 2:
        print 'unhandled option'
        sys.exit(2)

    grammar = Grammar(args[0])
    print grammar
