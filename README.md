# XSSearch

**xssearch.py** is a fast, flexible, and browser-based XSS payload tester for web applications.  
It uses Selenium and Chrome to automate XSS detection, supports customizable wordlists, GET/POST/complex requests, progress reporting, and now lets you provide a custom cookie for session-based GET fuzzing.

---

## Installation

Quick install (all dependencies):

```bash
git clone https://github.com/shan0ar/xssearch.git \
&& python3 -m venv xssearch/xssearch \
&& source xssearch/xssearch/bin/activate \
&& pip install -r xssearch/requirements.txt \
&& cd xssearch
```

Or download `xssearch.py` and install requirements manually.

---

## Features

- **Customizable Target:** Inject payloads into any parameter or header using `XSS` in the URL, POST, or headers.
- **Flexible Wordlists:** Supports any file with one payload per line.
- **Progress Tracking:** Prints progress dynamically (every 10s for 1min, every 30s up to 10min, every 3min up to 20min, then every 20min).
- **Success Control:** Stops after the first XSS (default), or continues with `--continue-if-success`.
- **Comprehensive Output:** Only successful payloads are shown, with a summary at the end.
- **Headless Chrome:** Uses Chrome in headless mode for reliability.
- **Raw HTTP Request Support:** Fuzz POST and complex requests using a raw HTTP request (`--request`).
- **Multi-parameter Detection:** Detects all params using the `XSS` keyword in URL, body, and headers.
- **Session Cookie for GET:** Use `--cookie` to test with a real session (GET).
- **Automatic Alert Handling:** Automatically closes JS alerts to avoid Selenium blocks.

---

## Usage

### Basic Command (GET)

```bash
python xssearch.py --wordlist /path/to/wordlist.txt --url "https://target.com/search?query=XSS"
```

### With Cookie (GET)

```bash
python xssearch.py --wordlist xss_payloads.txt --url "https://target.com/search?query=XSS" --cookie "PHPSESSID=xxxxxx"
```

### Advanced Command (POST / complex)

```bash
python xssearch.py --wordlist /path/to/wordlist.txt --request /path/to/request.txt
```

### Options

| Option                   | Description                                                                                                  |
|--------------------------|--------------------------------------------------------------------------------------------------------------|
| `--wordlist`             | Path to XSS payload wordlist file (required).                                                                |
| `--url`                  | Target URL with `XSS` where the payload should be injected (for GET).                                        |
| `--request`              | Path to a raw HTTP request file (useful for POST or complex requests).                                       |
| `--cookie`               | Cookie header (e.g. `"PHPSESSID=xxxx; csrf=yyy"`) for GET (optional).                                       |
| `--continue-if-success`  | Continue testing all payloads even after a found XSS (optional).                                             |
| `--help`                 | Show usage information.                                                                                      |

---

### Example: Single Success (default)

```bash
python xssearch.py --wordlist xss_payloads.txt --url "https://site.com/search?q=XSS"
```

**Output:**
```
Payload: <svg onload=alert(1)> | Alert detected: True

XSS found
Payload: <svg onload=alert(1)> | Vulnerable parameter: q
```

---

### Example: Continue on Success

```bash
python xssearch.py --wordlist xss_payloads.txt --url "https://site.com/search?q=XSS" --continue-if-success
```

**Output:**
```
Payload: <img src=x onerror=alert(1)> | Alert detected: True
Payload: <svg onload=alert(2)> | Alert detected: True
[00:10] Progress: 20/6613 payloads tested (0.30%)
...
XSS found
Payload: <img src=x onerror=alert(1)> | Vulnerable parameter: q
Payload: <svg onload=alert(2)> | Vulnerable parameter: q
```

---

### Example: POST Request with --request

```bash
python xssearch.py --wordlist xss_payloads.txt --request request.txt
```

**Output:**
```
Payload: <img src=x onerror=alert(1)> | Vulnerable parameter: searchFor | Alert detected: True
...
XSS found
Payload: <img src=x onerror=alert(1)> | Vulnerable parameter: searchFor
```

---

### Example: No XSS Found

```bash
python xssearch.py --wordlist xss_payloads.txt --url "https://site.com/search?q=XSS"
```

**Output:**
```
[00:10] Progress: 10/6613 payloads tested (0.15%)
...
Finish without XSS
```

---

### Progress Display

- Progress is shown:
  - Every 10 seconds up to 1 minute,
  - Every 30 seconds from 1 to 10 minutes,
  - Every 3 minutes from 10 to 20 minutes,
  - Every 20 minutes after 20 minutes.
- Example:  
  `[00:30] Progress: 54/6613 payloads tested (0.82%)`

---

## Wordlist Format

Your wordlist should be a plain text file, **one payload per line**.  
Example:
```
<script>alert('XSS')</script>
"><svg/onload=alert(1)>
<img src=x onerror=alert('XSS')>
```

---

## Target URL Format

Use the string `XSS` in your target URL where you want the payload to be injected.  
Example:
- `https://test.com/?search=XSS`
- `https://victim.com/page.php?input=XSS`

**For POST or complex requests:**  
Export the raw HTTP request (e.g. from Burp Suite) and use the `XSS` keyword in any parameter or header you want to fuzz.

---

## Requirements

See [requirements.txt](requirements.txt) for exact dependencies.

- Python 3.7+
- Google Chrome (installed)
- ChromeDriver (matching Chrome version)
- Selenium Python package

Install with:
```bash
pip install -r requirements.txt
```

---

## Troubleshooting

- **Chrome/ChromeDriver not found:**  
  Install both and ensure they’re in your PATH.
- **Permission errors:**  
  Try running with elevated privileges or adjust Chrome options.
- **Selenium errors / unexpected alert:**  
  If errors, increase timeout or check your ChromeDriver version.

---

## License

BALEC.

---
