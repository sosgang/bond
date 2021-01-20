# bond: Bibliometrics on non-bibliometric disciplines

Repository containing code and data for our "...." paper.

## Intro

Our study is rooted in the context of the Italian National Scientific Qualification (NSQ). The NSQ is a national assessment exercise that qualifies scholars to the positions of Associate Professor and Full Professor. It consists of a quantitative and qualitative evaluation process, making use of both bibliometrics and a peer-review process. In the NSQ, academic disciplines are divided into two categories, i.e. citation-based disciplines (CDs) and non-citation-based disciplines (NDs). This division affects the bibliometrics used in the first part of the process. This study aims at exploring whether citation-based metrics can yield insights on how the peer-review of NDs is conducted.

Specifically, our work focuses on citation-centric metrics that capture the relationship between the candidate of the NSQ and the assessment committee (a.k.a. the commission), by measuring the overlap between their citation networks. Our hypothesis is that citations implicitly inform the qualitative peer-review evaluation, even in the case of NDs. In addition, our study exclusively utilizes open bibliographic data and metrics. This enables other scholars to reproduce our analysis and gives us the opportunity of investigating the open datasets’ coverage of the considered NDs, meaning the number of publications listed in the candidates’ CVs can be found in such datasets.

We ground our analysis on the data of the candidates and commissions that took part in the 2016, 2017, and 2018 sessions of the NSQ for the disciplines *Historical and General Linguistics* and *Mathematical Methods of Economics, Finance and Actuarial Sciences*, having Recruiting Fields (RF) 10/G1 and 13/D4 respectively according to the NSQ classification. And we collected the bibliographic metadata and citation data from the following open datasets: [Microsoft Academic Graph](https://www.microsoft.com/en-us/research/project/microsoft-academic-graph/), [OpenAIRE](https://www.openaire.eu/), [Crossref](https://www.crossref.org/), and [OpenCitations](https://opencitations.net/).

## Materials

### 1. Candidates' CV Json files

- **cv_jsons** folder: contains all the json files extracted from the candidate CVs (they previously were in PDF format). The folder is structured as follows:
  - NSQ session folder: named after the beginning date (e.g. "2016" for the 2016-18 session)
    - term folders: named after the order in which they took place (e.g. "term1" for the 1st term)
      - role folders: named after the academic role the candidates applied to (e.g. "AP" for associate and "FP" for full professorship)
        - field folders: named after the alphanumeric code of the RF in the taxonomy defined by the Ministerial Decree 159 (e.g. 10-G1 and 13-D4)
          - candidate file: named after the application's unique ID, the family name and first name of the candidate. A unique ID is created for each application. Therefore if a candidate casts two applications in a session, they will be assigned two unique IDs: one for each application.
 

- ### **bib-cit_data** : Json files containing the bibliographic and citation data of each candidate
  - Data are divided by term, section and field
  - Files are named after the term number, section number and field identification code, separated by a dash
  
- ### **citmetrics** containing the citation-based metrics calculated for each candidate
  - **"complete metrics.csv"*** contains all the calculated metrics for each candidate
  - Json files contains the same metrics in dict format divided by term, section and field
    - Files are named after the term number, section number and field identification code, separated by a dash
