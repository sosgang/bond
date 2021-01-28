"""Retrieving Articles from Author Identifiers:
AuthorIDs > Article IDs"""
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


def search_pubbs(author_id, pubbs, pubbs_mag, date):

    hdr_mag = {'Ocp-Apim-Subscription-Key': 'ac0d6ea6f26845e8b41c0df9f4e45120'}
    query = f"And(Composite(AA.AuId={author_id}),Y<{date})&count=300&attributes=Id,DOI,Ti,Y,RId,J.JN,Pt"
    url_mag = f"https://api.labs.cognitive.microsoft.com/academic/v1.0/evaluate?expr={query}"
    r = requests.get(url_mag, headers=hdr_mag).json()

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


def retrieving_bib(authors_dict, limit):

    for author, info in authors_dict.items():

        info["pubbs_mag"] = []
        for au_id in info["AuIds"]:
            p_a, p_mag_a = search_pubbs(au_id, info["pubbs"], info["pubbs_mag"], limit)
            info["pubbs"] = p_a
            info["pubbs_mag"] = p_mag_a

    return authors_dict


def adding_bib(dd):

    print("adding bib")

    for asn_year, terms in dd["cand"].items():
        for term, roles in terms.items():
            for role, fields in roles.items():
                for field, candidates in fields.items():

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

                    dd["cand"][asn_year][term][role][field] = retrieving_bib(candidates, limit)

    for asn_year, fields in dd["comm"].items():
        for field, commission in fields.items():
            dd["comm"][asn_year][field] = retrieving_bib(commission, 2021)

    return dd
