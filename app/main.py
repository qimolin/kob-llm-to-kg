import json
import ollama
import re
import requests
from bs4 import BeautifulSoup
from requests import HTTPError, Response
from neo4j import GraphDatabase
import os
import uuid

def get_url(url: str) -> Response:
    """Retrieve page from kcholdbazaar.com."""
    if "kcholdbazaar.com" not in url:
        raise ValueError(f"Can only retrieve KOB URLs, cannot get {url}.")

    print(f'retrieving {url}')
    res = requests.get(url)
    res.raise_for_status()

    return res


def get_contents(res: Response) -> str:
    """Extract English text from Response."""
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


def load_content_to_database(filePath: str) -> None:
    """Load data to Neo4j database."""
    print (f"Loading {filePath} to database")

    # check if file exists and is csv
    if not filePath.endswith(".csv"):
        raise ValueError(f"Can only load .csv files, cannot load {filePath}")

    if os.path.getsize(filePath) == 0:
        raise ValueError(f"File {filePath} is empty")

    nodes = "_id,_labels,id,name,type\n"
    relationships = "_start,_end,_type\n"
    idIntTableRow = {} # _id is only table row and not fixed

    with open(filePath, "r") as f:
        for line in f:
            # skip header
            if line.startswith("_id"):
                continue
            # add row to nodes csv
            if line.split(",")[0].isdecimal() and line.split(",")[0].strip() !='' :
                nodes += ','.join(line.split(",")[:5]) + "\n"
                idIntTableRow[int(line.split(",")[0])] = line.split(",")[2]
            # add row to relationships csv
            else:
                start_id = line.split(",")[5]
                end_id = line.split(",")[6]
                relationship = idIntTableRow[int(start_id)] + "," + idIntTableRow[int(end_id)] + "," + line.split(",")[7]
                relationships += relationship

    # write to file
    nodes_file_path = f"./neo4j/import/{filePath.split("/")[-1]}".replace(".csv", "_nodes.csv")
    relationships_file_path = f"./neo4j/import/{filePath.split("/")[-1]}".replace(".csv", "_relationships.csv")

    with open(nodes_file_path, "w+") as f:
        f.write(nodes.strip())
    with open(relationships_file_path, "w+") as f:
        f.write(relationships.strip())

    # Insert contents to database
    print(f"Inserting {filePath} to database")

    uri = os.getenv('NEO4J_URI')
    auth = ("neo4j",  os.getenv('NEO4J_PASSWORD'))
    # auth = ("neo4j",  "neo4jpass")
    nodes_query=f"LOAD CSV WITH HEADERS FROM 'file:///{nodes_file_path.split('/')[-1]}' AS csvLine CALL {{ WITH csvLine CREATE (:n {{id: csvLine.id, labels: csvLine._labels, name: csvLine.name, type: csvLine.type }} ) }}"

    relationships_query=f"""LOAD CSV WITH HEADERS from 'file:///{relationships_file_path.split('/')[-1]}' AS line
        WITH line._start AS subject, line._end AS object, line._type AS relation_type
        MATCH (s:n {{id: subject}})
        MATCH (o:n {{id: object}})
        CALL apoc.merge.relationship(s, relation_type, {{}}, {{}}, o, {{}})
        YIELD rel
        RETURN rel"""

    with GraphDatabase.driver(uri, auth=auth) as driver:
        driver.verify_connectivity()
        driver.execute_query(
            nodes_query,
            database_="neo4j"
        )
        print(f"Inserted nodes from {nodes_file_path} to database")
        driver.execute_query(
            relationships_query,
            database_="neo4j"
        )
        print(f"Inserted relationships from {relationships_file_path} to database")

def check_if_in_ontology(ontology: dict, check: str) -> str | None:
    """Check if 'check' is in ontology and if so, return with proper ID."""
    if check in ontology["@context"]:
        return check

    check_without_id = "_".join(check.split("_")[0:])
    for k in ontology["@context"]:
        if k == "crm": continue
        if "_".join(k.split("_")[1:]) == check_without_id:
            return k

    print("ERROR: did not find", check, "in ontology, skipping")
    return None


