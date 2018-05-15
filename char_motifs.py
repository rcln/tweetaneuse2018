#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import json

sys.path.append("rstr_max/")
from text import *
from tools import *

from sklearn import svm
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import LinearSVC
from sklearn.model_selection import StratifiedKFold

from scipy import sparse

class process_data():
  def __init__(self, config, out_name):
    self.textsList = self.getTextsList()
    NbTrain = len(self.textsList["texts"])

    if o.test==True:
      self.testData = self.getTextsList(o.test)
      for etiq, liste in self.testData.iteritems():
        self.textsList[etiq] += liste
      NbTotal = len(self.textsList["texts"])

    self.motifsOccurences = get_motifs(self.textsList["texts"], config)
    self.getVecteursTraits()
    self.getClassesTextes()

    if o.verbose==True:
      print "\n  Train set size :\t %s"%str(NbTrain)
      if o.test==True:
        print "  Test set size :\t %s"%str(NbTotal-NbTrain)
      print "  NB motifs :\t\t %s"%str(self.NBmotifs)

    for name, clf in self.get_classifiers():
      predictions_clf = []
      print "\n","-"*10, name
      if o.test ==True:
        INDICES = [[[x for x in range(0, NbTrain)],
                    [x for x in range(NbTrain, NbTotal)]]]
      else:
        kf_total = StratifiedKFold(n_splits = 10)
        INDICES = kf_total.split(self.X,self.Y)
      for train_indices, test_indices in INDICES:
        self.create_sets(train_indices, test_indices)
        clf.fit(self.trainX, self.trainY)
        self.predictions = clf.predict(self.testX)
        predictions_clf += self.translate_predictions(test_indices)
      generate_output(out_name, [[name, predictions_clf]], "|")

  def translate_predictions(self, test_indices):
        cl_pred = [self.class_names[x] for x in self.predictions]
        tw_ids = [self.textsList["IDs"][i] for i in test_indices ]
        return [[tw_ids[i], cl_pred[i]] for i in range(0, len(cl_pred))]
    
  def create_sets(self, train_indices, test_indices):
    self.trainX = sparse.csr_matrix([self.X[i] for i in train_indices])
    self.trainY = [self.Y[i] for i in train_indices]
    self.testX = sparse.csr_matrix([self.X[i] for i in test_indices])
    self.testY = [self.Y[i] for i in test_indices]

  def get_classifiers(self):
    liste_classif=[
     ["OneVsRest-Linear", OneVsRestClassifier(LinearSVC(random_state=0))],
#     ["Svm-C1-linear", svm.SVC(kernel='linear')],
#     ["svm-C-1-poly", svm.SVC(kernel='poly')],
#     ["svm-C-1-rbf", svm.SVC(kernel='rbf')],
     ]
    return liste_classif
  def get_texts_cls(self, lines):
      stats = {}
      cls_list = []
      for lig in lines:
        ID, classe = re.split('\|', lig)
        stats.setdefault(classe, 0)
        stats[classe]+=1
        cls_list.append(classe)
      return stats, cls_list

  def get_texts_ids(self, lines):
    txts_list, IDs_list = [], []
    for lig in lines:
      ID, tweet = re.split('"\t"', re.sub('^"|"$', '',lig))
      txts_list.append(tweet)
      IDs_list.append(ID)
    return  txts_list, IDs_list
 
  def getTextsList(self, test=False):
    if test==False:
      path = "%s/id_tweets"%o.corpus
    else:
      path = "%s/T1_test"%o.corpus
      print "\nTest data : %s"%path
    lines = open_utf8(path, True)
    txts_list, IDs_list = self.get_texts_ids(lines)
    if test==False:
      train_path = "%s/T%s_cat_tweets"%(o.corpus, o.task)
      print "Training data : %s"%train_path
      lines = open_utf8(train_path, True)
      stats, cls_list = self.get_texts_cls(lines)
      print "  Classes :",stats
    else:
      cls_list =[" "]*len(lines)
    return {"texts":txts_list,"classes": cls_list,"IDs":IDs_list}

  def getVecteursTraits(self):
    dico = self.motifsOccurences
    self.X = []
    self.traits = [dico[i][0] for i in xrange(0, len(dico))]
    for numTexte in range(len(self.textsList["texts"])):
      vecteurTexte = []
      for motif in range(len(dico)):
          if numTexte in dico[motif][1]:
              vecteurTexte.append(dico[motif][1][numTexte])
          else:
              vecteurTexte.append(0)
      self.X.append(vecteurTexte)
    self.NBmotifs = len(self.traits)

  def getClassesTextes(self):
      self.Y = []
      dic_classes = {}
      cpt = 0
      for classe in self.textsList["classes"]:
          if classe not in dic_classes:
            dic_classes[classe] = cpt
            cpt+=1
          self.Y.append(dic_classes[classe])
      self.class_names = {y:x for x,y in dic_classes.iteritems()}

def get_config(options):
  ml, Ml = [int(x) for x in re.split(",", options.len)]
  ms, Ms = [int(x) for x in re.split(",", options.sup)]
  config = {"minsup":ms, "maxsup":Ms, "minlen":ml, "maxlen":Ml, "ngrams":options.ngrams, "test":options.test}
  return config

def generate_output(out_name, predictions, sep = "\t"):
  for clf_name, pred in predictions:
    pred = [sep.join(x) for x in pred]
    write_utf8("%s__%s"%(out_name, clf_name), "\n".join(pred)) 

def  get_config_name(config):
  L = []
  config = sorted([[x, y] for x,y in config.iteritems()])
  for x, y in config:
    L.append("%s-%s"%(str(x), str(y))) 
  config_name = "_".join(L)
  return config_name

if __name__ == "__main__":
  o = get_args()
  print o
  if o.corpus==None:
    print "\nUSE -c option to specify data location\n"
    o.corpus = "dummy_data"
  path_results = "results_char_motifs/%s/"%o.corpus
  mkdirs(path_results)

  config = get_config(o)
  config_name = get_config_name(config)
  out_name = "%s/T%s_%s"%(path_results, o.task,  config_name)

  process_data(config, out_name)
