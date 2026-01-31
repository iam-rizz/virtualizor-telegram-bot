#!/bin/bash

APP_NAME="virtualizor-bot"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"
REQUIREMENTS="$SCRIPT_DIR/requirements.txt"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}  Virtualizor Bot Updater${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

if [ ! -d "$SCRIPT_DIR/.git" ]; then
    echo -e "${RED}[!] Not a git repository${NC}"
    echo -e "${YELLOW}    Please clone the repository using git${NC}"
    exit 1
fi

echo -e "${YELLOW}[*] Pulling latest changes...${NC}"
cd "$SCRIPT_DIR"
git fetch origin

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" = "$REMOTE" ]; then
    echo -e "${GREEN}[+] Already up to date${NC}"
else
    git pull origin main
    if [ $? -ne 0 ]; then
        echo -e "${RED}[!] Git pull failed. Please resolve conflicts manually${NC}"
        exit 1
    fi
    echo -e "${GREEN}[+] Updated successfully${NC}"
fi

if [ -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}[*] Updating dependencies...${NC}"
    source "$VENV_DIR/bin/activate"
    pip install -q --upgrade pip
    pip install -q -r "$REQUIREMENTS"
    echo -e "${GREEN}[+] Dependencies updated${NC}"
fi

echo -e "${YELLOW}[*] Restarting bot...${NC}"

if command -v pm2 &> /dev/null && pm2 list | grep -q "$APP_NAME"; then
    pm2 restart "$APP_NAME"
    echo -e "${GREEN}[+] Bot restarted with PM2${NC}"
elif screen -list | grep -q "$APP_NAME"; then
    screen -S "$APP_NAME" -X quit 2>/dev/null
    sleep 1
    screen -dmS "$APP_NAME" bash -c "source $VENV_DIR/bin/activate && python $SCRIPT_DIR/main.py"
    echo -e "${GREEN}[+] Bot restarted with screen${NC}"
else
    echo -e "${YELLOW}[!] Bot not running. Use ./start.sh to start${NC}"
fi

echo ""
echo -e "${GREEN}[+] Update complete!${NC}"
