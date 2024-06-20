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
    id_counter = 1

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
                nodes[name] = { "id": id_counter, "label": label }
                id_counter += 1 # TODO: fix this
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
    inp = input("Please enter the webpage url: ").lower().strip()
    if re.fullmatch(r"(https?:\/\/)?(www\.)?kcholdbazaar\.com\/\b([-a-zA-Z0-9()@:%_\+.~#?&\/=]*)", inp) is None:
        print("URL invalid, must be a page of kcholdbazaar.com, try again.")
        get_inp_url()

    return inp


if __name__ == '__main__':
    # url = "https://kcholdbazaar.com/040-temple-street-green-hill/"
    url = get_inp_url()
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
    prompt = f"You are a data scientist working for a company that is building a knowledge graph about Kuching Old Bazaar. Your task is to extract information from a text about Kuching Old Bazaar and convert it into a graph database. " + \
            f"Use the following ontology: {ontology}, returning a set of nodes and relationships." + \
            "For a node, give the name of the node and its type according to the ontology, according to the following format: NAME, crm:NODE_TYPE." + \
            "For a relationship, give the name of the first node, the name of the second node, and the relationship type according to the ontology according to the following format: NODE1, NODE2, crm:RELAIONSHIP_TYPE " + \
            "IMPORTANT: DO NOT MAKE UP ANYTHING AND DO NOT ADD ANY EXTRA DATA THAT IS NOT SPECIFICALLY GIVEN IN THE TEXT. " + \
            "Only add nodes and relationships that are part of the ontology, if you cannot find any relationships in the text, only return nodes." + \
            f"This is the text from which you should extract the nodes and relationships, the title of the text is denoted with 'TITLE=': {contents}"    # prompt = f"You are a data scientist working for a company that is building a graph database. Your task is to extract information from data about {title} and convert it into a graph database. " + \
    response = ollama.generate(model="llama3", prompt=prompt)["response"]
#     response = """**Nodes:**

# 1. Temple Street, crm:Place
# 2. Green Hill, crm:Place
# 3. Reservoir Park, crm:Place
# 4. Thompson Road, crm:Place (now known as Jalan Tunku Abdul Rahman)
# 5. Tua Pek Kong Temple, crm:Place
# 6. Old Chinese Chamber of Commerce, crm:Organization
# 7. Sungai Kuching, crm:BodyOfWater
# 8. Sungai Sarawak, crm:BodyOfWater
# 9. Bukit Mata Kuching, crm:GeographicLocation

# **Relationships:**

# 1. Temple Street, Tua Pek Kong Temple, crm:P195_was_a_presence_of
# 2. Temple Street, Thompson Road, crm:P182i_starts_after_or_with_the_end_of
# 3. Temple Street, Sungai Kuching, crm:P179i_was_sales_price_of

# Please note that I have only extracted nodes and relationships mentioned in the provided text and according to the ontology. If there are no specific relationships mentioned in the text, I did not create any fictional ones.
# """
    print(response)

    csv_str = output_to_csv(response, ontology_without_money)
    with open(f"./outputs/{page_name}.csv", "w+") as f:
        f.write(csv_str)

    # from ollama import Client
    # client = Client(host='ollama')
    # response = client.generate(model="llama3", prompt=prompt)
