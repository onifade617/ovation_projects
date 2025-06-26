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

            list_of_productions_urls.append({"Month": {i["Month"]},
                                             "Production":full_url,
                                             "Year": year})
        result.append( list_of_productions_urls) 
        driver.quit()  # Ensure browser closes even if there's an error


#==== open each production  and get the details via selenium ====

def production_details():
    for i in result:
        list_of_productions_details = []
        # Set default values first
        list_of_productions_details["Title"] = "N/A"
        list_of_productions_details["Director"] = "N/A"
        list_of_productions_details["Playwright"] = "N/A"
        list_of_productions_details["Lyricist/Composer"] = "N/A"
        

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

        # === Open the target webpage ===
        driver.get(i["Production"])
        sleep(10)  # Allow time for JavaScript to load the content
        
        

        soup = BeautifulSoup(driver.page_source, "html.parser")

        tabs_prod = soup.find("main")\
                .find_all("div")
        detail_flex = tabs_prod[0].find("div", class_="container event-detail__container px-0 md:pb-xl md:px-xxl")\
                .find_all("div", class_="layout flex content-start flex-col gap-md md:grid md:gap-xl")
        detail_container =  detail_flex[0].find_all("div", class_="event-detail__left")
        
        detail_event = detail_container[1].find("div", class_="event-detail__description")\
                .find("div", id="tabs")
        
        detail_tab = detail_event.find("div", class_="tabs__content")\
                    .find("div", class_="tabs__frame tabs__frame--active")\
                    .find("div", class_="collapsible")\
                    .find("div", class_="collapsible__content")\
                    .find("div", class_="collapsible__content-wrapper")\
                    .find("div", class_="markdown-holder tab-show text-lg leading-normal md:pb-5 text-gray-700")\
                    .find_all("ul")
        
        #Production Title
        detail_title = detail_container[1].find("div", class_="event-detail__description")\
                    .find("div", class_="event-info px-lg sm:px-xxl md:px-0 pt-3 md:pt-2xl")\
                    .find("h1", class_="text-gray-700 text-2xl sm:text-4xl font-semibold leading-8 mb-1 md:mb-2")
        
        list_of_productions_details["Title"]= next(detail_title.stripped_strings)           


        # Director
        for div in detail_tab:
            lis = div.find_all("li")
            for li in lis:
                strong = li.find("strong")
                if strong and strong.get_text(strip=True) == "Director":
                    full_text = li.get_text(separator=" ", strip=True)
                    director_name = full_text.replace("Director", "", 1).strip()
                    list_of_productions_details["Director"] = director_name
                    break  # Stop after first match
            if list_of_productions_details["Playwright"] != "N/A":
                break

        # Playwright (Book / Book by / Written by)
        for div in detail_tab:
            lis = div.find_all("li")
            for li in lis:
                strong = li.find("strong")
                if strong:
                    label = strong.get_text(strip=True)
                    if label in ["Book", "Book by", "Written by"]:
                        full_text = li.get_text(separator=" ", strip=True)
                        playwright_name = full_text.replace(label, "", 1).strip()
                        list_of_productions_details["Playwright"] = playwright_name
                        break  # Stop after first match
            if list_of_productions_details["Playwright"] != "N/A":
                break

        # Lyrics (Lyrics / Music )
        for div in detail_tab:
            lis = div.find_all("li")
            for li in lis:
                strong = li.find("strong")
                if strong:
                    label = strong.get_text(strip=True)
                    if label in ["Lyrics", "Music"]:
                        full_text = li.get_text(separator=" ", strip=True)
                        lyricist_name = full_text.replace(label, "", 1).strip()
                        list_of_productions_details["Lyricist/Composer"] = lyricist_name
                        break  # Stop after first match
            if list_of_productions_details["Lyricist/Composer"] != "N/A":
                break

        result.append(list_of_productions_details)

        driver.quit()  # Ensure browser closes even if there's an error

if __name__ == "__main__":

    london_direct()
    production_link()