#!/usr/bin/env python
"""
An Earley Parser for CS465, Fall '08

Matt Ziegelbaum <mziegelbaum@acm.jhu.edu>
Ian Miers <imichaelmiers@gmail.com>
"""
import getopt, sys , pdb

try:
    import psyco
    psyco.full()
except ImportError:
    sys.stderr.write("You don't have psyco installed. \
        This will run faster with psyco.\n")

START_RULE = 'ROOT'

INFO = 1 # Info log level
LOG = 0 # Implied
WARN = 2 # Warning log level

class Weight:
    def __init__(self, weight):
        self.weight = weight
    def set(self, weight):
        self.weight = weight
    def get(self):
        return self.weight
    def __str__(self):
        return str(self.weight)

class Rule:
    def __init__(self, entry):
        assert entry is not None
        self.rule = entry

    def set(self, entry):
        assert entry is not None
        self.rule = entry

    def append(self, entry):
        assert entry is not None
        self.rule.append(entry)

    def cat(self, entry):
        assert entry is not None
        self.rule += entry
    def __str__(self):
        return str(self.rule)

class EarleyParser:
    """ A class for parsing sentences.  Implements Earley's Algorithm """
    def __init__(self, grammar, trace=False):
        self._grammar = grammar
        self._state = []
        self._state_by_predict = []
        self._state_duplicates = []
        self._progress = 0
        self._trace = trace
        self.tokens = None
        self._parse_weight = 0

    def _log(self, msg, level=LOG):
        """ Logs a message. """
        if self._trace or level > 0:
            sys.stderr.write(msg)

    def _reset(self):
        """ Reset the parser's state. """
        self._state = []
        self._state_by_predict = []
        self._state_duplicates = []
        self.tokens = None
        self._progress = 0
        self._parse_weight = 0

    def _make_progress(self, msg=''):
        """ Will mark a progress "." every 5000 operations. """
        self._progress += 1
        if self._progress % 5000 == 0:
            self._log(msg + '.')

    def get_state_table(self):
        """ Returns the state table. """
        return self._state
    
    def _setup_state_by_predict_table(self, length):
        """ Initializes the state prediction table. """
        for i in xrange(length):
            self._state_by_predict.append({})
            self._state_duplicates.append({})

    def _setup_table(self, length):
        """ Initializes Earley column table. """
        for i in xrange(length):
            self._state.append([])

    def _add_entry(self, column, entry):
        """ Adds an entry to a column in the state table. """
        assert len(entry) == 5
        assert isinstance(entry[3], Rule)
        dot_pos = entry[1]
        rule = entry[2]
        try:
            dotsym = rule[dot_pos]
        except IndexError:
            dotsym = None
            
        states = self._state
        dup_key = (entry[0], entry[1], entry[2])
        if dup_key not in self._state_duplicates[column]:
            self._state_duplicates[column][dup_key] = entry
            states[column].append(entry)
            state_by_predict = self._state_by_predict[column]
            if dotsym in state_by_predict:
                state_by_predict[dotsym] += [entry]
            else:
                state_by_predict[dotsym] = [entry]
            return None
        else:
            return self._state_duplicates[column][dup_key]
                
    def _scan(self, word, state, entry):
        """ Scan phase of Earley's """
        if state == len(self.tokens):
            pass
        elif self.tokens[state] == word:
            self._add_entry(state + 1, (entry[0], entry[1] + 1, entry[2],
                entry[3], entry[4]))
        self._make_progress('Scanning')

    def _predict(self, symbol, state, predicted, SJ):
        if symbol not in predicted:
            predicted[symbol] = True
            self._make_progress('Predicting')
            # given the possible left ancestors B  for the current token, 
            # for each of these , see if there is a rule for A -> B * 
            # if so expand 
            for B in SJ.get(symbol,[]):
                for rule in self._grammar.get((symbol, B)):
                    parse = list(rule[2:])
                    self._add_entry(state, (state, 2, rule, Rule([rule]), Weight(rule[0])))
                    self._make_progress()
            SJ[symbol] = []
    def _complete(self, state, entry):
        """ Takes the state  and a completed entry
        and attaches customers. Eg  we have NUM -> 3 as an entry
        then we will add Factor ->num 
        """
        lhs = entry[2][1]
        self._make_progress('Attaching')
        entry_state = entry[0]
        pstate = self._state_by_predict[entry_state]
        if not pstate.has_key(lhs):
            return
        for i in pstate[lhs]:
            dot_pos = i[1]
            rule = i[2]
            try:
                dotsym = rule[dot_pos]
            except IndexError:
                continue
            if dotsym == lhs:
                predict = i[1] - 2
                parse = i[3]
                weight = Weight(i[4].get() + entry[4].get())

                exp = Rule(parse.rule + [entry[3].rule])
                dup = self._add_entry(state, (i[0], i[1] + 1, i[2], exp, weight))
                if dup:
                    if weight.get() < dup[4].get():
                        dup[3].set(parse.rule + [entry[3].rule])
                        dup[4].set(weight.get())
            self._make_progress()

    def _best_parse_help(self, entry):
        """
        Helper function for generating the lightest parse of a sentence.
        """
        self._parse_weight += entry[0][0]
        rule = entry[0][1]
        expand = entry[0][2:]
        o = "(%s " % (rule)
        prod = 1
        for e in expand:
            if self._grammar.is_terminal(e):
                o += str(e)
            else:
                o += self._best_parse_help(entry[prod])
                prod += 1
        return o + ")"
    
    def get_best_parse(self, entry):
        """
        Returns the lightest parse of the sentence.
        """
        return self._best_parse_help(entry.rule)
    
    def _left_corner(self, SJ, Y):
        """
        Builds the left corner ancestor table for the given column 
        SJ the left ancestor table for our current state.
        """
        for X in self._grammar.get_P(Y):
            if X not in SJ : # if this is the first addition to SJ(X)
                SJ[X] = [Y]  # add Y 
                self._left_corner(SJ, X) # recursively process X 
            else: # other wise just add Y
                SJ[X].append(Y) # FIXME memory wastfull ?? better to do append ?
     
    def parse(self, tokens):
        """
        Parses a sentence of tokens into the appropriate syntax tree.
        """
        self._reset()
        
        self.tokens = tokens
        grammar = self._grammar

        tok_len = len(tokens)
        self._setup_table(tok_len + 1)
        self._setup_state_by_predict_table(tok_len + 2)
        # Rule format: (start at, index to predictor, rule, clients)
        self._add_entry(0, (0, 2, self._grammar.start(), Rule([self._grammar.start()]), Weight(0.0)))
        self._log('# Parsing...')
        # Here is the actual algorithm
        for i in xrange(tok_len + 1):
            token = None
            if i != len(self.tokens):
                token = self.tokens[i]
            SJ = {} # the left ancestor table
            # build the left corner table 
            self._left_corner(SJ, token)
            predicted_symbols = {}
            for entry in self._state[i]:
                dot_pos = entry[1]
                rule = entry[2]
                try:
                    dotsym = rule[dot_pos]
                except IndexError:
                    dotsym = None

                if dotsym == None:
                    self._complete(i, entry)
                elif grammar.is_terminal(dotsym):
                    pass 
                #    self._scan(dotsym, i, entry)
                # XXX FIXME  the pass above prevnets a bug
                # in is non temrinal. it fails if given a terminal.
                # this is bad 
                elif grammar.is_nonterminal(dotsym):
                    self._predict(dotsym, i, predicted_symbols, SJ)

            for entry in self._state_by_predict[i].get(token, []):
                dot_pos = entry[1]
                rule = entry[2]
                try:
                    dotsym = rule[dot_pos]
                except IndexError:
                    continue 

                self._scan(dotsym, i, entry)

            self._make_progress('Parsing')
            
        self._log('\n# ...done!\n')
        for i in self._state[tok_len]:
            if i[2][1] == START_RULE:
                print self.get_best_parse(i[3])
                return True
        return False
    def parse_weight(self):
        return self._parse_weight
                

