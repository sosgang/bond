import logging
from meta_extraction import *
from add_info import *
from id_search import *
from bib_retrieval import *
from cit_retrieval import *
from graph_analysis import *


def BoND(cand_jsons_path, comm_csv_path, outcomes_path, final_path):

    logging.basicConfig(filename='data_collection.log', level=logging.ERROR,
                        format='%(asctime)s %(levelname)s %(name)s %(message)s')
    logger = logging.getLogger(__name__)

    cv_dict = extracting_metadata(cand_jsons_path, comm_csv_path)  # extracting metadata from the CV jsons

    outcome_dict = adding_name_outcome(cv_dict, outcomes_path)  # adding clean name and outcome

    ids_dict = adding_ids(logger, outcome_dict)  # adding AuIds and DOIs to the existing metadata

    bib_dict = adding_bib(logger, ids_dict)  # adding extra publications found in MAG

    with open('bib_data.json', 'w') as bib_file:
        json.dump(bib_dict, bib_file, sort_keys=True, indent=4)

    cit_dict = adding_cit(logger, bib_dict)  # adding citations for each publications

    with open('bib-cit_data.json', 'w') as cit_file:
        json.dump(cit_dict, cit_file, sort_keys=True, indent=4)

    metrics_dict = adding_citmetrics(cit_dict)  # creating and analyzing networks, and calculating citation metrics

    complete_dict = adding_cov(metrics_dict)

    with open('complete_data.json', 'w') as complete_file:
        json.dump(complete_dict, complete_file, sort_keys=True, indent=4)

    with open(final_path, 'w', encoding='utf-8', newline='') as metrics_csv:
        writer = csv.writer(metrics_csv)
        writer.writerow(("coverage", "term", "role", "field", "id",
                         "cand", "co-au",
                         "books", "articles", "other_pubbs",
                         "cand_comm", "comm_cand",
                         "BC", "CC",
                         "cand_other", "other_cand",
                         "nd_m1", "nd_m2", "nd_m3",
                         "outcome"))

        for asn_year, terms in complete_dict["cand"].items():
            for term, roles in terms.items():
                for role, fields in roles.items():
                    for field, candidates in fields.items():
                        for candidate, info in candidates.items():

                            if "1" in info["citmetrics"]["cand_paths"].keys():
                                cand_comm = len(info["citmetrics"]["cand_paths"]["1"])
                            else:
                                cand_comm = 0
                            if "1" in info["citmetrics"]["comm_paths"].keys():
                                comm_cand = len(info["citmetrics"]["comm_paths"]["1"])
                            else:
                                comm_cand = 0

                            writer.writerow((info["coverage"]["cov_sect"], term, role, field, candidate,
                                             info["citmetrics"]["cand_nodes"],
                                             info["citmetrics"]["co-au"]["number"],
                                             info["coverage"]["books"], info["coverage"]["articles"],
                                             info["coverage"]["other_pubbs"],
                                             cand_comm, comm_cand,
                                             info["citmetrics"]["bc"]["number"], info["citmetrics"]["cc"]["number"],
                                             info["citmetrics"]["other"]["cand_other"],
                                             info["citmetrics"]["other"]["other_cand"],
                                             info["ind_anvur"][0], info["ind_anvur"][1], info["ind_anvur"][2],
                                             info["ind_anvur"][3]))


'''
Need commissions' data in a csv with rows: asn_year, field, id, surname, name, pub_id, title, doi
Need candidates' cv data in a series of folders:
- asn sessions folders named: "2016" and "2018"
- terms folders named: term1
- role folders named: "FP" and "AP"
- recruitment field folders
- in rf folders, candidate jsons named: 0000_surname_name.json
Need outcomes data for all candidates

How can we get commission data?
'''

BoND("C:\\Users\\Federica\\PycharmProjects\\assegno\\cv_jsons", "commissions.csv", "indicatoriCalcolati-ASN16-18.tsv",
     "complete_metrics.csv")
