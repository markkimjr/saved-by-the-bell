from log import Logger

log = Logger.get_instance()
# TODO implement daily scheduler for crawling and updating fighters, schedules


if __name__ == "__main__":
    log.info("STARTING BOXING SCRAPING")
    # scrape_fighters()
    # scrape_schedules()

    # send notification to users about upcoming fights (based on user preferences for fighters they are following)
    log.info("BOXING SCRAPING COMPLETED")