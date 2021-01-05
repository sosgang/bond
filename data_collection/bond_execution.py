'''
Python file with calls to all the necessary functions
for collecting the citation data of both the candidates and the commission
'''
import time
import logging
import csv
from meta_extraction import *
from id_search import *
from bib_retrieval import *
from cit_retrieval import *
from graph_analysis import *
from add_info import *


def BoND(cand_jsons_path, comm_csv_path, outcomes_path):

    logging.basicConfig(filename='my_log.log', level=logging.ERROR,
                        format='%(asctime)s %(levelname)s %(name)s %(message)s')
    logger = logging.getLogger(__name__)

    cv_dict = extracting_metadata(cand_jsons_path, comm_csv_path)  # extracting metadata from the CV jsons

    outcome_dict = adding_name_outcome(cv_dict, outcomes_path)  # adding clean name and outcome

    ids_dict = adding_ids(logger, outcome_dict)  # adding AuIds and DOIs to the existing metadata

    bib_dict = adding_bib(ids_dict)  # adding extra publications found in MAG

    cit_dict = adding_cit(logger, bib_dict)  # adding citations for each publications

    metrics_dict = adding_graphmetrics(cit_dict)  # creating, analyzing networks and

    complete_dict = adding_cov(metrics_dict, cit_dict)

    with open(outcomes_path, 'w', encoding='utf-8', newline='') as metrics_csv:
        writer = csv.writer(metrics_csv)
        writer.writerow(("coverage", "term", "section", "field", "id",
                         "surname", "name",
                         "cand", "co-au",
                         "cand_comm", "comm_cand",
                         "BC", "CC",
                         "cand_other", "other_cand",
                         "books", "articles", "other_pubbs",
                         "I1", "I2", "I3",
                         # "pubbs", "pubbs_found", "pubbs_ind", "pubbs_ind_found",
                         # "total_pubbs", "total_found", "total_extra_found",
                         # "comm", "other", "comm_other", "other_comm",
                         "esito"))

        for asn_year, quads in complete_dict.items():
            for quad, sects in quads.items():
                for sect, fields in sects.items():
                    for field, candidates in fields.items():
                        for candidate, info in candidates.items():

                            if "1" in info["cand_paths"].keys():
                                cand_comm = len(info["cand_paths"]["1"])
                            else:
                                cand_comm = 0
                            if "1" in info["comm_paths"].keys():
                                comm_cand = len(info["comm_paths"]["1"])
                            else:
                                comm_cand = 0

                            writer.writerow((info["coverage"]["cov_sect"], quad, sect, field, candidate,
                                             info["fullname"][0], info["fullname"][1],
                                             info["cand_nodes"], info["co-au"],
                                             cand_comm, comm_cand,
                                             info["BC"], info["CC"],
                                             info["other"]["cand_other"], info["other"]["other_cand"],
                                             info["coverage"]["books"], info["coverage"]["articles"],
                                             info["coverage"]["other_pubbs"],
                                             info["ind_anvur"][0], info["ind_anvur"][1], info["ind_anvur"][2],
                                             # info["coverage"]["pubbs"], info["coverage"]["pubbs_found"],
                                             # info["coverage"]["pubbs_ind"], info["coverage"]["pubbs_ind_found"],
                                             # info["coverage"]["total_pubbs"], info["coverage"]["total_found"],
                                             # info["coverage"]["total_extra_found"],
                                             # info["comm_nodes"], info["other_nodes"],
                                             # info["other"]["comm_other"], info["other"]["other_comm"],
                                             info["ind_anvur"][3]))

'''
Need commissions' data in a csv with rows: asn_year, field, id, surname, name, pub_id, title, doi
Need candidates' cv data in a series of folders:
- asn sessions folders named: "2016" and "2018"
- section folders named "fascia1" and "fascia2"
- recruitment field folders
- in rf folders, candidate jsons named: 0000_surname_name.json
Need outcomes data for all candidates

How can we get commission data?
'''

