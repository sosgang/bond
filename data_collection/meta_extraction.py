import os
import json
import csv
import re
import unicodedata


def cleaning_doi(doi_raw):
    doi_clean = doi_raw.strip("DOI: ").strip("HTTPS://DX.DOI.ORG/").strip("#").replace(" ", "")

    return doi_clean


def cleaning_title(title_raw):

    title_clean = u"".join([c for c in unicodedata.normalize("NFKD", title_raw) if not unicodedata.combining(c)])  # remove accents
    title_clean = title_clean.lower()
    title_clean = re.sub(r" p$", '', title_clean)
    title_clean = re.sub(r"[^\w\d\s]", ' ', title_clean)
    title_clean = re.sub(r"\s+", ' ', title_clean)

    return title_clean


def matching_pubbs(list_pubbs, new):
    value = 0
    n = len(list_pubbs)
    idx = 0
    while idx < n:
        if "doi" in new.keys() and "doi" in list_pubbs[idx].keys():
            if new["doi"] == list_pubbs[idx]["doi"]:
                list_pubbs[idx]["cv_id"]["pubbs"] = new["cv_id"]["pubbs"]
                value = 1
                idx = n
        elif "title" in new.keys() and "title" in list_pubbs[idx].keys():
            if (new["title"].replace(" ", "") == list_pubbs[idx]["title"].replace(" ", "")
                    and new["year"] == list_pubbs[idx]["year"]):
                list_pubbs[idx]["cv_id"]["pubbs"] = new["cv_id"]["pubbs"]
                value = 1
                idx = n
        idx += 1

    if value == 0:
        list_pubbs.append(new)

    return list_pubbs


def extracting_metadata_cand(path, cand_dd):

    with os.scandir(path) as asn_years:

        for asn_year in asn_years:
            asn_year_name = asn_year.name
            cand_dd[asn_year_name] = dict()
            asn_year_path = os.path.join(path, asn_year_name)
            with os.scandir(asn_year_path) as terms:

                for term in terms:
                    term_name = term.name[-1]
                    cand_dd[asn_year_name][term_name] = dict()
                    term_path = os.path.join(asn_year_path, term.name)
                    with os.scandir(term_path) as roles:

                        for role in roles:
                            role_name = role.name
                            cand_dd[asn_year_name][term_name][role_name] = dict()
                            role_path = os.path.join(term_path, role.name)
                            with os.scandir(role_path) as fields:

                                for field in fields:
                                    field_name = field.name
                                    cand_dd[asn_year_name][term_name][role_name][field_name] = dict()
                                    field_path = os.path.join(role_path, field_name)
                                    with os.scandir(field_path) as cvs:

                                        for cv in cvs:
                                            cv_name = cv.name[:-5]
                                            cand_id = cv_name.split("_", 1)[0]
                                            cv_dir = os.path.join(field_path, cv.name)

                                            cand_dd[asn_year_name][term_name][role_name][field_name][cand_id] = dict()
                                            ddict = cand_dd[asn_year_name][term_name][role_name][field_name][cand_id]

                                            with open(cv_dir, 'r') as json_file:
                                                data = json.load(json_file)
                                                ddict["pubbs"] = []

                                                for pub in data["pubbs_ind"]:
                                                    d1 = dict()
                                                    d1["cv_id"] = dict()
                                                    d1["cv_id"]["pubbs_ind"] = pub["id"]
                                                    d1["year"] = int(pub["anno"])
                                                    d1["type"] = pub["type"].lower()
                                                    if pub["parsed"] is not None:
                                                        if "doi" in pub["parsed"].keys():
                                                            d1["doi"] = cleaning_doi(pub["parsed"]["doi"][0].upper())
                                                        if "titolo" in pub["parsed"].keys():
                                                            d1["title"] = cleaning_title(pub["parsed"]["titolo"])
                                                        if "journal" in pub["parsed"].keys():
                                                            d1["journal"] = pub["parsed"]["journal"]
                                                        if "ISBN" in pub["parsed"].keys():
                                                            d1["ISBN"] = pub["parsed"]["ISBN"]
                                                        if "ISSN" in pub["parsed"].keys():
                                                            d1["ISSN"] = pub["parsed"]["ISSN"]
                                                    ddict["pubbs"].append(d1)

                                                for pub in data["pubbs"]:
                                                    d2 = dict()
                                                    d2["cv_id"] = dict()
                                                    d2["cv_id"]["pubbs"] = pub["id"]
                                                    d2["type"] = pub["type"].lower()
                                                    d2["year"] = int(pub["anno"])
                                                    if pub["parsed"] is not None:
                                                        if "doi" in pub["parsed"].keys():
                                                            d2["doi"] = cleaning_doi(pub["parsed"]["doi"][0].upper())
                                                        if "titolo" in pub["parsed"].keys():
                                                            d2["title"] = cleaning_title(pub["parsed"]["titolo"])
                                                        if "journal" in pub["parsed"].keys():
                                                            d2["journal"] = pub["parsed"]["journal"]
                                                        if "ISBN" in pub["parsed"].keys():
                                                            d2["ISBN"] = pub["parsed"]["ISBN"]
                                                        if "ISSN" in pub["parsed"].keys():
                                                            d2["ISSN"] = pub["parsed"]["ISSN"]

                                                    copy = matching_pubbs(ddict["pubbs"], d2)
                                                    ddict["pubbs"] = copy

    return cand_dd


def extracting_metadata_comm(path):

    comm_dd = dict()

    with open(path, 'r', encoding='utf-8') as csvfile:
        comm_csv = csv.reader(csvfile)

        for row in comm_csv:
            if row[0]:
                if row[0] in comm_dd.keys():
                    if row[1] in comm_dd[row[0]].keys():
                        if row[2] in comm_dd[row[0]][row[1]].keys():
                            pub = dict()
                            pub["id"] = row[5]
                            pub["title"] = cleaning_title(row[6])
                            pub["year"] = int(row[7])
                            if row[8]:
                                pub["doi"] = cleaning_doi(row[8])
                            comm_dd[row[0]][row[1]][row[2]]["pubbs"].append(pub)
                        # asn year, field, id
                        else:
                            comm_dd[row[0]][row[1]][row[2]] = dict()
                            comm_dd[row[0]][row[1]][row[2]]["fullname"] = [row[3], row[4]]
                            comm_dd[row[0]][row[1]][row[2]]["pubbs"] = []
                            pub = dict()
                            pub["id"] = row[5]
                            pub["title"] = cleaning_title(row[6])
                            pub["year"] = int(row[7])
                            if row[8]:
                                pub["doi"] = cleaning_doi(row[8])
                            comm_dd[row[0]][row[1]][row[2]]["pubbs"].append(pub)
                    else:
                        comm_dd[row[0]][row[1]] = dict()
                else:
                    comm_dd[row[0]] = dict()

    return comm_dd


def extracting_metadata(jsons_path, csv_path):

    dd = dict()
    dd["cand"] = dict()
    cand_dict = extracting_metadata_cand(jsons_path, dd["cand"])
    dd["cand"] = cand_dict

    dd["comm"] = dict()
    comm_dict = extracting_metadata_comm(csv_path)
    dd["comm"] = comm_dict

    return dd
