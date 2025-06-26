import os
import re
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime

# Get today's date for use in each data row
today = datetime.today().strftime('%Y-%m-%d')

def details(theatre_file):
    """Scrape data from a single CSV containing theatre show links."""

    # Check if the file exists
    if not theatre_file or not os.path.exists(theatre_file):
        print("The provided CSV file does not exist.")
        return

    file_name = os.path.basename(theatre_file)
    results_current = []
    visited_links = set()

    df = pd.read_csv(theatre_file)

    # Launch the browser
    driver = webdriver.Chrome()

    for idx, row in df.iterrows():
        x = row.get("web_Link", None)
        title = row.get("Title", None)

        data_row = {
            "web_Link": x,
            "Production Name": title,
            "Director": None,
            "Composer/Lyricist": None,
            "Playwright": None,
            "Rights Holder": None,
            "Preview Date": None,
            "Opening Date": None,
            "Closing Date": None,
            "Scraped Date": today,
            "Category": "Creative Team and Performance Data",
            
        }

        if pd.isna(x) or x in visited_links:
            print(f"Skipping: {x}")
            results_current.append(data_row)
            continue

        visited_links.add(x)

        for attempt in range(3):
            try:
                driver.get(x)
                sleep(3)
                break
            except Exception as e:
                print(f"[Attempt {attempt+1}] Error loading {x}: {e}")
                if attempt == 2:
                    print(f"Skipping {x} after three failed attempts.")
                    results_current.append(data_row)
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

            team_length = len(creative_team)
            print(f"creative_team length for {x}: {team_length}")

            production_details = creative_team[2].find("div", class_="row active", id = "ProductionStaff")
            production_div = production_details.find_all("div", class_="col s12")

            # Director
            for div in production_div:
                if "Directed by" in div.get_text(strip=True):
                    match = re.search(r"Directed\s*by\s*([^;]+)", div.get_text(strip=True))
                    if match:
                        data_row["Director"] = match.group(1).strip()
                    break

            # Composer/Lyricist
            for div in production_div:
                text = div.get_text(strip=True)
                for label in ["Lyrics by", "Music by", "Music orchestrated by"]:
                    if label in text:
                        match = re.search(fr"{label}\s*([^;]+)", text)
                        if match:
                            data_row["Composer/Lyricist"] = match.group(1).strip()
                            break
                if data_row["Composer/Lyricist"]:
                    break

            # Playwright
            for div in production_div:
                text = div.get_text(strip=True)
                if "Book by" in text:
                    match = re.search(r"Book\s*by\s*([^;]+)", text)
                elif "Written by" in text:
                    match = re.search(r"Written\s*by\s*([^;]+)", text)
                else:
                    continue
                if match:
                    data_row["Playwright"] = match.group(1).strip()
                    break

            # Rights Holder / Producer
            for div in production_div:
                if "Produced by" in div.get_text(strip=True):
                    match = re.search(r"Produced\s*by\s*([^;]+)", div.get_text(strip=True))
                    if match:
                        data_row["Rights Holder"] = match.group(1).strip()
                    break

            # Performance Info
            performance_info = base_bar.find("div", class_=re.compile("col l4 m10 push-m1 s12 s12 xt-l-col-left"))\
                .find("div", class_=re.compile("production-info-panel"))\
                .find("div", class_=re.compile("xt-fixed-sidebar"))\
                .find("div", class_=re.compile("xt-fixed-block"), attrs={"data-id": "part-b"})\
                .find("div", class_="xt-info-block")\
                .find_all("div", class_="row wrapper")

            # Opening Date
            try:
                data_row["Opening Date"] = performance_info[0].find(class_='col s5 m3 l5 txt-paddings')\
                    .find("div", class_="xt-main-title").text.strip()
            except:
                data_row["Opening Date"] = "N/A"

            # Closing Date
            try:
                data_row["Closing Date"] = performance_info[0].find(class_='col s7 m6 l7 txt-paddings vertical-divider')\
                    .find("div", class_="xt-main-title").text.strip() or "Present"
            except:
                data_row["Closing Date"] = "Present"

            # Preview Date
            try:
                data_row["Preview Date"] = base_bar.find("div", class_=re.compile("col l4 m10 push-m1 s12 s12 xt-l-col-left"))\
                    .find("div", class_=re.compile("production-info-panel"))\
                    .find("div", class_=re.compile("xt-fixed-sidebar"))\
                    .find("div", class_=re.compile("xt-fixed-block"), attrs={"data-id": "part-b"})\
                    .find("div", class_="xt-info-block")\
                    .find("div", class_="row wrapper hide-on-med-only")\
                    .find("div", class_='col s12 txt-paddings')\
                    .find("div", class_="xt-main-title").text.strip() or data_row["Opening Date"]
            except:
                data_row["Preview Date"] = data_row["Opening Date"]

        except Exception as e:
            print(f"Failed to parse {x}: {e}")

        results_current.append(data_row)

    driver.quit()

    # Save the results
    output_file = os.path.splitext(file_name)[0] + "_details.csv"
    pd.DataFrame(results_current).to_csv(output_file, index=False)
    print(f"Scraped data saved to: {output_file}")



if __name__ == "__main__":
    folder = "theatres"  # adjust this if files are in another folder
    # Get all CSV files in the folder
    all_files = [f for f in os.listdir(folder) if f.endswith(".csv")]
    for file_name in all_files:
        full_path = os.path.join(folder, file_name)

        if os.path.exists(full_path):
            print(f"Processing: {file_name}")
            details(full_path)  # your existing function
        else:
            print(f"File not found: {file_name}")
       