def output_to_csv(res: str, ontology: dict) -> str:
    """Save nodes and relationships to csv."""
    nodes = {}
    relationships = set()

    reading_nodes = False
    reading_relationships = False
    for line in res.split("\n"):
        line = line.strip("*")
        if re.fullmatch(r"[^\w]*Nodes[^\w]*", line):
            reading_nodes = True
            reading_relationships = False
            continue

        if re.fullmatch(r"[^\w]*Relationships[^\w]*", line):
            reading_nodes = False
            reading_relationships = True
            continue

        if line.startswith("Note"):
            reading_nodes = False
            reading_relationships = False
            continue

        if reading_nodes:
            m = re.match(r"[0-9]\. *(.+), *crm:([^\s]+) *(\(.*\))*", line)
            if m is None: continue
            name = m.group(1)
            label = m.group(2)

            if name in nodes:
                assert nodes[name]["label"] == label
            else:
                label = check_if_in_ontology(ontology, label)
                if label is None: continue
                nodes[name] = { "id": uuid.uuid4(), "label": label }
        elif reading_relationships:
            m = re.match(r"[0-9]\. *(.+), *(.+), *crm:([^\s]+) *(\(.*\))*", line)
            if m is None: continue
            name1 = m.group(1)
            name2 = m.group(2)
            label = m.group(3)
            print(label)

            if not (name1 in nodes and name2 in nodes): continue
            label = check_if_in_ontology(ontology, label)
            if label is None: continue
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


def get_inp_url() -> str:
    """Prompt user to input URL for kcholdbazaar.com page."""
    inp = input("Please enter the webpage url: ").lower().strip()
    if re.fullmatch(r"(https?:\/\/)?(www\.)?kcholdbazaar\.com\/\b([-a-zA-Z0-9()@:%_\+.~#?&\/=]*)", inp) is None:
        print("URL invalid, must be a page of kcholdbazaar.com, try again.")
        get_inp_url()

    return inp


def send_to_ollama(contents: str) -> str:
    """Use ollama to extract nodes and relationships for knowledge graph."""
    url = get_inp_url()
    try:
        res = get_url(url)
    except HTTPError:
        raise ConnectionError(f"Error retrieving list from {url}")
    page_name = url.strip("/").split("/")[-1]

    contents = get_contents(res)
    print(contents)

    with open("./ontology.json", "r") as f:
        ontology = json.loads(f.read())

    with open("./ontology_without_money.json", "r") as f:
        # Ontology without money is used because otherwise LLM over-focuses on relationships related to money.
        ontology_without_money = json.loads(f.read())

    # OLLAMA
    print("starting with ollama")
    prompt = f"You are a data scientist working for a company that is building a knowledge graph about Kuching Old Bazaar. Your task is to extract information from a text about Kuching Old Bazaar and convert it into a graph database. " + \
            f"Use the following ontology: {ontology}, returning a set of nodes and relationships." + \
            "For a node, give the name of the node and its type according to the ontology, according to the following format: (NAME, crm:NODE_TYPE). " + \
            "For a relationship, give the name of the first node, the name of the second node, and the relationship type according to the ontology according to the following format: (NODE1, NODE2, crm:RELAIONSHIP_TYPE) " + \
            "IMPORTANT: DO NOT MAKE UP ANYTHING AND DO NOT ADD ANY EXTRA DATA THAT IS NOT SPECIFICALLY GIVEN IN THE TEXT. " + \
            "Only add nodes and relationships that are part of the ontology, if you cannot find any relationships in the text, only return nodes." + \
            f"This is the text from which you should extract the nodes and relationships, the title of the text is denoted with 'TITLE=': {contents}"
    response = ollama.generate(model="llama3", prompt=prompt)["response"]

    csv_str = output_to_csv(response, ontology_without_money)
    with open(f"./outputs/{page_name}.csv", "w+") as f:
        f.write(csv_str)


if __name__ == '__main__':
    url = "https://kcholdbazaar.com/040-temple-street-green-hill/"
    try:
        res = get_url(url)
    except HTTPError:
        raise ConnectionError(f"Error retrieving list from {url}")

    contents = get_contents(res)

    page_name = url.strip("/").split("/")[-1]
    print(contents)

    if os.getenv("SKIP_OLLAMA").lower() != "true":
        send_to_ollama(contents)

    load_content_to_database(f"./outputs/{page_name}.csv")