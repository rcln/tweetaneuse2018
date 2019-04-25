#coding:utf-8
import sys
sys.path.append("rstr_max")
from tools import * 
import glob
import re
import numpy as np
import matplotlib.pyplot as plt 
import math
import json

def parse_file(path):
  lignes = open_utf8(path, True)
  dic = {}
  for lig in lignes:
    ID, classe = re.split("\|", lig)
    dic[ID] = classe
  return dic

def init_data_struct(classes_names):
  mes = ["TP", "FP", "FN", "VN"]
  d_classes = {}
  for name in classes_names:
    d_classes[name] = {}
    for s in mes:
      d_classes[name][s] = 0
  return d_classes

def compute_results(dic, has_date, verbose):
  all_F = []
  acc_data = [0, 0]
  out =""
  if verbose == True:
    print("  CLASSE\tPrecision\tRecall\tF-measure\tTP\tFP\tFN")
  l_classes = sorted(dic.keys())
  for classe in l_classes:
    scores = dic[classe]
    TP = float(scores["TP"])
    FP = scores["FP"]
    FN = scores["FN"]
    out+= classe+ str(scores)
    if TP==0:R=P=F1=0
    else:
      R = TP/(TP+FN)
      P = TP/(TP+FP)
      F1 = (2*P*R)/(P+R)
    acc_data[0]+=TP
    acc_data[1]+=FP+TP
    all_F.append(F1)
    if verbose==True:
      print("  '%s'"%classe[:10]+"\t"+"\t".join([str(round(x,4)) for x in [P,R, F1]])+"\t"+"\t".join([str(scores[x]) for x in ["TP", "FP",  "FN"]]))
  if acc_data[0]>0:
    accuracy = round(acc_data[0]/acc_data[1], 4)
  else:
    accuracy = 0
  dic = {"Accuracy": accuracy, "Macro-F1": round(moyenne(all_F), 4)}
#  dic = {"Macro-F1": round(moyenne(all_F), 4)}
#  dic = {"Accuracy": accuracy}
  if verbose==True:
    print("  Accuracy : %f"%accuracy)
    print("  Macro F1 : %f"%round(moyenne(all_F), 4))
  return dic

def get_scores(ref, pred, has_date, verbose):
  classes_names = set(ref.values())
  d_classes = init_data_struct(classes_names)
  missing = []
  eval_dates = {"dist":0, "dist_pond":0, "sim_gauss":0}
  for ID, classe in ref.items():
    if ID not in pred:
      missing.append(ID)
      continue
    if classe==pred[ID]:
      d_classes[classe]["TP"]+=1
      eval_dates["sim_gauss"]+=1/float(len(pred))
    else:
      d_classes[classe]["FN"]+=1
      d_classes[pred[ID]]["FP"]+=1
      if has_date==True:
        ecart_abs = float(int(classe)-int(pred[ID]))
        if ecart_abs<0:ecart_abs = -ecart_abs
        eval_dates["dist"]+=ecart_abs/len(pred)
        eval_dates["dist_pond"]+=ecart_abs*ecart_abs/len(pred)
        sim_gauss = (2.72818**(-(3.1415/10)*ecart_abs*ecart_abs))
        eval_dates["sim_gauss"]+=sim_gauss/len(pred)
  scores = compute_results(d_classes, has_date,verbose)
  if has_date:
    print(eval_dates)
    scores["sim_gauss"] = round(eval_dates["sim_gauss"], 4)
  if len(missing)>0:
    print("Missing : %s"%str(len(missing)))
  return scores, eval_dates
print("-"*20)
print("Usage : ARG1=GOLD_FILE ARG2= PATH_RESULTS")
print("-"*20)
if len(sys.argv)!=3:
  print("ARGS", sys.argv)
  exit()

liste_results = glob.glob(sys.argv[2]+"*")
ref = parse_file(sys.argv[1])

dic_pyplot = {}
D={}
has_date = False#for adapting to regression cases
verbose = False

for result_file in liste_results:
  print("\n Processing %s"%result_file[-80:])
  pred = parse_file(result_file)
  scores, scores_date = get_scores(ref, pred, has_date, verbose)
  if verbose==False:
    print(scores)
  maxlen = re.findall("maxlen-([0-9])", result_file)[0]
  minlen = re.findall("minlen-([0-9])", result_file)[0]
  if int(minlen)>1:continue
  parametres = re.findall("([a-z]*)-([A-Z][a-z]*|[0-9][0-9]*)", result_file)
  print(scores)
  print(parametres)
  parametres = {x:y for x, y in parametres}
  if "words" not in parametres:
    parametres["words"]="False"
  name_config = ""
  par_config = ["ngrams", "words"]
  for par in par_config:
    name_config+= "_"+par+"-"+parametres[par]
  etiq_scores = sorted(scores.keys())
  dic_pyplot.setdefault(name_config, [])
  dic_pyplot[name_config].append([parametres[x] for x in ["minlen","maxlen","minsup","maxsup"]]+list([scores[x] for x in etiq_scores]))

dic_pyplot = {x:sorted(y) for x,y in dic_pyplot.items()}
dic_name = "pyplot.json"
w = open(dic_name, "w")
w.write(json.dumps(dic_pyplot, indent = 2))
w.close()
print("Output written in %s"%dic_name)

for lg, Dic in D.items():
  legendes = []
  print(Dic.keys())
  for tup, scores in Dic.items():
    nom = "_".join(list(tup))
    y = []
    print(scores)
    for dic in scores:
      if len(dic)=={}:continue
      for a,b in dic.items():
        y.append(b)
    X = range(1, len(y)+1)
    plt.plot(X,y)
    legendes.append(tup)
  plt.legend(legendes)
  plt.savefig("%s.png"%lg) 
  plt.show() 
