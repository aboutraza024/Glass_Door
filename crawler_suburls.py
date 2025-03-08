
from botasaurus.browser import browser, Driver
from botasaurus.soupify import soupify
from botasaurus.browser import Wait
import time
import csv
from urllib.parse import urljoin

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


def write_to_csv(link):
    with open(output_file, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([link])


@browser(parallel=10)  # Open 10 browser instances
def scrape_heading_task(driver: Driver, link):
    pages = 1
    try:
        driver.google_get(link)
        while True:
            time.sleep(2)
            page_numbers = driver.select_all('p.pagination_PageNumberText__zy_hr')
            total_pages = page_numbers[-1].text
            if pages > int(total_pages):
                break
            sub_links = driver.select_all('a.salarylist_job-title-link__MXnPX')
            for sub_link in sub_links:
                link = sub_link.get_attribute('href')
                if link:
                    full_url = urljoin(base_url, link)
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
            pages = pages + 1
    except Exception as e:
        print(f"EXCEPTION {str(e)}")


if __name__ == "__main__":
    urls = read_url_from_csv()
    print(f"Starting scraping with 10 browser instances for {len(urls)} URLs.")
    scrape_heading_task(["https://www.glassdoor.co.uk/Salary/Johnson-and-Johnson-Salaries-E364.htm"])  # Pass all URLs to scrape concurrently
    print("Scraping complete.")