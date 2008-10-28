#!/usr/bin/env python

import getopt, sys , pdb

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
        self._state_by_predict = []
        self._progress = 0

    def _reset(self):
        self._state = {}
        self._state_by_predict = []
        self.tokens = None
        self._progress = 0

    def _make_progress(self):
        self._progress += 1
        if self._progress % 5000 == 0:
            sys.stderr.write('.')

    def get_state_table(self):
        return self._state
    
    def _setup_state_by_predict_table(self,length):
        for i in xrange(length):
            self._state_by_predict.append({})

    def _setup_table(self, length):
        for i in xrange(length):
            self._state[i] = []

    def _add_entry(self, column, entry):
        dot_pos=entry[1]
        rule=entry[2]
        try:
            dotsym=rule[dot_pos]
        except IndexError:
            dotsym=None

        if entry not in self._state[column]:
            self._state[column].append(entry)
            self._state_by_predict[column][dotsym] = self._state_by_predict[column].get(dotsym,[]) + [entry]
                
    def _scan(self, word, state, entry):
        if state == len(self.tokens):
            pass
        elif self.tokens[state] == word:
            self._add_entry(state + 1, (entry[0], entry[1] + 1, entry[2], entry[3]))
        self._make_progress()

    def _predict(self, symbol, state):
        expansions = self._grammar.get(symbol)
        for rule in expansions:
            self._add_entry(state, (state, 2, rule, [rule]))
            self._make_progress()
            
    def _complete(self, state, entry):
        lhs = entry[2][1]
        for i in self._state_by_predict[entry[0]].get(lhs,[]):
            dot_pos = i[1]
            rule = i[2]
            try:
                dotsym = rule[dot_pos]
            except IndexError:
                continue
            if dotsym == lhs:
                self._add_entry(state, (i[0], i[1] + 1, i[2], i[3]+[entry[3]]))
            self._make_progress()

    def _best_parse_help(self, trace):
        #print trace
        rule = trace[0][1]
        o = "(%s " % (rule)
        for j in xrange(len(trace[1:])):
            if len(trace[j + 1]) == 1:
                nt = trace[j +1][0]
                o += '(%s %s)' % (nt[1], nt[2])
            else:
                o += self._best_parse_help(trace[j + 1])
        return o + ")"
    def get_best_parse(self, trace):
        return "(ROOT %s)" % self._best_parse_help(trace)

    def parse(self, tokens):
        self._reset()
        
        self.tokens = tokens
        self.cur_token = 0
        grammar = self._grammar

        tok_len = len(tokens)
        self._setup_table(tok_len + 1)
        self._setup_state_by_predict_table(tok_len+2)
        # Rule format: (start at, index to predictor, rule, clients)
        self._add_entry(0, (0, 2, self._grammar.start(), []))
        sys.stderr.write('# Parsing...')
        # Here is the actual algorithm
        for i in xrange(tok_len + 1):
            count = 0
            for entry in self._state[i]:
                count += 1
                dot_pos = entry[1]
                rule = entry[2]
                try:
                    dotsym = rule[dot_pos]
                except IndexError:
                    dotsym = None

                if dotsym == None:
                    self._complete(i, entry)
                elif grammar.is_terminal(dotsym):
                    self._scan(dotsym, i, entry)
                elif grammar.is_nonterminal(dotsym):
                    self._predict(dotsym, i)
            self._make_progress()
        sys.stderr.write('# ...done!')
        for i in self._state[tok_len]:
            if i[2][1] == START_RULE:
                print self.get_best_parse(i[3][0])
                return True
        return False
    
                

class Grammar:
    def __init__(self, file):
        self.grammar = {}
        self.num_rules = 0
        print "# Parsing grammar..."
        self._make_grammar(file)
        print "# Parsed %d grammar rules." % (self.num_rules)

    def is_terminal(self, symbol): return self.grammar.get(symbol) == None
    def is_nonterminal(self, symbol): return len(self.grammar.get(symbol)) > 0
        
    def _parse_rule(self, line):
        line = line.split('#')[0].split()
        if not len(line) or '#' in line[0]:
            return
        weight, symbol, expansion = float(line[0]), line[1], line[2:]
        self.grammar[symbol] = self.grammar.get(symbol, []) + [(weight, symbol) + tuple(expansion)]
        self.num_rules += 1

    def _make_grammar(self, file):
        [self._parse_rule(line) for line in open(file, 'r').readlines()]

    def get(self, rule):
        return self.grammar.get(rule, None)

    def start(self):
        return self.grammar[START_RULE][0]

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
        opts, args = getopt.getopt(sys.argv[1:], "tc")
    except getopt.GetoptError, err:
        print str(err)
        sys.exit(2)
    trace = False # Set whether to trace output using "#" comments
    columns = False 
    for o, a in opts:
        if o == '-t':
            trace = true
        if o == '-c':
            columns=True
    if len(args) != 2:
        print 'unhandled option'
        sys.exit(2)

    grammar = Grammar(args[0])
    parser = EarleyParser(grammar)

    sentences = open(args[1], 'r').readlines()
    for sen in sentences:
        sen = sen.split()
        if len(sen) == 0:
            continue
        print "# Parsing: %s" % str(' '.join(sen))
        valid = parser.parse(sen)
        if valid:
            print "# Yes"
        else:
            print "# No"

        if trace:
            pass  
        if columns:
            states = parser.get_state_table()
            for i in states.keys():
                print '*** Column %d' % i
                for sym in states[i]:
                    print sym
                print '***'
