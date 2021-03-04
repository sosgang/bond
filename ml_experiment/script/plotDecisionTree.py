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
import mylib

inputFile = "../../complete_metrics.csv"

def myIncremental(df,field,section,features,classifierType,coverage=["A"],doBalance=True):
	
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
			df_TrainSet = mylib.balanceSample(df_TrainSet)
		
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
			clf = tree.DecisionTreeClassifier(random_state=2018)
		
		clf = clf.fit(df_TrainSet[features], df_TrainSet["outcome"])
		

		tree.plot_tree(clf,feature_names=features,class_names=clf.classes_)
		plt.show()
		
		y_true = df_TestSet["esito"].tolist()
		y_pred = clf.predict(df_TestSet[features]).tolist()
		
		print (classification_report(y_true, y_pred,output_dict=True))
		
		if mylib.isDivergent(y_pred):
			return {"divergent": True}
			
		return {
				"report": classification_report(y_true, y_pred,output_dict=True),
				"y_pred": y_pred,
				"divergent": False
				}

df = pd.read_csv(inputFile)

# Figure 7 
features = ["co-au","CC","books","nd_m1"]
resMetrics = myIncremental(df,"10-G1","AP",features,"decisionTree",list("AB"),False)
