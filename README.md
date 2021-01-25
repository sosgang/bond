# bond: Bibliometrics on non-bibliometric disciplines

Repository containing code and data for our "Do open citations inform the qualitative peer-review evaluation in research assessments? An analysis of the Italian National Scientific Qualification" paper.

1. [Introduction](##Introduction)
2. [Resulting data](##Resulting data)
3. [Reproducing the data collection](##Reproducing the data collection)


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

- [**bib-cit_data**](https://github.com/sosgang/bond/tree/main/bib-cit_data): contains all the bibliographic and citation data of the candidates and the commission. Candidates' data is divided into Jsons files that are named after the term candidates applied in (e.g. "t1" for first term), the role (e.g. "AP" for Associate Professorship) and the field (e.g. "10-G1") they applied for. Each Jsons file contains a dict of dicts. Keys are the candidates' identifiers and values are the candidates' dictionaries. Each candidate's dictionary contains:
  - "AuIds" : list of MAG Author Ids found for the candidates
  - "pubbs" : list of publications contained in the candidate's CV as a list of dictionaries
    - Each publication is a dictionary with year, title, Paper Id, DOI, ISSN, ISBN, citing and cited publications
      - "citing" and "cited" : lists of citing and cited publications as lists of dictionaries
  - "pubbs_MAG" : structured as "pubbs", contains the list of publications found in MAG that the candidate did not included in her/his CV


### 2.3 Citation networks and citation-based metrics
  
- [**citmetrics**](https://github.com/sosgang/bond/tree/main/citmetrics): contains information on the citation network built for each candidate connecting her/his publications with those of her/his evaluating commission. Candidates' data is divided into Jsons files that are named after the term candidates applied in (e.g. "t1" for first term), the role (e.g. "AP" for Associate Professorship) and the field (e.g. "10-G1") they applied for. Each Jsons file contains a dict of dicts. Keys are the candidates' identifiers and values are the candidates' dictionaries. Each candidate's dictionary contains:
  - "bc" : information on the publications cited by both a publication authored by the candidate and a publication authored by at least one member of the commission.
    - "articles": dictionary where: each key is a string with the Paper Id of the publication authored by the candidated and the Paper Id of the publication authored by at least one member of the commission;  each value is the number of publications they both cite;
    - "number" : total number of unique publications cited by both a publication authored by the candidate and a publication authored by at least one member of the commission. 
  - "cand_nodes" : overall number of publications authored by the candidate found in the open sources of use.
  - "cand_paths" : dictionary with information on the paths starting from a publication authored by the candidate and ending at a publication authored by at least one member of the commission. Each key is the length of the paths (the number of edges (citations) between the two publications). Each value is a list of lists. Each list contains the Paper Ids of the starting and ending publications.
  - "cc" : information on the publications citing both a publication authored by the candidate and a publication authored by at least one member of the commission.
    - "articles": dictionary where: each key is a string with the Paper Id of the publication authored by the candidated and the Paper Id of the publication authored by at least one member of the commission; each value is the number of publications citing both;
    - "number" : total number of unique publications citing both a publication authored by the candidate and a publication authored by at least one member of the commission. 
  - "co-au" : dictionary with information about the publications authored by both the candidate and at least one member of the commission.
    - "articles" is the list of Paper Ids of the co-authored publications.
    - "number" is the number of co-authored publications.
  - "comm_nodes" : overall number of publications authored by at least one member of the commission.
  - "comm_paths" : dictionary with information on the paths starting from a publication authored by at least one member of the commission and ending at a publication authored by the candidate.Each key is the length of the paths (the number of edges (citations) between the two publications). Each value is a list of lists. Each list contains the Paper Ids of the starting and ending publications. 
  - "other" : dictionary with information on citations from and to publications not authored by neither the candidate nor any member of the commission.
    - "cand_other" : number of other publications cited by a publication authored by the candidate.
    - "comm_other" : number of other publications cited by a publication authored by at least one member of the commission.
    - "other_cand" : number of other publications citing a publication authored by the candidate.
    - "other_comm" : number of other publications citing a publication authored by at least one member of the commission.
  - "other_nodes" : overall number of publications not authored neither by the candidate nor by any member of the commission.
      
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

- [**coverage.csv**](https://github.com/sosgang/bond/blob/main/coverage.csv) contains the coverage information calculated for each candidate. Each row corresponds to one candidate. The columns are the following:
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
 
## 3. Reproducing the data collection

### 3.1 Necessary materials

  - [**cv_jsons** folder](https://github.com/sosgang/bond/tree/main/cv_jsons): the folder containing the json files extracted from the candidates' CVs. The internal structure of the folder should remain as is at the moment: cv_jsons/asn_session name/term name/role name/field name/
  - [**data_collection** folder](https://github.com/sosgang/bond/tree/main/data_collection): the folder containing the python files for the data collection process.

### 3.2 Data collection
- **bond_execution.py** : executes the entire collection process by calling all the other necessary python files, and saves the results in json format and csv.
- meta_extraction.py : extracts the publications' metadata from the CV json files, disambiguating duplicate publications, and stores it in a dictionary.
- add_info.py : adds other types of information to the dictionary: the full name of the candidate, the ANVUR metrics, the outcome of the NSQ and the coverage of the candidate's publications.
- id_search.py : searches for each candidate’s Author Ids in MAG and for each article’s DOI in OA and CR.
- bib_retrieval.py : queries MAG for each Author Id and retrieves all the available bibliographic information for each Author Id.
- cit_retrieval.py : retrieves the metadata of all the cited and citing publications for each candidate's publication from MAG, COCI and CR.

### 3.3 Citation network analysis and metrics
- graph_analysis.py : creates and analyzes citation networks, and calculates our citation-based metrics for each candidate.

### 3.4 Analyzing coverage






