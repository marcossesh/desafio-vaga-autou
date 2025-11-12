#!/bin/bash
set -e

echo "========================================"
echo "Email Classifier AI - Setup Script"
echo "========================================"
echo ""

echo "Step 1: Updating pip..."
pip install --upgrade pip setuptools wheel
echo "✓ Pip updated successfully"
echo ""

echo "Step 2: Installing PyTorch CPU version..."
pip install torch==2.1.2 --index-url https://download.pytorch.org/whl/cpu
echo "✓ PyTorch installed successfully"
echo ""

echo "Step 3: Installing FastAPI and dependencies..."
pip install fastapi==0.109.0
pip install uvicorn[standard]==0.27.0
pip install python-multipart==0.0.6
echo "✓ FastAPI dependencies installed"
echo ""

echo "Step 4: Installing NLP dependencies..."
pip install transformers==4.37.2
pip install PyPDF2==4.0.1
echo "✓ NLP dependencies installed"
echo ""

echo "Step 5: Installing utilities..."
pip install python-dotenv==1.0.0
pip install pydantic==2.5.3
pip install nltk==3.8.1
pip install aiofiles==23.2.1
echo "✓ Utilities installed"
echo ""

echo "========================================"
echo "✓ Setup completed successfully!"
echo "========================================"
echo ""
echo "To run the application:"
echo "  python main.py"
echo ""