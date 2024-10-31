#!/bin/bash

REPO_DIR="$(pwd)"
GIT_REPO="https://github.com/karlos1998/simply-connect-device-workstation"
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
    CRON_JOB="@reboot cd $REPO_DIR && ./setup.sh start-background"
    if crontab -l | grep -Fxq "$CRON_JOB"; then
        echo "Crontab entry already exists: Application is set to start 1 minute after reboot."
    else
        (crontab -l; echo "$CRON_JOB") | crontab -
        echo "Crontab entry added: Application will start 1 minute after reboot."
    fi
}

function update_repo {
    echo "Updating repository..."
    git fetch origin
    git reset --hard origin/main
}

function check_background {
    if pgrep -f "$MAIN_SCRIPT" > /dev/null; then
        echo "Application is running in background."
    else
        echo "Application is not running in background."
    fi
}

function stop_background {
    if pkill -f "$MAIN_SCRIPT"; then
        echo "Application stopped."
    else
        echo "Application is not running."
    fi
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
    check-background)
        check_background
        ;;
    stop-background)
        stop_background
        ;;
    *)
        echo "Usage: $0 {start|start-background|install-crontab|update|check-background|stop-background}"
        exit 1
esac
