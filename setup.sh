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

echo "Step 2: Install numpy 1.x (compatibility with compiled extensions)"
python -m pip install --no-cache-dir numpy==1.26.4
echo "✓ numpy installed"
echo ""

echo "Step 3: Install PyTorch CPU wheel from the official PyTorch index"
python -m pip install --no-cache-dir torch==2.2.2+cpu --index-url https://download.pytorch.org/whl/cpu
echo "✓ PyTorch (CPU) installed"
echo ""

echo "Step 4: Install remaining dependencies from requirements.txt"
python -m pip install --no-cache-dir -r requirements.txt
echo "✓ Remaining dependencies installed"
echo ""

echo "========================================"
echo "Setup completed successfully!"
echo "========================================"
echo ""