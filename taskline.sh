#!/usr/bin/env bash

set -e

APP_NAME="TaskLine"
REPO_DIR="$HOME/$APP_NAME"
VENV_DIR="$REPO_DIR/venv"
CLI_LINK="/usr/local/bin/taskline"

function install_app() {
    echo "Installing $APP_NAME CLI..."

    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv venv
        echo "Virtual environment created."
    fi

    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip
    pip install -r requirements.txt
    deactivate
    echo "Dependencies installed."

    if [ ! -f "$CLI_LINK" ]; then
        sudo ln -s "$REPO_DIR/cli.py" "$CLI_LINK"
        sudo chmod +x "$REPO_DIR/cli.py"
        echo "CLI command linked: taskline"
    fi

    echo "$APP_NAME installed successfully!"
}

function uninstall_app() {
    echo "Uninstalling $APP_NAME CLI..."

    if [ -f "$CLI_LINK" ]; then
        sudo rm "$CLI_LINK"
        echo "Removed CLI symlink."
    fi

    if [ -d "$VENV_DIR" ]; then
        rm -rf "$VENV_DIR"
        echo "Removed virtual environment."
    fi

    if [ -d "$REPO_DIR" ]; then
        rm -rf "$REPO_DIR"
        echo "Removed repository folder."
    fi

    echo "$APP_NAME uninstalled successfully!"
}

function usage() {
    echo "Usage: $0 {install|uninstall}"
    exit 1
}

# Check command
if [ "$#" -ne 1 ]; then
    usage
fi

case "$1" in
    install)
        install_app
        ;;
    uninstall)
        uninstall_app
        ;;
    *)
        usage
        ;;
esac
