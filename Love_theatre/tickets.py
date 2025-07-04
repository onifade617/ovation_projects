from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from time import sleep
from urllib.parse import urljoin
import re
import pandas as pd
from urllib.parse import urlparse
import os
from datetime import date
import csv
import time


today = date.today().isoformat()
tickets_link = []

def calendar_page():
    df = pd.read_csv(r'love_theatre_shows.csv')

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/123.0.0.0 Safari/537.36")
    
    for url in df["Link"]:
        

        
        # Initialize driver once
        driver = webdriver.Chrome(options=options)
        try:
            
            driver.get(url)
            sleep(5)

            soup = BeautifulSoup(driver.page_source, "html.parser")

            selector = "body > main > section:nth-child(1) > section:nth-child(1) > div > div > div.col-lg-4 > div > div.modal.show-calendar-modal > div > div > div.modal-header > div > div:nth-child(2) > a"

            link = soup.select_one(selector)

            if link:
                print(link['href'])
                tickets_link.append(link['href'])
            
            else: 
                print("link not found")
                tickets_link.append("N/A")
        

        finally:
            driver.quit()

    my_tickets = pd.DataFrame(tickets_link)

    my_tickets.to_csv('my_tickets.csv', index = False)



def show_selector():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=options)
    driver.get("https://secure.lovetheatre.com/book/1H2AJ-the-producers/#")

    results = []

    try:
        wait = WebDriverWait(driver, 10)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        trs = soup.select(
            "#calendar-inner-container > calendar > section > div > div.section-container.month-by-month-calendar > div.calendar-days-container > table > tbody > tr"
        )

        for tr in trs:
            tds = tr.find_all("td")
            for td in tds:
                date_cell = td.find("date-cell")
                if not date_cell:
                    continue

                date_tag = date_cell.find("p", class_="date-number")
                if not date_tag:
                    continue

                date_text = date_tag.get_text(strip=True)
                h4_tags = date_cell.find_all("h4")

                if not h4_tags:
                    continue  # Skip if no performance times

                for h4 in h4_tags:
                    time_text = h4.get_text(strip=True)
                    results.append({"Date": date_text, "Time": time_text})

    except Exception as e:
        print(f"Error occurred: {e}")

    finally:
        driver.quit()

    df = pd.DataFrame(results)
    df.to_csv("calendar_times.csv", index=False)
    print(df)





def show_selector_with_bs_and_click_urls():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")

    url_link = pd.read_csv(r'love_theatre_shows.csv')
    
    driver = webdriver.Chrome(options=options)
    for i in url_link["Link"]:
        url = i if i.endswith("#") else i + "#"
        driver.get(url)


        results = []

        try:
            wait = WebDriverWait(driver, 15)
            time.sleep(5)

            # ✅ Step 1: Parse date/time with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, "html.parser")

            performance_map = []
            trs = soup.select(
                "#calendar-inner-container > calendar > section > div > div.section-container.month-by-month-calendar > div.calendar-days-container > table > tbody > tr"
            )

            for tr in trs:
                tds = tr.find_all("td")
                for td in tds:
                    date_cell = td.find("date-cell")
                    if not date_cell:
                        continue

                    date_tag = date_cell.find("p", class_="date-number")
                    if not date_tag:
                        continue

                    date_text = date_tag.get_text(strip=True)
                    h4_tags = date_cell.find_all("h4")

                    if not h4_tags:
                        continue  # Skip if no time

                    for h4 in h4_tags:
                        time_text = h4.get_text(strip=True)
                        performance_map.append((date_text, time_text))

            # ✅ Step 2: For each date/time, click matching li and get URL
            driver.get(url)
            time.sleep(5)

            perf_lis = driver.find_elements(By.CSS_SELECTOR, "li.perf[role='button']")

            for i, (date_val, time_val) in enumerate(performance_map):
                try:
                    perf_lis = driver.find_elements(By.CSS_SELECTOR, "li.perf[role='button']")
                    perf = perf_lis[i]

                    driver.execute_script("arguments[0].scrollIntoView(true);", perf)
                    time.sleep(0.5)
                    driver.execute_script("arguments[0].click();", perf)

                    wait.until(lambda d: "#perf=" in d.current_url)
                    current_url = driver.current_url

                    results.append({
                        "Date": date_val,
                        "Time": time_val,
                        "URL": current_url
                    })

                    # Reset for next click
                    driver.get(url)
                    time.sleep(4)

                except Exception as e:
                    print(f"Click/URL error at index {i}: {e}")
                    results.append({
                        "Date": date_val,
                        "Time": time_val,
                        "URL": "N/A"
                    })

        except Exception as e:
            print("Top-level error:", e)

        finally:
            driver.quit()

    df = pd.DataFrame(results)
    df.to_csv("calendar_times_from_bs_with_click_urls.csv", index=False)
    print(df)












