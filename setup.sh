#!/bin/bash
set -e

echo "========================================"
echo "Email Classifier AI - Setup Script"
echo "========================================"
echo ""

echo "Step 1: Updating pip, setuptools and wheel..."
pip install --upgrade pip setuptools wheel
echo "✓ Pip updated successfully"
echo ""

echo "Step 2: Installing PyTorch CPU wheel (from official PyTorch index)..."
pip install torch==2.2.2+cpu --index-url https://download.pytorch.org/whl/cpu
echo "✓ PyTorch (CPU) installed successfully"
echo ""

echo "Step 3: Installing remaining dependencies from requirements.txt..."
pip install -r requirements.txt
echo "✓ Remaining dependencies installed"
echo ""

echo "========================================"
echo "✓ Setup completed successfully!"
echo "========================================"
echo ""