import traceback
import bs4
from typing import List

from http_request import get_request
from log import Logger

log = Logger.get_instance()

BOXING_DIVISIONS = 17
"""
Boxing organizations:
WBC
WBA
IBF
WBO
"""

url = "https://www.boxingscene.com/rankings"
headers = {
  'sec-ch-ua': '"Not A(Brand";v="99", "Brave";v="121", "Chromium";v="121"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"macOS"',
  'Upgrade-Insecure-Requests': '1',
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
  'Sec-GPC': '1',
  'host': 'www.boxingscene.com',
  # 'Cookie': 'XSRF-TOKEN=eyJpdiI6Ilk1ZDFWN1VmV2g4VW5HVE52NjJtN0E9PSIsInZhbHVlIjoiOHJwLzFUcDgrZlBEc3NiYTB5YjV4c0JOYkxFVXhUVDhmR1NkTHA4ZFp4blpEQy92bTF4UHlRMys2MWdySXlkNjdCMTZocE1rUS9jMXFQM2xEeUxDZVBNUnZhRmVmbnVkR3EwQlFWWTV4SkZ3b2tabU1BeUVYRnB4UDNmUDBpZkwiLCJtYWMiOiI0YmUzYWQ0MDFjYzM2NDM2NmI5MjE1ODkwZDZhMTdhNjZlMWU5M2ExOGU0YTI3OWI3YzA3OTk0NzZiNmM0Y2FhIiwidGFnIjoiIn0%3D; boxingscene_session=eyJpdiI6IlVuUmE4ako1UW53Z2ZrUXprMXlhWEE9PSIsInZhbHVlIjoicnZmc0pVVUVIYUZGWjI0M29sUUdkZXR2aTljSmxUV2ppaW8rMkZ4L2Fxeis1TmhvaHdkQ1ZnN1h0NjN3ZlpMazB5UnRVYlk4SlAzSVFkU0J3d3pybklxZUZwU2lheHpPYWhLOVNPbWdGYkJiUjMyY1FvenZ6aDJPQi9IWCtzUmoiLCJtYWMiOiJiNWYxOTA3Nzk5YWNjNDRmM2Y3NTkzMzU5NzNiYTM1Yjk4NjdhZWRjZTEzZTBjZDk3NDhhYmVlNTQ3OWZjY2JmIiwidGFnIjoiIn0%3D'
}


class Boxer(object):
    def __init__(self, name, division, current_rank, is_champ):
        self.name = name
        self.division = division
        self.current_rank = current_rank
        self.is_champ = is_champ

    def __str__(self):
        return f"Name: {self.name}, Division: {self.division}, Rank: {self.current_rank}, Champ: {self.is_champ}"


def crawl_boxing_fighters() -> List[Boxer]:
    try:
        res = get_request(url=url, headers=headers)
        if res.status_code == 200:
            html_source = res.text
            fighters = parse_boxing_res(html_source=html_source)

            return fighters
    except Exception as e:
        log.error(f"ERROR OCCURRED WHILE CRAWLING BOXERS")
        traceback.print_exc()


# WBC only for now TODO: Add other organizations (WBA, IBF, WBO)
def parse_boxing_res(html_source: str) -> List[Boxer]:
    all_fighters = []
    soup = load_soup(html_source=html_source)
    rankings_section = soup.find("section", {"class": "rankings"})
    for i in range(BOXING_DIVISIONS):
        div_id = f"ranking-cat-{i}"
        main_section = rankings_section.find("div", {"id": div_id})
        division = main_section.find("h3", {"class": "ranking-category-title"}).text.strip()
        main_container = main_section.find("div", {"class": "ranking-table-container"})
        flex_columns = main_container.find_all("table", {"class": "d-block flex-grow-1"})
        for j, column in enumerate(flex_columns):
            # DO WBC ONLY FOR NOW (idx = 0)
            if j == 0:
                table = column.find("tbody")
                rows = table.find_all("td")
                for x, td in enumerate(rows):
                    # td class = "first" tag is champion row
                    if td.has_attr("class") and "first" in td["class"]:
                        name = td.find("div").text.strip()
                        if name != "VACANT":
                            boxer = Boxer(name=name, division=division, is_champ=True, current_rank=0)
                            all_fighters.append(boxer)
                            continue

                    name = td.text.strip()
                    current_rank = x
                    boxer = Boxer(name=name, division=division, is_champ=False, current_rank=current_rank)
                    all_fighters.append(boxer)

    return all_fighters


def load_soup(html_source: str) -> bs4.BeautifulSoup:
    return bs4.BeautifulSoup(html_source, 'lxml')


if __name__ == "__main__":
    crawl_boxing_fighters()
