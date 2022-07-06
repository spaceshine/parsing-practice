import json
from bs4 import BeautifulSoup


def get_data(url):
    with open("msk.html") as f:
        src = f.read()

    soup = BeautifulSoup(src, 'lxml')
    json_dict = soup.find("div", style="display: none").get("data-services-list")

    with open("msk.json", 'w') as f:
        json.dump(json.loads(json_dict), f, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    get_data("https://kdl.ru/analizy-i-tseny/msk?results=1&filter[all_complexes]=1")