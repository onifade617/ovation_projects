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
                


def details():


    for file_name in os.listdir("theatres"):
        results_current = []
        
        
        if file_name.endswith(".csv"):
            file_path = os.path.join("theatres", file_name)
            df = pd.read_csv(file_path)
            

        for x in df["web_Link"]:

    

            # Initialize driver once
            driver = webdriver.Chrome()
                
            

                    
            for attempt in range(3):  # Maximum of 3 attempts
                    
                try:
                        # === Open the target webpage ===
                        
                    driver.get(x)
                    sleep(5)  # Allow time for JavaScript to load the content
                    break  # Break out of loop if successful
                except Exception as e:
                    print(f"[Attempt {attempt+1}] Error loading {x}: {e}")
                    if attempt == 1:  # On second failure
                        print(f"Skipping {x} after two failed attempts.")
                        continue  # Move to the next show

                
                    
                    # === Parse the individual show page ===
            show_soup = BeautifulSoup(driver.page_source, "html.parser")
            base_bar1 = show_soup.find("body", class_="winOS")
                        #print(show_soup.prettify())  # (Optional) print full HTML structure

                        
                
                            # === Drill down to show detail section ===
            base_bar = base_bar1.find("div", class_=re.compile("^production-page"))\
                    .find("div", class_=re.compile("^xt-c-box"))\
                    .find("div", class_="row xt-fixed-sidebar-row")
                    
                        
                            
                    



                                  
                    
                            # === Navigate to production details container ===
            creative_team = base_bar.find("div", class_=re.compile("col l8 m12 def-text s12 xt-l-col-right"))\
                    .find("div", id=re.compile("People"))\
                    .find("div", class_=re.compile("row"))\
                    .find_all("div", class_= re.compile("col s12"))
                    
                    
                    # === Extract production staff info ===
            production_details = creative_team[2].find("div", class_="row active")


                    # === Extract director info ===
            production_div = production_details.find_all("div", class_= "col s12")
            #print(len(production_div))
            director_name = None

            for div in production_div:
                if "Directed by" in div.get_text(strip=True):
                    director_text = div.get_text(strip=True)
                    match = re.search(r"Directed\s*by\s*([^;]+)", director_text)
                    director_name = match.group(1).strip() if match else None
                    break  # stop at the first match

                    
                    

            print(director_name)

                    # === Extract Composer info ===
            production_div = production_details.find_all("div", class_= "col s12")

            composer_name = None

            for div in production_div:
                if "Lyrics by" in div.get_text(strip=True):
                    lyrics_text = div.get_text(strip=True)
                    match = re.search(r"Lyrics\s*by\s*([^;]+)", lyrics_text)
                    composer_name = match.group(1).strip() if match else None
                    break  # stop at the first match
                elif "Music by" in div.get_text(strip=True):
                    lyrics_text = div.get_text(strip=True)
                    match = re.search(r"Music\s*by\s*([^;]+)", lyrics_text)
                    composer_name = match.group(1).strip() if match else None
                    break  # stop at the first match
                elif "Music orchestrated by" in div.get_text(strip=True):
                    lyrics_text = div.get_text(strip=True)
                    match = re.search(r"Music\s*orchestrated\s*by\s*([^;]+)", lyrics_text)
                    composer_name = match.group(1).strip() if match else None
                    break  # stop at the first match
            print(composer_name)

                    # === Extract Playwright info ===
            production_div = production_details.find_all("div", class_= "col s12")

            playwright_name = None

            for div in production_div:
                playwright_text = div.get_text(strip=True)

                if "Book by" in playwright_text:
                    match = re.search(r"Book\s*by\s*([^;]+)", playwright_text, re.IGNORECASE)
                    playwright_name = match.group(1).strip() if match else None
                    break  # stop at the first match
                elif "Written by" in playwright_text:
                    match = re.search(r"Written\s*by\s*([^;]+)", playwright_text, re.IGNORECASE)
                    playwright_name = match.group(1).strip() if match else None
                    break  # stop at the first match


            print(playwright_name)


                    # === Extract Rights info ===
            production_div = production_details.find_all("div", class_= "col s12")

            producer_name = None

            
            for div in production_div:
                if "Produced by" in div.get_text(strip=True):
                    lyrics_text = div.get_text(strip=True)
                    match = re.search(r"Produced\s*by\s*([^;]+)", lyrics_text)
                    producer_name = match.group(1).strip() if match else None
                    break  # stop at the first match
            print(producer_name)

            
          

            











                    # === scraped result info ===
            results_current.append({
                "Director" : director_name,
                "Composer/Lyricist": composer_name,
                "Playwright" : playwright_name,
                "Rights Holder": producer_name,
                
                        

                })

            
            #file.to_csv(f"rights_details/{theatre}_details.csv", index=False)
            
        df2 = pd.DataFrame(results_current)
        df= pd.concat([df, df2], axis=1)
        df.to_csv(f"theatres/{file_name}.csv", index=False)
        #print(f'End of {theatre} productions.')
        driver.quit()


def join_dataframes_on_column(df1, df2, join_column, how='inner', suffixes=('_left', '_right')):
    if join_column not in df1.columns or join_column not in df2.columns:
        raise ValueError(f"Column '{join_column}' must exist in both DataFrames.")
    
    joined_df = pd.merge(df1, df2, on=join_column, how=how, suffixes=suffixes)
    return joined_df



            


    








if __name__ == "__main__":
    #scrape_ibdb_shows()
    #current_theatre()
    details()
