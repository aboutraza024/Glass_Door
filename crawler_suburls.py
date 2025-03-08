
from botasaurus.browser import browser, Driver
from botasaurus.soupify import soupify
from botasaurus.browser import Wait
from datetime import datetime
import time
import csv
import threading
import logging

log_filename = f"logs/crawler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_filename), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

write_lock = threading.Lock()
concurrency = 10
input_file = "output/company_urls.csv"
output_file = "output/company_suburls.csv"
base_url = "https://www.glassdoor.co.uk"
companies_jobs_suburls = []
crawler_urls = []


def read_url_from_csv():
    with open(input_file, mode="r", newline="", encoding='utf-8') as file:
        reader = csv.reader(file)
        crawler_urls = [row[0] for row in reader if row]
        return crawler_urls[1:]


# Initialize CSV file with header
with open(output_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Salary_URL"])


def write_to_csv(link):
    with write_lock:
        with open(output_file, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([link])


url = "https://www.glassdoor.co.uk/Salary/DONE-by-NONE-Salaries-E619738.htm"


@browser(parallel=concurrency, max_retry=20, output=None, close_on_crash=True, raise_exception=True,
         create_error_logs=True)
def scrape_heading_task(driver: Driver, link):
    page_number = 1
    try:
        driver.google_get(link)
        while True:
            time.sleep(2)
            page_numbers = driver.select_all('p.pagination_PageNumberText__zy_hr')
            total_pages = page_numbers[-1].text
            # print(total_pages)
            if page_number > int(total_pages):
                break
            sub_links = driver.select_all('a.salarylist_job-title-link__MXnPX')
            time.sleep(1)
            for sub_link in sub_links:
                link = sub_link.get_attribute('href')
                if link:
                    with write_lock:
                        full_url = f"{base_url}{link}"
                        print(full_url)
                        companies_jobs_suburls.append(full_url)
                        write_to_csv(full_url)
            element = driver.select("button[data-test='next-page']")
            if element:
                element.scroll_into_view()
                time.sleep(1)
                element.click()
                time.sleep(15)
            else:
                print("Element not found.")
            page_number = page_number + 1
            logger.info(f"Scraped {len(companies_jobs_suburls)} job sub-links from {page_number} pages.")

    except Exception as e:
        logger.error(f"Page {page_number} error: {str(e)}")
    return companies_jobs_suburls


if __name__ == "__main__":
    urls = read_url_from_csv()
    logger.info(f"Start crawling sub links ")
    result = scrape_heading_task(urls)
    logger.info(f"Crawling complete. Total links collected: {len(result)} ")
