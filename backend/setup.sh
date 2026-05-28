#!/bin/bash

# SentinelOS Backend Development Startup Script

set -e

echo "🔧 SentinelOS Backend - Development Setup"
echo "==========================================="
echo ""

# Check Python version
echo "✓ Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Python $python_version"

if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 is required but not installed"
    exit 1
fi

# Check PostgreSQL
echo ""
echo "✓ Checking PostgreSQL..."
if ! command -v psql &> /dev/null; then
    echo "  ⚠ PostgreSQL not found in PATH"
    echo "  If using Docker Compose, you can skip this"
else
    echo "  PostgreSQL found"
fi

# Check Redis
echo ""
echo "✓ Checking Redis..."
if ! command -v redis-cli &> /dev/null; then
    echo "  ⚠ Redis not found in PATH"
    echo "  If using Docker Compose, you can skip this"
else
    echo "  Redis found"
fi

# Create virtual environment if it doesn't exist
echo ""
echo "✓ Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "  Virtual environment created"
else
    echo "  Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
echo "  Virtual environment activated"

# Install/upgrade pip
echo ""
echo "✓ Installing dependencies..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo "  Dependencies installed"

# Create .env if it doesn't exist
echo ""
echo "✓ Checking environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "  .env file created (update with your settings)"
else
    echo "  .env file already exists"
fi

# Create uploads directory
mkdir -p uploads

echo ""
echo "==========================================="
echo "✓ Setup complete!"
echo ""
echo "To start the development server:"
echo "  source venv/bin/activate"
echo "  uvicorn main:app --reload"
echo ""
echo "To use Docker Compose (recommended):"
echo "  docker-compose up --build"
echo ""
