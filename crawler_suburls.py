# # TODO: Crawl suburls of each company
import logging
from botasaurus.soupify import soupify
from botasaurus.request import request, Request
import threading
from datetime import datetime
import csv
from urllib.parse import urljoin

log_filename = f"logs/crawler_sublinks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_filename), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

write_lock = threading.Lock()
input_file = "output/company_urls.csv"
output_file = "output/company_suburls.csv"
# num_pages = 110
concurrency = 10
base_url = "https://www.glassdoor.co.uk"
crawler_urls_from_csv = []
companies_jobs_suburls = []
total_number_of_pages = None
company_urls = "output/company_urls1.csv"


def refactor_url(url, page_number):
    parts = url.split("-E")
    if len(parts) < 2:
        return "INVALID URL"
    base_url, employer_id = parts[0], parts[1].split(".htm")[0]
    new_url = f"{base_url}-EI_IE{employer_id}.0,16_IP{page_number}.htm"
    return new_url


def read_from_csv():
    with open(input_file, "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            crawler_urls_from_csv.extend(row)

    return crawler_urls_from_csv[1:]


def write_to_csv(link):
    with write_lock:
        with open(output_file, mode="a", newline="", encoding="utf-8") as file:
            file.write(link + "\n")


# Initialize CSV file with header
with open(output_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Salary_SUBURLS"])


@request(
    cache=False,
    parallel=concurrency,
    max_retry=20,
    close_on_crash=True,
    raise_exception=True,
    create_error_logs=False,
    output=None,
)
def crawl_companies_suburls(request: Request, main_url):
    page_number = 1
    while True:
        try:
            url = refactor_url(main_url, page_number)

            page_number = page_number + 1

            response = request.get(url)

            # print("FINAL URL:", response.url)

            if response.status_code == 200:
                soup = soupify(response)
                # find the total number of job pages from company url in crawler we get input from user the number of pages know extract from the company page
                page_numbers = soup.find_all('p', class_='pagination_PageNumberText__zy_hr')
                if page_numbers:
                    total_pages = len(page_numbers)
                    total_number_of_pages = page_numbers[total_pages - 1].text
                else:
                    page_number = 1

                if page_number > int(total_number_of_pages):
                    break

                subelements = soup.find_all('a', class_="salarylist_job-title-link__MXnPX")
                for subelement in subelements:
                    link = subelement.get("href")
                    if link:
                        full_url = f"{base_url}{link}"
                        companies_jobs_suburls.append(full_url)
                        write_to_csv(full_url)

                logger.info(f"Page {page_number - 1}: Found {len(companies_jobs_suburls)} links")
            else:
                print(response.status_code)

            # print(len(companies_jobs_suburls))

        except Exception as e:
            logger.error(f"Page {page_number - 1} error: {str(e)}")

    return companies_jobs_suburls


if __name__ == "__main__":
    main_urls = read_from_csv()
    # print(main_urls)
    logger.info(f"Starting crawling from page no 1")
    results = crawl_companies_suburls("https://www.glassdoor.co.uk/Salary/SelfEmployed-com-Salaries-E5529631.htm")
    logger.info(f"Crawling complete. Total sublinks collected: {len(results)}")

    # pages_data = [{"page_number": i} for i in range(1, num_pages + 1)]
    # logger.info(f"Starting crawl for {len(pages_data)} pages")
    # results = crawl_suburls_companies(pages_data)
    # logger.info(f"Crawling complete. Total sublinks collected: {len(results)}")
