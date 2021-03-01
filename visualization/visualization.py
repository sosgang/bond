import os
import json
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from xml.dom import minidom
from wand.api import library
import wand.color
import wand.image


def create_graph_pid(graph, list_pubbs, group, author):
    for pub in list_pubbs:
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

    return graph


def draw_graph(comm_dd, cand_dd, cand_surname, path_graph):
    comm_g_a = nx.DiGraph()
    for comm_id, comm_dict in comm_dd.items():
        comm_surname = comm_dict["fullname"][0]
        comm_g_b = create_graph_pid(comm_g_a, comm_dict["pubbs"], "commission", comm_surname)
        comm_graph = create_graph_pid(comm_g_b, comm_dict["pubbs_mag"], "commission", comm_surname)
    cand_g_a = create_graph_pid(comm_graph, cand_dd["pubbs"], "candidate", cand_surname)
    cand_graph = create_graph_pid(cand_g_a, cand_dd["pubbs_mag"], "candidate", cand_surname)

    if 1 in cand_dd["citmetrics"]["cand_paths"].keys():
        for article_pair in cand_dd["citmetrics"]["cand_paths"][1]:
            cand_graph.add_edge(article_pair[0], article_pair[1])
    if 1 in cand_dd["citmetrics"]["comm_paths"].keys():
        for article_pair in cand_dd["citmetrics"]["comm_paths"][1]:
            cand_graph.add_edge(article_pair[0], article_pair[1])

    for articles, number in cand_dd["citmetrics"]["bc"]["articles"].items():
        cand_graph.add_node(articles, n=number)
        cand_graph.add_edge(articles.split("_+_", 1)[0], articles)
        cand_graph.add_edge(articles.split("_+_", 1)[1], articles)
    for articles, number in cand_dd["citmetrics"]["cc"]["articles"].items():
        cand_graph.add_node(articles, n=number)
        cand_graph.add_edge(articles, articles.split("_+_", 1)[0])
        cand_graph.add_edge(articles, articles.split("_+_", 1)[1])

    cand_nodes = [n for n in cand_graph.nodes() if "candidate" in cand_graph.nodes[n].keys()]
    comm_nodes = [n for n in cand_graph.nodes() if "commission" in cand_graph.nodes[n].keys()]
    inter = cand_dd["citmetrics"]["co-au"]["articles"]
    other = [(node, cand_graph.nodes[node]["n"]) for node in cand_graph.nodes()
             if node not in cand_nodes and node not in comm_nodes]

    plt.figure(figsize=(15, 15))
    pos = nx.nx_pydot.graphviz_layout(cand_graph, "sfdp")
    nx.draw_networkx_nodes(cand_graph, pos=pos, nodelist=[n for n in cand_nodes if n not in inter], node_size=150,
                           node_color="blue")
    nx.draw_networkx_nodes(cand_graph, pos=pos, nodelist=[n for n in comm_nodes if n not in inter], node_size=150,
                           node_color="red")
    nx.draw_networkx_nodes(cand_graph, pos=pos, nodelist=inter, node_size=150, node_color="green")
    if other:
        nx.draw_networkx_nodes(cand_graph, pos=pos, nodelist=[node[0] for node in other], node_size=80,
                               node_color=[node[1] + 2 for node in other], alpha=0.5, cmap=plt.get_cmap("binary"),
                               vmin=0, vmax=np.max([node[1] + 2 for node in other]))
    nx.draw_networkx_edges(cand_graph, pos=pos, width=0.5, edge_color="grey", arrows=False)
    plt.savefig(path_graph, bbox_inches="tight")


