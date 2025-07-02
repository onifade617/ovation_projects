from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
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
import traceback


list_of_month_urls = []
result = []


#==== open london direct  to get the links of productions by month via selenium ====

def london_direct():

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
        url = "https://www.londontheatredirect.com"
        driver.get(url)
        sleep(5)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        tabs = soup.find_all("div")
        

        for conatiner in tabs:

            inner_div = conatiner.find("div", class_="affiliate-hidden container text-gray-700 mt-9 mb-3")
            

            if inner_div:
                
                links = inner_div.find("div", class_="flex justify-between overflow-auto pt-6 pb-6")\
                .find_all("a", class_="px-5 py-2 rounded-full font-semibold cursor-pointer text-gray-700")
        
                for tab in links:
                    
                    anchor = tab.get("href")
                    

                    if anchor:
                       
                        
                        full_url = urljoin("https://www.londontheatredirect.com/", anchor)

                        month_name = anchor.lstrip("/")

                        print(f'{month_name}: {full_url}')

                        
                        #append the name and links to the list
                        list_of_month_urls.append({
                            "Month": month_name,
                            "Month Link": full_url,
                            }
                        )
        
        
    finally:
        driver.quit()  # Ensure browser closes even if there's an error




#==== open each month link and get the links of production via selenium ====

def production_link():
    for i in list_of_month_urls:
        list_of_productions_urls = []
       
        
        # Initialize driver once
        driver = webdriver.Chrome()

        # === Open the target webpage ===
        driver.get(i["Month Link"])
        sleep(10)  # Allow time to load the content

        # === Accept cookies if prompted ===
        try:
            # Example: button contains "Accept" (adjust selector if needed)
            accept_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Accept")]'))
            )
            accept_button.click()
            print("Cookies accepted!")
            sleep(2)  # wait for DOM to update after accepting
        except Exception as e:
            print("Cookie banner not found or already accepted:", e)

        
        sleep(10)  # Allow time for JavaScript to load the content

        soup = BeautifulSoup(driver.page_source, "html.parser")

        tabs_prod = soup.find("main")\
                .find("div")\
                .find("div", class_="filter-wrapper")\
                .find("div", class_="relative")\
                .find_all("a", class_="event-tile text-left")
                
              
        

        for tab in tabs_prod:
            anchor = tab.get("href")
            print(anchor)
           
                
            full_url = urljoin("https://www.londontheatredirect.com/", anchor)

             

        
            # Extract the full text first
            year_text = soup.find("main")\
                .find("div")\
                .find("div", class_="filter-wrapper")\
                .find("section", class_="affiliate-hidden")\
                .find("div", class_="container py-2xl")\
                .find("h2").text

            # Use regex to extract only digits
            year = re.findall(r'\d+', year_text)

            year = year[0]

            print(f'{i["Month"]} : {full_url} : {year}')

            list_of_productions_urls.append({"Month": i["Month"].capitalize(),
                                             "Production":full_url,
                                             "Year": year})
            file = pd.DataFrame(list_of_productions_urls)
            file.to_csv(f"month/{i['Month']}{year}.csv", index=False) 
        driver.quit()  # Ensure browser closes even if there's an error


#==== open each production  and get the details via selenium ====


