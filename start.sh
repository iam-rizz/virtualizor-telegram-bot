#!/bin/bash

APP_NAME="virtualizor-bot"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"
ENV_FILE="$SCRIPT_DIR/.env"
ENV_EXAMPLE="$SCRIPT_DIR/.env.example"
REQUIREMENTS="$SCRIPT_DIR/requirements.txt"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}  Virtualizor Telegram Bot${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

if [ ! -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}[!] .env file not found${NC}"
    if [ -f "$ENV_EXAMPLE" ]; then
        cp "$ENV_EXAMPLE" "$ENV_FILE"
        echo -e "${GREEN}[+] Created .env from .env.example${NC}"
        echo -e "${RED}[!] Please edit .env file with your configuration${NC}"
        echo -e "${YELLOW}    nano $ENV_FILE${NC}"
        exit 1
    else
        echo -e "${RED}[!] .env.example not found${NC}"
        exit 1
    fi
fi

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[!] Python 3 not found. Installing...${NC}"
    sudo apt update && sudo apt install -y python3
fi

if ! python3 -m venv --help &> /dev/null; then
    echo -e "${YELLOW}[!] python3-venv not found. Installing...${NC}"
    sudo apt update && sudo apt install -y python3-venv
fi

if ! python3 -m pip --version &> /dev/null; then
    echo -e "${YELLOW}[!] pip not found. Installing...${NC}"
    sudo apt update && sudo apt install -y python3-pip
fi

if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}[*] Creating virtual environment...${NC}"
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}[+] Virtual environment created${NC}"
fi

echo -e "${YELLOW}[*] Activating virtual environment...${NC}"
source "$VENV_DIR/bin/activate"

echo -e "${YELLOW}[*] Installing dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -r "$REQUIREMENTS"
echo -e "${GREEN}[+] Dependencies installed${NC}"

if command -v pm2 &> /dev/null; then
    echo -e "${GREEN}[+] PM2 detected${NC}"
    
    if pm2 list | grep -q "$APP_NAME"; then
        echo -e "${YELLOW}[*] Restarting $APP_NAME...${NC}"
        pm2 restart "$APP_NAME"
    else
        echo -e "${YELLOW}[*] Starting $APP_NAME with PM2...${NC}"
        pm2 start "$VENV_DIR/bin/python" --name "$APP_NAME" -- "$SCRIPT_DIR/main.py"
        pm2 save
    fi
    
    echo -e "${GREEN}[+] Bot started with PM2${NC}"
    echo -e "${YELLOW}    View logs: pm2 logs $APP_NAME${NC}"
    echo -e "${YELLOW}    Stop bot:  pm2 stop $APP_NAME${NC}"
else
    if ! command -v screen &> /dev/null; then
        echo -e "${YELLOW}[!] screen not found. Installing...${NC}"
        sudo apt update && sudo apt install -y screen
    fi
    
    echo -e "${GREEN}[+] Using screen${NC}"
    
    screen -S "$APP_NAME" -X quit 2>/dev/null
    
    echo -e "${YELLOW}[*] Starting $APP_NAME with screen...${NC}"
    screen -dmS "$APP_NAME" bash -c "source $VENV_DIR/bin/activate && python $SCRIPT_DIR/main.py"
    
    echo -e "${GREEN}[+] Bot started with screen${NC}"
    echo -e "${YELLOW}    Attach:    screen -r $APP_NAME${NC}"
    echo -e "${YELLOW}    Detach:    Ctrl+A then D${NC}"
    echo -e "${YELLOW}    Stop bot:  screen -S $APP_NAME -X quit${NC}"
fi

echo ""
echo -e "${GREEN}[+] Done!${NC}"
