#!/bin/sh
set -eu
PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
MODEL_NAMES="vosk-model-small-en-us-0.15 vosk-model-small-hi-0.22 vosk-model-small-en-in-0.4"
MODEL_HOME="$HOME/.local/share/jarvis"
CONFIG_HOME="$HOME/.config/jarvis"
AUTOSTART_HOME="$HOME/.config/autostart"

python3 -m venv --system-site-packages "$PROJECT_DIR/.venv"
"$PROJECT_DIR/.venv/bin/pip" install -e "$PROJECT_DIR"
mkdir -p "$MODEL_HOME" "$CONFIG_HOME" "$AUTOSTART_HOME"
for MODEL_NAME in $MODEL_NAMES; do
    if [ ! -d "$MODEL_HOME/$MODEL_NAME" ]; then
        ARCHIVE=$(mktemp)
        curl -fL --retry 3 "https://alphacephei.com/vosk/models/$MODEL_NAME.zip" -o "$ARCHIVE"
        unzip -q "$ARCHIVE" -d "$MODEL_HOME"
        rm -f "$ARCHIVE"
    fi
done
if [ ! -f "$CONFIG_HOME/config.toml" ]; then
    cp "$PROJECT_DIR/config.example.toml" "$CONFIG_HOME/config.toml"
fi
cat > "$AUTOSTART_HOME/jarvis.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Jarvis voice assistant
Comment=Wait for the local Jarvis wake phrase
Exec=$PROJECT_DIR/run-jarvis
Terminal=false
X-GNOME-Autostart-enabled=true
X-GNOME-Autostart-Delay=8
EOF
chmod +x "$PROJECT_DIR/run-jarvis"
printf 'Installed. Log out and back in, or run %s/run-jarvis now.\n' "$PROJECT_DIR"
