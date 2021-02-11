import time
import os
import json
import re
import unicodedata
import requests


"""Retrieving Cited MAG"""
def search_cited(loggr, idt):

    hdr_mag = {'Ocp-Apim-Subscription-Key': 'ac0d6ea6f26845e8b41c0df9f4e45120'}
    query = f"expr=Id={idt}&attributes=Id,DOI,AA.AuN,AA.AuId,Ti,Y,J.JN"
    url_mag = f"https://api.labs.cognitive.microsoft.com/academic/v1.0/evaluate?{query}"
    try:
        r_mag = requests.get(url_mag, headers=hdr_mag, timeout=10)

        try:
            r = r_mag.json()
            d = dict()
            if r["entities"]:
                d["PId"] = r["entities"][0]["Id"]
                d["author"] = r["entities"][0]["AA"]
                d["title"] = r["entities"][0]["Ti"]
                d["year_mag"] = r["entities"][0]["Y"]
                if "DOI" in r["entities"][0].keys():
                    d["doi"] = r["entities"][0]["DOI"]
                if "J" in r["entities"][0].keys():
                    d["journal"] = r["entities"][0]["J"]["JN"]

            return d

        except Exception as ex1:
            if "MaxRetryError" in repr(ex1):
                loggr.error("MAG-cited__" + repr(ex1) + "__" + url_mag)
                time.sleep(5.0)
                solution = search_cited(loggr, idt)
                return solution
            else:
                loggr.exception("MAG-cited__" + repr(ex1) + "__" + url_mag)

    except Exception as ex0:
        if "ConnectTimeout" in repr(ex0):
            loggr.error("MAG-cited__" + repr(ex0) + "__" + url_mag)
            time.sleep(5.0)
            solution = search_cited(loggr, idt)
            return solution


"""Retrieving Citing MAG"""
def search_citing(loggr, idt):

    hdr_mag = {'Ocp-Apim-Subscription-Key': 'ac0d6ea6f26845e8b41c0df9f4e45120'}
    query = f"expr=RId={idt}&count=3000&attributes=Id,DOI,AA.AuN,AA.AuId,Ti,Y,J.JN"
    url_mag = f"https://api.labs.cognitive.microsoft.com/academic/v1.0/evaluate?{query}"

    try:
        r_mag = requests.get(url_mag, headers=hdr_mag, timeout=10)

        try:
            r = r_mag.json()
            citing = []
            for entity in r["entities"]:
                d = dict()
                d["PId"] = entity["Id"]
                d["author"] = entity["AA"]
                d["title"] = entity["Ti"]
                d["year_mag"] = entity["Y"]
                if "DOI" in entity.keys():
                    d["doi"] = entity["DOI"]
                if "J" in r["entities"][0].keys():
                    d["journal"] = r["entities"][0]["J"]["JN"]
                citing.append(d)

            return citing

        except Exception as ex1:
            if "MaxRetryError" in repr(ex1):
                loggr.error("MAG-citing__" + repr(ex1) + "__" + url_mag)
                time.sleep(5.0)
                solution = search_citing(loggr, idt)
                return solution
            else:
                loggr.exception("MAG-citing__" + repr(ex1) + "__" + url_mag)

    except Exception as ex0:
        if "ConnectTimeout" in repr(ex0):
            loggr.error("MAG-citing__" + repr(ex0) + "__" + url_mag)
            time.sleep(5.0)
            solution = search_citing(loggr, idt)
            return solution


""" Cited and Citing from COCI"""
def clean_title_coci(title_raw):
    title_clean = u"".join(
        [c for c in unicodedata.normalize("NFKD", title_raw) if not unicodedata.combining(c)])  # remove accents
    title_clean = title_clean.lower()
    title_clean = re.sub(r"[^\w\d\s]", " ", title_clean)
    title_clean = re.sub(r"\s+", " ", title_clean)

    return title_clean


