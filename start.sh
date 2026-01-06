#!/bin/bash
# All-in-one startup script
# Updates venv, builds frontend, and starts the server

set -e

echo "🚀 Starting S2ST Translator (All-in-One)..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Running setup first...${NC}"
    ./setup.sh
fi

# Activate virtual environment
echo -e "${BLUE}🔌 Activating virtual environment...${NC}"
source venv/bin/activate

# Update Python dependencies
echo -e "${BLUE}📦 Updating Python dependencies...${NC}"
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -r requirements.txt --quiet
if [ -f "requirements-dev.txt" ]; then
    pip install -r requirements-dev.txt --quiet
fi
echo -e "${GREEN}✅ Python dependencies updated${NC}"
echo ""

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠️  Node.js not found. Skipping frontend build.${NC}"
    echo -e "${YELLOW}   Install Node.js to build the frontend, or use dev mode separately.${NC}"
    FRONTEND_BUILT=false
else
    # Check if frontend directory exists
    if [ ! -d "frontend" ]; then
        echo -e "${YELLOW}⚠️  Frontend directory not found. Skipping frontend build.${NC}"
        FRONTEND_BUILT=false
    else
        # Update frontend dependencies and build
        echo -e "${BLUE}📦 Updating frontend dependencies...${NC}"
        cd frontend
        
        # Check if node_modules exists, if not, install
        if [ ! -d "node_modules" ]; then
            echo -e "${BLUE}   Installing npm packages (this may take a while)...${NC}"
            npm install
        else
            # Update packages
            npm install --silent
        fi
        
        echo -e "${GREEN}✅ Frontend dependencies updated${NC}"
        echo ""
        
        # Build frontend (skip type checking if vue-tsc fails)
        echo -e "${BLUE}🔨 Building frontend...${NC}"
        if npm run build 2>&1; then
            if [ -d "dist" ]; then
                echo -e "${GREEN}✅ Frontend built successfully${NC}"
                FRONTEND_BUILT=true
            else
                echo -e "${YELLOW}⚠️  Frontend build completed but dist directory not found${NC}"
                FRONTEND_BUILT=false
            fi
        else
            echo -e "${YELLOW}⚠️  Frontend build failed, trying without type checking...${NC}"
            # Try building without type checking
            if npx vite build 2>&1; then
                if [ -d "dist" ]; then
                    echo -e "${GREEN}✅ Frontend built successfully (without type checking)${NC}"
                    FRONTEND_BUILT=true
                else
                    echo -e "${YELLOW}⚠️  Frontend build failed${NC}"
                    FRONTEND_BUILT=false
                fi
            else
                echo -e "${YELLOW}⚠️  Frontend build failed, but continuing with server...${NC}"
                FRONTEND_BUILT=false
            fi
        fi
        
        cd ..
        echo ""
    fi
fi

# Create necessary directories
mkdir -p input output/translated output/metadata output/logs output/backups config

# Start the server
echo -e "${GREEN}🎉 Starting server...${NC}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Setup complete!${NC}"
if [ "$FRONTEND_BUILT" = true ]; then
    echo -e "${GREEN}✅ Frontend built and ready${NC}"
fi
echo ""
echo -e "${BLUE}🌐 Server will be available at:${NC}"
echo -e "   ${GREEN}http://127.0.0.1:5000${NC}"
echo ""
echo -e "${BLUE}📚 API Documentation:${NC}"
echo -e "   ${GREEN}http://127.0.0.1:5000/docs${NC}"
echo ""
echo -e "${YELLOW}Press CTRL+C to stop the server${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Start the GUI server
python -m tool.main gui --host 127.0.0.1 --port 5000

