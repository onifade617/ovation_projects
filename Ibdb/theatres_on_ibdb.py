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



tab_urls = [] #list of theatres and their links

def ibdb_theatres():

     # Initialize driver once
    driver = webdriver.Chrome()

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
                tab_urls.append({
                    "Theatre Name": theatre_name,
                    "Theatre Link": full_url,
                    }
                )
        newdf = pd.DataFrame(tab_urls)
        newdf.to_csv("ibdb_theatres", index=False)       

    finally:
        driver.quit()


if __name__ == "__main__":
    ibdb_theatres()

    






"""

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
        .find("div", class_="venue-page")\
        .find("div", class_="venue-productions-wrap")\
        .find("div", class_="venue-page-content")\
        .find("div", class_="xt-c-box")\
        .find("div", class_="row venue-productions-list")\
        .find("div")\
        .find("ul", class_ = "collapsible xt-collapsible")\
        .find("li", class_="active")\
        .find("div", class_="collapsible-body xt-collapsible-body")\
        .find("div", class_="sub-tab-data")\
        .find("div", class_="active")\
        .find_all("div", class_="row")
    
        
        
        # === Loop through each show card to extract individual show links ===
    for link in heading:
        link_indv = link.find("div", class_="col s12 m8")\
            .find("a", href=True)
        

        if link_indv:
            full_url = base_url + link_indv['href']#production detals link
            print(full_url)



"""