def production_details(csv_file, output_file="production_details_output.csv"):
    df = pd.read_csv(csv_file)

    # Determine URL column
    if 'Production' in df.columns:
        url_column = 'Production'
    elif 'web_link' in df.columns:
        url_column = 'web_link'
    else:
        raise ValueError("CSV file must contain a 'Production' or 'web_link' column.")

    all_productions_details = []

    for index, row in df.iterrows():
        production_url = row[url_column]

        production_data = {
            "Title": "N/A",
            "Production URL": production_url,
            "Venue": "N/A",
            "Opening Date": "N/A",
            "Closing Date": "N/A",
            "Cast": "N/A",
            "Creatives": "N/A",
           
            }

        driver = webdriver.Chrome()
        try:
            driver.get(production_url)
            sleep(10)
            soup = BeautifulSoup(driver.page_source, "html.parser")

            tabs_prod = soup.find("main").find_all("div")
            detail_flex = tabs_prod[0].find("div", class_="container event-detail__container px-0 md:pb-xl md:px-xxl")\
                .find("div", class_="layout flex content-start flex-col gap-md md:grid md:gap-xl")
            detail_container = detail_flex.find("div", class_="event-detail__left")

            # Title
            try:
                detail_title = detail_container.find("div", class_="event-detail__description")\
                    .find("div", class_="event-info px-lg sm:px-xxl md:px-0 pt-3 md:pt-2xl")\
                    .find("h1", class_="text-gray-700 text-2xl sm:text-4xl font-semibold leading-8 mb-1 md:mb-2")
                production_data["Title"] = next(detail_title.stripped_strings)
            except Exception:
                pass

            # Venue
            try:
                detail_venue_0 = detail_container.find("div", class_="event-detail__description")\
                    .find("div", class_="md:mb-5 p-lg sm:py-xl sm:px-xxl md:px-0")\
                    .find_all("div", class_="flex gap-md items-center")
                detail_venue_1 = detail_venue_0[2].find("div", class_="flex flex-col mb-auto")\
                    .find("a", class_="cursor-pointer underline flex gap-1 pt-1 items-center")\
                    .find("p", class_="badge__title")
                production_data["Venue"] = detail_venue_1.text.strip()
            except Exception:
                pass

            detail_venue_0 = detail_container.find("div", class_="event-detail__description")\
                    .find("div", class_="md:mb-5 p-lg sm:py-xl sm:px-xxl md:px-0")\
                    .find("div", class_="grid sm:grid-cols-2 gap-md")\
                    .find_all("div", class_="flex gap-md items-center")
            # Step 2: Try <span> in [1]; if empty or missing, fallback to [0]
            date_range = "N/A"
            span_candidates = [1, 0]  # Try index 1 first, then 0

            for idx in span_candidates:
                try:
                    span = detail_venue_0[idx].find("div", class_="flex flex-col mb-auto")\
                        .find("p", class_="badge__description")\
                        .find("span")
                    
                    # If span exists and has meaningful text
                    if span and span.get_text(strip=True):
                        print(span.prettify())
                        date_range = span.get_text(strip=True)
                        break  # Stop after first valid non-empty <span>
                except Exception:
                    continue
            if " - " in date_range:
                opening, closing = date_range.split(" - ")
                production_data["Opening Date"] = opening.strip()
                production_data["Closing Date"] = closing.strip()
            else:
                production_data["Opening Date"] = date_range
                production_data["Closing Date"] = "N/A"


            
            # Creative Team
            try:
                detail_creative = detail_container.find("div", class_="event-detail__description")\
                    .find("div", class_="tabs mt-5")\
                    .find("div", class_="tabs__content")\
                    .find("div", class_="tabs__frame tabs__frame--active")\
                    .find("div", class_="collapsible")\
                    .find("div", class_="collapsible__content")\
                    .find("div", class_="collapsible__content-wrapper")\
                    .find("div", class_="markdown-holder tab-show text-lg leading-normal md:pb-5 text-gray-700")
                
                production_data["Cast"] = extract_roles(detail_creative, "cast")
                production_data["Creatives"] = extract_roles(detail_creative, "creatives")
                   

                '''
                if detail_creative:
                    last_ul = list(detail_creative[-1].find_all("li"))

                    # Define keyword groups
                    director_keywords = [
                        "director -",
                        "developed and directed by -",
                        "directed by -",
                        "original story and director -",
                        "director and choreographer -",
                        "original director -",
                        "director & choreographer -",
                    ]
                    playwright_keywords = [
                        "author -",
                        "book -",
                        "written by -",
                        "book by -",
                        "composer, book, co-orchestrator -",
                        "original story -",
                        "writer -"
                    ]
                    lyrics_keywords = [
                        "lyrics -",
                        "music -",
                        "music / lyrics -",
                        "music supervisor and composer -",
                        "musical supervisor -",
                        "music and lyrics -",
                        "music &amp; lyrics -",
                        "music supervisor, orchestrator, arrangements, &amp; additional lyrics -",
                        "Lyrics by -",
                        "music & lyrics -",
                    ]

                    rights_keywords = [
                        "Producer -",
                        "produced by -",
                        "created by -",
                        "creator -",
                        "musical supervisor - -",
                        "music and lyrics -",
                        "music &amp; lyrics -",
                        "music supervisor, orchestrator, arrangements, &amp; additional lyrics -"
                    ]

                    def extract_by_keywords(keywords):
                        for li in last_ul:
                            text = li.get_text(separator=" ", strip=True).lower()
                            for key in keywords:
                                if text.startswith(key):
                                    return text.split("-", 1)[1].strip()
                        return "N/A"
                    
                    production_data["Director"] = extract_by_keywords(director_keywords)
                    production_data["Playwright"] = extract_by_keywords(playwright_keywords)
                    production_data["Lyricist/Composer"] = extract_by_keywords(lyrics_keywords)
                    '''
            except Exception:
                pass
            
        except Exception as e:
            print(f"Error processing {production_url}: {e}")
        finally:
            driver.quit()

        all_productions_details.append(production_data)
    pd.DataFrame(all_productions_details).to_csv(output_file, index=False)


def extract_roles(creative_section, label):
    """
    Searches for a <h4> or <h3> containing the label text,
    extracts 'role - real name' from the next <ul>, and returns a string.
    Returns 'N/A' if nothing is found.
    """
    label = label.lower()
    header_tag = None
    role_list = []  # Always reset before use

    # Check <h4> first
    for tag in creative_section.find_all("h4"):
        if label in tag.get_text(strip=True).lower():
            header_tag = tag
            break

    # If not found in h4, check <h3>
    if not header_tag:
        for tag in creative_section.find_all("h3"):
            if label in tag.get_text(strip=True).lower():
                header_tag = tag
                break

    # Extract data from <ul> if found
    if header_tag:
        ul = header_tag.find_next_sibling("ul")
        if ul:
            for li in ul.find_all("li"):
                strong = li.find("strong")
                if strong:
                    role_name = strong.get_text(strip=True)
                    real_name = strong.next_sibling.strip(" -\n") if strong.next_sibling else ""
                    role_list.append(f"{role_name} - {real_name}")

    result = "\n".join(role_list) if role_list else "N/A"

    # Clean up variables
    del header_tag, ul, role_list
    return result



    







if __name__ == "__main__":

    #london_direct()
    #production_link()
    production_details("combined_data.csv")
    