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




today = date.today().isoformat()




list_of_productions_urls = []
list_of_theatres_urls = []


def scrape_ibdb_shows():
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
        url = "https://www.ibdb.com/theatres"
        driver.get(url)
        sleep(5)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        tabs = soup.find("div", class_="page-wrapper xtrr")\
            .find("div", class_="venue-page")\
            .find("div", class_="xt-c-box")\
            .find("div", class_="row bgcolor-greyWhite2 boxed-urls centering-container")\
            .find_all("div", class_="col s12 m3")

        
        for tab in tabs:
            anchor = tab.find('a')

            if anchor:
                href = anchor.get("href")
                
                full_url = urljoin("https://www.ibdb.com/", href)

                theatre_name = anchor.get_text(strip = True)

                print(f'{theatre_name}: {full_url}')

                
                #append the name and links to the list
                list_of_theatres_urls.append({
                    "Theatre Name": theatre_name,
                    "Theatre Link": full_url,
                    }
                )
            

    finally:
        driver.quit()  # Ensure browser closes even if there's an error






def current_theatre():
    
  

    for i in list_of_theatres_urls:
        
        # Initialize driver once
        driver = webdriver.Chrome()
            
        # === Open the target webpage ===
        driver.get(i["Theatre Link"])
        sleep(10)  # Allow time for JavaScript to load the content

        # === Get the HTML content and parse it with BeautifulSoup ===
        soup = BeautifulSoup(driver.page_source, "html.parser")
        base_url = "https://www.ibdb.com"

        # === Navigate to the container holding all show cards ===
        heading0 = soup.find("div", class_="page-wrapper xtrr")\
            .find("div", class_="venue-page")\
            .find("div", class_="venue-productions-wrap")\
            .find("div", class_="venue-page-content")\
            .find("div", class_="xt-c-box")\
            .find("div", class_="row venue-productions-list")\
            .find_all("div")
        heading1 =  heading0[1].find("ul")
        heading =   heading1.find("div", class_="collapsible-body xt-collapsible-body")\
            .find("div", class_="sub-tab-data")\
            .find("div", class_="active")\
            .find_all("div", class_="row")
    
        
        
        # === Loop through each show card to extract individual show links and show title ===
        for link in heading:
            link_indv = link.find("div", class_="col s12 m8")
            
            link_indv = link_indv.find("a", href=True)
            

            if link_indv:
                full_url = base_url + link_indv['href']#production detals link
                prod_title = link_indv.text.strip()#production title
                print(full_url)
                print(prod_title)

                #append the links of the production to the list
                list_of_productions_urls.append({
                    "Title": prod_title,
                    "web_Link":full_url
                    })
           #== Check whether file exist in folder==
        if not os.path.exists(f"theatres/{i['Theatre Name']}.csv")  :

            file = pd.DataFrame(list_of_productions_urls)
            file.to_csv(f"theatres/{i['Theatre Name']}.csv", index=False)
        driver.quit()
                


