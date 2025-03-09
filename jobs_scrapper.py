import time
import csv
from botasaurus.browser import browser, Driver

input_file = "output/company_suburls2.csv"  # Change it to the correct suburls
output_file = "output/companies_data.csv"


def read_url_from_csv():
    with open(input_file, mode="r", newline="", encoding='utf-8') as file:
        reader = csv.reader(file)
        crawler_urls = [row[0] for row in reader if row]
        return crawler_urls[1:]

header=["COUNTRY","COMPANY","JOB TITLE","YEARS OF EXPERIENCE","BASE PAY","ADDITIONAL PAY AVERAGE","ADDITIONAL PAY RANGE","CONFIDENCE","SALARIES SUBMITTED","UPDATED"]
companies_data=[]
def write_to_csv(data):
    with open(output_file, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(data)

with open(output_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(header)

url = "https://www.glassdoor.co.uk/Salary/Freelance-Freelancer-Salaries-E1130527_D_KO10,20.htm"

# List of experience levels to click
experience_levels = [
    "0-1 Year", "1-3 Years", "4-6 Years",
    "7-9 Years", "10-14 Years", "15+ Years"
]


def wait_for_element(driver, selector, timeout=5):
    """Wait for an element to appear on the page."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        element = driver.select(selector)
        if element:
            return element  # Return the found element
        time.sleep(0.5)  # Wait for 0.5s before checking again
    return None  # Return None if the timeout is reached


def open_experience_dropdown(driver):
    """ Opens the experience filter dropdown. """
    try:
        experience_elements = driver.select_all("div[class*='filter-chip_FilterChip']")
        if len(experience_elements) > 1:
            time.sleep(1.3)
            experience_elements[1].click()
            time.sleep(2)
    except Exception as e:
        print(f"Error opening dropdown: {e}")

base_pay_text=[]
def write_to_csv(data):
    """Appends a row to the CSV file."""
    with open(output_file, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(data)

def scrape_required_info(driver, experience):
    """Scrapes required information and writes to CSV."""
    try:
        companies_data = []  # New list for each row

        country = "UK"  # Set country manually (Glassdoor UK site)
        companies_data.append(country)

        company_name = driver.select("div.employer-header_nameAndRating___HtOS > p")
        company_name = company_name.text if company_name else "N/A"
        companies_data.append(company_name)

        job_text = driver.select('h1.undefined.hero_dInline__6YBn7 > span').text
        if job_text:
            split_title = job_text.split()
            job_title = split_title[len(split_title) // 2]
            companies_data.append(job_title)
        else:
            job_title="N/A"
            companies_data.append(job_title)

        companies_data.append(experience)  # Add years of experience

        base_pay_element = driver.select_all('div.hero_PayRange__nKzVj')
        base_pay_text = base_pay_element[0].text if base_pay_element else "N/A"
        companies_data.append(base_pay_text)

        average_pay = driver.select('div.hero_AdditionalPayAverage__yS6Cc > span')
        # print(average_pay.text)
        additional_pay_average = average_pay.text if average_pay else "N/A"
        companies_data.append(additional_pay_average)

        range_salary = driver.select("div.hero_AdditionalPayRange__I5R6_ > span")
        # print(range_salary.text)
        additional_pay_range = range_salary.text if range_salary else "N/A"
        companies_data.append(additional_pay_range)

        confidence = driver.select("span.confidence_ConfidenceLabel__M4wsy")
        confidence = confidence.text if confidence else "N/A"
        companies_data.append(confidence)

        submitted_salaries = driver.select('span[data-test="salaries-submitted"] > span')
        submitted_salaries = submitted_salaries.text if submitted_salaries else "N/A"
        companies_data.append(submitted_salaries)

        last_update = driver.select('span[data-test="last-updated"] > span')
        last_update = last_update.text if last_update else "N/A"
        companies_data.append(last_update)

        # Write data to CSV
        write_to_csv(companies_data)
        print("Saved:", companies_data)

    except Exception as e:
        print("Error while scraping data:", e)

@browser()
def scrape_companies_data(driver: Driver, link):
    try:
        driver.google_get(link)
        time.sleep(3)  # Wait for page to load

        for exp in experience_levels:
            open_experience_dropdown(driver)  # Open dropdown
            time.sleep(1)  # Small delay

            # Wait for button to appear
            button_selector = f"button[aria-label='{exp}']"
            experience_button = wait_for_element(driver, button_selector, timeout=5)

            if experience_button:
                experience_button.click()
                scrape_required_info(driver,exp)
                print(f"Clicked: {exp}")
            else:
                print(f"Button for {exp} not found!")

            time.sleep(5)  # Wait for data to load

    except Exception as e:
        print(f"Error: {e}")


scrape_companies_data(url)


