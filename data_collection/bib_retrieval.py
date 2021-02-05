"""Retrieving Articles from Author Identifiers:
AuthorIDs > Article IDs"""
import time
import os
import json
import requests


def matching_pubbs(list_pubbs, new):

    value = 0
    n = len(list_pubbs)
    idx = 0
    while idx < n:
        if "PId" in list_pubbs[idx].keys():
            if new["PId"] == list_pubbs[idx]["PId"]:
                if "journal" in new.keys() and "journal" not in list_pubbs[idx].keys():
                    list_pubbs[idx]["journal"] = new["journal"]
                value = 1
                idx = n
        elif "doi" in new.keys() and "doi" in list_pubbs[idx].keys():
            if new["doi"] == list_pubbs[idx]["doi"]:
                list_pubbs[idx]["PId"] = new["PId"]
                if "journal" in new.keys() and "journal" not in list_pubbs[idx].keys():
                    list_pubbs[idx]["journal"] = new["journal"]
                if "RId" in new.keys():
                    list_pubbs[idx]["RId"] = new["RId"]
                value = 1
                idx = n
        elif "title" in list_pubbs[idx].keys():
            new_title = new["title"].replace(" ", "")
            old_title = list_pubbs[idx]["title"].replace(" ", "")
            l_new = len(new_title)
            l_old = len(old_title)
            new_year = new["year_mag"]
            old_year = list_pubbs[idx]["year"]
            if l_old >= l_new:
                if new_title == old_title[:l_new] and old_year - 2 <= new_year <= old_year + 2:
                    list_pubbs[idx]["PId"] = new["PId"]
                    if "journal" in new.keys() and "journal" not in list_pubbs[idx].keys():
                        list_pubbs[idx]["journal"] = new["journal"]
                    if "RId" in new.keys():
                        list_pubbs[idx]["RId"] = new["RId"]
                    if "doi" in new.keys():
                        list_pubbs[idx]["doi"] = new["doi"]
                    value = 1
                    idx = n
                elif new_title == old_title[-l_new:] and old_year - 2 <= new_year <= old_year + 2:
                    list_pubbs[idx]["PId"] = new["PId"]
                    if "journal" in new.keys() and "journal" not in list_pubbs[idx].keys():
                        list_pubbs[idx]["journal"] = new["journal"]
                    if "RId" in new.keys():
                        list_pubbs[idx]["RId"] = new["RId"]
                    if "doi" in new.keys():
                        list_pubbs[idx]["doi"] = new["doi"]
                    value = 1
                    idx = n
            else:
                if new_title[:l_old] == old_title and old_year - 2 <= new_year <= old_year + 2:
                    list_pubbs[idx]["PId"] = new["PId"]
                    if "journal" in new.keys() and "journal" not in list_pubbs[idx].keys():
                        list_pubbs[idx]["journal"] = new["journal"]
                    if "RId" in new.keys():
                        list_pubbs[idx]["RId"] = new["RId"]
                    if "doi" in new.keys():
                        list_pubbs[idx]["doi"] = new["doi"]
                    value = 1
                    idx = n
                elif new_title[-l_old:] == old_title and old_year - 2 <= new_year <= old_year + 2:
                    list_pubbs[idx]["PId"] = new["PId"]
                    if "journal" in new.keys() and "journal" not in list_pubbs[idx].keys():
                        list_pubbs[idx]["journal"] = new["journal"]
                    if "RId" in new.keys():
                        list_pubbs[idx]["RId"] = new["RId"]
                    if "doi" in new.keys():
                        list_pubbs[idx]["doi"] = new["doi"]
                    value = 1
                    idx = n

        idx += 1

    return value, list_pubbs


