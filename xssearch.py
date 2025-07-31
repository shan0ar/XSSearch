import argparse
import sys
import tempfile
import re
import json
import shutil
import errno
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def print_help():
    help_text = """
xssearch.py - Automated XSS vulnerability tester

Usage:
    python xssearch.py --wordlist path/to/wordlist.txt --url "https://website.com/?param=XSS"
    python xssearch.py --wordlist path/to/wordlist.txt --request path/to/request.txt

Options:
    --wordlist              Path to the wordlist to test (required)
    --url                   Target URL with the GET parameter to test, use XSS where the payload will be injected
    --request               HTTP request file to use (see below for format)
    --continue-if-success   Continue after the first success (otherwise the script stops)
    --help                  Show this help message

Request file format:
    The file should contain a raw HTTP request (as exported by Burp or other proxies).
    Example:
        POST /vuln.php HTTP/2
        Host: pentwest.com
        ...
        param1=XSS&param2=XSS

Output:
    - Only successes (Alert detected: True) are displayed, with the vulnerable parameter
    - Progress shown (payload number/total, param name)
    - At the end: "Finish without XSS" or "XSS found" + the working payloads/parameter

Example:
    python xssearch.py --wordlist /usr/share/wordlists/xss_payloads.txt --request ./request.txt --continue-if-success
"""
    print(help_text)

def parse_http_request_file(path):
    with open(path, "r", encoding="utf8") as f:
        lines = f.read().splitlines()
    req_line = lines[0]
    method, uri, _ = req_line.split()
    headers = {}
    body = ''
    blank = False
    for line in lines[1:]:
        if line.strip() == '':
            blank = True
            continue
        if not blank:
            if ':' in line:
                k,v = line.split(':',1)
                headers[k.strip()] = v.strip()
        else:
            body += line + '\n'
    body = body.strip()
    return method, uri, headers, body

def filter_js_headers(headers):
    banned = [
        'Content-Length', 'Host', 'Accept-Encoding', 'Upgrade-Insecure-Requests',
        'Sec-Fetch-Site', 'Sec-Fetch-Mode', 'Sec-Fetch-User', 'Sec-Fetch-Dest',
        'Priority', 'Connection'
    ]
    allowed = {}
    for k, v in headers.items():
        if k in banned:
            continue
        allowed[k] = str(v)
    return allowed

def find_xss_params(url, headers, body):
    params = []
    url_match = re.findall(r'([?&])([^=]+)=XSS', url)
    for m in url_match:
        params.append(('url', m[1]))
    body_match = re.findall(r'([^=&]+)=XSS', body)
    for b in body_match:
        params.append(('body', b))
    for k, v in headers.items():
        if "XSS" in v:
            params.append(('header', k))
    return params

def inject_payload(url, headers, body, target_param, payload):

    if target_param[0] == 'url':
        def repl(match):
            name = match.group(2)
            return f"{match.group(1)}{name}={payload}" if name == target_param[1] else match.group(0)
        new_url = re.sub(r'([?&])([^=]+)=XSS', repl, url)
    else:
        new_url = url

    if target_param[0] == 'body':
        def repl(match):
            name = match.group(1)
            return f"{name}={payload}" if name == target_param[1] else match.group(0)
        new_body = re.sub(r'([^=&]+)=XSS', repl, body)
    else:
        new_body = body

    new_headers = headers.copy()
    if target_param[0] == 'header':
        for k in new_headers:
            if k == target_param[1]:
                new_headers[k] = new_headers[k].replace('XSS', payload, 1)
    return new_url, new_headers, new_body

