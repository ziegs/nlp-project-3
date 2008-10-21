#!/usr/bin/env python

grammar = {}

def parse_rule(line):
    line = line.split('#')[0].split()
    if not len(line) or '#' in line[0]:
        return
    weight, symbol, expansion = float(line[0]), line[1], line[2:]
    grammar[symbol] = grammar.get(symbol, []) + [(weight, expression)]
        
def make_gramar(file):
    [prase_rule(line) for line in open(file, 'r').readlines()]
