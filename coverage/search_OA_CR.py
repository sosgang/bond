import time
import re
import unicodedata
import requests
import Levenshtein


""" Cleaning title and identifying author name """
def cleaning_title(title, typ):

    if typ == "oa":
        n = 6
    else:
        n = 4
    stoplist = [line.strip() for line in open("stopwords-it.txt")]
    stoplist = set(stoplist)
    keywords = [w for w in title.split(" ") if w not in stoplist]
    keywords = " ".join(keywords[:n])

    return keywords


def cleaning_name(name_raw):

    name_clean = u"".join([c for c in unicodedata.normalize("NFKD", name_raw) if not unicodedata.combining(c)])
    name_clean = name_clean.lower()
    name_clean = re.sub(r"[^\w\d\s]", "", name_clean)

    return name_clean


def search_doi_oa(loggr, doi):

    url_oa = f"http://api.openaire.eu/search/publications?doi={doi}&format=json"

    try:
        r_oa = requests.get(url_oa, timeout=10)
        hdrs_oa = r_oa.headers

        try:
            r = r_oa.json()
            if r["response"]["results"] is not None:
                return 1
            else:
                return 0

        except Exception as ex1:
            loggr.error("OA__" + repr(ex1) + "__" + url_oa)
            return 0

    except Exception as ex0:
        if "ConnectTimeout" in repr(ex0):
            time.sleep(5.0)
            solution = search_doi_oa(loggr, doi)
            return solution
        else:
            return 0


def search_title_oa(loggr, fullname, title, year):

    keywords = cleaning_title(title, "oa")
    surname = cleaning_name(fullname[0].split(" ")[-1])
    query = f"title={keywords}&author={surname}&toDateAccepted={str(year)}-12-31&page=1&size=5&format=json"
    url_oa = f"http://api.openaire.eu/search/publications?{query}"

    try:
        r_oa = requests.get(url_oa, timeout=10)
        hdrs_oa = r_oa.headers

        try:
            r = r_oa.json()
            if r["response"]["results"] is not None:
                return 1
            else:
                return 0

        except Exception as ex1:
            loggr.error("OA__" + repr(ex1) + "__" + url_oa)
            return 0

    except Exception as ex0:
        if "ConnectTimeout" in repr(ex0):
            time.sleep(5.0)
            solution = search_title_oa(loggr, fullname, title, year)
            return solution
        else:
            return 0


def search_doi_cr(loggr, doi):

    hdr_cr = {'User-Agent': 'mailto:federica.bologna17@gmail.com'}
    url_cr = f"https://api.crossref.org/works/{doi}"

    try:
        r_cr = requests.get(url_cr, headers=hdr_cr, timeout=60)
        hdrs_cr = r_cr.headers

        try:
            r = r_cr.json()
            if r["message"]:
                return 1
            else:
                return 0

        except Exception as ex1:
            if hdrs_cr["content-type"] == 'text/plain' or hdrs_cr["content-type"] == 'text/html':
                r = r_cr.text
                if "503" in r:
                    time.sleep(5.0)
                    solution = search_doi_cr(loggr, doi)
                    return solution
            else:
                loggr.exception("CR__" + repr(ex1) + "__" + url_cr + "__" + hdrs_cr["content-type"])
            return 0

    except Exception as ex0:
        if "ConnectTimeout" in repr(ex0):
            loggr.error("CR__" + repr(ex0) + "__" + url_cr)
            time.sleep(5.0)
            solution = search_doi_cr(loggr, doi)
            return solution
        else:
            return 0


def search_title_cr(loggr, fullname, title, year):

    hdr_cr = {'User-Agent': 'mailto:federica.bologna17@gmail.com'}
    keywords = cleaning_title(title, "cr")
    surname = cleaning_name(fullname[0].split(" ")[-1])
    name = cleaning_name(fullname[1].split(" ")[0])
    query = f"query.bibliographic={keywords}&query.author={surname}&rows=4&select=DOI,title,author,issued"
    url_cr = f"https://api.crossref.org/works?{query}"
    try:
        r_cr = requests.get(url_cr, headers=hdr_cr, timeout=60)
        hdrs_cr = r_cr.headers

        try:
            r = r_cr.json()
            possible = []
            if r["message"]["items"]:
                idx = 0
                while idx < len(r["message"]["items"]):
                    point_a = 0
                    point_b = 0
                    point_c = 0
                    if "issued" in r["message"]["items"][idx].keys():
                        if "date-parts" in r["message"]["items"][idx]["issued"].keys():
                            if r["message"]["items"][idx]["issued"]["date-parts"][0][0]:
                                if r["message"]["items"][idx]["issued"]["date-parts"][0][0] == year:
                                    point_a += 3
                                elif year - 1 < r["message"]["items"][idx]["issued"]["date-parts"][0][0] < year + 1:
                                    point_a += 2
                                elif year - 2 < r["message"]["items"][idx]["issued"]["date-parts"][0][0] < year + 2:
                                    point_a += 1

                    if "author" in r["message"]["items"][idx].keys():
                        for n in r["message"]["items"][idx]["author"]:
                            if "family" in n.keys():
                                if "given" in n.keys():
                                    if n["family"].lower() == surname and n["given"].lower() == name:
                                        point_b += 2
                                    elif n["family"].lower() == surname and n["given"].lower()[0] == name[0]:
                                        point_b += 1
                                elif n["family"].lower() == surname:
                                    point_b += 1

                    if "title" in r["message"]["items"][idx].keys():
                        title_pub = r["message"]["items"][idx]["title"][0].lower()
                        point_c = Levenshtein.ratio(title, title_pub)

                    possible.append((point_c, point_b, point_a, idx))
                    idx += 1

                sort = sorted(possible)
                if sort[-1][0] > 0.8 and sort[-1][1] >= 1 and sort[-1][2] >= 1:
                    return 1

                else:
                    return 0

            else:
                return 0

        except Exception as ex1:
            if hdrs_cr["content-type"] == 'text/plain' or hdrs_cr["content-type"] == 'text/html':
                r = r_cr.text
                if "503" in r:
                    time.sleep(5.0)
                    solution = search_title_cr(loggr, fullname, title, year)
                    return solution
            else:
                loggr.exception("CR__" + repr(ex1) + "__" + url_cr + "__" + hdrs_cr["content-type"])
            return 0

    except Exception as ex0:
        if "ConnectTimeout" in repr(ex0):
            loggr.error("CR__" + repr(ex0) + "__" + url_cr)
            time.sleep(5.0)
            solution = search_title_cr(loggr, fullname, title, year)
            return solution
        else:
            return 0
