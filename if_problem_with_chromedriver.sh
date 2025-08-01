#!/bin/bash

set -e

if ! command -v chromium >/dev/null 2>&1 && ! command -v chromium-browser >/dev/null 2>&1; then
  echo "Erreur : Chromium is not installed or untraceable in the PATH."
  exit 1
fi

CHROMIUM_BIN=$(command -v chromium || command -v chromium-browser)

echo "Binaire Chromium détecté : $CHROMIUM_BIN"

CHROMIUM_VERSION_FULL=$($CHROMIUM_BIN --version | grep -oP '\d+\.\d+\.\d+\.\d+')
if [[ -z "$CHROMIUM_VERSION_FULL" ]]; then
  echo "Impossible to detect the Chromium version."
  exit 1
fi

CHROMIUM_VERSION_MAJOR=$(echo "$CHROMIUM_VERSION_FULL" | cut -d '.' -f1)
echo "Version majeure de Chromium détectée : $CHROMIUM_VERSION_MAJOR"

CHROMEDRIVER_URL="https://storage.googleapis.com/chrome-for-testing-public/${CHROMIUM_VERSION_MAJOR}.0.6998.88/linux64/chromedriver-linux64.zip"

echo "Download of ChromeDriver from : $CHROMEDRIVER_URL"

TMP_ZIP="/tmp/chromedriver-linux64.zip"
TMP_DIR="/tmp/chromedriver-linux64"

curl -L -o "$TMP_ZIP" "$CHROMEDRIVER_URL"

rm -rf "$TMP_DIR"
unzip -q "$TMP_ZIP" -d /tmp

sudo mv "$TMP_DIR/chromedriver" /usr/bin/chromedriver
sudo chmod +x /usr/bin/chromedriver

echo "ChromeDriver installé dans /usr/bin/chromedriver"

chromedriver --version
