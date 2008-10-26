#!/usr/bin/env python

import getopt, sys
import psyco
psyco.full()

START_RULE = 'ROOT'

class EarleyParser:

    def _scan(self, kwargs):
        pass

    def _predict(self, kwargs):
        pass

    def _complete(self, kwargs):
        pass

    def parse(self, tokens):
        pass

class Grammar:
    def __init__(self, file):
        self.grammar = {}
        self._make_grammar(file)
        
    def _parse_rule(self, line):
        line = line.split('#')[0].split()
        if not len(line) or '#' in line[0]:
            return
        weight, symbol, expansion = float(line[0]), line[1], line[2:]
        self.grammar[symbol] = self.grammar.get(symbol, []) + [(weight, symbol, expansion)]
        
    def _make_grammar(self, file):
        [self._parse_rule(line) for line in open(file, 'r').readlines()]

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
