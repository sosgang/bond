import time
import sys
import pandas as pd   
import numpy as np
import matplotlib.pyplot as plt
from sklearn import svm, tree
from sklearn.model_selection import cross_validate
from sklearn.metrics import *
from sklearn.utils import resample
from itertools import combinations

def balanceSample(data):
	countSi = data[data.outcome == "Si"].shape[0]
	countNo = data[data.outcome == "No"].shape[0]
	if countSi > countNo:
		# resample Sis with stratification
		data_resampled = resample(data[data.outcome == "No"], 
											replace=True,     # sample with replacement
											n_samples=countSi,    # to match majority class
											random_state=123, # reproducible results
											stratify=data[data.outcome == "No"])
		return pd.concat([data[data.outcome == "Si"], data_resampled])
		
	elif countSi < countNo:
		# resample Nos with stratification
		data_resampled = resample(data[data.outcome == "Si"], 
											replace=True,     # sample with replacement
											n_samples=countNo,    # to match majority class
											random_state=123, # reproducible results
											stratify=data[data.outcome == "Si"])
		return pd.concat([data[data.outcome == "No"], data_resampled])
	return data


def isDivergent(y_pred):
	if y_pred.count("Si") == 0 or y_pred.count("No") == 0:
		return True
	return False


def incremental(df,field,section,features,classifierType,coverage=["A"],doBalance=True):
	
	if classifierType not in ["svm_1","svm_0.5","svm_0.1","svm_0.02","decisionTree"]:
		print ("ERROR: classifierType should be 'svm' or 'decisionTree' - %s provided." % classifierType)
		sys.exit()
	
	# filter field, section and coverage, and remove NaN values
	temp = df[(df["field"] == field) & (df["role"] == section)]
	df_filtered = temp[temp["coverage"].isin(coverage)]
	
	for i in range(5,6):
		terms = list(range(1,i))
		df_TrainSet = df_filtered[df_filtered["term"].isin(terms)][features+["outcome"]].dropna()
		df_TestSet = df_filtered[df_filtered["term"].isin(list(range(i,6)))][features+["outcome"]].dropna()
		
		# RESAMPLE TEST
		if doBalance:
			df_TrainSet = balanceSample(df_TrainSet)
		
		if df_TrainSet.shape[0] == 0 or df_TestSet.shape[0] == 0:
			print ("\tSKIP.")
			continue
		
		##scoring = ['precision_macro', 'recall_macro', 'f1_macro']
		if classifierType == "svm_1":
			clf = svm.SVC(kernel='linear', C=1, random_state=0) #   ,class_weight='balanced', probability=True)
		elif classifierType == "svm_0.5":
			clf = svm.SVC(kernel='linear', C=0.5, random_state=0)
		elif classifierType == "svm_0.1":
			clf = svm.SVC(kernel='linear', C=0.1, random_state=0)
		elif classifierType == "svm_0.02":
			clf = svm.SVC(kernel='linear', C=0.02, random_state=0)
		elif classifierType == "decisionTree":
			clf = tree.DecisionTreeClassifier()
		
		clf = clf.fit(df_TrainSet[features], df_TrainSet["outcome"])
		
		y_true = df_TestSet["outcome"].tolist()
		y_pred = clf.predict(df_TestSet[features]).tolist()
		
		if isDivergent(y_pred):
			return {"divergent": True}
			
		return {
				"report": classification_report(y_true, y_pred,output_dict=True),
				"y_pred": y_pred,
				"divergent": False,
				}
		

