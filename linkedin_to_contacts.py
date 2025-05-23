import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
from dotenv import load_dotenv

load_dotenv()


LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")


LINKEDIN_LOGIN_URL = "https://www.linkedin.com/login"
SEARCH_URL = "https://www.linkedin.com/search/results/people/?currentCompany=%5B%226125149%22%5D&origin=FACETED_SEARCH&sid=SJE&titleFreeText=Talent%20OR%20Recruiter%20OR%20People%20OR%20Acquisition%20OR%20Quant"


CSV_FILE = "linkedin_profiles.csv"


def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")  
    options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid bot detection
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver


def linkedin_login(driver):
    driver.get(LINKEDIN_LOGIN_URL)
    time.sleep(3)

    # Enter email
    email_input = driver.find_element(By.ID, "username")
    email_input.send_keys(LINKEDIN_EMAIL)

    # Enter password
    password_input = driver.find_element(By.ID, "password")
    password_input.send_keys(LINKEDIN_PASSWORD)
    password_input.send_keys(Keys.RETURN)

    time.sleep(5)  # Wait for login to complete
    print("Logged into LinkedIn.")


def scrape_search_results(driver, search_url, max_pages=5):
    driver.get(search_url)
    time.sleep(5)

    all_profiles = []

    for page in range(max_pages):
        print(f"📄 Scraping page {page + 1}...")

        
        driver.execute_script("window.scrollBy(0, 2000);")
        time.sleep(5)

        
        profile_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/in/')]")
        print(f"Found {len(profile_links)} profile links.")

        for link in profile_links:
            try:
                profile_url = link.get_attribute("href")

                
                name_element = link.find_element(By.XPATH, ".//span[@aria-hidden='true']")
                full_name = name_element.text.strip()

                
                name_parts = full_name.split()
                first_name = name_parts[0]
                last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

                print(f"Found: {first_name} {last_name} - {profile_url}")
                all_profiles.append([first_name, last_name, profile_url])

            except Exception as e:
                print(f"Skipping a profile due to missing data: {e}")

        # Click "Next" button if it exists
        try:
            next_button = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Next')]")
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(5)  # Wait for next page to load
        except Exception:
            print("No more pages or 'Next' button not found.")
            break

    return all_profiles


def save_to_csv(profiles):
    existing_profiles = set()

    # Load existing data if file exists
    try:
        with open(CSV_FILE, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                if len(row) >= 3:
                    existing_profiles.add(row[2])  # Store LinkedIn URLs to avoid duplicates
    except FileNotFoundError:
        pass  # No existing file, continue

    # Filter out duplicates before writing new data
    unique_profiles = []
    for profile in profiles:
        _, _, profile_url = profile
        if profile_url not in existing_profiles:
            unique_profiles.append(profile)
            existing_profiles.add(profile_url)  # Add to set to prevent future duplicates

    
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["first_name", "last_name", "linkedin_url"])  # Write header
        writer.writerows(unique_profiles)  # Write unique contacts

    print(f"📂 Saved {len(unique_profiles)} new profiles to {CSV_FILE} (Total: {len(existing_profiles)})")


driver = setup_driver()
linkedin_login(driver)
profiles = scrape_search_results(driver, SEARCH_URL, max_pages=5)
save_to_csv(profiles)
driver.quit()
print("✅ Done! CSV file ready.")