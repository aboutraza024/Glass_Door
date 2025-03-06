
# code with threading
import csv
import time
import random
import threading
from urllib.parse import urljoin
from botasaurus.request import request, Request
from botasaurus.soupify import soupify

NUM_THREADS = 10
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
}
salaries_links = []
lock = threading.Lock()


@request
def scrape_heading_task(request: Request, thread_id):
    global salaries_links
    i = 1

    while True:
        sleep_duration = random.uniform(1, 2)
        response = request.get(
            "https://www.glassdoor.co.uk/Reviews/index.htm?filterType=RATING_OVERALL&page=100&overall_rating_low=4",
            headers=headers,
            )
        print(f"[Thread-{thread_id}] Page {i} - Status: {response.status_code}")

        soup = soupify(response)
        time.sleep(sleep_duration)

        try:
            salary = soup.find_all("a", datatype="Salaries")
            with lock:
                for s in salary:
                    link = s.get("href")
                    salaries_links.append(link)

            print(f"[Thread-{thread_id}] PAGE {i} , links: {len(salaries_links)}")

        except Exception as e:
            print(f"[Thread-{thread_id}] EXCEPTION:", e)

        # try:
        #     next_button = soup.find("button", {"aria-label": "Next"})
        #     if not next_button:
        #         print(f"[Thread-{thread_id}] NEXT BUTTON NOT FOUND. Stopping thread.")
        #         break
        # except Exception as e:
        #     print(f"[Thread-{thread_id}] Exception:", e)
        #     print("[Thread-{thread_id}] BREAKING....")
        #     break

        i += 1

    print(f"[Thread-{thread_id}] TOTAL LINKS SCRAPED: {len(salaries_links)}")


def write_in_csv():
    with open("links2.csv", mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Salary_URL"])
        with lock:
            for item in salaries_links:
                writer.writerow([item])

    print("CSV file saved successfully.")



threads = []
for thread_id in range(NUM_THREADS):
    thread = threading.Thread(target=scrape_heading_task, args=(Request(), thread_id))
    threads.append(thread)
    thread.start()


for thread in threads:
    thread.join()


write_in_csv()

print("All threads have finished execution.")
