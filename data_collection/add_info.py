import csv


def adding_cov(metrics_dd, cit_dd):

    for asn_year, quads in cit_dd["cand"].items():
        for quad, sects in quads.items():
            for sect, fields in sects.items():
                for field, candidates in fields.items():
                    for cand_id, info in candidates.items():

                        metrics_dd[asn_year][quad][sect][field][cand_id]["coverage"] = dict()
                        coverage = metrics_dd[asn_year][quad][sect][field][cand_id]["coverage"]
                        '''
                        coverage["pubbs"] = 0
                        coverage["pubbs_ind"] = 0
                        coverage["pubbs_found"] = 0
                        coverage["pubbs_ind_found"] = 0
                        '''
                        coverage["books"] = 0
                        coverage["articles"] = 0
                        coverage["other_pubbs"] = 0
                        coverage["total_pubbs"] = len(info["pubbs"])
                        coverage["total_found"] = 0

                        for pub in info["pubbs"]:
    
                            if "PId" in pub.keys() or "doi" in pub.keys():
                                coverage["total_found"] += 1

                            '''
                            if "pubbs" in pub["CV_id"].keys():
                                coverage["pubbs"] += 1
                                if "PId" in pub.keys() or "doi" in pub.keys():
                                    coverage["pubbs_found"] += 1
    
                            if "pubbs_ind" in pub["CV_id"].keys():
                                coverage["pubbs_ind"] += 1
                                if "PId" in pub.keys() or "doi" in pub.keys():
                                    coverage["pubbs_ind_found"] += 1
                            '''
    
                            if pub["type"][0] == "m":
                                coverage["books"] += 1
                            elif pub["type"][0] == "a":
                                coverage["articles"] += 1
                            else:
                                coverage["other_pubbs"] += 1

                        coverage["total_extra_found"] = coverage["total_found"] + len(info["pubbs_MAG"])
    
                        if coverage["total_found"] >= (coverage["total_pubbs"] * 0.7):
                            coverage["cov_sect"] = "A"

                        elif coverage["total_extra_found"] >= (coverage["total_pubbs"] * 0.7) \
                                or coverage["total_found"] > 15:
                            coverage["cov_sect"] = "B"

                        else:
                            coverage["cov_sect"] = "C"

    return metrics_dd


def adding_name_outcome(dd, outpath):

    with open(outpath, 'r') as tsv_file:
        ind_anvur_tsv = csv.reader(tsv_file, delimiter="\t")
        for row in ind_anvur_tsv:
            dd["cand"][row[1]][row[4]][row[5]][row[2]][row[0]]["fullname"] = [row[7], row[8]]
            dd["cand"][row[1]][row[4]][row[5]][row[2]][row[0]]["ind_anvur"] = [row[10], row[11], row[12], row[14]]

    return dd
