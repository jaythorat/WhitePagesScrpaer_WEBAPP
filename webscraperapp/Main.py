# Importing all the necessary libraries
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service 
from selenium import webdriver
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from bs4 import BeautifulSoup
import os
import time
import pandas as pd
from webscraperapp.upload_todrive import upload_file

progress = 0
# Chromedriver initial setup
def chromedriver_setup():
    chromedriver_path = os.getcwd()+"/webscraperapp/chromedriver"
    service = Service(executable_path=chromedriver_path)
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
    option = webdriver.ChromeOptions()
    option.add_argument("--headless")
    option.add_argument(f'user-agent={user_agent}')
    option.add_argument("--no-sandbox")
    option.add_argument("--window-size=1920,1080")
    option.add_argument("--start-maximized")
    # # option.add_argument('--proxy-server=%s' % PROXY)
    option.add_experimental_option("excludeSwitches", ["enable-automation"])
    option.add_experimental_option('useAutomationExtension', False)
    option.add_argument("--disable-blink-features=AutomationControlled")
    option.add_experimental_option("detach", True)
    driver = webdriver.Chrome(service=service,options=option)
    return driver

# Function to scrape the url form the input files
def source_url(name,location):
    return f"https://www.whitepages.com/name/{name}/{location}"

# Function to scrape the profile urls available on the website
def scrape_profile_urls(url):
    # Chromedrive initialisation & opening the url
    driver = chromedriver_setup()
    driver.get(url)
    time.sleep(3)
    try:
        driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div/div[2]/div/input').click()
        driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div/div[2]/button').click()
    except:
        pass
    time.sleep(4)
    source = driver.page_source 
    # Scraping the profile urls
    soup = BeautifulSoup(source,'html.parser')
    profile_urls,allpagesurl=[],[]
    a = soup.find_all("a",{"class":"serp-card hide-scrollbar amp-event"})
    for i in a:
        url1 = "https://www.whitepages.com"+i['href']
        profile_urls.append(url1)
    pages = (soup.find_all("a",{"data-amp-label":"WPClickedPagination"}))
    for i in pages:
        url1 = "https://www.whitepages.com"+i['href']
        if url1 not in allpagesurl and "?page=1" not in url1:
            allpagesurl.append(url1)
    for j in allpagesurl:
        try:
            driver.get(j)
            time.sleep(4)
            source = driver.page_source
            soup=BeautifulSoup(source,'html.parser')
            a = soup.find_all("a",{"class":"serp-card hide-scrollbar amp-event"})
            for i in a:
                url1 = "https://www.whitepages.com"+i['href']
                profile_urls.append(url1)
        except: 
            pass
    driver.close()
    return profile_urls

# Function to scrape the contact details from the profile urls
def profile_info(url,file_name):
    # Chromedrive initialisation & Scraping profile information
    driver = chromedriver_setup()
    driver.get(url)
    driver.implicitly_wait(3)
    source = driver.page_source
    soup = BeautifulSoup(source,'html.parser')
    name = soup.find_all("h1",{"class":"headline"})[0].text
    links = soup.find_all("a")
    telephone = []
    for link in links:
        try:
            if link['href'].startswith('/phone/1'):
                    tele = link['href'].replace('/phone/','')
                    telephone.append(tele)
            if link.has_attr('href'):
                if link['href'].startswith('/address/'):
                    address = link.getText().strip().replace('\n','').replace(13*" ",'')
        except:
            pass
    driver.close()
    if len(telephone) == 0:
        telephone0 = "N/A"
        telephone1 = "N/A"
        # info_df = pd.DataFrame([[name,telephone0,telephone1,address]],columns=["Name","Telephone-1","Telephone-2","Address"])
        # info_df.to_csv(file_name, mode='a', index=False, header=False)
        print(f"No telephone number found for the profile {name}. NOT ADDED TO CSV")

    if len(telephone) == 1:
        telephone0 = telephone[0]
        telephone1 = "N/A"
        info_df = pd.DataFrame([[name,telephone0,telephone1,address]],columns=["Name","Telephone-1","Telephone-2","Address"])
        info_df.to_csv(file_name, mode='a', index=False, header=False)
    if len(telephone) == 2:
        telephone0 = telephone[0]
        telephone1 = telephone[1]
        info_df = pd.DataFrame([[name,telephone0,telephone1,address]],columns=["Name","Telephone-1","Telephone-2","Address"])
        info_df.to_csv(file_name, mode='a', index=False, header=False)
    # Writing the scraped data to the output file
    # info_df = pd.DataFrame([[name,telephone0,telephone1,address]],columns=["Name","Telephone-1","Telephone-2","Address"])
    return {"name":name,"telephone":telephone,"address":address}

