import traceback
import datetime
from typing import List, Optional
from dataclasses import dataclass

from http_request import get_request
from util import load_soup
from db import bulk_insert, bulk_select
from log import Logger

log = Logger.get_instance()

URL = "https://www.boxingscene.com/schedule"
HEADERS = {
  'sec-ch-ua': '"Brave";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"macOS"',
  'Upgrade-Insecure-Requests': '1',
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
  'Sec-GPC': '1',
  'Sec-Fetch-Site': 'none',
  'Sec-Fetch-Mode': 'navigate',
  'Sec-Fetch-User': '?1',
  'Sec-Fetch-Dest': 'document',
  'host': 'www.boxingscene.com'
}
COLLECTION = "schedule"


@dataclass
class Schedule:
    fighters: List[str]
    belt: Optional[str]
    date: str
    location: Optional[str]
    network: Optional[str]


def scrape_schedules() -> List[Schedule]:
    try:
        fighters = bulk_select(collection="boxers")
        res = get_request(url=URL, headers=HEADERS)
        log.info(f"BOXING SCHEDULE RES: {res.status_code}")
        if res.status_code == 200:
            html_source = res.text
            scheduled_fights = parse_schedules(html_source=html_source, fighters=fighters)
            bulk_insert(collection="schedule", data=scheduled_fights)
            return scheduled_fights
    except Exception as e:
        traceback.print_exc()
        log.error(f"ERROR OCCURRED WHILE SCRAPING FIGHTERS")


def parse_schedules(html_source: str, fighters: List[dict]) -> List[Schedule]:
    parsed_schedules = []
    soup = load_soup(html_source=html_source)
    main_section = soup.find("section", {"class": "schedule"})
    fight_cards = main_section.find_all("div", class_="schedule-fight mb-4 mb-lg-0 py-lg-3 d-lg-flex align-items-center")
    for idx, fight_card in enumerate(fight_cards):
        try:
            log.info(f"PARSING FIGHT CARD: {idx+1}/{len(fight_cards)}")
            fighters = []

            # fighters
            title_div = fight_card.find("div", class_="fight-title mb-2")
            title_str = title_div.text.strip()
            fighter_names = title_str.split("vs.")
            for fighter in fighter_names:
                fighters.append(fighter.strip())

            # date
            fight_date_div = fight_card.find("div", class_="fight-date")
            date_str = fight_date_div.text.strip()
            # assume all fights are for year 2024 (date_str format - Jun 6)
            date_str = f"{date_str} 2024"
            date_obj = datetime.datetime.strptime(date_str, "%b %d %Y")
            date = date_obj.strftime("%Y-%m-%d")

            # location, network
            fight_details_div = fight_card.find("div", class_="schedule-details d-flex flex-column flex-lg-row")
            detail_divs = fight_details_div.find_all("div")
            location = None
            network = None
            for detail_div in detail_divs:
                i_tag = detail_div.find("i")
                if i_tag.get("data-feather") and "map-pin" in i_tag.get("data-feather", ""):
                    location = detail_div.text.strip()
                    continue
                if i_tag.get("data-feather") and "tv" in i_tag.get("data-feather", ""):
                    network = detail_div.text.strip()
                    continue

            # belt
            belt = None
            belt_div = fight_card.find("div", class_="fight-notes mb-2")
            if belt_div:
                belt = belt_div.text.strip()

            parsed_schedule = Schedule(fighters=fighters, belt=belt, date=date, location=location, network=network)
            parsed_schedules.append(parsed_schedule)
        except Exception as e:
            traceback.print_exc()
            log.error(f"ERROR OCCURRED WHILE PARSING FIGHT CARD: {idx+1}/{len(fight_cards)}")
            continue
    return parsed_schedules


if __name__ == "__main__":
    scrape_schedules()