def details(theatre_file):
    #theatre_file = get_unique_file_path("theatres", "theatres_details", extension=".csv")

    if not theatre_file:
        print("No unmatched file found.")
        return

    file_name = os.path.basename(theatre_file)  # get just the file name
    results_current = []
    visited_links = set()

    df = pd.read_csv(theatre_file)

    driver = webdriver.Chrome()

    for x in df["web_Link"]:
        if x in visited_links:
            print(f"Already visited: {x}, skipping.")
            continue

        visited_links.add(x)

        for attempt in range(3):
            try:
                driver.get(x)
                sleep(5)
                break
            except Exception as e:
                print(f"[Attempt {attempt+1}] Error loading {x}: {e}")
                if attempt == 1:
                    print(f"Skipping {x} after two failed attempts.")
                    continue

        try:
            show_soup = BeautifulSoup(driver.page_source, "html.parser")
            base_bar1 = show_soup.find("body", class_="winOS")

            base_bar = base_bar1.find("div", class_=re.compile("^production-page"))\
                .find("div", class_=re.compile("^xt-c-box"))\
                .find("div", class_="row xt-fixed-sidebar-row")

            creative_team = base_bar.find("div", class_=re.compile("col l8 m12 def-text s12 xt-l-col-right"))\
                .find("div", id=re.compile("People"))\
                .find("div", class_=re.compile("row"))\
                .find_all("div", class_=re.compile("col s12"))

            production_details = creative_team[2].find("div", class_="row active")
            production_div = production_details.find_all("div", class_="col s12")

            # === Director ===
            director_name = None
            for div in production_div:
                if "Directed by" in div.get_text(strip=True):
                    match = re.search(r"Directed\s*by\s*([^;]+)", div.get_text(strip=True))
                    director_name = match.group(1).strip() if match else None
                    break
            print(director_name)

            # === Composer / Lyricist ===
            composer_name = None
            for div in production_div:
                text = div.get_text(strip=True)
                for label in ["Lyrics by", "Music by", "Music orchestrated by"]:
                    if label in text:
                        match = re.search(fr"{label}\s*([^;]+)", text)
                        composer_name = match.group(1).strip() if match else None
                        break
                if composer_name:
                    break
            print(composer_name)

            # === Playwright ===
            playwright_name = None
            for div in production_div:
                text = div.get_text(strip=True)
                if "Book by" in text:
                    match = re.search(r"Book\s*by\s*([^;]+)", text)
                elif "Written by" in text:
                    match = re.search(r"Written\s*by\s*([^;]+)", text)
                else:
                    continue
                playwright_name = match.group(1).strip() if match else None
                break
            print(playwright_name)

            # === Producer ===
            producer_name = None
            for div in production_div:
                if "Produced by" in div.get_text(strip=True):
                    match = re.search(r"Produced\s*by\s*([^;]+)", div.get_text(strip=True))
                    producer_name = match.group(1).strip() if match else None
                    break
            print(producer_name)

            # === Performance Info ===
            performance_info = base_bar.find("div", class_=re.compile("col l4 m10 push-m1 s12 s12 xt-l-col-left"))\
                .find("div", class_=re.compile("production-info-panel"))\
                .find("div", class_=re.compile("xt-fixed-sidebar"))\
                .find("div", class_=re.compile("xt-fixed-block"), attrs={"data-id": "part-b"})\
                .find("div", class_="xt-info-block")\
                .find_all("div", class_="row wrapper")

            # === Opening Date ===
            try:
                opening_instance = performance_info[0].find(class_='col s5 m3 l5 txt-paddings')\
                    .find("div", class_="xt-main-title").text.strip()
                
            except:
                opening_instance = "N/A"
            print(opening_instance)

            # === Closing Date ===
            try:
                closing_instance = performance_info[0].find(class_='col s7 m6 l7 txt-paddings vertical-divider')\
                    .find("div", class_="xt-main-title").text.strip()
                if not closing_instance:
                    closing_instance = "Present"
            except:
                closing_instance = "Present"
            print(closing_instance)

            # === Preview Date ===
            try:
                preview_instance = base_bar.find("div", class_=re.compile("col l4 m10 push-m1 s12 s12 xt-l-col-left"))\
                .find("div", class_=re.compile("production-info-panel"))\
                .find("div", class_=re.compile("xt-fixed-sidebar"))\
                .find("div", class_=re.compile("xt-fixed-block"), attrs={"data-id": "part-b"})\
                .find("div", class_="xt-info-block")\
                .find("div", class_="row wrapper hide-on-med-only")\
                .find("div", class_='col s12 txt-paddings')\
                .find("div", class_="xt-main-title").text.strip()
                if not preview_instance:
                    preview_instance = opening_instance
            except:
                preview_instance = opening_instance
            print(preview_instance)

            # === Save scraped info ===
            results_current.append({
                "Director": director_name,
                "Composer/Lyricist": composer_name,
                "Playwright": playwright_name,
                "Rights Holder": producer_name,
                "Preview Date": preview_instance,
                "Opening Date": opening_instance,
                "Closing Date": closing_instance,
                "Scraped Date": today
            })

        except Exception as e:
            print(f"Failed to parse {x}: {e}")

    driver.quit()

    # Save result to CSV
    df2 = pd.DataFrame(results_current)
    df = pd.concat([df, df2], axis=1)
    df.to_csv(f"theatres_details/{file_name}", index=False)



def get_unique_file_path(folder1, folder2, extension=None):

    """
    Returns the full path of the first file in folder1 that does not exist in folder2.
    
    Parameters:
        folder1 (str): Path to the source folder.
        folder2 (str): Path to the comparison folder.
        extension (str, optional): If provided, filters by file extension (e.g., ".csv").

    Returns:
        str or None: Full path of the first unmatched file, or None if all exist in folder2.
    """
    # List files with optional extension filter
    files1 = [f for f in os.listdir(folder1) if not extension or f.endswith(extension)]
    files2 = set(os.listdir(folder2))

    # Find first file in folder1 not in folder2
    for file in files1:
        if file not in files2:
            return os.path.join(folder1, file)

    return None  # If all files exist in folder2





"""
    Loops through all files in folder_one and processes only those 
    not already present in folder_two.
"""



def process_all_unmatched_files(folder_one, folder_two):
    
    for file in os.listdir(folder_one):
        if file.endswith(".csv") and file not in os.listdir(folder_two):
            theatre_file_path = os.path.join(folder_one, file)
            print(f"Processing: {theatre_file_path}")
            details(theatre_file_path)
        else:
            print(f"Skipping: {file} (already processed or not a CSV)")
            


    








if __name__ == "__main__":
    #scrape_ibdb_shows()
    #current_theatre()
    #details()
    process_all_unmatched_files("theatres", "theatres_details")
