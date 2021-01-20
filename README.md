# bond: Bibliometrics on non-bibliometric disciplines

Repository containing code and data for our "...." paper.

## Intro

Our study focuses on the Italian National Scientific Qualification (NSQ). The NSQ is a national assessment exercise that qualifies scholars to the positions of Associate Professor and Full Professor. It consists of a quantitative and qualitative evaluation process, making use of both bibliometrics and a peer-review process. In the NSQ, academic disciplines are divided into two categories, i.e. citation-based disciplines (CDs) and non-citation-based disciplines (NDs). This division affects the bibliometrics used in the first part of the process. This study aims at exploring whether citation-based metrics can yield insights on how the peer-review of NDs is conducted. Specifically, our work focuses on citation-centric metrics devised to capture the relationship between the candidate of the NSQ and the assessment committee, by measuring the overlap between their citation networks. Our hypothesis is that citations implicitly inform the qualitative peer-review evaluation, even in the case of NDs. In addition, our study exclusively utilizes open bibliographic data and metrics. It also gives us the opportunity of investigating the open datasets’ coverage of the considered NDs, meaning the number of publications listed in the candidates’ CVs can be found in such datasets.




## Summary of contents:

- ### **cv_jsons** : Json files extracted from the candidates' CVs
  - Files are named after the candidate's ID number, Family Name and First Name, separated by a dash
  
- ### **bib-cit_data** : Json files containing the bibliographic and citation data of each candidate
  - Data are divided by term, section and field
  - Files are named after the term number, section number and field identification code, separated by a dash
  
- ### **citmetrics** containing the citation-based metrics calculated for each candidate
  - **"complete metrics.csv"*** contains all the calculated metrics for each candidate
  - Json files contains the same metrics in dict format divided by term, section and field
    - Files are named after the term number, section number and field identification code, separated by a dash
