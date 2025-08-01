import os
import re
import subprocess
import sys
import urllib.request
import zipfile
import shutil

def get_chromium_version():
    try:
        result = subprocess.run(['/usr/bin/chromium', '--version'], capture_output=True, text=True)
        version_output = result.stdout.strip()
        match = re.search(r'(\d+)\.(\d+)\.(\d+)\.(\d+)', version_output)
        if match:
            return match.group(1)
    except Exception as e:
        print(f"Error retrieving Chromium version: {e}")
    return None

def download_chromedriver(version):
    url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}.0.6998.88/linux64/chromedriver-linux64.zip"
    print(f"Download of ChromeDriver {version} from {url} ...")
    zip_path = "/tmp/chromedriver-linux64.zip"
    urllib.request.urlretrieve(url, zip_path)
    print("Download finished.")
    return zip_path

def install_chromedriver(zip_path):
    extract_path = "/tmp/chromedriver-linux64"
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall("/tmp")
    source = os.path.join(extract_path, "chromedriver")
    target = "/usr/bin/chromedriver"
    try:
        print(f"Installation of ChromeDriver in {target} ...")
        shutil.move(source, target)
        os.chmod(target, 0o755)
        print("Installation terminated.")
    except PermissionError:
        print("Erreur : Wrong rights. Restart the script with sudo.")
        sys.exit(1)

def main():
    version = get_chromium_version()
    if not version:
        print("Impossible to detect the version of Chromium.")
        sys.exit(1)
    print(f"Major version of Chromium detected : {version}")
    
    zip_path = download_chromedriver(version)
    install_chromedriver(zip_path)

    print("Checking the version of ChromeDriver installed :")
    subprocess.run(["chromedriver", "--version"])

if __name__ == "__main__":
    main()
