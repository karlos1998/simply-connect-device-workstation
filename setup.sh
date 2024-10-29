#!/bin/bash

REPO_DIR="$(pwd)"
GIT_REPO="https://github.com/yourusername/simply-connect-device-workstation.git"
PYTHON_EXEC="python3"
MAIN_SCRIPT="main.py"

function install_dependencies {
    echo "Installing dependencies..."
    sudo apt-get update
    sudo apt-get install -y ffmpeg
    pip install -r requirements.txt
}

function start {
    echo "Starting the application..."
    $PYTHON_EXEC $MAIN_SCRIPT
}

function start_background {
    echo "Starting the application in background..."
    sleep 30
    nohup $PYTHON_EXEC $MAIN_SCRIPT > /dev/null 2>&1 &
    echo "Application started in background."
}

function install_crontab {
    # Komenda do uruchomienia setup.sh z argumentem start-background po restarcie
    CRON_JOB="@reboot cd $REPO_DIR && ./setup.sh start-background"

    # Sprawdź, czy zadanie już istnieje w crontab
    if crontab -l | grep -Fxq "$CRON_JOB"; then
        echo "Crontab entry already exists: Application is set to start 1 minute after reboot."
    else
        # Dodaj zadanie do crontab, jeśli jeszcze go nie ma
        (crontab -l; echo "$CRON_JOB") | crontab -
        echo "Crontab entry added: Application will start 1 minute after reboot."
    fi
}

function update_repo {
    echo "Updating repository..."
    git pull
}

case "$1" in
    start)
        start
        ;;
    start-background)
        start_background
        ;;
    install-crontab)
        install_crontab
        ;;
    update)
        update_repo
        ;;
    *)
        echo "Usage: $0 {start|start-background|install-crontab|update}"
        exit 1
esac
