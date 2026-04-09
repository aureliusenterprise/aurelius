#!/bin/bash
set -euo pipefail

SONAR_VERSION=8.0.1.6346
SONAR_ZIP="sonarscanner-cli.zip"
SONAR_ROOT="/opt/sonarscanner"
SONAR_DIR="$SONAR_ROOT/sonar-scanner-$SONAR_VERSION-linux-x64"

# Install SonarScanner CLI
curl -o "$SONAR_ZIP" -L "https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-$SONAR_VERSION-linux-x64.zip"
sudo unzip -o "$SONAR_ZIP" -d "$SONAR_ROOT"
rm "$SONAR_ZIP"

# Make sonar-scanner available in all shells.
sudo ln -sf "$SONAR_DIR/bin/sonar-scanner" /usr/local/bin/sonar-scanner
