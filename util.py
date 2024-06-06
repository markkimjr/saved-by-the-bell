import bs4


def load_soup(html_source: str) -> bs4.BeautifulSoup:
    return bs4.BeautifulSoup(html_source, 'lxml')