class Grammar:
    def __init__(self, grammar_file):
        self.grammar = {}
        self.P = {}# the left parent table 
        self.num_rules = 0
        print "# Parsing grammar..."
        self._make_grammar(grammar_file)
        print "# Parsed %d grammar rules." % (self.num_rules)
        
    def is_terminal(self, symbol):
        return self.grammar.get(symbol) == None
    def is_nonterminal(self, symbol):
        return len(self.grammar.get(symbol)) > 0
        
    def _parse_rule(self, line):
        line = line.split('#')[0].split()
        if not len(line) or '#' in line[0]:
            return
        weight, symbol, leftchild, restOfexpansion = float(line[0]), line[1], line[2], line[3:]
        expansion = [leftchild] + restOfexpansion
        key = (symbol, leftchild)
        if key not in self.grammar: # if R(A,B) is empty add A to P(B)
            self.P[leftchild] = self.P.get(leftchild,[]) + [symbol]
        self.grammar[key] = self.grammar.get(key, []) + [(weight, symbol) + tuple(expansion)]
        # for 1  S-> NP VP we store S NP: 1 S NP VP and  S : 1 S NP VP
        key=symbol
        self.grammar[key] = self.grammar.get(key, []) + [(weight, symbol) + tuple(expansion)]

        self.num_rules += 1

    def _make_grammar(self, file):
        [self._parse_rule(line) for line in open(file, 'r').readlines()]

    def get(self, rule):
        return self.grammar.get(rule, None)
    def get_P(self, rule):
        return self.P.get(rule, [])
    def start(self):
        return self.grammar[START_RULE][0]

    def __str__(self):
        output = ""
        for lhs in self.grammar.keys():
            if type(lhs) == type(()):
                continue
         
            output+= "%s -> \n "%lhs 
            for sym in self.grammar[lhs]:
                output+="\t "
                for s in sym[2:]:
                    output+=" %s"%s
                output+="\n"
                
        return output

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "tc")
    except getopt.GetoptError, err:
        print str(err)
        sys.exit(2)

    trace = False # Set whether to trace output using "#" comments
    columns = False 
    for o, a in opts:
        if o == '-t':
            trace = True
        if o == '-c':
            columns = True
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
        if trace:
            print "# Parsing: %s" % str(' '.join(sen))
        valid = parser.parse(sen)
        if valid:
            print parser.parse_weight()
        else:
            print 'NONE'

        if trace:
            pass  
        if columns:
            states = parser.get_state_table()
            for i in xrange(len(states)):
                print '*** Column %d' % i
                for sym in states[i]:
                    print sym
                print '***'

def profile_main():
    # This is the main function for profiling 
    import cProfile, pstats
    prof = cProfile.Profile()
    try:
        prof = prof.runctx("main()", globals(), locals())
    except:
        pass
    print "<pre>"
    stats = pstats.Stats(prof)
    stats.sort_stats("time")  # Or cumulative
    stats.print_stats(80)  # 80 = how many to print
    # The rest is optional.
    # stats.print_callees()
    # stats.print_callers()
    print "</pre>"

if __name__ == '__main__':
    # Uncomment the following line to profile the app
    #profile_main()
    main()

    
