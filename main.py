# code without threading
import csv
from logging import exception
from urllib.parse import urljoin
from botasaurus.browser import browser, Driver
from botasaurus.soupify import soupify
from botasaurus.request import request, Request
import time
import random
import threading

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"}
salaries_links = []


@request
def scrape_heading_task(request: Request, data):
    main_url = "https://www.glassdoor.co.uk"
    i = 1
    while i <= 25:
        i=i+1
        sleep_duration = random.uniform(1, 2)
        response = request.get(
            f"https://www.glassdoor.co.uk/Reviews/index.htm?filterType=RATING_OVERALL&sgoc=1023&page={i}&overall_rating_low=4",
            headers=headers)
        print(response.status_code)
        soup = soupify(response)
        time.sleep(sleep_duration)
        try:
            salary = soup.find_all('a', datatype="Salaries")
            for s in salary:
                link = s.get("href")
                salaries_links.append(link)
            # print(f" PAGE {i} ,links {salaries_links}")

        except Exception as e:
            print("EXCEPTION :", e)
        print("\n\nTOTAL NUMBER OF LINKS:\n\n\n", len(salaries_links))
        print(salaries_links)
        # try:
        #     next = soup.find('button', {'aria-label': 'Next'})
        #     print("Next link ", next)
        #     if next:
        #         pass
        #     else:
        #         print("NEXT NOT FOUNDING")
        #         break
        # except Exception as e:
        #     print("exception ",e)
        #     print("BREAKING ....")
        #     break

        print(i)


    write_in_csv(salaries_links)
    # print("ALL LINKS ",salaries_links)


def write_in_csv(salaries_links):
    Heading = ["Salary_URL"]
    with open("links2.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(Heading)
        for item in salaries_links:
            writer.writerow([item])


scrape_heading_task()




