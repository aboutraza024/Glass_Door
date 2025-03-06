import csv
import os
from datetime import datetime
from botasaurus.soupify import soupify
from botasaurus.request import request, Request
import threading
import logging

os.makedirs("logs", exist_ok=True)
os.makedirs("output", exist_ok=True)

log_filename = f"logs/crawler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_filename), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)
write_lock = threading.Lock()
output_file = "output/company_urls.csv"
num_pages = 110


def write_to_csv(link):
    with write_lock:
        with open(output_file, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([link])


# Initialize CSV file with header
with open(output_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Salary_URL"])


@request(
    cache=False,
    parallel=10,
    max_retry=20,
    close_on_crash=True,
    raise_exception=True,
    create_error_logs=False,
    use_stealth=True,
)
def crawl_companies(request: Request, data):
    page_number = data["page_number"]
    company_links = []
    url = f"https://www.glassdoor.co.uk/Reviews/index.htm?filterType=RATING_OVERALL&sgoc=1023&page={page_number}&overall_rating_low=4"

    try:
        response = request.get(url)

        if response.status_code == 200:
            soup = soupify(response)
            salary_elements = soup.find_all("a", datatype="Salaries")

            for salary_element in salary_elements:
                link = salary_element.get("href")
                if link:
                    company_links.append(link)
                    write_to_csv(link)

            logger.info(f"Page {page_number}: Found {len(company_links)} links")

    except Exception as e:
        logger.error(f"Page {page_number} error: {str(e)}")

    return company_links


if __name__ == "__main__":
    pages_data = [{"page_number": i} for i in range(1, num_pages + 1)]
    logger.info(f"Starting crawl for {len(pages_data)} pages")
    results = crawl_companies(pages_data)
    logger.info(f"Crawling complete. Total links collected: {len(results)}")
