import csv


def adding_cov(metrics_dd):

    print("adding coverage section")

    for asn_year, terms in metrics_dd["cand"].items():
        for term, roles in terms.items():
            for role, fields in roles.items():
                for field, candidates in fields.items():
                    for cand_id, info in candidates.items():

                        info["coverage"] = dict()
                        info["coverage"]["pubbs"] = 0
                        info["coverage"]["pubbs_ind"] = 0
                        info["coverage"]["pubbs_found"] = 0
                        info["coverage"]["pubbs_ind_found"] = 0

                        info["coverage"]["books"] = 0
                        info["coverage"]["articles"] = 0
                        info["coverage"]["other_pubbs"] = 0

                        info["coverage"]["total_pubbs"] = len(info["pubbs"])
                        info["coverage"]["total_found"] = 0

                        for pub in info["pubbs"]:
    
                            if "PId" in pub.keys() or "doi" in pub.keys():
                                info["coverage"]["total_found"] += 1

                            if "pubbs" in pub["cv_id"].keys():  # might leave out this type of coverage info
                                info["coverage"]["pubbs"] += 1
                                if "PId" in pub.keys() or "doi" in pub.keys():
                                    info["coverage"]["pubbs_found"] += 1
    
                            if "pubbs_ind" in pub["cv_id"].keys():  # might leave out this type of coverage info
                                info["coverage"]["pubbs_ind"] += 1
                                if "PId" in pub.keys() or "doi" in pub.keys():
                                    info["coverage"]["pubbs_ind_found"] += 1
    
                            if pub["type"][0] == "m":
                                info["coverage"]["books"] += 1
                            elif pub["type"][0] == "a":
                                info["coverage"]["articles"] += 1
                            else:
                                info["coverage"]["other_pubbs"] += 1

                        info["coverage"]["total_extra_found"] = info["coverage"]["total_found"] + len(info["pubbs_mag"])
    
                        if info["coverage"]["total_extra_found"] >= (info["coverage"]["total_pubbs"] * 0.7) \
                                or info["coverage"]["total_extra_found"] >= 15:
                            if info["coverage"]["total_found"] >= (info["coverage"]["total_pubbs"] * 0.7) \
                                    or info["coverage"]["total_found"] > 15:
                                info["coverage"]["cov_sect"] = "A"
                            else:
                                info["coverage"]["cov_sect"] = "B"
                        else:
                            info["coverage"]["cov_sect"] = "C"

    return metrics_dd


def adding_name_outcome(dd, outpath):

    print("adding name outcome")

    with open(outpath, 'r', encoding='utf-8') as tsv_file:
        ind_anvur_tsv = csv.reader(tsv_file, delimiter="\t")
        for row in ind_anvur_tsv:
            if row[2] == "10-G1" or row[2] == "13-D4":
                if row[1] != "annoAsn":
                    if row[5] == "1":
                        role = "FP"
                    elif row[5] == "2":
                        role = "AP"

                    if row[10] and row[11] and row[12]:
                        dd["cand"][row[1]][row[4]][role][row[2]][row[0]]["fullname"] = [row[7], row[8]]
                        dd["cand"][row[1]][row[4]][role][row[2]][row[0]]["ind_anvur"] = [int(row[10]), int(row[11]), int(row[12]), row[14]]
                    else:
                        dd["cand"][row[1]][row[4]][role][row[2]][row[0]]["fullname"] = [row[7], row[8]]
                        dd["cand"][row[1]][row[4]][role][row[2]][row[0]]["ind_anvur"] = [row[10], row[11], row[12], row[14]]

    return dd
