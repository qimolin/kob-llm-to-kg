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


def get_contents(res: Response) -> tuple[str]:
    soup = BeautifulSoup(res.text, features="html.parser")

    title_soup = soup.find("h1", attrs={"class": "entry-title"})
    title = title_soup.text

    content_soup = soup.find("div", attrs={"class": "entry-content"})
    contents = "TITLE=" + title + "\n"
    for c in content_soup.children:
        if c.name != "p" and c.name != None:
            break
        contents += c.text

    return contents


if __name__ == '__main__':
    url = "https://kcholdbazaar.com/mural-art-the-big-well-and-the-coolie-keng/"
    try:
        res = get_url(url)
    except HTTPError:
        raise ConnectionError(f"Error retrieving list from {url}")

    contents = get_contents(res)

    page_name = url.strip("/").split("/")[-1]
    with open(f"./texts/{page_name}.txt", "w+") as f:
        f.write(contents.strip())
