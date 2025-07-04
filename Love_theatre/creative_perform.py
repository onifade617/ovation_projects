from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from time import sleep
from urllib.parse import urljoin
import re
import pandas as pd
from urllib.parse import urlparse
import os
from datetime import date
import csv


today = date.today().isoformat()

all_shows = []
#==== open london direct  to get the links of productions by month via selenium ====

def love_theatre():

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/123.0.0.0 Safari/537.36")
    
    # Initialize driver once
    driver = webdriver.Chrome(options=options)
    try:
        url = "https://www.lovetheatre.com/whats-on/"
        driver.get(url)
        sleep(5)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        tabs = soup.find("main")\
            .find("section", class_="mb-2 mb-xl-3 py-2")\
            .find("div", class_="container mt-1 mt-md-2")\
            .find("div", class_="post-listing all-show-list with-filters d-flex flex-column")\
            .find_all("div", class_="row")
        
        for show_row in tabs:
            link_title = show_row.find("div", class_ ="col-lg-12")
                # Get all following siblings after col-lg-12
            if link_title:
                next_divs = link_title.find_next_siblings("div")
                
                for div in next_divs:
                    folio_card = div.find("div", class_="folio-card")
                    if folio_card:
                        top_div = folio_card.find("div", class_="top")
                        if top_div:
                            h3 = top_div.find("h3")
                            if h3:
                                link_tag = h3.find("a", href=True)
                                if link_tag:
                                    title = link_tag.get_text().strip()
                                    link = link_tag["href"]
                                    venue_tag = top_div.find("p")
                                    venue = venue_tag.get_text().strip() if venue_tag else "N/A"

                                    print(f"Title: {title}")
                                    print(f"Link: {link}")
                                    print(f"Venue: {venue}")

                                    # Save to list
                                    all_shows.append({
                                        "Title": title,
                                        "Link": link,
                                        "Venue": venue
                                    })

               
        # Write to CSV
        with open("love_theatre_shows.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["Title", "Link", "Venue"])
                writer.writeheader()
                writer.writerows(all_shows)

        print("CSV file 'theatre_shows.csv' has been created.")   
        
    finally:
        driver.quit()  # Ensure browser closes even if there's an error



def date_cast():

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/123.0.0.0 Safari/537.36")
    
    # Initialize driver once
    driver = webdriver.Chrome(options=options)

    df = pd.read_csv(r"love_theatre_shows.csv")

    performance_dates = []
    cast_creatives = []

    for url in df["Link"]:

        
        
        
        try:
            
            driver.get(url)
            sleep(5)

            soup = BeautifulSoup(driver.page_source, "html.parser")

            info1 = soup.find("main")\
                .find("section", class_="mb-2 mb-xl-3 no-border")\
                .find("section", class_="py-2")\
                .find("div", class_="container")\
                .find("div", class_="row")\
                .find("div", class_="col-lg-8")\
                .find("div")\
                .find_all("h3")
            
            print(info1[0].prettify())
                
            
            cast_info = "N/A"
            perf_date = "N/A"
                
                
            
            # Loop through all <p> tags
            for h3 in info1:
                if "ticket information" in h3.get_text(strip=True).lower():
                    next_element = h3.find_next_sibling()
                    if next_element:
                        perform_date = next_element.get_text(strip=True)
                        # Remove everything before the first number
                        cleaned_text = re.sub(r"^[^\d]*", "", perform_date)
                        print("Next sibling content:", perform_date)
                        perf_date = cleaned_text
                        
                   


                if "cast" in h3.get_text(strip=True).lower():
                    next_element = h3.find_next_sibling()
                    if next_element:
                        cast_info = next_element.get_text(strip=True)
                        print("Next sibling content:", cast_info)
                        
                        
            performance_dates.append(perf_date)
            cast_creatives.append(cast_info)      
            
        except Exception as e:
            print(f"Error processing {url}: {e}")
            performance_dates.append("Error")
            cast_creatives.append("Error")
        
    df["Performance Date"] = performance_dates
    df["Cast & Creatives"] = cast_creatives
     
    df.to_csv("love_theatre_shows.csv", index=False)
    driver.quit()  # Ensure browser closes even if there's an error












if __name__ == "__main__":
    #love_theatre()
    date_cast()
