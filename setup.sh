#!/bin/bash
set -e

echo "========================================"
echo "Email Classifier AI - Setup Script"
echo "========================================"
echo ""

echo "Step 1: Upgrade pip, setuptools and wheel"
python -m pip install --upgrade pip setuptools wheel
echo "✓ pip, setuptools and wheel updated"
echo ""

echo "Step 2: Install numpy (compatibility with compiled extensions)"
python -m pip install --no-cache-dir numpy==1.26.4
echo "✓ numpy installed"
echo ""

echo "Step 3: Install remaining dependencies from requirements.txt"
python -m pip install --no-cache-dir -r requirements.txt
echo "✓ Remaining dependencies installed"
echo ""

echo "========================================"
echo "Setup completed successfully!"
echo "========================================"
echo ""