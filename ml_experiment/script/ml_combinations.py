import time
import sys
import pandas as pd   
import numpy as np
#import matplotlib.pyplot as plt
from sklearn import svm, tree
from sklearn.model_selection import cross_validate
from sklearn.metrics import *
from sklearn.utils import resample
from itertools import combinations
import mylib

sections = ["AP", "FP"]
fields = ["10-G1", "13-D4"]
coverages = ["A","AB","ABC"]
features= ['cand', 'co-au',
			'cand_comm', 'comm_cand',
			'BC', 'CC',
			'cand_other', 'other_cand',
			'books', 'articles', 'other_pubbs' ,
			"nd_m1","nd_m2","nd_m3"
			]
inputFile = "../../complete_metrics.csv"
outputFile_Partial = "../data/combinations_%d_features.csv"
outputFile_Total = "../data/combinations_ALL_features.csv"
outputFile_F1 = "../data/combinations_F1_0.7.csv"

def featureListToDict(features):
	res = dict()
	for feature in features:
		res[feature] = "X"
	return res


def filterDF(df,field,section,terms,features,coverage):
	temp = df[(df["field"] == field) & (df["role"] == section)]
	temp2 = temp[temp["coverage"].isin(coverage)]
	return temp2[temp2["term"].isin(terms)][features+["outcome"]].dropna()


def featureListToDict(features):
	res = dict()
	for feature in features:
		res[feature] = "X"
	return res


df = pd.read_csv(inputFile)
counter = 0
for i in range(1,len(features)+1):
	res = pd.DataFrame(columns=["field","role","coverage","classifier","divergent","precision","recall","f1-score","train (Si/No)","test (Si/No)", "pred Si/No",
								"index-feat.comb.", "num-features", "cand", "co-au","cand_comm","comm_cand","BC", "CC","cand_other","other_cand","books", 
								"articles","other_pubbs","nd_m1","nd_m2","nd_m3"
								])
	for combination in list(combinations(features,i)):
		print ("%d) %d" % (i, counter))
		counter += 1
		featureList = list(combination)
		for field in ["10-G1", "13-D4"]:
			for section in sections:
				for coverage in coverages:
					for classifierType in ["svm_1","svm_0.5","svm_0.1","svm_0.02","decisionTree"]:
						resMetrics = mylib.incremental(df,field,section,featureList,classifierType,list(coverage),True)
						
						if resMetrics["divergent"]:
							print ("\t%s %s %s %s - divergent" % (field, section, coverage, classifierType))
							d = dict()
							d["field"] = field
							d["role"] = section
							d["coverage"] = coverage
							d["classifier"] = classifierType
							tempTrain = filterDF(df,field,section,list(range(1,5)),featureList,list(coverage))
							d["train (Si/No)"] = "%d (%d/%d)" % (tempTrain.shape[0],tempTrain[tempTrain.outcome == "Si"].shape[0],tempTrain[tempTrain.outcome == "No"].shape[0])
							tempTest = filterDF(df,field,section,[5],featureList,list(coverage))
							d["test (Si/No)"] = "%d (%d/%d)" % (tempTest.shape[0],tempTest[tempTest.outcome == "Si"].shape[0],tempTest[tempTest.outcome == "No"].shape[0]) #getSiNo(df,field,section,[5],featureList,list(coverage))
							d["divergent"] = True
							d["index-feat.comb."] = counter
							d["num-features"] = i
							f = featureListToDict(featureList)
							d = {**d, **f}
							res = res.append(d, ignore_index=True)
							continue
						
						d = resMetrics["report"]["weighted avg"]
						d["field"] = field
						d["role"] = section
						d["coverage"] = coverage
						d["classifier"] = classifierType
						tempTrain = filterDF(df,field,section,list(range(1,5)),featureList,list(coverage))
						d["train (Si/No)"] = "%d (%d/%d)" % (tempTrain.shape[0],tempTrain[tempTrain.outcome == "Si"].shape[0],tempTrain[tempTrain.outcome == "No"].shape[0])
						tempTest = filterDF(df,field,section,[5],featureList,list(coverage))
						d["test (Si/No)"] = "%d (%d/%d)" % (tempTest.shape[0],tempTest[tempTest.outcome == "Si"].shape[0],tempTest[tempTest.outcome == "No"].shape[0]) #getSiNo(df,field,section,[5],featureList,list(coverage))
						d["pred Si/No"] = "(%d/%d)" % (resMetrics["y_pred"].count("Si"), resMetrics["y_pred"].count("No"))
						d["divergent"] = False
						d["index-feat.comb."] = counter
						d["num-features"] = i
						f = featureListToDict(featureList)
						d = {**d, **f}
						
						res = res.append(d, ignore_index=True)
						continue
	# save results computed using i feature/s
	res.to_csv(outputFile_Partial % i)


# concatenate all results in a single file
for i in range(1,len(features)+1):
	df = pd.read_csv(outputFile_Partial % i)
	if i == 1:
		res = df
	else:
		res = res.append(df)
res.to_csv(outputFile_Total)


# concatenate results having f1-score >= 0.700 in a single file
for i in range(1,len(features)+1):
	df = pd.read_csv(outputFile_Partial % i)
	if i == 1:
		res = df[(df["f1-score"] >= 0.7)]
	else:
		res = res.append(df[(df["f1-score"] >= 0.7)])	
res.to_csv(outputFile_F1)

