#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import json
import glob

sys.path.append("tweetaneuse2018/rstr_max/")
sys.path.append("rstr_max/")
from extracteur_motifs import *
from tools import *

from sklearn import svm
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import LinearSVC
from sklearn.model_selection import StratifiedKFold

from scipy import sparse

class process_data():
  def __init__(self, config, out_name):
    self.textsList = self.getTextsList()
    self.NbTrain = len(self.textsList["texts"])
    print(self.NbTrain, "examples")
    if o.test==True:
      self.testData = self.getTextsList(o.test)
      for etiq, liste in self.testData.iteritems():
        self.textsList[etiq] += liste
      self.NbTotal = len(self.textsList["texts"])

    self.motifsOccurences = get_motifs(self.textsList["texts"], config)
    self.getVecteursTraits()
    self.getClassesTextes()

    if o.verbose==True:
      self.print_status()

    for name, clf in self.get_classifiers():
      predictions_clf = []
      print "\n","-"*10, name
      if o.test ==True:
        INDICES = [[[x for x in range(0, self.NbTrain)],
                    [x for x in range(self.NbTrain, self.NbTotal)]]]
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

  def print_status(self):
      print "\n  Train set size :\t %s"%str(self.NbTrain)
      print "    Classes :",self.stats
      if o.test==False:
        print "\nTraining data : %s"%self.train_path
      else:
        print "  Test set size :\t %s"%str(self.NbTotal-self.NbTrain)
        print "\nTest data : %s"%self.path_ids

  def get_classifiers(self):
    liste_classif=[
     ["OneVsRest-Linear", OneVsRestClassifier(LinearSVC(random_state=0))],
#     ["Svm-C1-linear", svm.SVC(kernel='linear')],
#     ["svm-C-1-poly", svm.SVC(kernel='poly')],
#     ["svm-C-1-rbf", svm.SVC(kernel='rbf')],
     ]
    return liste_classif

  def get_texts_cls(self):
      stats = {}
      cls_list = []
      for fic in glob.glob(o.data+"/*/*"):
        elems = re.split("/", fic)
        ID = elems[len(elems)-1]
        classe = elems[len(elems)-2]
        stats.setdefault(classe, 0)
        stats[classe]+=1
        cls_list.append(classe)
      return stats, cls_list

  def get_texts_ids(self):
    txts_list, IDs_list = [], []
    for fic in glob.glob(o.data+"/*/*"):
      elems = re.split("/", fic)
      ID = elems[len(elems)-1]
      txt = open_utf8(fic)
      txts_list.append(txt)
      IDs_list.append(ID)
    return  txts_list, IDs_list
 
  def getTextsList(self, test=False):
    txts_list, IDs_list = self.get_texts_ids()
    if test==False:
      self.stats, cls_list = self.get_texts_cls()
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
  config = {"minsup":ms, "maxsup":Ms, "minlen":ml, "maxlen":Ml, "ngrams":options.ngrams, "test":options.test, "words":options.words}
  return config

def generate_output(out_name, predictions, sep = "\t"):
  for clf_name, pred in predictions:
    pred = [sep.join(x) for x in pred]
    write_utf8("%s"%(out_name), "\n".join(pred)) 
#    write_utf8("%s__%s"%(out_name, clf_name), "\n".join(pred)) 

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
  if o.data==None:
    print "\nUSE -d option to specify data location\n"
    o.data = "dummy_data"
  path_results = "results_char_motifs/%s/"%o.data
  mkdirs(path_results)

  config = get_config(o)
  config_name = get_config_name(config)
  out_name = "%s/T%s_%s"%(path_results, o.task,  config_name)
  if os.path.exists(out_name) and o.force==False:
    print "-"*10
    print "Already done"
    print "-"*10
  else:
    print out_name
    process_data(config, out_name)
