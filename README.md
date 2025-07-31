# XSSearch

**xssearch.py** is a fast and customizable XSS payload tester for web applications. It uses Selenium to automate browser interactions, allowing you to test for Cross-Site Scripting (XSS) vulnerabilities with your own wordlists and target URLs. The tool supports progress reporting, interruption handling, and several runtime options to streamline your workflow.

---

## Installation

You can install everything in **one command**:

```bash
git clone https://github.com/shan0ar/xssearch.git \
&& python3 -m venv xssearch/xssearch \
&& source xssearch/xssearch/bin/activate \
&& pip install -r xssearch/requirements.txt \
&& cd xssearch
```

Alternatively, you can manually download `xssearch.py` and install dependencies.

---

## Features

- **Customizable Target:** Specify any URL and parameter location for payload injection using the `XSS` keyword.
- **Flexible Wordlists:** Use any file containing XSS payloads, one per line.
- **Progress Tracking:** Shows percentage, number of tested payloads, and progress intervals (configurable by count).
- **Success Control:** Stop testing after the first detected XSS by default, or continue with `--continue-if-success`.
- **Comprehensive Output:** Only successful payloads are displayed, with summary at the end.
- **Headless Chrome:** Uses Chrome in headless mode for speed and reliability.

---

## Usage

### Basic Command

```bash
python xssearch.py --wordlist /path/to/wordlist.txt --url "https://target.com/search?query=XSS"
```

### Options

| Option                   | Description                                                                                                  |
|--------------------------|--------------------------------------------------------------------------------------------------------------|
| `--wordlist`             | Path to your XSS payload wordlist file (required).                                                           |
| `--url`                  | Target URL with `XSS` where the payload should be injected (required).                                       |
| `--continue-if-success`  | Continue testing all payloads even after a success (optional).                                               |
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
Payload: <svg onload=alert(1)> | Alert text: 1
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
Progression: 0.30% (20/6613)
...
XSS found
Payload: <img src=x onerror=alert(1)> | Alert text: 1
Payload: <svg onload=alert(2)> | Alert text: 2
```

---

### Example: No XSS Found

```bash
python xssearch.py --wordlist xss_payloads.txt --url "https://site.com/search?q=XSS"
```

**Output:**
```
Progression: 0.15% (10/6613)
...
Finish without XSS
```

---

### Progress Display

- Progress is shown every 10 tested payloads up to 1000, every 50 between 1000 and 10000, and every 100 after 10000.
- Example:  
  `Progression: 0.90% (60/6613)`

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

---

## Requirements

See [requirements.txt](requirements.txt) for exact dependencies.

- Python 3.7+
- Google Chrome (installed)
- ChromeDriver (matching your Chrome version)

---

## Troubleshooting

- **Chrome/ChromeDriver not found:**  
  Ensure Chrome and ChromeDriver are installed and in your PATH.
- **Permission errors:**  
  Try running with elevated privileges or adjust Chrome options.
- **Selenium errors:**  
  Make sure all Python dependencies are installed.

---

## License

MIT License.

---

## Author

shan0ar

---

## Contributing

Pull requests and suggestions are welcome!  
Feel free to open issues for bug reports or feature requests.
