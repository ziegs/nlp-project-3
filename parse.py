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
        self._state = {} # FIXME

    def _add_entry(self, column, entry):
        if self._state.get(column) == None:
            self._state[column] = []
        if entry not in self._state[column]:
            self._state[column].append(entry)

    def _scan(self, word, state, entry):
        if self.tokens[state] == word:
            self._add_entry(state + 1, (entry[0], entry[1] + 1, entry[2], entry[3]))

    def _predict(self, symbol, state):
        expansions = self._grammar.get(symbol)
        for rule in expansions:
            self._add_entry(state, (state, 2, rule, []))
        
    def _complete(self, state, entry):
        lhs = entry[2][1]
        print lhs
        for i in self._state[entry[0]]:
            dot_pos = i[1]
            rule = i[2]
            try:
                dotsym = rule[dot_pos]
            except IndexError:
                # print '# Error with rule %s' % str(i)
                continue
            if dotsym == lhs:
                self._add_entry(state, (state, i[1] + 1, i[2], i[3]))

    def parse(self, tokens):
        self.tokens = tokens
        self.cur_token = 0
        grammar = self._grammar
        
        tok_len = len(tokens)

        # Rule format: (start at, index to predictor, rule, clients)
        self._add_entry(0, (0, 2, self._grammar.start(), []))

        # Here is the actual algorithm
        for i in xrange(tok_len):
            changed = True
            for entry in self._state[i]:
                dot_pos = entry[1]
                rule = entry[2]
                try:
                    dotsym = rule[dot_pos]
                except IndexError:
                    dotsym = None
                if dotsym is not None and grammar.is_terminal(dotsym):
                    self._scan(dotsym, i, entry)
                elif dotsym is not None and grammar.is_nonterminal(dotsym):
                    self._predict(dotsym, i)
                elif dotsym == None:
                    self._complete(i, entry)
            print 'finish loop %d' % i
        print self._state[-1]
                

class Grammar:
    def __init__(self, file):
        self.grammar = {}
        self._make_grammar(file)

    def is_terminal(self, symbol): return self.grammar.get(symbol) == None
    def is_nonterminal(self, symbol): return len(self.grammar.get(symbol)) != 1
        
    def _parse_rule(self, line):
        line = line.split('#')[0].split()
        if not len(line) or '#' in line[0]:
            return
        weight, symbol, expansion = float(line[0]), line[1], line[2:]
        self.grammar[symbol] = self.grammar.get(symbol, []) + [(weight, symbol) + tuple(expansion)]
        
    def _make_grammar(self, file):
        [self._parse_rule(line) for line in open(file, 'r').readlines()]

    def get(self, rule):
        return self.grammar.get(rule, None)

    def start(self):
        return self.grammar['ROOT'][0]

    def __str__(self):
        print self.grammar
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
    parser = EarleyParser(grammar)
    parser.parse("3 * 5")
