import re
import unicodedata
import requests
import Levenshtein

stoplist = [line.strip() for line in open("stopwords-it.txt")]
stoplist = set(stoplist)


def cleaning_author(author_raw):
    author_clean = author_raw.lower()  # lower-case
    author_clean = re.sub("[^\w\d\s]", "", author_clean)  # remove punctuation
    author_clean = u"".join \
        ([c for c in unicodedata.normalize("NFKD", author_clean) if not unicodedata.combining(c)])  # remove accents
    author_clean = author_clean.split("_")
    if len(author_clean[1]) <= 3:
        author_surname = author_clean[2]
    else:
        author_surname = author_clean[1]
    author_name = author_clean[-1]

    return author_surname, author_name


def search_doi_oa(loggr, doi):

    url_oa = f"http://api.openaire.eu/search/publications?doi={doi}&format=json"
    try:
        r = requests.get(url_oa).json()
        if r["response"]["results"] is not None:
            return 1
        else:
            return 0
    except Exception as ex:
        loggr.error("OA____" + repr(ex) + "____" + url_oa)
        return 0


def search_title_oa(loggr, author, title, year):

    keywords = [w for w in title.split(" ") if w not in stoplist]
    keywords = " ".join(keywords[:6])
    surname, name = cleaning_author(author)
    query = f"title={keywords}&author={surname}&toDateAccepted={str(year)}-12-31&page=1&size=5&format=json"
    url_oa = f"http://api.openaire.eu/search/publications?{query}"
    try:
        r = requests.get(url_oa).json()
        if r["response"]["results"] is not None:
            return 1
        else:
            return 0
    except Exception as ex:
        loggr.error("OA____" + repr(ex) + "____" + url_oa)
        return 0


def search_doi_cr(loggr, doi):

    hdr_cr = {'User-Agent': 'mailto:federica.bologna17@gmail.com'}
    url_cr = f"https://api.crossref.org/works/{doi}"
    try:
        r = requests.get(url_cr, headers=hdr_cr).json()
        if r["message"]:
            return 1
    except Exception as ex:
        loggr.error("CR____" + repr(ex) + "____" + url_cr)
        return 0


def search_title_cr(loggr, author, title, year):
    hdr_cr = {'User-Agent': 'mailto:federica.bologna17@gmail.com'}
    keywords = [w for w in title.split(" ") if w not in stoplist]
    keywords = " ".join(keywords[:4])
    surname, name = cleaning_author(author)
    query = f"query.bibliographic={keywords}&query.author={surname}&rows=4&select=DOI,title,author,issued"
    url_cr = f"https://api.crossref.org/works?{query}"

    try:
        r = requests.get(url_cr, headers=hdr_cr).json()
        possible = []
        if r["message"]["items"]:
            idx = 0
            while idx < len(r["message"]["items"]):
                point_a = 0
                point_b = 0
                if r["message"]["items"][idx]["issued"]["date-parts"][0][0]:
                    if r["message"]["items"][idx]["issued"]["date-parts"][0][0] == year:
                        point_a += 3
                    elif year - 1 < r["message"]["items"][idx]["issued"]["date-parts"][0][0] < year + 1:
                        point_a += 2
                    elif year - 2 < r["message"]["items"][idx]["issued"]["date-parts"][0][0] < year + 2:
                        point_a += 1

                for n in r["message"]["items"][idx]["author"]:
                    if "family" in n.keys() and "given" in n.keys():
                        if n["family"].lower() == surname and n["given"].lower() == name:
                            point_b += 2
                        elif n["family"].lower() == surname and n["given"].lower()[0] == name[0]:
                            point_b += 1

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

    except Exception as ex:
        loggr.error("CR____" + repr(ex) + "____" + url_cr)