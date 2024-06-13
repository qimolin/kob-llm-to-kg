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

    # OLLAMA
    print("starting with ollama")
    prompt = f"Given the following text, why is Temple Street called Temple Street? {contents}"
    from ollama import Client
    # response = ollama.generate(model="llama3", prompt=prompt)
    client = Client(host='ollama')
    response = client.generate(model="llama3", prompt=prompt)
    print(response)