# Function to create the output file
def createCSV():
    # Creating the output file wih with name as the current date
    now = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    column = ["Name","Telephone-1","Telephone-2","Address"]
    df = pd.DataFrame([['','','','']],columns=column)
    pd.set_option("max_colwidth", 350)
    output_file = f"outputfiles/Details_{now}.csv"
    df.to_csv(output_file,index=False)
    print(f"{output_file} created!!!!")
    return output_file

# Main function
def main(names,locations):
    total = len(names)*len(locations)*75
    current_val = 0
    st = time.time()
    try:
        os.mkdir('backup')
        os.mkdir('outputfiles')
    except:
        pass
    # Creating the output file
    filename = createCSV()
    locations = locations
    for location in locations:
        if len(location)<1:
            locations.remove(location)
    locations_backup = locations.copy()
    names = names
    for name in names:
        if len(name)<1:
            names.remove(name)
    names_backup = names.copy()
    all_details = []
    # Iterating through the input data to extract the data
    for location in locations:
        if len(location) > 0 :
            try:
                for name in names:
                    print(f"Scraping {name} from {location}")
                    # Passing name and location to the source url function and then passing the return value to the scrape_profile_urls function
                    profile_urls_for_source = scrape_profile_urls(source_url(name,location))
                    # List to store the profile urls which are not scraped 
                    failed_profile_urls = []
                    try:
                        # Using ThreadPoolExecutor to extract the data in parallel
                        # Make sure you set the max_workers according to processing power of your machine and Netwrork speed
                        with ThreadPoolExecutor(max_workers=8) as executor:
                            futures = {
                                executor.submit(profile_info, url,filename): url for url in profile_urls_for_source
                            }
                            # Extracting the data from the futures after it completes its execution
                            for future in as_completed(futures):    
                                url = futures[future]
                                print(url)
                                try:
                                    data = future.result()
                                    all_details.append(data)
                                except Exception as exc:
                                    failed_profile_urls.append(url)
                                    print('%r generated an exception: %s' % (url, exc))
                                current_val += 1
                                global progress
                                progress = current_val/total*100
                                print(f"current progress {progress}% , {current_val}/{total}")
                    except Exception as e:
                        print(e)
                        pass
                    # List to store the profile urls which are not scraped (second attempt)
                    failed_profile_urls_twice = []
                    try:
                        # trying failed urls again if any
                        # Make sure to  set the max_workers according to processing power of your machine and Netwrork speed
                        with ThreadPoolExecutor(max_workers=4) as executor:
                            futures = {
                                executor.submit(profile_info, url,filename): url for url in failed_profile_urls
                            }
                            for future in as_completed(futures):
                                url = futures[future]
                                print(url)
                                try:
                                    data = future.result()
                                    all_details.append(data)
                                    print(data)
                                except Exception as exc:
                                    failed_profile_urls_twice.append(url)
                                    print('%r generated an exception: %s' % (url, exc))
                                current_val += 1
                                progress = current_val/total*100
                                print(f"current progress {progress}% , {current_val}/{total}")
                    except Exception as exc:
                        print(exc)
                    # Maintaining the list of names as a backup in case of failure of code to resume where it left off
                    names_backup.remove(name)
                    if len(names_backup) == 0:
                        with open(f'{os.getcwd()}/backup/backupnames.txt', 'w') as bn:
                            bn.write("File is empty.")
                        break
                    else:
                        with open(f'{os.getcwd()}/backup/backupnames.txt', 'w') as bn:
                            for name_backup in names_backup:
                                bn.write(name_backup+'\n')
                    try:
                        # quitting the browser if there are no more names to be scraped to save resources
                        # os.system("pkill chrome") -- MAC/Linux
                        os.system("taskkill /im chrome.exe /f")  # -- Windows
                        pass
                    except :
                        pass
                names_backup=names.copy()
                try:
                    #quitting the browser if there are no more names to be scraped to save resources
                    # os.system("pkill chrome") -- MAC/Linux
                    os.system("taskkill /im chrome.exe /f") # -- Windows
                    pass
                except :
                    pass
                # Maintaining the list of locations as a backup in case of failure of code to resume where it left off
                locations_backup.remove(location)
                if len(locations_backup) == 0:
                    with open(f'{os.getcwd()}/backup/backuplocations.txt', 'w') as bl:
                        bl.write("File is empty.")
                    break
                else:
                    with open(f'{os.getcwd()}/backup/backuplocations.txt', 'w') as bl:
                        for location_backup in locations_backup:
                            bl.write(location_backup+'\n')
            except:
                pass
        else:
            return    
    # calling a function to upload a file to google drive
    #upload_file([os.path.join(os.getcwd(), f'{filename}')])
    print("File Uploaded to drive successfully")
    et = time.time()
    print(f"Time taken for execution : {et-st}")
    progress = 0
    return filename

# Calling the main function
if __name__=='__main__':
    st = time.time()
    names = ["jack"]
    locations = ["California"]
    main(names,locations)
    et = time.time()
    print(f"Time taken for execution : {et-st}")
