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


if __name__ == '__main__':
    url = "https://kcholdbazaar.com/040-temple-street-green-hill/"
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

    # OLLAMA
    print("starting with ollama")
    prompt = "You are a data scientist working for a company that is building a graph database. Your task is to extract information from data and convert it into a graph database." + \
            f"Use the following ontology: {ontology}" + \
            "Pay attention to the type of the properties, if you can't find data for a property set it to null. IMPORTANT: DONT MAKE ANYTHING UP AND DONT ADD ANY EXTRA DATA. If you can't find any data for a node or relationship don't add it." + \
            f"Only add nodes and relationships that are part of the ontology. If you don't get any relationships in the schema only add nodes. Give the response in json format. This is the data, the title of the text is denoted with 'TITLE=': {contents}"
    # response = ollama.generate(model="llama3", prompt=prompt)
    client = Client(host='ollama')
    from ollama import Client
    response = client.generate(model="llama3", prompt=prompt)
    print(response["response"])
