# bond: Bibliometrics on non-bibliometric disciplines

Repository containing code and data for our "...." paper.

## Intro

Our study is rooted in the context of the Italian National Scientific Qualification (NSQ). The NSQ is a national assessment exercise that qualifies scholars to the positions of Associate Professor and Full Professor. It consists of a quantitative and qualitative evaluation process, making use of both bibliometrics and a peer-review process. In the NSQ, academic disciplines are divided into two categories, i.e. citation-based disciplines (CDs) and non-citation-based disciplines (NDs). This division affects the bibliometrics used in the first part of the process. This study aims at exploring whether citation-based metrics can yield insights on how the peer-review of NDs is conducted.

Specifically, our work focuses on citation-centric metrics that capture the relationship between the candidate of the NSQ and the assessment committee (a.k.a. the commission), by measuring the overlap between their citation networks. Our hypothesis is that citations implicitly inform the qualitative peer-review evaluation, even in the case of NDs. In addition, our study exclusively utilizes open bibliographic data and metrics. This enables other scholars to reproduce our analysis and gives us the opportunity of investigating the open datasets’ coverage of the considered NDs, meaning the number of publications listed in the candidates’ CVs can be found in such datasets.

We ground our analysis on the data of the candidates and commissions that took part in the 2016, 2017, and 2018 sessions of the NSQ for the disciplines *Historical and General Linguistics* and *Mathematical Methods of Economics, Finance and Actuarial Sciences*, having Recruiting Fields (RF) 10/G1 and 13/D4 respectively according to the NSQ classification. And we collected the bibliographic metadata and citation data from the following open datasets: [Microsoft Academic Graph](https://www.microsoft.com/en-us/research/project/microsoft-academic-graph/), [OpenAIRE](https://www.openaire.eu/), [Crossref](https://www.crossref.org/), and [OpenCitations](https://opencitations.net/).

## Materials

### 1. Candidates' CV Json files

- [**cv_jsons** folder](https://github.com/sosgang/bond/tree/main/cv_jsons): contains all the json files extracted from the candidates' CVs (they were previously in PDF format). The folder is structured as follows:
  - NSQ session folders: named after the beginning date (e.g. "2016" for the 2016-18 session) contain
    - term folders: named after the order in which they took place (e.g. "term1" for the 1st term) contain:
      - role folders: named after the academic role the candidates applied to (e.g. "AP" for associate and "FP" for full professorship) contain:
        - field folders: named after the alphanumeric code of the RF in the taxonomy defined by the Ministerial Decree 159 (e.g. 10-G1 and 13-D4) contain:
          - candidate file: named after the application's unique ID. A unique ID is created for each application. Therefore if a candidate casts two applications in a session, they will be assigned two unique IDs: one for each application.
 
 
### 2. Bibliographic and citation data

- [**bib-cit_data**](https://github.com/sosgang/bond/tree/main/bib-cit_data): contains all the bibliographic and citation data of the candidates and the commission.
  - Candidates' data is divided into Jsons files that are named after the term the candidates applied in (e.g. "t1" for first term), the role (e.g. "AP" for Associate Professorship) and the field (e.g. "10-G1") they applied for.
    - Each Jsons file contains a dict of dicts. Keys are the candidates' identifiers and values are the candidates' dictionaries.
      - Each candidate's dictionary contains:
        - "AuIds" : list of MAG Author Ids found for the candidates
        - "pubbs" : list of publications contained in the candidate's CV as a list of dictionaries
          - Each publication is a dictionary with year, title, Paper Id, DOI, ISSN, ISBN, citing and cited publications
            - "citing" and "cited" : lists of citing and cited publications as lists of dictionaries
        - "pubbs_MAG" : structured as "pubbs"
  
- ### **citmetrics** containing the citation-based metrics calculated for each candidate
  - **"complete metrics.csv"*** contains all the calculated metrics for each candidate
  - Json files contains the same metrics in dict format divided by term, section and field
    - Files are named after the term number, section number and field identification code, separated by a dash