#=== final code====

def show_selector_from_csv(csv_path="love_theatre_shows.csv"):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")

    df_links = pd.read_csv(csv_path)

    all_results = []

    for idx, row in df_links.iterrows():
        base_url = str(row[5]).strip()

        if pd.isna(row[5]) or base_url.upper() == "N/A" or base_url == "":
            continue  # Skip NaN, "N/A", empty or whitespace-only strings

        if not base_url.endswith("/#"):
            base_url += "#"

        


        print(f"\nProcessing: {base_url}")

        driver = webdriver.Chrome(options=options)
        driver.get(base_url)

        try:
            wait = WebDriverWait(driver, 15)
            time.sleep(5)

            # Step 1: Parse with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, "html.parser")

            performance_map = []
            trs = soup.select(
                "#calendar-inner-container > calendar > section > div > div.section-container.month-by-month-calendar > div.calendar-days-container > table > tbody > tr"
            )

            for tr in trs:
                tds = tr.find_all("td")
                for td in tds:
                    date_cell = td.find("date-cell")
                    if not date_cell:
                        continue

                    date_tag = date_cell.find("p", class_="date-number")
                    if not date_tag:
                        continue

                    date_text = date_tag.get_text(strip=True)
                    h4_tags = date_cell.find_all("h4")

                    if not h4_tags:
                        continue

                    for h4 in h4_tags:
                        time_text = h4.get_text(strip=True)
                        performance_map.append((date_text, time_text))

            # Step 2: Use Selenium to get updated URLs
            driver.get(base_url)
            time.sleep(5)

            perf_lis = driver.find_elements(By.CSS_SELECTOR, "li.perf[role='button']")

            for i, (date_val, time_val) in enumerate(performance_map):
                try:
                    perf_lis = driver.find_elements(By.CSS_SELECTOR, "li.perf[role='button']")
                    perf = perf_lis[i]

                    driver.execute_script("arguments[0].scrollIntoView(true);", perf)
                    time.sleep(0.5)
                    driver.execute_script("arguments[0].click();", perf)

                    wait.until(lambda d: "#perf=" in d.current_url)
                    current_url = driver.current_url

                    all_results.append({
                        "Show URL": base_url,
                        "Date": date_val,
                        "Time": time_val,
                        "Booking URL": current_url
                    })

                    driver.get(base_url)
                    time.sleep(4)

                except Exception as e:
                    print(f"Click error for {date_val} {time_val}: {e}")
                    all_results.append({
                        "Show URL": base_url,
                        "Date": date_val,
                        "Time": time_val,
                        "Booking URL": "N/A"
                    })

        except Exception as e:
            print(f"Page-level error: {e}")
        finally:
            driver.quit()

    final_df = pd.DataFrame(all_results)
    final_df.to_csv("all_calendar_results.csv", index=False)
    print(final_df)







if __name__ == "__main__":
    #calendar_page()
    #show_selector()
    #show_selector_with_bs_and_click_urls()
    show_selector_from_csv()
