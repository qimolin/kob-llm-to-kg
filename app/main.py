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

def load_content_to_database(filePath: str) -> None:
    if not filePath.endswith(".csv"):
        raise ValueError(f"Can only load .csv files, cannot load {filePath}")
    
    if os.path.getsize(filePath) == 0:
        raise ValueError(f"File {filePath} is empty")
    
    nodes = "_id,_labels,id,name,type\n"
    relationships = "_start,_end,_type\n"
    idIntTableRow = {} # _id is only table row and not fixed
    
    with open(filePath, "r") as f:
        for line in f:
            if line.startswith("_id"):
                continue
            if line.split(",")[0].isdecimal() and line.split(",")[0].strip() !='' :
                nodes += ','.join(line.split(",")[:5]) + "\n"
                idIntTableRow[int(line.split(",")[0])] = line.split(",")[2] 
            else:
                startId = line.split(",")[5]
                endId = line.split(",")[6]
                relationship = idIntTableRow[int(startId)] + "," + idIntTableRow[int(endId)] + "," + line.split(",")[7]
                relationships += relationship

    nodesFilePath = f"./neo4j/import/{filePath.split("/")[-1]}".replace(".csv", "_nodes.csv")
    relationshipsFilePath = f"./neo4j/import/{filePath.split("/")[-1]}".replace(".csv", "_relationships.csv")

    with open(nodesFilePath, "w+") as f:
        f.write(nodes.strip())
    with open(relationshipsFilePath, "w+") as f:
        f.write(relationships.strip())        

    # Insert contents to database
    print(f"Inserting {filePath} to database")

    URI = "neo4j://neo4j"
    URI="bolt://localhost:7687"
    # AUTH = ("neo4j",  os.getenv('NEO4J_PASSWORD'))
    AUTH = ("neo4j",  "neo4jpass")
    nodesQuery=f"LOAD CSV WITH HEADERS FROM 'file:///{nodesFilePath.split('/')[-1]}' AS csvLine CALL {{ WITH csvLine CREATE (:n {{id: csvLine.id, labels: csvLine._labels, name: csvLine.name, type: csvLine.type }} ) }}"
    
    realtionsipQuery=f"""LOAD CSV WITH HEADERS from 'file:///{relationshipsFilePath.split('/')[-1]}' AS line
        WITH line._start AS subject, line._end AS object, line._type AS relation_type
        MATCH (s:n {{id: subject}})
        MATCH (o:n {{id: object}})
        CALL apoc.merge.relationship(s, relation_type, {{}}, {{}}, o, {{}})
        YIELD rel
        RETURN rel"""

    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.verify_connectivity()
        driver.execute_query(
            nodesQuery,
            database_="neo4j"
        )
        print(f"Inserted nodes from {nodesFilePath} to database")
        driver.execute_query(
            realtionsipQuery,
            database_="neo4j"
        )
        print(f"Inserted relationships from {relationshipsFilePath} to database")

def check_if_in_ontology(ontology: dict, check: str) -> str | None:
    if check in ontology["@context"]:
        return check

    check_without_id = "_".join(check.split("_")[0:])
    print(check_without_id)
    for k in ontology["@context"]:
        if k == "crm": continue
        if "_".join(k.split("_")[1:]) == check_without_id:
            return k

    print("ERROR: did not find", check, "in ontology, skipping")
    return None


def output_to_csv(res: str, ontology: dict) -> str:
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

def send_to_ollama(contents: str) -> str:
    with open("./ontology.json", "r") as f:
            ontology = json.loads(f.read())

    with open("./ontology_without_money.json", "r") as f:
        ontology_without_money = json.loads(f.read())

    # OLLAMA
    print("starting with ollama")
    prompt = f"You are a data scientist working for a company that is building a knowledge graph about Kuching Old Bazaar. Your task is to extract information from a text about Kuching Old Bazaar and convert it into a graph database. " + \
            f"Use the following ontology: {ontology}, returning a set of nodes and relationships." + \
            "For a node, give the name of the node and its type according to the ontology, according to the following format: NAME, crm:NODE_TYPE." + \
            "For a relationship, give the name of the first node, the name of the second node, and the relationship type according to the ontology according to the following format: NODE1, NODE2, crm:RELAIONSHIP_TYPE " + \
            "IMPORTANT: DO NOT MAKE UP ANYTHING AND DO NOT ADD ANY EXTRA DATA THAT IS NOT SPECIFICALLY GIVEN IN THE TEXT. " + \
            "Only add nodes and relationships that are part of the ontology, if you cannot find any relationships in the text, only return nodes." + \
            f"This is the text from which you should extract the nodes and relationships, the title of the text is denoted with 'TITLE=': {contents}"    # prompt = f"You are a data scientist working for a company that is building a graph database. Your task is to extract information from data about {title} and convert it into a graph database. " + \
    # response = ollama.generate(model="llama3", prompt=prompt)["response"]
    response = """**Nodes:**

1. Temple Street, crm:Place
2. Green Hill, crm:Place
3. Reservoir Park, crm:Place
4. Thompson Road, crm:Place (now known as Jalan Tunku Abdul Rahman)
5. Tua Pek Kong Temple, crm:Place
6. Old Chinese Chamber of Commerce, crm:Organization
7. Sungai Kuching, crm:BodyOfWater
8. Sungai Sarawak, crm:BodyOfWater
9. Bukit Mata Kuching, crm:GeographicLocation

**Relationships:**

1. Temple Street, Tua Pek Kong Temple, crm:P195_was_a_presence_of
2. Temple Street, Thompson Road, crm:P182i_starts_after_or_with_the_end_of
3. Temple Street, Sungai Kuching, crm:P179i_was_sales_price_of

Please note that I have only extracted nodes and relationships mentioned in the provided text and according to the ontology. If there are no specific relationships mentioned in the text, I did not create any fictional ones.
"""
    print(response)

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
    # with open(f"./texts/{page_name}.txt", "w+") as f:
    #     print(contents)
    #     f.write(contents.strip())
    # if os.getenv("SKIP_OLLAMA") == "True":
    if False:
        send_to_ollama(contents)

    load_content_to_database(f"./outputs/{page_name}.csv")