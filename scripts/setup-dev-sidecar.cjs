const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 1. Detect Host Target Triple
let targetTriple = '';
try {
  targetTriple = execSync("rustc -Vv | grep host: | cut -d ' ' -f 2", { encoding: 'utf8' }).trim();
} catch (e) {
  // Fallback for Mac M-series
  if (process.platform === 'darwin' && process.arch === 'arm64') {
    targetTriple = 'aarch64-apple-darwin';
  } else if (process.platform === 'darwin' && process.arch === 'x64') {
    targetTriple = 'x86_64-apple-darwin';
  } else {
    console.error('❌ Failed to detect target triple. Please ensure rustc is installed.');
    process.exit(1);
  }
}

console.log(`🎯 Target Triple: ${targetTriple}`);

// 2. Define Paths
const binDir = path.join(__dirname, '../src-tauri/bin');
const sidecarName = 'sidecar'; // Must match tauri.conf.json "externalBin"
const binaryName = `${sidecarName}-${targetTriple}${process.platform === 'win32' ? '.exe' : ''}`;
const binaryPath = path.join(binDir, binaryName);
const sidecarSourceDir = path.resolve(__dirname, '../sidecar');

// 3. Ensure bin directory exists
if (!fs.existsSync(binDir)) {
  fs.mkdirSync(binDir, { recursive: true });
}

// 4. Create the Proxy Script
console.log(`🔌 Creating Sidecar Proxy at: ${binaryPath}`);

let scriptContent = '';

if (process.platform === 'win32') {
  // Windows Batch Shim
  scriptContent = `@echo off
cd /d "${sidecarSourceDir}"
uv run python main.py %*
`;
  // Note: On Windows, Tauri might expect a .exe. 
  // If this fails, we might need a simple C++ or Go wrapper.
  // But for the current user (Darwin), shell script is perfect.
} else {
  // Unix (Mac/Linux) Shell Script
  scriptContent = `#!/bin/bash
# TAURI DEV SIDE-CAR PROXY
# Redirects to source code for live-reload experience

# Navigate to project root sidecar folder
cd "${sidecarSourceDir}"

# Run with uv
echo "🚀 [Proxy] Starting Python Sidecar from Source..." >&2
exec uv run python main.py "$@"
`;
}

// 5. Write and Chmod
fs.writeFileSync(binaryPath, scriptContent);
if (process.platform !== 'win32') {
  fs.chmodSync(binaryPath, '755');
}

console.log('✅ Sidecar Proxy linked. Python changes will now apply on restart.');
