import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 🔑 LinkedIn Credentials
LINKEDIN_EMAIL = "ethan.chkrn@gmail.com"
LINKEDIN_PASSWORD = "Koalam2369"

# 🔗 LinkedIn Login & Search URL (Replace with your search query)
LINKEDIN_LOGIN_URL = "https://www.linkedin.com/login"
SEARCH_URL = "https://www.linkedin.com/search/results/people/?currentCompany=%5B%2215823%22%5D&origin=FACETED_SEARCH&sid=saI&titleFreeText=Talent%20OR%20Recruiter%20OR%20Recruitment%20OR%20Quant%20OR%20Acquisition"

# 📂 Output CSV file
CSV_FILE = "linkedin_profiles.csv"

# 🚀 Set up WebDriver
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")  
    options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid bot detection
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# 🔐 Log into LinkedIn
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
    print("✅ Logged into LinkedIn.")

# 🔍 Scrape LinkedIn Search Results
def scrape_search_results(driver, search_url, max_pages=5):
    driver.get(search_url)
    time.sleep(5)

    all_profiles = []

    for page in range(max_pages):
        print(f"📄 Scraping page {page + 1}...")

        # Scroll to load profiles (fixes lazy loading)
        driver.execute_script("window.scrollBy(0, 2000);")
        time.sleep(5)

        # Find all profile links
        profile_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/in/')]")
        print(f"🔗 Found {len(profile_links)} profile links.")

        for link in profile_links:
            try:
                profile_url = link.get_attribute("href")

                # Extract name from aria-hidden span inside the link
                name_element = link.find_element(By.XPATH, ".//span[@aria-hidden='true']")
                full_name = name_element.text.strip()

                # Split first & last name
                name_parts = full_name.split()
                first_name = name_parts[0]
                last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

                print(f"✅ Found: {first_name} {last_name} - {profile_url}")
                all_profiles.append([first_name, last_name, profile_url])

            except Exception as e:
                print(f"⚠️ Skipping a profile due to missing data: {e}")

        # Click "Next" button if it exists
        try:
            next_button = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Next')]")
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(5)  # Wait for next page to load
        except Exception:
            print("🚫 No more pages or 'Next' button not found.")
            break

    return all_profiles

# 📝 Save results to CSV
def save_to_csv(profiles):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["first_name", "last_name", "linkedin_url"])
        writer.writerows(profiles)
    print(f"📂 Saved {len(profiles)} profiles to {CSV_FILE}")

# 🚀 Run the script
driver = setup_driver()
linkedin_login(driver)
profiles = scrape_search_results(driver, SEARCH_URL, max_pages=5)
save_to_csv(profiles)
driver.quit()
print("✅ Done! CSV file ready.")