def search_pubbs(loggr, author_id, pubbs, pubbs_mag, date):

    hdr_mag = {'Ocp-Apim-Subscription-Key': 'ac0d6ea6f26845e8b41c0df9f4e45120'}
    query = f"And(Composite(AA.AuId={author_id}),Y<{date})&count=300&attributes=Id,DOI,Ti,Y,RId,J.JN,Pt"
    url_mag = f"https://api.labs.cognitive.microsoft.com/academic/v1.0/evaluate?expr={query}"
    try:
        r_mag = requests.get(url_mag, headers=hdr_mag, timeout=10)
        r = r_mag.json()
        if "entities" in r.keys():
            for entity in r["entities"]:
                d = dict()
                d["PId"] = entity["Id"]
                d["year_mag"] = entity["Y"]
                d["title"] = entity["Ti"]
                if "Pt" in entity.keys():
                    d["type"] = entity["Pt"]
                if "DOI" in entity.keys():
                    d["doi"] = entity["DOI"]
                if "RId" in entity.keys():
                    d["RId"] = entity["RId"]
                if "J" in entity.keys():
                    d["journal"] = entity["J"]["JN"]

                value, pubbs = matching_pubbs(pubbs, d)
                if value == 0:
                    pubbs_mag.append(d)

        return pubbs, pubbs_mag

    except Exception as ex0:
        if "ConnectTimeout" in repr(ex0):
            loggr.error("MAG-bib__" + repr(ex0) + "__" + url_mag)
            time.sleep(5.0)
            solution = search_pubbs(loggr, author_id, pubbs, pubbs_mag, date)
            return solution


def retrieving_bib(logger, info, limit):

    info["pubbs_mag"] = []
    for au_id in info["AuIds"]:
        p_a, p_mag_a = search_pubbs(logger, au_id, info["pubbs"], info["pubbs_mag"], limit)
        info["pubbs"] = p_a
        info["pubbs_mag"] = p_mag_a

    return info


def adding_bib(logger, dd):

    logger.error("________________RETRIEVE BIB________________")
    print("adding bib")

    bib_folder = os.path.join(os.getcwd(), "bib_data")
    if os.path.exists(bib_folder) is False:
        os.mkdir(bib_folder)

    for asn_year, terms in dd["cand"].items():
        for term, roles in terms.items():
            for role, fields in roles.items():
                for field, candidates in fields.items():
                    for cand_id, cand_dict in candidates.items():

                        limit = 0
                        if asn_year == "2016":
                            if term == "1":
                                limit = 2017
                            elif term == "5":
                                limit = 2019
                            else:
                                limit = 2018
                        elif asn_year == "2018":
                            if term == "1":
                                limit = 2019
                            elif term == "5" or term == "6":
                                limit = 2021
                            else:
                                limit = 2020

                        cand_file = os.path.join(bib_folder, f'{asn_year}_{term}_{role}_{field}_{cand_id}_bib.json')

                        if os.path.exists(cand_file) is False:
                            dd["cand"][asn_year][term][role][field][cand_id] = retrieving_bib(logger, cand_dict, limit)
                            cand_bib_dict = dd["cand"][asn_year][term][role][field][cand_id]
                            with open(cand_file, 'w') as bib_file:
                                json.dump(cand_bib_dict, bib_file, sort_keys=True, indent=4)
                        else:
                            with open(cand_file) as bib_file:
                                cand_bib_dict = json.load(bib_file)
                                dd["cand"][asn_year][term][role][field][cand_id] = cand_bib_dict

    for asn_year, fields in dd["comm"].items():
        for field, commission in fields.items():
            for comm_id, comm_dict in commission.items():

                comm_file = os.path.join(bib_folder, f'{asn_year}_{field}_{comm_id}_bib.json')

                if os.path.exists(comm_file) is False:
                    dd["comm"][asn_year][field][comm_id] = retrieving_bib(logger, comm_dict, 2021)
                    comm_bib_dict = dd["comm"][asn_year][field][comm_id]
                    with open(comm_file, 'w') as bib_file:
                        json.dump(comm_bib_dict, bib_file, sort_keys=True, indent=4)
                else:
                    with open(comm_file) as bib_file:
                        comm_bib_dict = json.load(bib_file)
                        dd["comm"][asn_year][field][comm_id] = comm_bib_dict

    return dd
