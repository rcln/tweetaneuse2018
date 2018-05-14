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
  def __init__(self, options, config, out_name):
    self.textsList = self.getTextsList(o.corpus, o.task)
    NbTrain = len(self.textsList["texts"])
    if options.test==True:
      self.testData = self.getTextsList(o.corpus,o.task, o.test)
      for etiq, liste in self.testData.iteritems():
        self.textsList[etiq] += liste
    self.motifsOccurences = get_motifs(self.textsList["texts"], config)
    self.X, self.traits = self.getVecteursTraits()
    self.NBmotifs = len(self.traits)

    self.Y, self.dic_classes = self.getClassesTextes()
    self.class_names = {y:x for x,y in self.dic_classes.iteritems()}
    classifiers = self.get_classifiers()

    if options.verbose==True:
      print "\n  Train set size :\t %s"%str(NbTrain)
      if o.test==True:
        print "  Test set size :\t %s"%str(len(self.textsList["texts"])-NbTrain)
      print "  NB motifs :\t\t %s"%str(self.NBmotifs)
      print "  Classifiers :\t\t %s\n"%", ".join([x[0] for x in classifiers])

    for name, clf in classifiers:
      self.all_predictions = []
      all_predictions_clf = []
      print "-"*10, name
      if options.test ==False:
        kf_total = StratifiedKFold(n_splits = 10)
        INDICES = kf_total.split(self.X,self.Y)
      else:
        INDICES = [[[x for x in xrange(0, NbTrain)], [x for x in xrange(NbTrain, len(self.textsList["texts"]))]]]
      for train_indices, test_indices in INDICES:
        self.create_sets(train_indices, test_indices)
        clf.fit(sparse.csr_matrix(self.trainX), self.trainY)
        self.predictions = clf.predict(sparse.csr_matrix(self.testX))
        all_predictions_clf += self.translate_predictions(test_indices)
      self.all_predictions.append([name, all_predictions_clf])
      generate_output(out_name, self.all_predictions, "|")

  def translate_predictions(self, test_indices):
        cl_pred=[self.class_names[x] for x in self.predictions]
        tw_ids = [self.textsList["IDs"][i] for i in test_indices ]
        paires = [[tw_ids[i], cl_pred[i]] for i in range(0, len(cl_pred))]
	return paires
    

  def create_sets(self, train_indices, test_indices):
    self.trainX = [self.X[i] for i in train_indices]
    self.trainY = [self.Y[i] for i in train_indices]
    self.testX = [self.X[i] for i in test_indices]
    self.testY = [self.Y[i] for i in test_indices]

  def get_classifiers(self):
    liste_classif=[
     ["OneVsRest-Linear", OneVsRestClassifier(LinearSVC(random_state=0))],
#     ["Svm-C1-linear", svm.SVC(kernel='linear')],
#     ["svm-C-1-poly", svm.SVC(kernel='poly')],
#     ["svm-C-1-rbf", svm.SVC(kernel='rbf')],
     ]
    return liste_classif

  def getTextsList(self, folder, task, test=False):
    texts_ids = {}
    txts_list, cls_list, IDs_list = [], [], []
    if test==False:
      lignes = open_utf8("%s/id_tweets"%folder, True)
    else:
      test_path = "%s/T1_test"%folder
      print "\nTest data : %s"%test_path
      lignes = open_utf8(test_path, True)
      cls_list =[" "]*len(lignes)
    for lig in lignes:
      ID, tweet = re.split('"\t"', re.sub('^"|"$', '',lig))
      texts_ids[ID] = tweet
      if test==True:
        txts_list.append(tweet)
        IDs_list.append(ID)
    if test==False:
      train_path = "%s/T%s_cat_tweets"%(folder, task)
      print "Training data : %s"%train_path
      lignes = open_utf8(train_path, True)
      stats = {}
      for lig in lignes:
        ID, classe = re.split('\|', lig)
        stats.setdefault(classe, 0)
        stats[classe]+=1
        txts_list.append(texts_ids[ID])
        IDs_list.append(ID)
        cls_list.append(classe)
      print stats
    return {"texts":txts_list,"classes": cls_list,"IDs":IDs_list}

  def getVecteursTraits(self):
    dico = self.motifsOccurences
    listeVecteurs = []
    traits = [dico[i][0] for i in xrange(0, len(dico))]
    for numTexte in range(len(self.textsList["texts"])):
      vecteurTexte = []
      for motif in range(len(dico)):
          if numTexte in dico[motif][1]:
              vecteurTexte.append(dico[motif][1][numTexte])
          else:
              vecteurTexte.append(0)
      listeVecteurs.append(vecteurTexte)
    return listeVecteurs, traits

  def getClassesTextes(self):
      listeClasses = []
      dic_classes = {}
      cpt = 0
      for classe in self.textsList["classes"]:
          if classe not in dic_classes:
            dic_classes[classe] = cpt
            cpt+=1
          listeClasses.append(dic_classes[classe])
      return listeClasses, dic_classes

  def predict(self):
      return self.clf.predict([vecteurX])

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
  path_results = "results_char_motifs/"
  mkdirs(path_results)
  config = get_config(o)
  config_name = get_config_name(config)
  out_name = "%s/T%s_%s"%(path_results, o.task,  config_name)
  process_data(o, config, out_name)
