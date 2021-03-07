import time
import sys
import pandas as pd   
import numpy as np
from sklearn import svm, tree
from sklearn.model_selection import cross_validate
from sklearn.metrics import *
from sklearn.utils import resample
from itertools import combinations
import ray

sections = ["AP", "FP"]
fields = ["10-G1", "13-D4"]
coverages = ["A","AB","ABC"]
classifierTypes = ["svm_1","svm_0.5","svm_0.1","svm_0.02","decisionTree"]
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

cpus = 4
ray.init(num_cpus=cpus, ignore_reinit_error=True)


def balanceSample(data):
	countSi = data[data.outcome == "Si"].shape[0]
	countNo = data[data.outcome == "No"].shape[0]
	if countSi > countNo:
		# resample Sis with stratification
		data_resampled = resample(data[data.outcome == "No"], 
											replace=True,			# sample with replacement
											n_samples=countSi,		# to match majority class
											random_state=123,		# reproducible results
											stratify=data[data.outcome == "No"])
		return pd.concat([data[data.outcome == "Si"], data_resampled])
		
	elif countSi < countNo:
		# resample Nos with stratification
		data_resampled = resample(data[data.outcome == "Si"], 
											replace=True,			# sample with replacement
											n_samples=countNo,		# to match majority class
											random_state=123,		# reproducible results
											stratify=data[data.outcome == "Si"])
		return pd.concat([data[data.outcome == "No"], data_resampled])
	return data


def isDivergent(y_pred):
	if y_pred.count("Si") == 0 or y_pred.count("No") == 0:
		return True
	return False


@ray.remote
def incremental(df,field,section,features,classifierType,coverage=["A"],doBalance=True):
	
	if classifierType not in ["svm_1","svm_0.5","svm_0.1","svm_0.02","decisionTree"]:
		print ("ERROR: classifierType should be 'svm' or 'decisionTree' - %s provided." % classifierType)
		sys.exit()
	
	# filter field, section and coverage, and remove NaN values
	temp = df[(df["field"] == field) & (df["role"] == section)]
	df_filtered = temp[temp["coverage"].isin(coverage)]
	
	df_TrainSet = df_filtered[df_filtered["term"].isin(list(range(1,5)))][features+["outcome"]].dropna()
	df_TestSet = df_filtered[df_filtered["term"].isin(list(range(5,6)))][features+["outcome"]].dropna()
		
	# Save this info before resampling
	res = dict()
	res["train (Si/No)"] = "%d (%d/%d)" % (df_TrainSet.shape[0], df_TrainSet[df_TrainSet.outcome == "Si"].shape[0], df_TrainSet[df_TrainSet.outcome == "No"].shape[0])
	res["test (Si/No)"] = "%d (%d/%d)" % (df_TestSet.shape[0], df_TestSet[df_TestSet.outcome == "Si"].shape[0], df_TestSet[df_TestSet.outcome == "No"].shape[0])
		
	# Resample test
	if doBalance:
		df_TrainSet = balanceSample(df_TrainSet)
	
	if df_TrainSet.shape[0] == 0 or df_TestSet.shape[0] == 0:
		print ("\tSKIP.")
		return
		
	if classifierType == "svm_1":
		clf = svm.SVC(kernel='linear', C=1, random_state=0)
	elif classifierType == "svm_0.5":
		clf = svm.SVC(kernel='linear', C=0.5, random_state=0)
	elif classifierType == "svm_0.1":
		clf = svm.SVC(kernel='linear', C=0.1, random_state=0)
	elif classifierType == "svm_0.02":
		clf = svm.SVC(kernel='linear', C=0.02, random_state=0)
	elif classifierType == "decisionTree":
		clf = tree.DecisionTreeClassifier(random_state=0)
		
	clf = clf.fit(df_TrainSet[features], df_TrainSet["outcome"])
		
	y_true = df_TestSet["outcome"].tolist()
	y_pred = clf.predict(df_TestSet[features]).tolist()
		
	if isDivergent(y_pred):
		res["divergent"] = True
	else:
		res = {**res,**classification_report(y_true, y_pred,output_dict=True)["weighted avg"]}
		res["precision"] = round(res["precision"],3)
		res["recall"] = round(res["recall"],3)
		res["f1-score"] = round(res["f1-score"],3)
		res["divergent"] = False
		res["pred Si/No"] = "(%d/%d)" % (y_pred.count("Si"), y_pred.count("No"))
	res["field"] = field
	res["role"] = section
	res["coverage"] = "".join(coverage)
	res["classifier"] = classifierType
	res["num-features"] = len(features)
	
	return {**res, **featureListToDict(features)}


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

for i in range(1,len(features)+1):
	start_time = time.time()
	counter = 0
	ray_results = list()
	for combination in list(combinations(features,i)):
		featureList = list(combination)
		for field in fields:
			for section in sections:
				for coverage in coverages:
					for classifierType in classifierTypes:
						ray_results.append(incremental.remote(df,field,section,featureList,classifierType,list(coverage),True))
						counter += 1
	
	duration1 = time.time() - start_time
	print ('Executing the for loop # ' + str(i) + ' took {:.3f} seconds.'.format(duration1))
	print ('Computing ' + str(counter) + ' models...')
	
	dictResultsModels = ray.get(ray_results)
	duration2 = time.time() - start_time
	print ('Executing the WHOLE COMPUTATION for loop #' + str(i) + ' took {:.3f} seconds.'.format(duration2))
	
	columnsOrdered = ["field","role","coverage","classifier","divergent","precision","recall","f1-score","train (Si/No)","test (Si/No)", "pred Si/No",
		"num-features", "cand", "co-au","cand_comm","comm_cand","BC", "CC","cand_other","other_cand","books", 
		"articles","other_pubbs","nd_m1","nd_m2","nd_m3", 'support'
	]
	results_iteration_df = pd.DataFrame(dictResultsModels).reindex(columns=columnsOrdered,copy=False)
	results_iteration_df.to_csv(outputFile_Partial % i, index=False)


# concatenate all results and save to single file
for i in range(1,len(features)+1):
	df = pd.read_csv(outputFile_Partial % i)
	if i == 1:
		results_total_df = df
	else:
		results_total_df = results_total_df.append(df)
results_total_df.to_csv(outputFile_Total, index=False)

# save results having f1-score >= 0.700 to file
best_results = results_total_df[(results_total_df["f1-score"] >= 0.7)]
best_results.to_csv(outputFile_F1, index=False)
