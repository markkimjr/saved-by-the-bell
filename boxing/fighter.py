import traceback
from typing import List
from dataclasses import dataclass

from http_request import get_request
from util import load_soup
from db import bulk_insert
from log import Logger

log = Logger.get_instance()

"""
Boxing organizations:
WBC
WBA
IBF
WBO
"""

BOXING_DIVISIONS = 17
URL = "https://www.boxingscene.com/rankings"
HEADERS = {
  'sec-ch-ua': '"Not A(Brand";v="99", "Brave";v="121", "Chromium";v="121"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"macOS"',
  'Upgrade-Insecure-Requests': '1',
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
  'Sec-GPC': '1',
  'host': 'www.boxingscene.com',
}

COLLECTION = "boxers"


@dataclass
class Boxer:
    name: str
    division: str
    is_champ: bool
    current_rank: int


def scrape_fighters() -> List[Boxer]:
    try:
        res = get_request(url=URL, headers=HEADERS)
        if res.status_code == 200:
            html_source = res.text
            fighters = parse_fighters(html_source=html_source)
            bulk_insert(collection=COLLECTION, data=fighters)
            return fighters
    except Exception as e:
        traceback.print_exc()
        log.error(f"ERROR OCCURRED WHILE SCRAPING FIGHTERS")


# WBC only for now TODO: Add WBA, IBF, WBO
def parse_fighters(html_source: str) -> List[Boxer]:
    pasred_fighters = []
    soup = load_soup(html_source=html_source)
    rankings_section = soup.find("section", {"class": "rankings"})
    for i in range(BOXING_DIVISIONS):
        div_id = f"ranking-cat-{i}"
        main_section = rankings_section.find("div", {"id": div_id})
        division = main_section.find("h3", {"class": "ranking-category-title"}).contents[0].strip()
        log.info(f"Scraping fighters for division: {division} - {i+1}/{BOXING_DIVISIONS}")
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
                            log.info(f"Scraped fighter: {name} - {division} CHAMPION")
                            pasred_fighters.append(boxer)
                            continue

                    name = td.text.strip()
                    # skip ranks that aren't rated yet
                    if "NOT RATED" in name:
                        continue
                    current_rank = x
                    boxer = Boxer(name=name, division=division, is_champ=False, current_rank=current_rank)
                    pasred_fighters.append(boxer)
                    log.info(f"Scraped fighter: {name} - {division} - rank: {current_rank}")

    return pasred_fighters


if __name__ == "__main__":
    scrape_fighters()
