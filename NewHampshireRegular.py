import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import re
import string
import urllib.request
import ssl
import requests
from urllib.request import OpenerDirector
import os
import math

options = Options()
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://business.nh.gov/NSOR/search.aspx")


def download_image(image_url, image_name):
    try:
        # Create the folder if it doesn't exist
        folder_name = "NewHampshireRegular"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        # Set the path for the image file
        image_path = os.path.join(folder_name, image_name)

        # Skip downloading if the image file already exists
        if os.path.exists(image_path):
            print(f"Skipped image: {image_name}. Already exists.")
            return

        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=context))
        urllib.request.install_opener(opener)

        with urllib.request.urlopen(image_url) as response, open(image_path, 'wb') as out_file:
            out_file.write(response.read())

        print(f"Downloaded image: {image_name}")
    except Exception as e:
        print(f"Failed to download image: {image_name}. Error: {str(e)}")


with open("NewHampshireRegular.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Full Name", "Aliases", "Tier Level", "Offense", "Image Link"])

    for letter in string.ascii_lowercase:
        # Write in the lastname box

        time.sleep(2)
        driver.find_element("xpath", '//*[@id="ctl00_cphMain_txtLname"]').send_keys(letter)
        # Click on the search button
        time.sleep(1)
        driver.find_element("xpath", '//*[@id="ctl00_cphMain_btnSubmit"]').click()
        # next button
        base_xpath = '//*[@id="ctl00_cphMain_gvwOffender"]/tbody/tr[12]/td/table/tbody/tr/td'

        # Get the total number of elements to determine the loop range
        total_elements = len(driver.find_elements("xpath", base_xpath))
        print(total_elements)
        prematured_end = "Deactivated"

        # for j in range(2, 10):
        for index in range(2, total_elements + 1):

            for i in range(2, 12):
                print("The values are j = ", index, "and i = ", i)
                try:
                    if i == 10 or i == 11:
                        driver.find_element("xpath", '//*[@id="ctl00_cphMain_gvwOffender_ctl' + str(i) + '_hypName"]').click()
                    else:
                        # Access the profile
                        driver.find_element("xpath", '//*[@id="ctl00_cphMain_gvwOffender_ctl0' + str(i) + '_hypName"]').click()
                except Exception as e:
                    # Code to handle the exception
                    print(f" Prematured end of profile list : {str(e)}")
                    prematured_end = "Activated"
                    # Code to consider the i loop finished
                    break  # Exit the i loop if an error occurs

                # Name
                full_name = driver.find_element("xpath", '//*[@id="ctl00_cphMain_lblNameYes"]').text.strip()
                print("Full Name: " + full_name)
                # Tier Level
                tier_level = "Not Available"
                # Aliases
                time.sleep(1)
                try:
                    Aliases = driver.find_element("xpath",
                                                  '//*[@id="ctl00_cphMain_lblAliasYes"]')
                    aliases = Aliases.text.strip()
                    if aliases.startswith("Alias(es):"):
                        aliases = aliases[len("Alias(es):"):]
                except:
                    aliases = "No Alias"
                print(aliases)
                # Convictions
                time.sleep(1)
                conviction_elements = driver.find_elements("xpath", '//*[@id="ctl00_cphMain_tblCourt"]/tbody/tr[2]/td')
                for convictions in conviction_elements:
                    convictions = convictions.text.strip()
                    if convictions.startswith("Qualifying Offense(s):"):
                        convictions = convictions[len("Qualifying Offense(s):"):]
                    print(convictions)

                # Image
                try:
                    image_element = driver.find_element("xpath", '//*[@id="ctl00_cphMain_imgOffender"]')
                    image_link = image_element.get_attribute("src")
                    print("Image Link: " + image_link)
                except:
                    image_link = "None/Any"
                # Write the extracted data to the CSV file
                writer.writerow([full_name, aliases, tier_level, convictions, image_link])
                # Download the image
                image_name = full_name + ".jpg"  # Customize the image name as per your requirements
                download_image(image_link, image_name)
                print("Data written for", full_name)

                time.sleep(2)
                driver.execute_script("window.history.go(-1)")
                # Refresh the page because every time I go back there is "Confirm Form Resubmission"
                time.sleep(2)
                driver.refresh()

                if i == 11:
                    time.sleep(5)
                    xpath = base_xpath + '[' + str(index) + ']/a'
                    print(xpath)
                    try:
                        element = driver.find_element("xpath", xpath)
                        element.click()
                        print("Next Page Accessed")

                    except NoSuchElementException:
                        print(" 'next' element is not found. Trying to proceed to the next letter")  # Exit the loop if the next element is not found
            if index == total_elements or prematured_end == "Activated":
                driver.execute_script("window.history.go(-1)")
                driver.find_element("xpath", '//*[@id="ctl00_cphMain_txtLname"]').clear()
                prematured_end = "Deactivated"
                index == total_elements
        # //*[@id="ctl00_cphMain_gvwOffender"]/tbody/tr[12]/td/table/tbody/tr/td[2]/a

        # //*[@id="ctl00_cphMain_gvwOffender"]/tbody/tr[12]/td/table/tbody/tr/td[2]/a

        # //*[@id="ctl00_cphMain_gvwOffender_ctl02_hypName"]
        # //*[@id="ctl00_cphMain_gvwOffender_ctl02_hypName"]
