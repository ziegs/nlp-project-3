#!/usr/bin/env python

import getopt, sys

grammar = {}

def parse_rule(line):
    line = line.split('#')[0].split()
    if not len(line) or '#' in line[0]:
        return
    weight, symbol, expansion = float(line[0]), line[1], line[2:]
    grammar[symbol] = grammar.get(symbol, []) + [(weight, expansion)]
        
def make_grammar(file):
    [parse_rule(line) for line in open(file, 'r').readlines()]


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

    make_grammar(args[0])
    print grammar