def matching_coci(loggr, list_pubbs, new):

    value = 0
    n = len(list_pubbs)
    idx = 0
    try:
        while idx < n:
            if "year_oc" not in list_pubbs[idx].keys():
                if "doi" in list_pubbs[idx].keys():
                    if new["doi"] == list_pubbs[idx]["doi"]:
                        value = 1
                        idx = n

                elif "title" in list_pubbs[idx].keys() and "title" in new.keys():
                    new_title = new["title"].replace(" ", "")
                    old_title = list_pubbs[idx]["title"].replace(" ", "")
                    yr = list_pubbs[idx]["year_mag"]
                    if new_title == old_title and yr - 2 <= new["year_oc"] <= yr + 2:
                        value = 1
                        idx = n

            idx += 1

        return value

    except Exception as ex:
        loggr.exception("MATCH____" + repr(ex))
        return value


def search_cr(loggr, doi):

    url_cr = f"https://api.crossref.org/works/{doi}"
    hdr_cr = {'User-Agent': 'mailto:federica.bologna17@gmail.com'}
    try:
        r_cr = requests.get(url_cr, headers=hdr_cr, timeout=60)
        hdrs_cr = r_cr.headers
        d = dict()

        try:
            r2 = r_cr.json()
            d["doi"] = doi.upper()
            if "author" in r2["message"].keys():
                d["author"] = r2["message"]["author"]
            if "title" in r2["message"].keys() and r2["message"]["title"]:
                d["title"] = clean_title_coci(r2["message"]["title"][0])
            d["year_oc"] = r2["message"]["issued"]["date-parts"][0][0]

            return d

        except Exception as ex1:
            if hdrs_cr["content-type"] == 'text/plain' or hdrs_cr["content-type"] == 'text/html':
                r2 = r_cr.text
                if "503" in r2:
                    loggr.error("CR__" + repr(ex1) + "__" + url_cr)
                    time.sleep(5.0)
                    solution = search_cr(loggr, doi)
                    return solution
                else:
                    loggr.error("CR__" + repr(ex1) + "__" + url_cr + "__" + r2)
            else:
                loggr.error("CR__" + repr(ex1) + "__" + url_cr + "__" + hdrs_cr["content-type"])

            return d

    except Exception as ex0:
        if "ConnectTimeout" in repr(ex0):
            loggr.error("CR__" + repr(ex0) + "__" + url_cr)
            time.sleep(5.0)
            solution = search_cr(loggr, doi)
            return solution


def search_coci(loggr, t, pubb):

    lim_cr = 0

    api = ""
    key = ""
    if t == 1:
        api = "references"
        key = "cited"
    elif t == 2:
        api = "citations"
        key = "citing"

    doi = pubb["doi"].lower()
    url_oc = f"https://opencitations.net/index/api/v1/{api}/{doi}?format=json"
    try:
        r_oc = requests.get(url_oc, timeout=10)
        hdrs_oc = r_oc.headers

        try:
            r1 = r_oc.json()
            if r1:
                if key not in pubb.keys():
                    pubb[key] = []
                for entity in r1:
                    cit = entity[key][8:]

                    if lim_cr < 49:
                        new_d = search_cr(loggr, cit)
                        lim_cr += 1
                    else:
                        time.sleep(1.0)
                        new_d = search_cr(loggr, cit)
                        lim_cr = 1

                    if new_d:
                        value = matching_coci(loggr, pubb[key], new_d)
                        if value == 0:
                            pubb[key].append(new_d)

            return pubb

        except Exception as ex1:
            if hdrs_oc['Content-Type'] == 'text/html':
                r1 = r_oc.text
                loggr.error("COCI__" + repr(ex1) + "__" + url_oc + "__" + r1)

            elif "MaxRetryError" in repr(ex1):
                loggr.error("COCI__" + repr(ex1) + "__" + url_oc)
                time.sleep(5.0)
                solution = search_coci(loggr, t, pubb)
                return solution

            else:
                loggr.error("COCI__" + repr(ex1) + "__" + url_oc + "__" + hdrs_oc["Content-Type"])

            return pubb

    except Exception as ex0:
        if "ConnectTimeout" in repr(ex0):
            loggr.error("COCI__" + repr(ex0) + "__" + url_oc)
            time.sleep(5.0)
            solution = search_coci(loggr, t, pubb)
            return solution


