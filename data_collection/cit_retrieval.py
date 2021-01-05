import requests
import re
import unicodedata

"""Retrieving Cited MAG"""
def search_cited(idt):

    hdr_mag = {'Ocp-Apim-Subscription-Key': 'ac0d6ea6f26845e8b41c0df9f4e45120'}
    query = f"expr=Id={idt}&attributes=Id,DOI,AA.AuN,AA.AuId,Ti,Y,J.JN"
    url_mag = f"https://api.labs.cognitive.microsoft.com/academic/v1.0/evaluate?{query}"
    r = requests.get(url_mag, headers=hdr_mag).json()
    d = dict()
    d["PId"] = r["entities"][0]["Id"]
    d["author"] = r["entities"][0]["AA"]
    d["title"] = r["entities"][0]["Ti"]
    d["year_mag"] = r["entities"][0]["Y"]
    if "DOI" in r["entities"][0].keys():
        d["doi"] = r["entities"][0]["DOI"]
    if "J" in r["entities"][0].keys():
        d["journal"] = r["entities"][0]["J"]["JN"]

    return d


"""Retrieving Citing MAG"""
def search_citing(idt):

    hdr_mag = {'Ocp-Apim-Subscription-Key': 'ac0d6ea6f26845e8b41c0df9f4e45120'}
    query = f"expr=RId={idt}&attributes=Id,DOI,AA.AuN,AA.AuId,Ti,Y,J.JN"
    url_mag = f"https://api.labs.cognitive.microsoft.com/academic/v1.0/evaluate?{query}"
    r = requests.get(url_mag, headers=hdr_mag).json()
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


""" Cited and Citing from COCI"""
def clean_title_coci(title_raw):

    title_clean = u"".join(
        [c for c in unicodedata.normalize("NFKD", title_raw) if not unicodedata.combining(c)])  # remove accents
    title_clean = title_clean.lower()
    title_clean = re.sub(r"[^\w\d\s]", " ", title_clean)
    title_clean = re.sub(r"\s+", " ", title_clean)

    return title_clean


def matching_coci(list_pubbs, new):

    value = 0
    n = len(list_pubbs)
    idx = 0
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


def search_coci(loggr, t, pubb):

    api = ""
    key = ""
    if t == 1:
        api = "references"
        key = "cited"
    elif t == 2:
        api = "citations"
        key = "citing"

    doi = pubb["doi"].lower()
    url_oc = f"http://opencitations.net/index/api/v1/{api}/{doi}?format=json"
    hdr_cr = {'User-Agent': 'mailto:federica.bologna17@gmail.com'}

    try:
        r1 = requests.get(url_oc).json()
        if r1:
            if key not in pubb.keys():
                pubb[key] = []
            for entity in r1:
                d = dict()
                cit = entity[key][8:]
                url_cr = f"https://api.crossref.org/works/{cit}"
                r2 = requests.get(url_cr, headers=hdr_cr).json()
                d["doi"] = cit.upper()
                if "author" in r2["message"].keys():
                    d["author"] = r2["message"]["author"]
                if "title" in r2["message"].keys() and r2["message"]["title"]:
                    d["title"] = clean_title_coci(r2["message"]["title"][0])
                d["year_oc"] = r2["message"]["issued"]["date-parts"][0][0]

                value = matching_coci(pubb[key], d)
                if value == 0:
                    pubb[key].append(d)

        return pubb

    except Exception as ex:
        loggr.error(ex)
        return pubb


def retrieving_cit(logger, authors_dict):

    for author, info in authors_dict.items():

        for pub1 in info["pubbs"]:
            if "RId" in pub1.keys():
                pub1["cited"] = [search_cited(rid) for rid in pub1["RId"]]
                pub1.pop("RId")
            if "PId" in pub1.keys():
                result = search_citing(pub1["PId"])
                if result:
                    pub1["citing"] = result
            if "doi" in pub1.keys():
                pub_a = search_coci(logger, 1, pub1)
                pub_b = search_coci(logger, 2, pub1)
                pub1.update(pub_a)
                pub1.update(pub_b)

        for pub2 in info["pubbs_mag"]:
            if "RId" in pub2.keys():
                pub2["cited"] = [search_cited(rid) for rid in pub2["RId"]]
                pub2.pop("RId")
            if "PId" in pub2.keys():
                result = search_citing(pub2["PId"])
                if result:
                    pub2["citing"] = result
            if "doi" in pub2.keys():
                pub_a = search_coci(logger, 1, pub2)
                pub_b = search_coci(logger, 2, pub2)
                pub2.update(pub_a)
                pub2.update(pub_b)

    return authors_dict


def adding_cit(logger, dd):

    logger.info("________________RETRIEVE CIT________________")

    for asn_year, quads in dd["cand"].items():
        for quad, sects in quads.items():
            for sect, fields in sects.items():
                for field, candidates in fields.items():
                    dd[asn_year][quad][sect][field] = retrieving_cit(logger, candidates)

    for asn_year, fields in dd["comm"].items():
        for field, commission in fields.items():
            dd[asn_year][field] = retrieving_cit(logger, commission)

    return dd
