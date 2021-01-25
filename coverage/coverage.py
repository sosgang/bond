import logging
import json
import csv
from search_OA_CR import *


def calculate_coverage(folder):
    logging.basicConfig(filename='my_log.log', level=logging.ERROR,
                        format='%(asctime)s %(levelname)s %(name)s %(message)s')
    logger = logging.getLogger(__name__)

    cov_dict = dict()

    terms = ["1", "2", "3", "4", "5"]
    roles = ["FP", "AP"]
    fields = ["10-G1", "13-D4"]

    for term in terms:
        cov_dict[term] = dict()
        for role in roles:
            cov_dict[term][role] = dict()
            for field in fields:

                cov_dict[term][role][field] = dict()
                with open(f'{folder}\\t{term}_{role}_{field}.json', 'r') as bib_file:
                    dd = json.load(bib_file)

                    cov = cov_dict[term][role][field]

                    for name, info in dd.items():
                        cov[name] = dict()
                        cov[name]["total_CV"] = len(info["pubbs"])
                        cov[name]["mag"] = 0
                        cov[name]["oa"] = 0
                        cov[name]["cr"] = 0
                        cov[name]["combined"] = 0

                        for pub in info["pubbs"]:
                            if "PId" in pub.keys() or "doi" in pub.keys():
                                cov[name]["combined"] += 1

                            if "PId" in pub.keys():
                                cov[name]["mag"] += 1

                            if "doi" in pub.keys():
                                cov[name]["oa"] += search_doi_oa(logger, pub["doi"])
                                cov[name]["cr"] += search_doi_cr(logger, pub["doi"])
                            elif "title" in pub.keys():
                                cov[name]["oa"] += search_title_oa(logger, name, pub["title"], pub["year"])
                                cov[name]["cr"] += search_title_cr(logger, name, pub["title"], pub["year"])

                        cov[name]["extra_found"] = cov[name]["combined"] + len(info["pubbs_MAG"])

                        if cov[name]["extra_found"] >= (cov[name]["total_CV"] * 0.7) or cov[name]["extra_found"] > 15:
                            if cov[name]["combined"] >= (cov[name]["total_CV"] * 0.7) or cov[name]["combined"] > 15:
                                cov[name]["cov_sect"] = "A"
                            else:
                                cov[name]["cov_sect"] = "B"
                        else:
                            cov[name]["cov_sect"] = "C"

    return cov_dict


def saving_coverage(folder, path):
    coverage = calculate_coverage(folder)

    with open(path, 'w', encoding='utf-8', newline='') as data_csv:
        writer = csv.writer(data_csv)
        writer.writerow(("cov_sect", "term", "role", "field", "id",
                         "MAG", "OA", "CR", "combined",
                         "MAG%", "OA%", "CR%", "combined", "total_CV"))

        for term, roles in coverage.items():
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


saving_coverage("\\bib-cit_data", "coverage.csv")
