# bond: Bringing Open data in Non-citation-based Disciplines

Repository containing code and data for our **"Do open citations inform the qualitative peer-review evaluation in research assessments? An analysis of the Italian National Scientific Qualification"** paper.

1. [Introduction](#1-introduction)
2. [Resulting data](#2-resulting-data)
3. [Reproducing the data collection](#3-reproducing-the-data-collection)
4. [Analyzing coverage](#4-analyzing-coverage)
5. [Reproducing the citation network visualization](#3-reproducing-the-citation-network-visualization)
6. [Machine learning experiment](#6-machine-learning-experiment)

## 1. Introduction

Our study is rooted in the context of the Italian National Scientific Qualification (NSQ). The NSQ is a national assessment exercise that qualifies scholars to the positions of Associate Professor and Full Professor. It consists of a quantitative and qualitative evaluation process, making use of both bibliometrics and a peer-review process. In the NSQ, academic disciplines are divided into two categories, i.e. citation-based disciplines (CDs) and non-citation-based disciplines (NDs). This division affects the bibliometrics used in the first part of the process. This study aims at exploring whether citation-based metrics can yield insights on how the peer-review of NDs is conducted.

Specifically, our work focuses on citation-centric metrics that capture the relationship between the candidate of the NSQ and the assessment committee (a.k.a. the commission), by measuring the overlap between their citation networks. Our hypothesis is that citations implicitly inform the qualitative peer-review evaluation, even in the case of NDs. In addition, our study exclusively utilizes open bibliographic data and metrics. This enables other scholars to reproduce our analysis and gives us the opportunity of investigating the open datasets’ coverage of the considered NDs, meaning the number of publications listed in the candidates’ CVs can be found in such datasets.

We ground our analysis on the data of the candidates and commissions that took part in the 2016, 2017, and 2018 sessions of the NSQ for the disciplines *Historical and General Linguistics* and *Mathematical Methods of Economics, Finance and Actuarial Sciences*, having Recruiting Fields (RF) 10/G1 and 13/D4 respectively according to the NSQ classification. And we collected the bibliographic metadata and citation data from the following open datasets: [Microsoft Academic Graph](https://www.microsoft.com/en-us/research/project/microsoft-academic-graph/), [OpenAIRE](https://www.openaire.eu/), [Crossref](https://www.crossref.org/), and [OpenCitations](https://opencitations.net/).

 
## 2. Resulting data

### 2.1 Candidates' CV Json files

- [**cv_jsons** folder](https://github.com/sosgang/bond/tree/main/cv_jsons): contains all the json files extracted from the candidates' CVs (they were previously in PDF format). The folder is structured as follows:
  - NSQ session folders: named after the beginning date (e.g. "2016" for the 2016-18 session) contain
    - term folders: named after the order in which they took place (e.g. "term1" for the 1st term) contain:
      - role folders: named after the academic role the candidates applied to (e.g. "AP" for associate and "FP" for full professorship) contain:
        - field folders: named after the alphanumeric code of the RF in the taxonomy defined by the Ministerial Decree 159 (e.g. 10-G1 and 13-D4) contain:
          - candidate file: named after the application's unique ID. A unique ID is created for each application. Therefore if a candidate casts two applications in a session, she/he will be assigned two unique IDs: one for each application.

 
### 2.2 Bibliographic and citation data

- [**complete_data** folder](https://github.com/sosgang/bond/tree/main/complete_data): contains all the bibliographic and citation data of the candidates and the commission. Files ending in "complete" are candidates' files. Whereas, files ending in "cit" are commission members' files. Each file contains a dictionary with all the bibliographic and citation data of one candidate or one member of the commission. Candidate files are named after the ASN session they applied in, the term they applied in (e.g. "1" for first term), the role (e.g. "AP" for Associate Professorship) and the field (e.g. "10-G1") they applied for, and their unique Id. Commission member files are named after the ASN session they took part in, the field (e.g. "10-G1") they belong to, and their unique Id. Each  dictionary contain:
  - "AuIds" : list of MAG Author Ids found for the author
  - "citmetrics" : the citation-based and non-citation-based metrics resulting from the citation network analysis
  - "coverage" : information on the coverage of the candidate's publications
  - "fullname" : list of the candidate's name and family name
  - "ind_anvur" : list of the ANVUR non-citation-based metrics and outcome of the NSQ
  - "pubbs" : list of publications contained in the candidate's CV as a list of dictionaries
    - Each publication is a dictionary with year, title, Paper Id, DOI, ISSN, ISBN, citing and cited publications
      - "citing" and "cited" : lists of citing and cited publications as lists of dictionaries
  - "pubbs_MAG" : structured as "pubbs", contains the list of publications found in MAG that the candidate did not included in her/his CV
  - 


### 2.3 Citation networks and citation-based metrics
      
- [**complete_metrics.csv**](https://github.com/sosgang/bond/blob/main/complete_metrics.csv) : contains the citation-based metrics calculated for each candidate. Each row corresponds to one candidate. The columns are the following:
  - "coverage" : level of coverage of the candidate's publications by the open sources of use.
    - "A" >= 75% or >= 15 CV publications found;
    - "B" < 70% of CV publications but additional publications not listed in the CV were found in MAG to reach a number of found publications comparable to the original one;
    - "C" few or no publications found;
  - "term" : term the candidate applied in.
  - "role" : role the candidate applied for.
  - "field" : field the candidate applied for.
  - "id" : unique ID of the application.
  - "cand" : overall number of publications authored by the candidate found in the open sources of use.
  - "books" : number of books authored by the candidate.
  - "articles" : number of journal articles authored by the candidate.
  - "other_pubbs" : number of other kinds of publications (e.g. proceedings articles and workshop papers) authored by the candidate.
  - "co-au" : number of publications authored by both the candidate and at least one member of the commission.
  - "cand_comm" : number of citations going from a candidate’s publication to a publication authored by at least one member of the commission.
  - "comm_cand" : number of citations going from a publication authored by at least one member of the commission to a candidate’s publication.
  - "bc" : number of publications cited by both a publication authored by the candidate and a publication authored by at least one member of the commission.
  - "cc" : number of publications citing both a publication authored by the candidate and a publication authored by at least one member of the commission.
  - "cand_other" : number of other publications (i.e. which are not authored neither by the candidate nor by any member of the commission) cited by a publication authored by the candidate.
  - "other_cand" : number of other publications (i.e. which are not authored neither by the candidate nor by any member of the commission) citing a publication authored by the candidate.
  - "nd_m1" : number of books authored by the candidate; bibliometric retrieved from Scopus and Web of Science, and calculated by ANVUR.
  - "nd_m2" : number of book chapters authored by the candidate; bibliometric retrieved from Scopus and Web of Science, and calculated by ANVUR.
  - "nd_m3" : number of papers authored by the candidate; bibliometric retrieved from Scopus and Web of Science, and calculated by ANVUR.
  - "outcome" : outcome of the NSQ.

### 2.4 Coverage data

- [**coverage.csv**](https://github.com/sosgang/bond/blob/main/coverage/coverage.csv) contains the coverage information calculated for each candidate. Each row corresponds to one candidate. The columns are the following:
  - "cov_sect" : level of coverage of the candidate's publications by the open sources of use.
    - "A" >= 75% or >= 15 CV publications found;
    - "B" < 70% of CV publications but additional publications not listed in the CV were found in MAG to reach a number of found publications comparable to the original one;
    - "C" few or no publications found;
  - "term" : term the candidate applied in.
  - "role" : role the candidate applied for.
  - "field" : field the candidate applied for.
  - "id" : unique ID of the application.
  - "MAG" : raw number of publications authored by the candidate found in Microsoft Academic Graph.
  - "OA" : raw number of publications authored by the candidate found in OpenAIRE.
  - "CR" : raw number of publications authored by the candidate found in CrossRef.
  - "combined" : raw number of publications found when the open sources of use are combined.
  - "MAG% : percentage of the number of publications authored by the candidate found in Microsoft Academic Graph over the total number of unique publications in the CV.
  - "OA%" : percentage of the number of publications authored by the candidate found in OpenAIRE over the total number of unique publications in the CV.
  - "CR%" : percentage of the number of publications authored by the candidate found in Crossref over the total number of unique publications in the CV.
  - "combined%" : percentage of the number of publications authored by the candidate found over the total number of unique publications in the CV when the open sources of use are combined.
  - "total_CV" : total number of unique publications in the candidate's cv
 
## 3. Reproducing the data collection and the citation network analysis

### 3.1 Materials

- [**cv_jsons** folder](https://github.com/sosgang/bond/tree/main/cv_jsons)
- All the files in [**data_collection** folder](https://github.com/sosgang/bond/tree/main/data_collection)
 - [stopwords-it.txt](https://github.com/sosgang/bond/blob/main/stopwords-it.txt) : list of stopwords in italian
 - [indicatoriCalcolati-ASN16-18.tsv](https://github.com/sosgang/bond/blob/main/indicatoriCalcolati-ASN16-18.tsv) : file containing the ANVUR metrics and outcomes for each candidate
 - [commissions.csv](https://github.com/sosgang/bond/blob/main/commissions.csv) : file containing initial bibliographic metadata of the members of the commissions
 - bond_execution.py : executes the entire collection process by calling all the other necessary python files, saving the bibliographic and citation data in jsons in separate folders at numerous steps throughout the process, and storing the final metrics in a csv file. This ensures that no information is lost if the computation suddenly shuts down.
 - meta_extraction.py : extracts the publications' metadata from the CV json files, disambiguating duplicate publications, and stores it in a dictionary.
 - add_info.py : adds other types of information to the dictionary: the full name of the candidate, the ANVUR metrics, the outcome of the NSQ and the coverage of the candidate's publications.
 - id_search.py : searches for each candidate’s Author Ids in MAG and for each article’s DOI in OA and CR.
 - bib_retrieval.py : queries MAG for each Author Id and retrieves all the available bibliographic information for each Author Id.
 - cit_retrieval.py : retrieves the metadata of all the cited and citing publications for each candidate's publication from MAG, COCI and CR.
 - graph_analysis.py : creates and analyzes citation networks, and calculates our citation-based metrics for each candidate.

### 3.2 Execution
- [**bond_execution.py**](https://github.com/sosgang/bond/blob/main/data_collection/bond_execution.py): executes the entire collection process. Before running this code, it is necessary to make sure that the folder and file paths at the end of this python file correspond to the appropriate ones. If, for whatever reason, the execution is stopped, it is sufficient to run this python file again.

## 4. Analyzing coverage

### 4.1 Materials

- [**complete_data** folder](https://github.com/sosgang/bond/tree/main/complete_data)
- The python files contained in [**coverage** folder](https://github.com/sosgang/bond/blob/main/coverage):
 - coverage.py : executes the functions for calculating the coverage of the CV publications of each candidate and stores the results in a CSV file.
 - search_OA_CR.py : searches for each publication in OpenAIRE and Crossref.

### 4.2 Execution

- [**coverage.py**](https://github.com/sosgang/bond/blob/main/coverage/coverage.py): executes the functions for calculating the coverage. Before running this code, it is necessary to make sure that the folder and file paths at the end of this python file correspond to the appropriate ones.

## 5. Reproducing the citation network visualization

### 5.1 Materials

- [**complete_data** folder](https://github.com/sosgang/bond/tree/main/complete_data)
- The python files contained in [**visualization** folder](https://github.com/sosgang/bond/blob/main/visualization):
 - visualization.py : executes the functions for creating a graph and a diagram representing the citation network of one candidate.
 - venn.svg : diagram mold which is modified to represent the candidate's information

### 5.2 Execution

- [**visualization.py**](https://github.com/sosgang/bond/blob/main/visualization/visualization.py): executes the functions for creating a graph and a diagram representing the citation network of one candidate. Before running this code, it is necessary to make sure that the folder path at the end of this python file correspond to the appropriate ones, and to specify the correct information that identify the candidate.

## 6. Machine learning experiment

### 6.1 Materials

- [**ml_experiment/data** folder](https://github.com/sosgang/bond/tree/main/ml_experiment/data): contains both the input file (i.e. results.csv) for the python scripts that perform the analysis, and the output produced by the scripts.
  - [**results.csv**](https://github.com/sosgang/bond/tree/main/ml_experiment/data/results.csv): the citation-based metrics calculated for each candidate. Each row corresponds to one candidate. This file is the input of the python scripts.
  - [**combinations_F1_0.7.csv**](https://github.com/sosgang/bond/tree/main/ml_experiment/data/combinations_F1_0.7.csv): the results of the classifiers having f1-score >= 0.700. This file is the output of the experiment (script file: ml_combinations.py).
  - [**combinations_ALL_features.zip**](https://github.com/sosgang/bond/tree/main/ml_experiment/data/combinations_ALL_features.zip): an archive containing the results of all the 982,980 computed classifiers in a single file. This file is the output of the experiment (script file: ml_combinations.py).
  - [**combinations_i_features.zip**](https://github.com/sosgang/bond/tree/main/ml_experiment/data/combinations_i_features.zip): an archive containing the same data contained in combinations_ALL_features.zip split in multiple files. This file is the output of the experiment (script file: ml_combinations.py).

### 6.2 Execution

- [**ml_experiment/script** folder](https://github.com/sosgang/bond/tree/main/ml_experiment/script): contains the python scripts developed for the experiment based on machine learning techniques presented in the paper.
  - [**ml_combinations.py**](https://github.com/sosgang/bond/tree/main/ml_experiment/script/ml_combinations.py): the script evaluates the classifiers that can be computed using all the possible combinations of metrics, input data coverages and classification algorithms, for each field and role. The classifiers are trained on the data about candidates to the first four terms of the NSQ, and are tested on the candidates of the last term.
  - [**plotDecisionTree.py**](https://github.com/sosgang/bond/tree/main/ml_experiment/script/plotDecisionTree.py): the script plots the decision tree presented in Figure 7 in the paper.
  - [**mylib.py**](https://github.com/sosgang/bond/tree/main/ml_experiment/script/mylib.py): the library file containing functions used by the python scripts.
  

