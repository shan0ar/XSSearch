import argparse
import sys
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def print_help():
    help_text = """
xssearch.py - Automated XSS vulnerability tester

Usage:
    python xssearch.py --wordlist path/to/wordlist.txt --url "https://website.com/?param=XSS" [--continue-if-success]

Options:
    --wordlist              Path to the wordlist to test (required)
    --url                   Target URL with the GET parameter to test, use XSS where the payload will be injected (required)
    --continue-if-success   Continue after the first success (otherwise the script stops)
    --help                  Show this help message

Output:
    - Only successes (Alert detected: True) are displayed
    - Progress shown as percentage, current line/total lines
    - Countdown by 10 up to 1,000; by 50 up to 10,000; by 100 above that
    - At the end: "Finish without XSS" or "XSS found" + the working payloads

Example:
    python xssearch.py --wordlist /usr/share/wordlists/xss_payloads.txt --url "https://website.com/?q=XSS" --continue-if-success
"""
    print(help_text)

def test_xss(driver, base_url, payload):
    url = base_url.replace("XSS", payload.strip())
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
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--wordlist", type=str, required=False)
    parser.add_argument("--url", type=str, required=False)
    parser.add_argument("--continue-if-success", action='store_true')
    parser.add_argument("--help", action='store_true')
    args = parser.parse_args()

    if args.help or not args.wordlist or not args.url:
        print_help()
        sys.exit(0)

    wordlist_path = args.wordlist
    base_url = args.url
    continue_if_success = args.continue_if_success

    with open(wordlist_path, "r", encoding="utf8") as f:
        payloads = f.readlines()

    total = len(payloads)
    results = []
    service = Service("/usr/bin/chromedriver")
    try:
        with tempfile.TemporaryDirectory() as tmpdirname:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--blink-settings=imagesEnabled=false')
            options.add_argument(f"--user-data-dir={tmpdirname}")
            driver = webdriver.Chrome(service=service, options=options)

            try:
                for idx, payload in enumerate(payloads, start=1):
                    success, alert_text = test_xss(driver, base_url, payload)
                    if success:
                        print(f"Payload: {payload.strip()} | Alert detected: True")
                        results.append((payload.strip(), alert_text))
                        if not continue_if_success:
                            break

                    show = False
                    if idx < 1000 and idx % 10 == 0:
                        show = True
                    elif 1000 <= idx < 10000 and idx % 50 == 0:
                        show = True
                    elif idx >= 10000 and idx % 100 == 0:
                        show = True

                    if show or idx == total:
                        percent = (idx / total) * 100
                        print(f"Progress: {percent:.2f}% ({idx}/{total})")
            except KeyboardInterrupt:
                print("\nKeyboard interruption")
            finally:
                driver.quit()
    except Exception as e:
        print(f"[!] Critical error: {e}")

    if results:
        print("\nXSS found")
        for payload, alert_text in results:
            print(f"Payload: {payload} | Alert text: {alert_text}")
    else:
        print("\nFinish without XSS")

if __name__ == "__main__":
    main()
