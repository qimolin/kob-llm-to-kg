import json
import ollama
import re
import requests
from bs4 import BeautifulSoup
from requests import HTTPError, Response


def get_url(url: str) -> Response:
    if "kcholdbazaar.com" not in url:
        raise ValueError(f"Can only retrieve KOB URLs, cannot get {url}.")

    print(f'retrieving {url}')
    res = requests.get(url)
    res.raise_for_status()

    return res


def get_contents(res: Response) -> str:
    soup = BeautifulSoup(res.text, features="html.parser")

    title_soup = soup.find("h1", attrs={"class": "entry-title"})
    title = title_soup.text
    if title.split()[0].isnumeric():
        title = " ".join(title.split()[1:])

    content_soup = soup.find("div", attrs={"class": "entry-content"})
    contents = "TITLE=" + title
    english_heading = True
    for c in content_soup.children:
        if c.name != "p" and c.name != None:
            if len(re.findall(r'[\u4e00-\u9fff]+', c.text)) > 0:
                english_heading = False
            else:
                english_heading = True
                contents += "\n"

        if english_heading:
            contents += c.text

    return contents


def check_if_in_ontology(ontology: dict, check: str) -> bool:
    if check in ontology["@context"]:
        return True

    # TODO: only look at name not at ID, get ID yourself

    print("ERROR: did not find", check, "in ontology, skipping")
    return False
    # assert False TODO: remove?


def output_to_csv(res: str, ontology: dict) -> str:
    nodes = {}
    relationships = set()
    id_counter = 1

    reading_nodes = False
    reading_relationships = False
    for line in res.split("\n"):
        line = line.strip("*")
        print(line, reading_nodes)
        if line.startswith("Nodes"): # TODO: regex
            reading_nodes = True
            reading_relationships = False
            continue

        if line.startswith("Relationships"):
            reading_nodes = False
            reading_relationships = True
            continue

        if line.startswith("Note"):
            reading_nodes = False
            reading_relationships = False
            continue

        try:
            line = line.split(".")[1].split(",")
        except IndexError:
            continue

        if reading_nodes:
            try:
                name = line[0].strip()
                label = line[1].split("(")[0].split(":")[1].strip()
            except IndexError:
                continue
            if name in nodes:
                assert nodes[name]["label"] == label
            else:
                if not check_if_in_ontology(ontology, label): continue
                nodes[name] = { "id": id_counter, "label": label }
                id_counter += 1 # TODO: fix this
        elif reading_relationships:
            try:
                name1 = line[0].strip()
                name2 = line[1].strip()
                if not (name1 in nodes and name2 in nodes): continue
                label = line[2].split("(")[0].split(":")[1].strip()
            except IndexError:
                continue
            check_if_in_ontology(ontology, label)
            relationships.add((name1, name2, label))

    csv = "_id,_labels,id,name,type,_start,_end,_type\n"
    for name in nodes:
        label = nodes[name]["label"]
        id = nodes[name]["id"]
        csv += f"{id},:{label},{id},{name},,,,\n"
    for name1, name2, label in relationships:
        id1 = nodes[name1]["id"]
        id2 = nodes[name2]["id"]
        csv += f",,,,,{id1},{id2},{label}\n"

    return csv


if __name__ == '__main__':
    url = "https://kcholdbazaar.com/039-wayang-street/"
    try:
        res = get_url(url)
    except HTTPError:
        raise ConnectionError(f"Error retrieving list from {url}")

    contents = get_contents(res)

    page_name = url.strip("/").split("/")[-1]
    with open(f"./texts/{page_name}.txt", "w+") as f:
        print(contents)
        f.write(contents.strip())

    with open("./ontology.json", "r") as f:
        ontology = json.loads(f.read())

    with open("./ontology_without_money.json", "r") as f:
        ontology_without_money = json.loads(f.read())

    # OLLAMA
    print("starting with ollama")
    title = "Temple Street / Green Hill"
    prompt = f"You are a data scientist working for a company that is building a knowledge graph about Kuching Old Bazaar. Your task is to extract information from a text about {title} and convert it into a graph database. " + \
            f"Use the following ontology: {ontology}, returning a set of nodes and relationships." + \
            "For a node, give the name of the node and its type according to the ontology, according to the following format: NAME, crm:NODE_TYPE." + \
            "For a relationship, give the name of the first node, the name of the second node, and the relationship type according to the ontology according to the following format: NODE1, NODE2, crm:RELAIONSHIP_TYPE " + \
            "IMPORTANT: DO NOT MAKE UP ANYTHING AND DO NOT ADD ANY EXTRA DATA THAT IS NOT SPECIFICALLY GIVEN IN THE TEXT." + \
            "Only add nodes and relationships that are part of the ontology, if you cannot find any relationships in the text, only return nodes." + \
            f"This is the text from which you should extract the nodes and relationships, the title of the text is denoted with 'TITLE=': {contents}"    # prompt = f"You are a data scientist working for a company that is building a graph database. Your task is to extract information from data about {title} and convert it into a graph database. " + \
    response = ollama.generate(model="llama3", prompt=prompt)["response"]
    print(response)

#     response = """After analyzing the text, I found the following nodes and relationships:

# **Nodes:**

# 1. Wayang Street, crm:E52_Temporal_Entity
# 2. Hua Xiang Street, crm:E52_Temporal_Entity
# 3. Hong San Si Temple, crm:E22_Man_Made_Thing
# 4. Malaysia, crm:E39_Social_Event (note: this is not a direct match, but I assume "Malay" refers to the Malaysian ethnicity)

# **Relationships:**

# 1. Wayang Street, Hua Xiang Street, crm:P9_consists_of (the street has an alternative name)
# 2. Wayang Street, Hong San Si Temple, crm:P46_is_location_of (the temple is located on the street)
# 3. Wayang Street, Malaysia, crm:P7_was_influenced_by (the Malay ethnicity had an influence on the street's culture)

# Please note that I did not create any new nodes or relationships outside of what was explicitly mentioned in the text.
# """

    csv_str = output_to_csv(response, ontology_without_money)
    with open(f"./outputs/{page_name}.csv", "w+") as f:
        f.write(csv_str)

    # from ollama import Client
    # client = Client(host='ollama')
    # response = client.generate(model="llama3", prompt=prompt)
