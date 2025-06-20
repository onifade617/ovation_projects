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

    