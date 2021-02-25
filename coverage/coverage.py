import logging
import os
import json
import csv
from search_OA_CR import *


def calculate_coverage(logger, cand_dict):

    cov = dict()
    cov["total_CV"] = len(cand_dict["pubbs"])
    cov["mag"] = 0
    cov["oa"] = 0
    cov["cr"] = 0
    cov["combined"] = 0

    for pub in cand_dict["pubbs"]:
        if "PId" in pub.keys() or "doi" in pub.keys():
            cov["combined"] += 1

        if "PId" in pub.keys():
            cov["mag"] += 1

        if "doi" in pub.keys():
            cov["oa"] += search_doi_oa(logger, pub["doi"])
            cov["cr"] += search_doi_cr(logger, pub["doi"])
        elif "title" in pub.keys():
            cov["oa"] += search_title_oa(logger, cand_dict["fullname"], pub["title"], pub["year"])
            cov["cr"] += search_title_cr(logger, cand_dict["fullname"], pub["title"], pub["year"])

    cov["extra_found"] = cov["combined"] + len(cand_dict["pubbs_mag"])

    if cov["extra_found"] >= (cov["total_CV"] * 0.7) or cov["extra_found"] > 15:
        if cov["combined"] >= (cov["total_CV"] * 0.7) or cov["combined"] > 15:
            cov["cov_sect"] = "A"
        else:
            cov["cov_sect"] = "B"
    else:
        cov["cov_sect"] = "C"

    return cov


def saving_coverage(file_path, path):

    with open(file_path) as complete_file:
        dd = json.load(complete_file)

    logging.basicConfig(filename='coverage.log', level=logging.ERROR,
                        format='%(asctime)s %(levelname)s %(name)s %(message)s')
    logger = logging.getLogger(__name__)
    logger.error("____COVERAGE____")

    cov_folder = os.path.join(os.getcwd(), "cov_data")
    if os.path.exists(cov_folder) is False:
        os.mkdir(cov_folder)

    cov_dict = dict()

    for asn_year, terms in dd["cand"].items():
        cov_dict[asn_year] = dict()
        for term, roles in terms.items():
            cov_dict[asn_year][term] = dict()
            for role, fields in roles.items():
                cov_dict[asn_year][term][role] = dict()
                for field, candidates in fields.items():
                    cov_dict[asn_year][term][role][field] = dict()
                    for cand_id, cand_dict in candidates.items():

                        cand_file = os.path.join(cov_folder, f"{asn_year}_{term}_{role}_{field}_{cand_id}_cov.json")

                        if os.path.exists(cand_file) is False:
                            cov_dict[asn_year][term][role][field][cand_id] = calculate_coverage(logger, cand_dict)
                            cand_cov_dict = cov_dict[asn_year][term][role][field][cand_id]
                            with open(cand_file, 'w') as cov_file:
                                json.dump(cand_cov_dict, cov_file, sort_keys=True, indent=4)
                        else:
                            with open(cand_file) as cov_file:
                                cand_cov_dict = json.load(cov_file)
                                cov_dict[asn_year][term][role][field][cand_id] = cand_cov_dict

    with open(path, 'w', encoding='utf-8', newline='') as cov_csv:
        writer = csv.writer(cov_csv)
        writer.writerow(("cov_sect", "term", "role", "field", "id",
                         "MAG", "OA", "CR", "combined",
                         "MAG%", "OA%", "CR%", "combined", "total_CV"))

        for asn_year, terms in cov_dict.items():
            for term, roles in terms.items():
                for role, fields in roles.items():
                    for field, names in fields.items():
                        for name, info in names.items():
                            cand_id = name.split("_")[0]
                            mag = info["mag"] / info["total_CV"]
                            oa = info["oa"] / info["total_CV"]
                            cr = info["cr"] / info["total_CV"]
                            comb = info["combined"] / info["total_CV"]

                            writer.writerow(
                                (info["cov_sect"], term, role, field, cand_id,
                                 info["mag"], info["oa"], info["cr"], info["combined"],
                                 mag, oa, cr, comb, info["total_CV"]))


saving_coverage("complete_data.json", "coverage.csv")
