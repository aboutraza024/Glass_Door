from botasaurus.browser import browser, Driver
from botasaurus.soupify import soupify
from botasaurus.browser import Wait
import time
import csv

output_file = "output/test.csv"
base_url = "https://www.glassdoor.co.uk"
companies_jobs_suburls = []


def write_to_csv(link):
    with open(output_file, mode="a", newline="", encoding="utf-8") as file:
        # file.write(link + "\n")
        writer = csv.writer(file)
        writer.writerow([link])


url = "https://www.glassdoor.co.uk/Salary/DONE-by-NONE-Salaries-E619738.htm"


@browser
def scrape_heading_task(driver: Driver, data):
    try:
        driver.google_get(url)
        response = driver.requests.get(url)
        time.sleep(2)
        if response.status_code == 200:
            soup = soupify(response)
            time.sleep(2)
            button = soup.find_all("button", class_="pagination_ListItemButton__se7rv pagination_Chevron__9Eauq")
            time.sleep(2)
            page_numbers = soup.find_all('p', class_='pagination_PageNumberText__zy_hr')
            print(page_numbers[-1].text)
            total_pages = page_numbers[-1].text
            subelements = soup.find_all('a', class_="salarylist_job-title-link__MXnPX")
            for subelement in subelements:
                link = subelement.get("href")
                if link:
                    full_url = f"{base_url}{link}"
                    companies_jobs_suburls.append(full_url)
                    write_to_csv(full_url)


        else:
            print(response.status_code)
        time.sleep(5)
        search_results = driver.wait_for_element("button.pagination_ListItemButton__se7rv.pagination_Chevron__9Eauq", wait=Wait.LONG)
        driver.click("button.pagination_ListItemButton__se7rv.pagination_Chevron__9Eauq")
        element = driver.select("button.pagination_ListItemButton__se7rv.pagination_Chevron__9Eauq")
        element.click()
        time.sleep(10)


    except Exception as e:
        print(f"EXCEPTION {str(e)}")


scrape_heading_task()