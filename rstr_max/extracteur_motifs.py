#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append("rstr_max/")
from rstr_max.rstr_max import *
import pickle
import os
import re

def is_word(ss, options):
  mots = [x for x in re.split("_", ss) if x!=""]
  if len(mots)>=options['minlen']:
    if len(mots)<=options['maxlen']:
      return True
  return False

def exploit_rstr(r, rstr, dic_occur, options):
    l_str = []
    cpt_ss = 0
    for (offset_end, nb), (l, start_plage) in r.iteritems():
        ss = rstr.global_suffix[offset_end-l:offset_end]
        if options["words"]==True:
          if is_word(ss, options)==False:
            continue
        elif len(ss)<options['minlen'] or len(ss)>options['maxlen']:
            continue
        cpt_ss+=1
        set_occur = set()
        for o in xrange(start_plage, start_plage+nb) :
            id_str = rstr.idxString[rstr.res[o]]
            dic_occur[id_str][cpt_ss]=dic_occur[id_str].setdefault(cpt_ss,0)+1
            set_occur.add(id_str)
        if len(set_occur)>=options['minsup'] and len(set_occur)<=options['maxsup'] :
            occurences = {}
            for x in set_occur:
                occurences[x] = dic_occur[x][cpt_ss]
            sortie = [ss, occurences]
            l_str.append(sortie)
    return l_str

def get_n_grams(textes, options):
  dic ={}
  cpt_texte = 0
  for t in textes:
    if options["words"]==True:
      t = re.split(" |,|;|:|\.|\(|\)|<|>", t)
      t = [x for x in t if x!=""]
    for i in range(0, len(t)):
      for j in range(options["minlen"], options["maxlen"]+1):
        car = tuple(t[i:i+j])
        dic.setdefault(car, {})
        dic[car].setdefault(cpt_texte, 0)
        dic[car][cpt_texte]+=1
    cpt_texte+=1
  L= []
  for ss, occs in dic.iteritems():
    L.append([ss, occs])
  return L
  
def get_motifs(lignes_texte,options = { 'minsup':1,
                                        'maxsup':10,
                                        'minlen':1,
                                        'maxlen':10}):
    if options["ngrams"]==True:
      l_motifs = get_n_grams(lignes_texte, options)
      return l_motifs
    rstr = Rstr_max()
    for ligne in lignes_texte:
      if options["words"]==True:
        ligne = re.sub(" |,|;|:|\.|\(|\)|<|>|\n", "_", ligne)
      rstr.add_str(ligne)
    dic_occur= {x:{} for x in xrange(0,len(lignes_texte))}
    r = rstr.go()
    l_motifs = exploit_rstr(r, rstr, dic_occur, options)
    return l_motifs

if __name__=="__main__":
  fic = sys.argv[1]
  f = open(fic)
  lignes = f.readlines()
  f.close()
  get_motifs(lignes)
