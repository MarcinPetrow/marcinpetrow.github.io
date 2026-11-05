#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
BLOG_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
TARGET_DIR=${XDG_DATA_HOME:-"$HOME/.local/share"}/applications
TARGET="$TARGET_DIR/io.boldmerge.BlogEditor.desktop"
mkdir -p "$TARGET_DIR"
sed "s|^Exec=.*|Exec=$BLOG_ROOT/editor/blog-editor|" \
  "$SCRIPT_DIR/io.boldmerge.BlogEditor.desktop" > "$TARGET"
chmod 644 "$TARGET"
echo "Installed application launcher: $TARGET"
