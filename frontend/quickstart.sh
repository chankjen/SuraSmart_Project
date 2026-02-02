#!/bin/bash

# SuraSmart Frontend Setup Script for Linux/macOS

echo "================================"
echo "SuraSmart Frontend Setup"
echo "================================"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

echo "✓ Node.js $(node --version) detected"

# Navigate to frontend directory
cd "$(dirname "$0")/frontend" || exit 1

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo ""
    echo "📦 Installing dependencies..."
    npm install
    echo "✓ Dependencies installed"
else
    echo "✓ Dependencies already installed"
fi

# Copy .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "📋 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✓ .env file created"
fi

echo ""
echo "================================"
echo "Setup Complete! ✓"
echo "================================"
echo ""
echo "Available commands:"
echo "  npm start       - Start development server (port 3000)"
echo "  npm run build   - Create production build"
echo "  npm test        - Run tests"
echo ""
echo "Starting development server..."
echo "Frontend will be available at: http://localhost:3000"
echo ""

npm start
