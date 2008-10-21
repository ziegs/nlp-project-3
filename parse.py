#!/usr/bin/env python

makegrammar(file):
  """
  Returns a dictionary that contains a grammar as parsed from the
  input file
  """
  grammar={}
  #for each line in the file
  for line in file.readlines():
    #if the line is empty or is a comment , ignore
    if line.startswith("#") or line.isspace():
      continue
    else:   # return a list of words ingore anything after #
      tokens=line.partition("#")[0].split();
      
      # the freqency with wich to use a given replacement rule
      # given by the first token
      frequency=float(tokens[0])
      
      #the left hand side of the replace ment rule
      # in S-> foo  bar this would be S
      left_hand_side=tokens[1]
      
      # the right hand side of the replacemnt rule
      # eg foo bar. Note this is a list
      right_hand_side=[frequency,tokens[2:]]
      
      # a list of of production rules for the given non terminal
      # each such rule is a itself a list of one or more symbols
      
      
      if tokens[1] not in grammar:
        grammar[left_hand_side]=[0,[]]
        grammar[left_hand_side][1].append(right_hand_side)
        grammar[left_hand_side][0]+=frequency
