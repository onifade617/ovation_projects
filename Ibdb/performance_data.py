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



scraped_results_current = []
scraped_results_upcoming = []
tab_urls = []
scraped_results_tours_c = []
scraped_results_tours_u = []

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
        url = "https://www.ibdb.com/shows"
        driver.get(url)
        sleep(5)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        tabs = soup.find("div", class_="page-wrapper xtrr")\
            .find("div", class_="shows-page")\
            .find("div", class_="row bgcolor-greyWhite2")\
            .find("div", class_="tabs-wrap")\
            .find("div", class_="xt-c-box")\
            .find("ul", class_="tabs")\
            .find_all("li", class_="tab")

        
        for tab in tabs:
            anchor = tab.find('a')
            href = anchor.get("href")
            if href:
                full_url = urljoin(url, href)
                tab_urls.append(full_url)

        print("Collected tab URLs:")
        for tab_url in tab_urls:
            print(tab_url)       

    finally:
        driver.quit()  # Ensure browser closes even if there's an error







def current_parse():
    
    # Initialize driver once
    driver = webdriver.Chrome()
        
    # === Open the target webpage ===
    driver.get(tab_urls[0])
    sleep(5)  # Allow time for JavaScript to load the content

    # === Get the HTML content and parse it with BeautifulSoup ===
    soup = BeautifulSoup(driver.page_source, "html.parser")
    base_url = "https://www.ibdb.com"

    # === Navigate to the container holding all show cards ===
    heading = soup.find("div", class_="page-wrapper xtrr")\
        .find("div", class_="shows-page")\
        .find("div", class_="row bgcolor-greyWhite2")\
        .find("div", class_="xt-c-box row")\
        .find("div", id="current")\
        .find("div", class_="row show-images xt-iblocks")\
        .find_all("div", class_="xt-iblock")
        # === Loop through each show card to extract individual show links ===
    for link in heading:
        link_indv = link.find("div", class_="xt-iblock-inner")\
            .find("a", href=True)
        img_indv = link_indv.find('span', class_='iblock-image')#image link text
        title = link_indv.find('i').get_text(strip=True)#Title text
        print(title)  

        style = img_indv.get('style', '')

                # Extract URL using regex
        match = re.search(r'url\((.*?)\)', style)
        if match:
            url = match.group(1)
            print(url)
        else:
            print("No URL found")

        if link_indv:
            full_url = base_url + link_indv['href']#production detals link
            print(full_url)
                
            
            for attempt in range(3):  # Maximum of 3 attempts
                driver.set_page_load_timeout(300) 
                try:
                    driver.get(full_url)
                    sleep(5)
                    break  # Break out of loop if successful
                except Exception as e:
                    print(f"[Attempt {attempt+1}] Error loading {full_url}: {e}")
                    if attempt == 1:  # On second failure
                        print(f"Skipping {full_url} after two failed attempts.")
                        continue  # Move to the next show

            
                
                # === Parse the individual show page ===
            show_soup = BeautifulSoup(driver.page_source, "html.parser")
            base_bar1 = show_soup.find("body", class_="winOS")
                #print(show_soup.prettify())  # (Optional) print full HTML structure

                
           
                    # === Drill down to show detail section ===
            base_bar = base_bar1.find("div", class_=re.compile("^production-page"))\
                    .find("div", class_=re.compile("^xt-c-box"))\
                    .find("div", class_="row xt-fixed-sidebar-row")

                    # === Navigate to image/title/type container ===
            img_type_title = base_bar.find("div", class_=re.compile("col l4 m10 push-m1 s12 s12 xt-l-col-left"))\
                    .find("div", class_=re.compile("production-info-panel"))\
                    .find("div", class_=re.compile("xt-fixed-sidebar"))\
                    .find("div", class_= re.compile("xt-fixed-block"),attrs={"data-id": "part-b"})
            
            #print(img_type_title.prettify())
       
            # === Extract Performance Info (e.g., Broadway, Off-Broadway) ===
            perform = img_type_title.find("div", class_="xt-info-block")\
                .find_all("div", class_="row wrapper")
            
            # === Extract opening date Info (e.g., Broadway, Off-Broadway) ===
            try:
                opening_instance = perform[0].find(class_='col s5 m3 l5 txt-paddings')\
                    .find("div", class_="xt-main-title").text
            except:
                opening_instance =  "N/A"  
            
            print(opening_instance)


            # === Extract closing date Info (e.g., Broadway, Off-Broadway) ===
            try:
                closing_instance = perform[0].find(class_='col s7 m6 l7 txt-paddings vertical-divider')\
                    .find("div", class_="xt-main-title").text
            except:
                closing_instance =  "N/A"  
            
            print(closing_instance)


             # === Extract Preview Info (e.g., Broadway, Off-Broadway) ===
            try:
                preview_instance = perform[1].find(class_='col s12 txt-paddings')\
                    .find("div", class_="xt-main-title").text
            except:
                preview_instance =  None  
            
            print(preview_instance)
          


            scraped_results_current.append({
                "Title": title,
                "Opening Date" : opening_instance,
                "Closing Date" : closing_instance,
                "Preview" : preview_instance,
                "Web page Link" : full_url,
                "Image Link" : url

            })



    driver.quit()


if __name__ == "__main__":
    scrape_ibdb_shows()
    current_parse()