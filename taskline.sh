#!/bin/bash
# Taskline installer/uninstaller
# Usage:
#   ./taskline.sh install
#   ./taskline.sh uninstall

INSTALL_DIR="$HOME/.local/bin"
VENV_DIR="$HOME/.taskline_venv"
TASKLINE="$INSTALL_DIR/taskline"

mkdir -p "$INSTALL_DIR"

case "$1" in
  install)
    # Create virtual environment
    if [ ! -d "$VENV_DIR" ]; then
      python3 -m venv "$VENV_DIR"
      echo "Created virtual environment at $VENV_DIR"
    fi

    # Install dependencies
    "$VENV_DIR/bin/pip" install --upgrade pip
    "$VENV_DIR/bin/pip" install requests

    # Create wrapper executable
    cat > "$TASKLINE" <<EOL
#!/usr/bin/env bash
"$VENV_DIR/bin/python" "$(pwd)/cli.py" "\$@"
EOL

    chmod +x "$TASKLINE"
    echo "Taskline CLI installed at $TASKLINE"
    echo "Add $INSTALL_DIR to PATH to use 'taskline' globally."
    ;;
    
  uninstall)
    rm -f "$TASKLINE"
    rm -rf "$VENV_DIR"
    echo "Taskline uninstalled."
    ;;
    
  *)
    echo "Usage: $0 install | uninstall"
    exit 1
    ;;
esac
