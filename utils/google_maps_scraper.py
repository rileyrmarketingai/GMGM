import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, NoSuchWindowException
from time import time, sleep
from random import uniform

class GoogleMaps:
    _maps_url = "https://www.google.com/maps"
    _finger_print_defender_ext = "./extensions/finger_print_defender.crx"

    def __init__(self, unavailable_text="Not Available", headless=True, wait_time=15, scroll_minutes=1, verbose=False):
        self._unavailable_text = unavailable_text
        self._headless = headless
        self._wait_time = wait_time
        self._scroll_minutes = scroll_minutes
        self._verbose = verbose

    def create_chrome_driver(self):
        options = uc.ChromeOptions()
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--headless=new')
        options.add_argument('--window-size=1920,1080')
        try:
            options.add_extension(self._finger_print_defender_ext)
        except Exception:
            pass  # Extension is optional for cloud
        driver = uc.Chrome(options=options, headless=True, use_subprocess=False)
        self._wait = WebDriverWait(driver, self._wait_time, ignored_exceptions=(NoSuchElementException, StaleElementReferenceException))
        return driver

    def handle_consent_screen(self, driver):
        try:
            WebDriverWait(driver, 15).until(
                lambda d: (
                    d.find_elements(By.XPATH, "//button[contains(., 'Accept all')]")
                    or d.find_elements(By.XPATH, "//button[contains(., 'Accept')]")
                    or d.find_elements(By.XPATH, "//button[contains(., 'I agree')]")
                    or d.find_elements(By.XPATH, "//button[contains(., 'Reject all')]")
                    or d.find_elements(By.XPATH, "//button[contains(., 'Reject')]")
                    or d.find_elements(By.XPATH, "//button[@id='L2AGLb']")
                )
            )
            possible_xpaths = [
                "//button[contains(., 'Accept all')]",
                "//button[contains(., 'Accept')]",
                "//button[contains(., 'I agree')]",
                "//button[contains(., 'Reject all')]",
                "//button[contains(., 'Reject')]",
                "//button[@id='L2AGLb']",
            ]
            for xpath in possible_xpaths:
                buttons = driver.find_elements(By.XPATH, xpath)
                for btn in buttons:
                    if btn.is_displayed() and btn.is_enabled():
                        btn.click()
                        sleep(1.5)
                        return
        except Exception:
            pass

    def search_query(self, driver, query):
        search_box = self._wait.until(EC.presence_of_element_located((By.ID, "searchboxinput")))
        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        sleep(2)

    def scroll_to_the_end_event(self, driver):
        try:
            self._wait.until(EC.presence_of_element_located((By.CLASS_NAME, "hfpxzc")))
        except TimeoutException:
            return ["continue"]

        start_time = time()
        scroll_wait = 1
        while True:
            results = driver.find_elements(By.CLASS_NAME, 'hfpxzc')
            driver.execute_script('arguments[0].scrollIntoView(true);', results[-1])
            driver.implicitly_wait(scroll_wait)
            sleep(uniform(0.2, 0.6))
            if time() - start_time > (self._scroll_minutes * 60):
                break
        return driver.find_elements(By.CLASS_NAME, 'hfpxzc')

    def validate_result_link(self, result, driver):
        if result != "continue":
            get_link = result.get_attribute("href")
            driver.execute_script(f'''window.open("{get_link}", "_blank");''')
            driver.switch_to.window(driver.window_handles[-1])
        else:
            get_link = driver.current_url
        try:
            self._wait.until(EC.url_contains("@"))
        except Exception:
            pass
        return get_link

    def get_cover_image(self, driver):
        try:
            cover_image = self._wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]/button/img')))
            return cover_image.get_attribute("src")
        except Exception:
            return self._unavailable_text

    def get_title(self, driver):
        """
        Tries several selectors to robustly get the business title from the panel.
        """
        selectors = [
            'h1[class*="fontHeadlineLarge"]',
            'h1[class*="DUwDvf"]',
            'h1',  # fallback to any h1
        ]
        for selector in selectors:
            try:
                title_elem = driver.find_element(By.CSS_SELECTOR, selector)
                title = title_elem.text.strip()
                if title and title.lower() != "results":
                    if self._verbose:
                        print(f"Scraped title using selector '{selector}': {title}")
                    return title
            except Exception:
                continue
        if self._verbose:
            print("Could not find business title, returning Not Available")
        return self._unavailable_text

    def get_rating_in_card(self, driver):
        try:
            rating = driver.find_element(By.CSS_SELECTOR, '#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.TIHn2 > div > div.lMbq3e > div.LBgpqf > div > div.fontBodyMedium.dmRWX > div.F7nice > span:nth-child(1) > span:nth-child(1)')
            return rating.text
        except Exception:
            return self._unavailable_text

    def get_category(self, driver):
        try:
            category = driver.find_element(By.CSS_SELECTOR, '#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.TIHn2 > div > div.lMbq3e > div.LBgpqf > div > div:nth-child(2) > span > span > button')
            return category.text
        except Exception:
            return self._unavailable_text

    def get_address(self, driver):
        try:
            address = driver.find_element(By.CLASS_NAME, 'rogA2c')
            return address.text
        except Exception:
            return self._unavailable_text

    def get_website_link(self, driver):
        try:
            website = driver.find_element(By.CSS_SELECTOR, 'div.UCw5gc > div > div:nth-child(1) > a[data-tooltip="Open website"]')
            return website.get_attribute("href")
        except Exception:
            return self._unavailable_text

    def get_phone_number(self, driver):
        try:
            phone = driver.find_elements(By.CLASS_NAME, 'rogA2c')
            for ph in phone:
                ph_text = ph.text.replace("(", "").replace(")", "").replace(" ", "").replace("+", "").replace("-", "")
                if ph_text.isnumeric():
                    return ph.text
            return self._unavailable_text
        except Exception:
            return self._unavailable_text

    def get_working_hours(self, driver):
        try:
            driver.find_element(By.CSS_SELECTOR, 'div.OqCZI.fontBodyMedium.WVXvdc > div.OMl5r.hH0dDd.jBYmhd').click()
            working_hours = driver.find_element(By.CSS_SELECTOR, 'div.t39EBf.GUrTXd > div > table')
            working_hours_text = working_hours.text.strip().split("\n")
            working_hours_text = [x.strip() for x in working_hours_text if x]
            return ",".join(working_hours_text)
        except Exception:
            return self._unavailable_text

    def reset_driver_for_next_run(self, result, driver):
        if result != "continue":
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            self._wait.until(EC.presence_of_element_located((By.CLASS_NAME, "hfpxzc")))

    def scrape(self, query, row_number_start=1):
        """
        Returns a list of dicts, each matching the Roofing Leads New schema.
        """
        leads = []
        try:
            driver = self.create_chrome_driver()
            driver.get(self._maps_url)
            self.handle_consent_screen(driver)
            self.search_query(driver, query)
            self._main_handler = driver.current_window_handle
            results = self.scroll_to_the_end_event(driver)
            row_number = row_number_start
            for result in results:
                if result == "continue":
                    continue
                lead = {}
                lead["RowNumber"] = row_number
                lead["map_link"] = self.validate_result_link(result, driver)
                # After switching to the business tab, get its title
                lead["title"] = self.get_title(driver)
                lead["cover_image"] = self.get_cover_image(driver)
                lead["rating"] = self.get_rating_in_card(driver)
                lead["category"] = self.get_category(driver)
                lead["address"] = self.get_address(driver)
                lead["webpage"] = self.get_website_link(driver)
                lead["phone_number"] = self.get_phone_number(driver)
                lead["working_hours"] = self.get_working_hours(driver)
                leads.append(lead)
                row_number += 1
                self.reset_driver_for_next_run(result, driver)
            driver.quit()
        except NoSuchWindowException:
            pass
        except Exception as e:
            if self._verbose:
                print(f"Error during scraping: {e}")
        return leads

