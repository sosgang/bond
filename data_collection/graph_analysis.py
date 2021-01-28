""" Create graph, measure features and collect results """

import networkx as nx
import numpy as np

''' Create graph'''


def create_graph_pid(graph, list_pubbs, group, author, key, end_date):
    for pub in list_pubbs:
        if pub[key] < end_date:
            if "PId" in pub.keys() or "doi" in pub.keys():
                id_a = ''
                if "PId" in pub.keys():
                    id_a = str(pub["PId"])
                elif "doi" in pub.keys():
                    id_a = pub["doi"]

                if id_a in graph.nodes() and group in graph.nodes[id_a].keys():
                    graph.nodes[id_a][group].add(author)
                elif id_a in graph.nodes():
                    graph.nodes[id_a][group] = set()
                    graph.nodes[id_a][group].add(author)

                else:
                    graph.add_node(id_a)
                    graph.nodes[id_a][group] = set()
                    graph.nodes[id_a][group].add(author)

                if "cited" in pub.keys():
                    for ref in pub["cited"]:
                        if "PId" in ref.keys():
                            id_b = str(ref["PId"])
                            graph.add_edge(id_a, id_b)
                        elif "doi" in ref.keys():
                            id_b = ref["doi"]
                            graph.add_edge(id_a, id_b)

                if "citing" in pub.keys():
                    for cit in pub["citing"]:
                        if "PId" in cit.keys():
                            id_c = str(cit["PId"])
                            graph.add_edge(id_c, id_a)
                        elif "doi" in cit.keys():
                            id_c = cit["doi"]
                            graph.add_edge(id_c, id_a)

    return graph


def merge_graphs_pid(comm_dd, cand_dd, author, end_date):
    comm_g_a = nx.DiGraph()
    for comm_id, info in comm_dd.items():
        surname = info["fullname"][0]
        comm_g_b = create_graph_pid(comm_g_a, info["pubbs"], "commission", surname, "year", end_date)
        comm_graph = create_graph_pid(comm_g_b, info["pubbs_mag"], "commission", surname, "year_mag", end_date)
    cand_g_a = create_graph_pid(comm_graph, cand_dd["pubbs"], "candidate", author, "year", end_date)
    candidate_graph = create_graph_pid(cand_g_a, cand_dd["pubbs_mag"], "candidate", author, "year_mag", end_date)

    return candidate_graph


"""Co-Authorship"""


def co_authorship(cand_nodes, comm_nodes):
    co_aut = dict()
    co_aut["articles"] = [n for n in np.intersect1d(cand_nodes, comm_nodes)]
    co_aut["number"] = len(co_aut["articles"])

    return co_aut


"""Shortest path (1: Direct Citation)"""


def find_paths(nodes1, nodes2, paths):
    paths_dict = dict()
    for n1 in nodes1:
        if n1 in paths.keys():
            for n2 in nodes2:
                if n2 in paths[n1].keys():
                    p = paths[n1][n2]
                    li = len(p) - 1
                    if li > 0:
                        if li in paths_dict.keys():
                            paths_dict[li].append((n1, n2))
                        else:
                            paths_dict[li] = [(n1, n2)]

    return paths_dict


"""Bibliographic couplings"""


def bibliographic_coupling(graph, candidate_nodes, commission_nodes):
    bc_dict = dict()
    bc_dict["articles"] = dict()
    bc_cited = set()
    for n1 in candidate_nodes:
        for n2 in commission_nodes:
            if n1 != n2:
                cited_n1 = list(graph.adj[n1])
                cited_n2 = list(graph.adj[n2])
                cited = list(np.intersect1d(cited_n1, cited_n2))
                if cited:
                    n = len(cited)
                    bc_dict["articles"][f"{n1}_+_{n2}"] = n
                    bc_cited.update(set(cited))

    bc_dict["number"] = len(list(bc_cited))

    return bc_dict


"""Co-citation"""


def co_citations(graph, other_nodes, candidate_nodes, commission_nodes):
    cc_dict = dict()
    cc_dict["articles"] = dict()
    cc_citing = set()
    for n3 in other_nodes:
        cited_n3 = list(graph.adj[n3])
        cand_cit = list(np.intersect1d(cited_n3, candidate_nodes))
        comm_cit = list(np.intersect1d(cited_n3, commission_nodes))
        if cand_cit and comm_cit:
            for a in cand_cit:
                for b in comm_cit:
                    if a != b:
                        if (a, b) in cc_dict["articles"].keys():
                            cc_dict["articles"][f"{a}_+_{b}"] += 1
                        else:
                            cc_dict["articles"][f"{a}_+_{b}"] = 0
                            cc_dict["articles"][f"{a}_+_{b}"] += 1
            cc_citing.add(n3)
    cc_dict["number"] = len(list(cc_citing))

    return cc_dict


"""Relationships with other articles"""


def other_citations(graph, nodes1, nodes2):
    other_cit = 0
    for n1 in nodes1:
        for n2 in nodes2:
            if n2 in graph.adj[n1]:
                other_cit += 1

    return other_cit


"""Assemble"""


def analyze_graph(comm, cand_json, author, end_date):
    results = dict()
    merged_graph = merge_graphs_pid(comm, cand_json, author, end_date)

    cand_nodes = [n for n in merged_graph.nodes() if "candidate" in merged_graph.nodes[n].keys()]
    results["cand_nodes"] = len(cand_nodes)
    comm_nodes = [n for n in merged_graph.nodes() if "commission" in merged_graph.nodes[n].keys()]
    results["comm_nodes"] = len(comm_nodes)
    others = [n for n in merged_graph.nodes() if n not in cand_nodes and n not in comm_nodes]
    results["other_nodes"] = len(others)

    results["co-au"] = co_authorship(cand_nodes, comm_nodes)

    merged_paths = nx.shortest_path(merged_graph)
    results["cand_paths"] = find_paths(cand_nodes, comm_nodes, merged_paths)
    results["comm_paths"] = find_paths(comm_nodes, cand_nodes, merged_paths)

    results["bc"] = bibliographic_coupling(merged_graph, cand_nodes, comm_nodes)
    results["cc"] = co_citations(merged_graph, others, cand_nodes, comm_nodes)

    results["other"] = dict()
    results["other"]["cand_other"] = other_citations(merged_graph, cand_nodes, others)
    # results["other"]["comm_other"] = other_citations(merged_graph, comm_nodes, others)
    results["other"]["other_cand"] = other_citations(merged_graph, others, cand_nodes)
    # results["other"]["other_comm"] = other_citations(merged_graph, others, comm_nodes)

    return results


"""create and """


def adding_citmetrics(dd):

    print("adding citmetrics")

    for asn_year, terms in dd["cand"].items():
        for term, roles in terms.items():
            for role, fields in roles.items():
                for field, candidates in fields.items():

                    comm = dd["comm"][asn_year][field]

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

                    for cand_id, info in candidates.items():
                        info["citmetrics"] = analyze_graph(comm, info, info["fullname"][0], limit)

    return dd