def modify_svg(cand_dd, path_svg):
    with open('venn.svg') as svg:
        dom = minidom.parse(svg)

        for text in dom.getElementsByTagName("text"):

            if text.firstChild.firstChild.nodeValue == "AAA":
                text.firstChild.firstChild.nodeValue = str(cand_dd["citmetrics"]["cand_nodes"])
            elif text.firstChild.firstChild.nodeValue == "BBB":
                text.firstChild.firstChild.nodeValue = str(cand_dd["citmetrics"]["comm_nodes"])
            elif text.firstChild.firstChild.nodeValue == "DDDD":
                text.firstChild.firstChild.nodeValue = str(cand_dd["citmetrics"]["other_nodes"])
            elif text.firstChild.firstChild.nodeValue == "CO":
                text.firstChild.firstChild.nodeValue = str(cand_dd["citmetrics"]["co-au"]["number"])

            elif text.firstChild.firstChild.nodeValue == "AA":
                if "1" in cand_dd["citmetrics"]["cand_paths"].keys():
                    text.firstChild.firstChild.nodeValue = str(len(cand_dd["citmetrics"]["cand_paths"]["1"]))
                else:
                    text.firstChild.firstChild.nodeValue = "0"
            elif text.firstChild.firstChild.nodeValue == "BB":
                if "1" in cand_dd["citmetrics"]["comm_paths"].keys():
                    text.firstChild.firstChild.nodeValue = str(len(cand_dd["citmetrics"]["comm_paths"]["1"]))
                else:
                    text.firstChild.firstChild.nodeValue = "0"

            elif text.firstChild.firstChild.nodeValue == "XXX":
                text.firstChild.firstChild.nodeValue = str(cand_dd["citmetrics"]["bc"]["number"])
            elif text.firstChild.firstChild.nodeValue == "YYY":
                text.firstChild.firstChild.nodeValue = str(cand_dd["citmetrics"]["cc"]["number"])

            elif text.firstChild.firstChild.nodeValue == "AADD":
                text.firstChild.firstChild.nodeValue = str(cand_dd["citmetrics"]["other"]["cand_other"])
            elif text.firstChild.firstChild.nodeValue == "BBDD":
                text.firstChild.firstChild.nodeValue = str(cand_dd["citmetrics"]["other"]["comm_other"])
            elif text.firstChild.firstChild.nodeValue == "DDAA":
                text.firstChild.firstChild.nodeValue = str(cand_dd["citmetrics"]["other"]["other_cand"])
            elif text.firstChild.firstChild.nodeValue == "DDBB":
                text.firstChild.firstChild.nodeValue = str(cand_dd["citmetrics"]["other"]["other_comm"])

        out_svg = open(path_svg, "w")
        out_svg.write(dom.toxml())
        out_svg.close()


def convert_to_png(path_svg, path_venn):
    with open(path_svg, "r") as svg_file:
        with wand.image.Image() as image:
            with wand.color.Color('transparent') as background_color:
                library.MagickSetBackgroundColor(image.wand,
                                                 background_color.resource)
            svg_blob = svg_file.read().encode('utf-8')
            image.read(blob=svg_blob, resolution=72)
            png_image = image.make_blob("png32")

        with open(path_venn, "wb") as out_png:
            out_png.write(png_image)


def create_visualizations(complete_folder, asn_year, term, role, field, cand_id):

    comm = dict()
    for n in range(1, 6):
        comm_id = str(n)
        comm_path = os.path.join(complete_folder, f'{asn_year}_{field}_{comm_id}_cit.json')
        with open(comm_path, 'r') as comm_file:
            comm[comm_id] = json.load(comm_file)

    cand_path = os.path.join(complete_folder, f'{asn_year}_{term}_{role}_{field}_{cand_id}_complete.json')
    with open(cand_path, 'r') as cand_file:
        cand = json.load(cand_file)

    vis_folder = os.path.join(os.getcwd(), "visualizations")
    if os.path.exists(vis_folder) is False:
        os.mkdir(vis_folder)

    cand_graph = os.path.join(vis_folder, f'{asn_year}_{term}_{role}_{field}_{cand_id}_graph')
    cand_svg = os.path.join(vis_folder, f'{asn_year}_{term}_{role}_{field}_{cand_id}_venn.svg')
    cand_venn = os.path.join(vis_folder, f'{asn_year}_{term}_{role}_{field}_{cand_id}_venn.png')

    if os.path.exists(cand_graph) is False:
        draw_graph(comm, cand, cand["fullname"][0], cand_graph)
    if os.path.exists(cand_svg) is False:
        modify_svg(cand, cand_svg)
    if os.path.exists(cand_venn) is False:
        convert_to_png(cand_svg, cand_venn)


complete_data_folder = os.path.join(os.getcwd(), "complete_data")
asn_year_cand = "2016"
term_cand = "1"
role_cand = "AP"
field_cand = "10-G1"
id_cand = "32140"

create_visualizations(complete_data_folder, asn_year_cand, term_cand, role_cand, field_cand, id_cand)