def test_xss_selenium(driver, url, method, headers, body):
    js_headers = filter_js_headers(headers)
    if method.upper() == "GET":
        driver.get(url)
    else:
        origin_url = headers.get("Origin", f"https://{headers.get('Host','localhost')}")
        driver.get(origin_url)
        headers_js = json.dumps(js_headers)
        safe_body = body.replace('\\', '\\\\').replace('`', '\\`')
        script = f'''
            fetch("{url}", {{
                method: "{method.upper()}",
                headers: {headers_js},
                body: `{safe_body}`
            }}).then(r => r.text()).then(t => {{
                document.open(); document.write(t); document.close();
            }});
        '''
        driver.execute_script(script)
    try:
        WebDriverWait(driver, 2).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert.accept()
        return True
    except Exception:
        return False

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--wordlist", type=str, required=False)
    parser.add_argument("--url", type=str, required=False)
    parser.add_argument("--request", type=str, required=False)
    parser.add_argument("--continue-if-success", action='store_true')
    parser.add_argument("--help", action='store_true')
    args = parser.parse_args()

    if args.help or not args.wordlist or (not args.url and not args.request):
        print_help()
        sys.exit(0)

    wordlist_path = args.wordlist
    continue_if_success = args.continue_if_success

    with open(wordlist_path, "r", encoding="utf8") as f:
        payloads = [line.strip() for line in f if line.strip()]
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
                if args.url:
                    url_params = []
                    url_match = re.findall(r'([?&])([^=]+)=XSS', args.url)
                    for m in url_match:
                        url_params.append(('url', m[1]))
                    if not url_params:
                        print("No XSS parameter found in URL")
                        sys.exit(1)
                    param_count = len(url_params)
                    for idx, payload in enumerate(payloads, start=1):
                        param = url_params[(idx-1) % param_count]
                        new_url, _, _ = inject_payload(args.url, {}, '', param, payload)
                        success = test_xss_selenium(driver, new_url, "GET", {}, '')
                        if success:
                            print(f"Payload: {payload} | Vulnerable parameter: {param[1]} | Alert detected: True")
                            results.append((payload, param[1]))
                            if not continue_if_success:
                                break
                        if idx % 10 == 0:
                            percent = (idx / len(payloads)) * 100
                            print(f"Progress: {percent:.2f}% ({idx}/{len(payloads)}) parameter: {param[1]}")
                elif args.request:
                    method, uri, headers, body = parse_http_request_file(args.request)
                    base_url = f"https://{headers.get('Host','localhost')}{uri}"
                    params = find_xss_params(base_url, headers, body)
                    if not params:
                        print("No XSS parameter found in request")
                        sys.exit(1)
                    param_count = len(params)
                    for idx, payload in enumerate(payloads, start=1):
                        param = params[(idx-1) % param_count]
                        url_inject, headers_inject, body_inject = inject_payload(base_url, headers, body, param, payload)
                        success = test_xss_selenium(driver, url_inject, method, headers_inject, body_inject)
                        if success:
                            param_name = param[1]
                            param_type = param[0]
                            if param_type == "header":
                                print(f"Payload: {payload} | Vulnerable parameter: {param_name} (header) | Alert detected: True")
                                results.append((payload, param_name, param_type))
                            else:
                                print(f"Payload: {payload} | Vulnerable parameter: {param_name} | Alert detected: True")
                                results.append((payload, param_name))
                            if not continue_if_success:
                                break
                        if idx % 10 == 0:
                            percent = (idx / len(payloads)) * 100
                            if param_type == "header":
                                print(f"Progress: {percent:.2f}% ({idx}/{len(payloads)}) parameter: {param_name} (header)")
                            else:
                                print(f"Progress: {percent:.2f}% ({idx}/{len(payloads)}) parameter: {param_name}")
            except KeyboardInterrupt:
                print("\nKeyboard interruption")
            finally:
                driver.quit()
                try:
                    shutil.rmtree(tmpdirname)
                except OSError as e:
                    if e.errno == errno.ENOTEMPTY or e.errno == 39:
                        pass
                    else:
                        print(f"[!] Critical error: {e}")
    except Exception as e:
        print(f"[!] Critical error: {e}")

    if results:
        print("\nXSS found")
        for r in results:
            if len(r) == 3 and r[2] == "header":
                print(f"Payload: {r[0]} | Vulnerable parameter: {r[1]} (header)")
            else:
                print(f"Payload: {r[0]} | Vulnerable parameter: {r[1]}")
    else:
        print("\nFinish without XSS")

if __name__ == "__main__":
    main()
