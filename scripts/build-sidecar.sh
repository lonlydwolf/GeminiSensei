#!/bin/bash

# Ensure we are in the project root
cd "$(dirname "$0")/.."

# Detect architecture and OS
TRIPLE=""
if [[ "$OSTYPE" == "darwin"* ]]; then
  if [[ $(uname -m) == "arm64" ]]; then
    TRIPLE="aarch64-apple-darwin"
  else
    TRIPLE="x86_64-apple-darwin"
  fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
  TRIPLE="x86_64-unknown-linux-gnu"
elif [[ "$OSTYPE" == "msys" ]]; then
  TRIPLE="x86_64-pc-windows-msvc"
else
  echo "Unsupported OS: $OSTYPE"
  exit 1
fi

echo "Building sidecar for target: $TRIPLE"

mkdir -p src-tauri/bin

cd sidecar

# Build with PyInstaller
# We use uv run to ensure we use the environment with dependencies
uv run pyinstaller --clean --name sidecar --onefile main.py --distpath ../src-tauri/bin

# Rename the binary to include the target triple
if [ -f "../src-tauri/bin/sidecar" ]; then
  mv "../src-tauri/bin/sidecar" "../src-tauri/bin/sidecar-$TRIPLE"
  echo "Success! Binary created at src-tauri/bin/sidecar-$TRIPLE"
else
  echo "Error: Binary not found after PyInstaller build."
  exit 1
fi
