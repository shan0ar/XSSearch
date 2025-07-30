import argparse
import sys
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def print_help():
    help_text = """
xssearch3.py - Testeur de failles XSS automatisé

Utilisation :
    python xssearch3.py --wordlist chemin/vers/wordlist.txt --url "https://site.com/?param=XSS" [--continue-if-success]

Options :
    --wordlist              Chemin vers la wordlist à tester (obligatoire)
    --url                   URL cible avec le paramètre GET à tester, utiliser XSS où le payload sera injecté (obligatoire)
    --continue-if-success   Continue après le premier succès (sinon le script s'arrête)
    --help                  Affiche cet aide

Affichage :
    - Seuls les succès (Alert detected: True) sont affichés
    - Progression avec pourcentage, ligne courante/nombre total de lignes
    - Décompte de 10 en 10 jusqu'à 1000 ; de 50 en 50 jusqu'à 10000 ; puis de 100 en 100 au-delà
    - À la fin : "Finish without XSS" ou "XSS found" + les payloads ayant fonctionné

Exemple :
    python xssearch3.py --wordlist /usr/share/wordlists/xss/xss3.txt --url "https://pentwest.com/?q=XSS" --continue-if-success
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
                        print(f"Progression: {percent:.2f}% ({idx}/{total})")
            except KeyboardInterrupt:
                print("\n[!] Interruption clavier reçue, arrêt propre du script.")
            finally:
                driver.quit()
    except Exception as e:
        print(f"[!] Erreur critique: {e}")

    if results:
        print("\nXSS found")
        for payload, alert_text in results:
            print(f"Payload: {payload} | Alert text: {alert_text}")
    else:
        print("\nFinish without XSS")

if __name__ == "__main__":
    main()