def retrieving_cit(logger, info):

    for pub1 in info["pubbs"]:
        if "RId" in pub1.keys():
            for rid in pub1["RId"]:
                result = search_cited(logger, rid)
                if result:
                    pub1["cited"].append(result)
            pub1.pop("RId")
        if "PId" in pub1.keys():
            result = search_citing(logger, pub1["PId"])
            if result:
                pub1["citing"] = result
        if "doi" in pub1.keys():
            pub_a = search_coci(logger, 1, pub1)
            time.sleep(1.0)
            pub_b = search_coci(logger, 2, pub1)
            if pub_a is not None:
                pub1.update(pub_a)
            else:
                logger.error(f"Cit OC: NoneType__{info['fullname']}__{pub1['doi']}")
            if pub_b is not None:
                pub1.update(pub_b)
            else:
                logger.error(f"Cit OC: NoneType__{info['fullname']}__{pub1['doi']}")

    for pub2 in info["pubbs_mag"]:
        if "RId" in pub2.keys():
            for rid in pub2["RId"]:
                result = search_cited(logger, rid)
                if result:
                    pub2["cited"].append(result)
            pub2.pop("RId")
        if "PId" in pub2.keys():
            result = search_citing(logger, pub2["PId"])
            if result:
                pub2["citing"] = result
        if "doi" in pub2.keys():
            pub_a = search_coci(logger, 1, pub2)
            time.sleep(1.0)
            pub_b = search_coci(logger, 2, pub2)
            if pub_a is not None:
                pub2.update(pub_a)
            else:
                logger.error(f"Cit OC: NoneType__{info['fullname']}__{pub2['doi']}")
            if pub_b is not None:
                pub2.update(pub_b)
            else:
                logger.error(f"Cit OC: NoneType__{info['fullname']}__{pub2['doi']}")

    return info


def adding_cit(logger, dd):

    logger.error("________________RETRIEVE CIT________________")
    print("adding cit")

    cit_folder = os.path.join(os.getcwd(), "cit_data")
    if os.path.exists(cit_folder) is False:
        os.mkdir(cit_folder)

    for asn_year, terms in dd["cand"].items():
        for term, roles in terms.items():
            for role, fields in roles.items():
                for field, candidates in fields.items():
                    for cand_id, cand_dict in candidates.items():

                        cand_file = os.path.join(cit_folder, f'{asn_year}_{term}_{role}_{field}_{cand_id}_cit.json')

                        if os.path.exists(cand_file) is False:
                            dd["cand"][asn_year][term][role][field][cand_id] = retrieving_cit(logger, cand_dict)
                            cand_cit_dict = dd["cand"][asn_year][term][role][field][cand_id]
                            with open(cand_file, 'w') as cit_file:
                                json.dump(cand_cit_dict, cit_file, sort_keys=True, indent=4)
                        else:
                            with open(cand_file) as cit_file:
                                cand_cit_dict = json.load(cit_file)
                                dd["cand"][asn_year][term][role][field][cand_id] = cand_cit_dict

    for asn_year, fields in dd["comm"].items():
        for field, commission in fields.items():
            for comm_id, comm_dict in commission.items():

                comm_file = os.path.join(cit_folder, f'{asn_year}_{field}_{comm_id}_cit.json')

                if os.path.exists(comm_file) is False:
                    dd["comm"][asn_year][field][comm_id] = retrieving_cit(logger, comm_dict)
                    comm_cit_dict = dd["comm"][asn_year][field][comm_id]
                    with open(comm_file, 'w') as cit_file:
                        json.dump(comm_cit_dict, cit_file, sort_keys=True, indent=4)
                else:
                    with open(comm_file) as cit_file:
                        comm_cit_dict = json.load(cit_file)
                        dd["comm"][asn_year][field][comm_id] = comm_cit_dict

    return dd
